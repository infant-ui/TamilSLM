const express = require("express");
const cors = require("cors");
const { exec, execFile } = require("child_process");
const path = require("path");
const Redis = require("ioredis");
const fs = require("fs");
const multer = require("multer");

const app = express();

app.use(cors());
app.use(express.json());

// Serve textbook PDF files statically from the data directory
app.use("/pdf", express.static(path.join(__dirname, "..", "..", "data")));

// Setup Multer for memory upload handling
const upload = multer({ storage: multer.memoryStorage() });

// ── REDIS CONNECTION (WITH RESILIENT FALLBACK) ──
const redis = new Redis({
    host: "127.0.0.1",
    port: 6379,
    maxRetriesPerRequest: 1,
    retryStrategy: () => null // Do not retry continuously, fail quickly and fallback
});

let isRedisConnected = false;
redis.on("connect", () => {
    isRedisConnected = true;
    console.log("💾 Redis connection established.");
});
redis.on("error", (err) => {
    isRedisConnected = false;
    console.warn("⚠️ Redis not running. Falling back to in-memory caching & direct execution.");
});

// In-Memory Fallback Cache & Job Stores
const memoryCache = new Map();
const memoryHistory = new Map();
const jobMap = new Map();

// Service Endpoints
const RETRIEVAL_URL = "http://127.0.0.1:8000/retrieve";
const GENERATION_STREAM_URL = "http://127.0.0.1:8001/generate/stream";

// ── 1. SSE STREAMING CHAT ROUTE ──
app.post("/query/stream", async (req, res) => {
    console.log("📥 SSE Stream Request Received:", req.body);
    const { 
        query, 
        language, 
        sessionId,
        class_id, 
        term, 
        preferred_medium, 
        allowed_content_types,
        include_previous_years,
        fallback_language_allowed,
        top_k,
        explicit_intent 
    } = req.body;

    if (!query || !language || !sessionId) {
        return res.status(400).json({ error: "Missing query, language, or sessionId" });
    }

    // A. Session-level filters memory using Redis or In-Memory fallback
    let activeClassId = null;
    let activeTerm = null;
    let activeMedium = null;
    let activeSubject = null;

    const sessionFilterKey = `session:filters:${sessionId}`;

    const reqClass = (class_id !== undefined && class_id !== null) ? parseInt(class_id) : null;
    const reqTerm = (term !== undefined && term !== null) ? parseInt(term) : null;
    const reqMedium = preferred_medium || null;
    const reqSubject = req.body.subject || null;

    // If any filter is explicitly specified, store it in session memory
    if (reqClass !== null || reqTerm !== null || reqMedium !== null || reqSubject !== null) {
        activeClassId = reqClass;
        activeTerm = reqTerm;
        activeMedium = reqMedium || (language.toLowerCase() === "tamil" ? "tamil" : "english");
        activeSubject = reqSubject || "auto";

        const filterData = {
            class_id: activeClassId,
            term: activeTerm,
            preferred_medium: activeMedium,
            subject: activeSubject
        };

        if (isRedisConnected) {
            await redis.set(sessionFilterKey, JSON.stringify(filterData), "EX", 1800); // Expires in 30 mins
        } else {
            memoryCache.set(sessionFilterKey, filterData);
        }
    } else {
        // Otherwise, reload filters from session memory
        let cachedFilters = null;
        if (isRedisConnected) {
            const raw = await redis.get(sessionFilterKey);
            if (raw) cachedFilters = JSON.parse(raw);
        } else {
            cachedFilters = memoryCache.get(sessionFilterKey);
        }

        if (cachedFilters) {
            activeClassId = cachedFilters.class_id;
            activeTerm = cachedFilters.term;
            activeMedium = cachedFilters.preferred_medium;
            activeSubject = cachedFilters.subject;
            console.log("🔄 Restored session filters:", cachedFilters);
        } else {
            activeClassId = null;
            activeTerm = null;
            activeMedium = language.toLowerCase() === "tamil" ? "tamil" : "english";
            activeSubject = "auto";
        }
    }

    const activeContentTypes = allowed_content_types || ["textbook", "guide"];
    const activeIncludePrevYears = include_previous_years !== undefined ? !!include_previous_years : false;
    const activeFallbackAllowed = fallback_language_allowed !== undefined ? !!fallback_language_allowed : false;
    const activeTopK = top_k !== undefined ? parseInt(top_k) : 3;

    // A.5 Intent Routing
    let intent = "Chat";
    if (explicit_intent === "image") {
        intent = "Image";
    } else {
        try {
            const intentRes = await fetch("http://localhost:8001/router/intent", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query })
            });
            if (intentRes.ok) {
                const data = await intentRes.json();
                intent = data.intent || "Chat";
            }
        } catch (err) {
            console.error("❌ Intent Router failed:", err.message);
        }
    }

    // Set SSE headers
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.flushHeaders();

    if (intent === "Image") {
        res.write(`data: ${JSON.stringify({ intent: "Image" })}\n\n`);
        try {
            const imgRes = await fetch("http://localhost:8001/generate/image", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "x-generation-service-admin-key": "dev-generation-secret-key-123"
                },
                body: JSON.stringify({ prompt: query, medium: language })
            });
            const data = await imgRes.json();
            if (data.success && data.image_path) {
                const parts = data.image_path.replace(/\\/g, "/").split("generated-images/");
                const imageUrl = parts.length > 1 ? `http://localhost:8001/images/${parts[1]}` : "";
                res.write(`data: ${JSON.stringify({ image_url: imageUrl })}\n\n`);
            } else {
                res.write(`data: ${JSON.stringify({ error: data.message || "Image generation failed" })}\n\n`);
            }
        } catch (err) {
            res.write(`data: ${JSON.stringify({ error: "Image service unreachable" })}\n\n`);
        }
        res.write("data: [DONE]\n\n");
        return res.end();
    }

    // Cache key incorporates all filters to avoid conflicts
    const cacheKey = `cache:query:${activeClassId}:${activeTerm}:${activeMedium}:${activeSubject}:${activeIncludePrevYears}:${activeFallbackAllowed}:${query.trim().toLowerCase()}`;

    try {
        // B. Check Cache
        let cachedAnswer = null;
        if (isRedisConnected) {
            cachedAnswer = await redis.get(cacheKey);
        } else {
            cachedAnswer = memoryCache.get(cacheKey);
        }

        if (cachedAnswer) {
            console.log("⚡ Cache hit!");
            res.write(`data: ${JSON.stringify({ token: cachedAnswer })}\n\n`);
            res.write("data: [DONE]\n\n");
            return res.end();
        }

        // C. Fetch session history summary
        let historySummary = "";
        if (isRedisConnected) {
            const rawHist = await redis.lrange(`session:history:${sessionId}`, 0, -1);
            if (rawHist && rawHist.length > 0) {
                historySummary = rawHist.map(item => {
                    try {
                        const parsed = JSON.parse(item);
                        return `${parsed.role}: ${parsed.text}`;
                    } catch (e) {
                        return "";
                    }
                }).filter(Boolean).join("\n");
            }
        } else {
            const hist = memoryHistory.get(sessionId) || [];
            historySummary = hist.map(h => `${h.role}: ${h.text}`).join("\n");
        }

        // D. Fetch context and system prompt from Retrieval Service
        console.log("🔍 Querying Retrieval Service...");
        let retrievalData = null;
        try {
            const retrieveRes = await fetch(RETRIEVAL_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question: query,
                    detected_language: language,
                    class_id: activeClassId,
                    subject: activeSubject,
                    term: activeTerm,
                    preferred_medium: activeMedium,
                    allowed_content_types: activeContentTypes,
                    include_previous_years: activeIncludePrevYears,
                    fallback_language_allowed: activeFallbackAllowed,
                    top_k: activeTopK
                })
            });
            if (retrieveRes.ok) {
                retrievalData = await retrieveRes.json();
            } else {
                console.error("❌ Retrieval API returned error:", retrieveRes.status);
            }
        } catch (err) {
            console.error("❌ Retrieval Service communication failed:", err.message);
        }

        const chunks = (retrievalData && retrievalData.results) ? retrievalData.results : [];
        const contextText = chunks.map(c => c.text).join("\n");
        const resolvedMedium = (retrievalData && retrievalData.medium) ? retrievalData.medium : activeMedium;
        const systemPrompt = (retrievalData && retrievalData.diagnostics && retrievalData.diagnostics.system_prompt)
            ? retrievalData.diagnostics.system_prompt
            : null;

        // Write retrieved source citations back to client immediately
        res.write(`data: ${JSON.stringify({ 
            sources: chunks,
            fallback_applied: retrievalData ? retrievalData.fallback_applied : false,
            resolved_medium: resolvedMedium
        })}\n\n`);

        // E. Call Generation Service for streaming
        console.log("🧠 Querying Generation Service stream...");
        const genRes = await fetch(GENERATION_STREAM_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query,
                context: contextText,
                language: resolvedMedium === "tamil" ? "tamil" : "english",
                history_summary: historySummary,
                system_prompt: systemPrompt // Dynamic tutor prompt
            })
        });

        if (!genRes.ok || !genRes.body) {
            throw new Error(`Generation Service error: ${genRes.statusText}`);
        }

        const reader = genRes.body.getReader();
        const decoder = new TextDecoder();
        let completeAnswer = "";
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop(); // keep last incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const cleanJSON = line.substring(6).trim();
                    if (!cleanJSON) continue;
                    try {
                        const parsed = JSON.parse(cleanJSON);
                        if (parsed.token) {
                            completeAnswer += parsed.token;
                            res.write(`data: ${JSON.stringify({ token: parsed.token })}\n\n`);
                        }
                        if (parsed.error) {
                            res.write(`data: ${JSON.stringify({ error: parsed.error })}\n\n`);
                        }
                    } catch (e) {
                        // Handle fragmented JSON
                    }
                }
            }
        }

        res.write("data: [DONE]\n\n");
        res.end();

        // F. Save to Cache and history (Asynchronously in background)
        if (completeAnswer.trim()) {
            if (isRedisConnected) {
                await redis.set(cacheKey, completeAnswer, "EX", 86400); // Cache for 24h
                const histKey = `session:history:${sessionId}`;
                await redis.rpush(histKey, JSON.stringify({ role: "user", text: query }));
                await redis.rpush(histKey, JSON.stringify({ role: "assistant", text: completeAnswer }));
                await redis.ltrim(histKey, -6, -1); // Keep last 6 turns
            } else {
                memoryCache.set(cacheKey, completeAnswer);
                const hist = memoryHistory.get(sessionId) || [];
                hist.push({ role: "user", text: query });
                hist.push({ role: "assistant", text: completeAnswer });
                if (hist.length > 6) hist.splice(0, hist.length - 6);
                memoryHistory.set(sessionId, hist);
            }
        }

    } catch (error) {
        console.error("🔥 Stream Route Error:", error);
        res.write(`data: ${JSON.stringify({ error: error.message })}\n\n`);
        res.end();
    }
});

// ── 2. BACKWARD-COMPATIBLE SYNCHRONOUS ROUTE ──
app.post("/query", async (req, res) => {
    console.log("📥 Sync Request Received:", req.body);
    const { 
        query, 
        language,
        class_id, 
        term, 
        preferred_medium, 
        allowed_content_types,
        include_previous_years,
        fallback_language_allowed,
        top_k 
    } = req.body;

    if (!query || !language) {
        return res.status(400).json({ error: "Missing query or language" });
    }

    const activeClassId = (class_id !== undefined && class_id !== null) ? parseInt(class_id) : null;
    const activeTerm = (term !== undefined && term !== null) ? parseInt(term) : null;
    const activeMedium = preferred_medium || (language.toLowerCase() === "tamil" ? "tamil" : "english");
    const activeContentTypes = allowed_content_types || ["textbook", "guide"];
    const activeIncludePrevYears = include_previous_years !== undefined ? !!include_previous_years : false;
    const activeFallbackAllowed = fallback_language_allowed !== undefined ? !!fallback_language_allowed : false;
    const activeTopK = top_k !== undefined ? parseInt(top_k) : 3;
    const activeSubject = req.body.subject || "auto";

    try {
        // Fetch context
        let retrievalData = null;
        try {
            const retrieveRes = await fetch(RETRIEVAL_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question: query,
                    detected_language: language,
                    class_id: activeClassId,
                    subject: activeSubject,
                    term: activeTerm,
                    preferred_medium: activeMedium,
                    allowed_content_types: activeContentTypes,
                    include_previous_years: activeIncludePrevYears,
                    fallback_language_allowed: activeFallbackAllowed,
                    top_k: activeTopK
                })
            });
            if (retrieveRes.ok) {
                retrievalData = await retrieveRes.json();
            }
        } catch (err) {
            console.error("Retrieval failed:", err.message);
        }

        const chunks = (retrievalData && retrievalData.results) ? retrievalData.results : [];
        const contextText = chunks.map(c => c.text).join("\n");
        const resolvedMedium = (retrievalData && retrievalData.medium) ? retrievalData.medium : activeMedium;
        const systemPrompt = (retrievalData && retrievalData.diagnostics && retrievalData.diagnostics.system_prompt)
            ? retrievalData.diagnostics.system_prompt
            : null;

        // Query stream and consolidate it
        const genRes = await fetch(GENERATION_STREAM_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query,
                context: contextText,
                language: resolvedMedium === "tamil" ? "tamil" : "english",
                history_summary: "",
                system_prompt: systemPrompt
            })
        });

        if (!genRes.ok || !genRes.body) {
            throw new Error(`Generation Service error: ${genRes.statusText}`);
        }

        const reader = genRes.body.getReader();
        const decoder = new TextDecoder();
        let completeAnswer = "";
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const cleanJSON = line.substring(6).trim();
                    if (!cleanJSON) continue;
                    try {
                        const parsed = JSON.parse(cleanJSON);
                        if (parsed.token) {
                            completeAnswer += parsed.token;
                        }
                    } catch (e) {}
                }
            }
        }

        res.json({ answer: completeAnswer || "No response generated" });

    } catch (error) {
        console.error("🔥 Sync Router Error:", error);
        res.status(500).json({ error: error.message });
    }
});

// ── 3. ASYNC MINDMAP GENERATION ROUTE ──
app.post("/mindmap/generate", async (req, res) => {
    const { text, language } = req.body;

    if (!text) {
        return res.status(400).json({ error: "Missing text for mindmap" });
    }

    const jobId = "job_" + Math.random().toString(36).substring(2, 15);
    const lang = language || "english";

    console.log(`🌀 Enqueueing mindmap job ${jobId} (lang: ${lang})`);

    // Set job status to pending
    const jobInfo = { status: "pending", data: null, error: null };
    jobMap.set(jobId, jobInfo);
    if (isRedisConnected) {
        await redis.set(`mindmap:job:${jobId}`, JSON.stringify(jobInfo), "EX", 1800); // 30 min expiration
    }

    // Trigger Python background execution asynchronously
    let pythonPath = path.join(__dirname, "..", "..", ".venv", "Scripts", "python.exe");
    // Handle standard fallback for Linux/macOS environments using bin/python
    if (!fs.existsSync(pythonPath)) {
        pythonPath = path.join(__dirname, "..", "..", ".venv", "bin", "python");
    }
    const scriptPath = path.join(__dirname, "..", "..", "Mindmap-20260625T150611Z-3-001", "Mindmap", "predict_json.py");
    const cacheDir = path.join(__dirname, "temp_jobs");
    
    if (!fs.existsSync(cacheDir)){
        fs.mkdirSync(cacheDir);
    }
    const outputFilePath = path.join(cacheDir, `${jobId}.json`);

    // Ensure parameters are sanitized and validated to prevent command injection and ensure type safety
    const sanitizedLang = typeof lang === "string" ? lang.replace(/[^a-zA-Z0-9_-]/g, "") : "english";
    const sanitizedText = typeof text === "string" ? text : "";

    console.log("🚀 Spawning background mindmap job:", jobId);

    // Validate that python and the script actually exist before trying to execute them.
    if (!fs.existsSync(pythonPath)) {
        const errorMsg = `Python executable not found at: ${pythonPath}`;
        console.error(`❌ Background Job ${jobId} failed:`, errorMsg);
        const errorInfo = { status: "failed", data: null, error: errorMsg };
        jobMap.set(jobId, errorInfo);
        if (isRedisConnected) {
            redis.set(`mindmap:job:${jobId}`, JSON.stringify(errorInfo), "EX", 1800).catch(err => {
                console.error("Redis set error:", err);
            });
        }
    } else if (!fs.existsSync(scriptPath)) {
        const errorMsg = `Python script not found at: ${scriptPath}`;
        console.error(`❌ Background Job ${jobId} failed:`, errorMsg);
        const errorInfo = { status: "failed", data: null, error: errorMsg };
        jobMap.set(jobId, errorInfo);
        if (isRedisConnected) {
            redis.set(`mindmap:job:${jobId}`, JSON.stringify(errorInfo), "EX", 1800).catch(err => {
                console.error("Redis set error:", err);
            });
        }
    } else {
        // Safe process execution using execFile (which executes the binary directly without spawning a shell, preventing shell injection)
        execFile(pythonPath, [scriptPath, sanitizedText, sanitizedLang, outputFilePath], async (err, stdout, stderr) => {
            if (err) {
                console.error(`❌ Background Job ${jobId} failed:`, err.message);
                const failedInfo = { status: "failed", data: null, error: err.message };
                jobMap.set(jobId, failedInfo);
                if (isRedisConnected) {
                    await redis.set(`mindmap:job:${jobId}`, JSON.stringify(failedInfo), "EX", 1800);
                }
                return;
            }
            
            console.log(`✅ Background Job ${jobId} execution completed.`);
            try {
                if (fs.existsSync(outputFilePath)) {
                    const rawData = fs.readFileSync(outputFilePath, "utf-8");
                    const graphJSON = JSON.parse(rawData);
                    const completeInfo = { status: "completed", data: graphJSON, error: null };
                    
                    jobMap.set(jobId, completeInfo);
                    if (isRedisConnected) {
                        await redis.set(`mindmap:job:${jobId}`, JSON.stringify(completeInfo), "EX", 1800);
                    }
                    
                    // delete temporary file
                    fs.unlinkSync(outputFilePath);
                } else {
                    throw new Error("Output JSON file was not generated");
                }
            } catch (e) {
                console.error(`❌ Error parsing background job output:`, e.message);
                const errorInfo = { status: "failed", data: null, error: e.message };
                jobMap.set(jobId, errorInfo);
                if (isRedisConnected) {
                    await redis.set(`mindmap:job:${jobId}`, JSON.stringify(errorInfo), "EX", 1800);
                }
            }
        });
    }

    // Return job ID immediately to client
    res.status(202).json({ jobId, status: "pending" });
});

// ── 4. MINDMAP JOB STATUS ROUTE ──
app.get("/mindmap/status/:jobId", async (req, res) => {
    const { jobId } = req.params;
    
    try {
        let jobInfo = null;
        if (isRedisConnected) {
            const raw = await redis.get(`mindmap:job:${jobId}`);
            if (raw) jobInfo = JSON.parse(raw);
        } else {
            jobInfo = jobMap.get(jobId);
        }

        if (!jobInfo) {
            return res.status(404).json({ error: "Job not found" });
        }

        res.json(jobInfo);

    } catch (err) {
        console.error("Error retrieving job status:", err);
        res.status(500).json({ error: err.message });
    }
});

// ── 5. PROXIED RESOURCE UPLOAD ENDPOINT ──
app.post("/api/upload", upload.single("file"), async (req, res) => {
    console.log("📥 Upload proxy request received.");
    try {
        if (!req.file) {
            return res.status(400).json({ error: "No file uploaded" });
        }
        
        const formData = new FormData();
        const blob = new Blob([req.file.buffer], { type: req.file.mimetype });
        formData.append("file", blob, req.file.originalname);
        
        if (req.body.class_id) formData.append("class_id", req.body.class_id);
        if (req.body.subject) formData.append("subject", req.body.subject);
        if (req.body.medium) formData.append("medium", req.body.medium);
        if (req.body.content_type) formData.append("content_type", req.body.content_type);
        if (req.body.term) formData.append("term", req.body.term);

        const response = await fetch("http://127.0.0.1:8000/upload", {
            method: "POST",
            body: formData
        });
        
        const data = await response.json();
        if (response.ok) {
            res.json(data);
        } else {
            res.status(response.status).json(data);
        }
    } catch (err) {
        console.error("Proxy upload error:", err);
        res.status(500).json({ error: err.message });
    }
});

// ── 6. PROXIED TEACHER FEEDBACK ENDPOINT ──
app.post("/api/feedback", async (req, res) => {
    console.log("📥 Feedback proxy request received.");
    try {
        const response = await fetch("http://127.0.0.1:8000/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(req.body)
        });
        const data = await response.json();
        if (response.ok) {
            res.json(data);
        } else {
            res.status(response.status).json(data);
        }
    } catch (err) {
        console.error("Proxy feedback error:", err);
        res.status(500).json({ error: err.message });
    }
});

// ── 7. PROXIED EVALUATION DASHBOARD ENDPOINT ──
app.get("/api/evaluation/dashboard", async (req, res) => {
    try {
        const response = await fetch("http://127.0.0.1:8000/evaluation/dashboard");
        const data = await response.json();
        if (response.ok) {
            res.json(data);
        } else {
            res.status(response.status).json(data);
        }
    } catch (err) {
        console.error("Proxy dashboard error:", err);
        res.status(500).json({ error: err.message });
    }
});

// Start Server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`🚀 API Gateway running on http://127.0.0.1:${PORT}`);
});