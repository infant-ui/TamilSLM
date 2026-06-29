import React, { useState, useEffect, useRef } from "react";
import "./App.css";

// ── CUSTOM INTERACTIVE SVG GRAPH RENDERER ──
// Renders nodes and edges dynamically with simple physics layout or hierarchical positioning.
const MindmapGraph = ({ graphData }) => {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [draggedNode, setDraggedNode] = useState(null);
  const [positions, setPositions] = useState({});
  const isDraggingCanvas = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });

  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];
  const graphType = graphData?.type || "concept";

  // Initialize node positions based on type
  useEffect(() => {
    if (!nodes.length) return;
    const initialPos = {};
    const width = 800;
    const height = 500;

    if (graphType === "hierarchical") {
      // Tree layout: root at top, children spaced out below
      const levels = {};
      nodes.forEach((n, idx) => {
        // Simple assignment: root is the first one
        if (idx === 0) levels[n.id] = { x: width / 2, y: 80, level: 0 };
      });

      // Find children by edges
      let currentLevel = 1;
      let unresolved = [...nodes.slice(1)];
      let parents = [nodes[0].id];

      while (unresolved.length > 0 && currentLevel < 10) {
        const nextParents = [];
        parents.forEach(pId => {
          const children = edges.filter(e => e.source === pId).map(e => e.target);
          children.forEach((cId, cIdx) => {
            const nodeIdx = unresolved.findIndex(n => n.id === cId);
            if (nodeIdx !== -1) {
              const xSpac = width / (children.length + 1);
              initialPos[cId] = {
                x: (cIdx + 1) * xSpac + (Math.random() - 0.5) * 20,
                y: 80 + currentLevel * 100,
                level: currentLevel
              };
              nextParents.push(cId);
              unresolved.splice(nodeIdx, 1);
            }
          });
        });
        if (nextParents.length === 0) {
          // fallback for orphans
          unresolved.forEach((n, idx) => {
            initialPos[n.id] = { x: 100 + idx * 120, y: 250, level: 2 };
          });
          break;
        }
        parents = nextParents;
        currentLevel++;
      }
      initialPos[nodes[0].id] = { x: width / 2, y: 80, level: 0 };
      setPositions(initialPos);

    } else if (graphType === "process") {
      // Horizontal chain layout
      nodes.forEach((n, idx) => {
        initialPos[n.id] = {
          x: 100 + idx * (width / (nodes.length || 1)),
          y: height / 2 + (idx % 2 === 0 ? 30 : -30)
        };
      });
      setPositions(initialPos);

    } else {
      // Circular or spring fallback for concept maps
      const radius = 160;
      nodes.forEach((n, idx) => {
        const angle = (idx * 2 * Math.PI) / nodes.length;
        initialPos[n.id] = {
          x: width / 2 + radius * Math.cos(angle),
          y: height / 2 + radius * Math.sin(angle)
        };
      });
      setPositions(initialPos);
    }
  }, [graphData]);

  // Handle Dragging Canvas (Panning)
  const handleMouseDown = (e) => {
    if (e.target.tagName === "svg" || e.target.id === "grid-overlay") {
      isDraggingCanvas.current = true;
      dragStart.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
    }
  };

  const handleMouseMove = (e) => {
    if (isDraggingCanvas.current) {
      setPan({
        x: e.clientX - dragStart.current.x,
        y: e.clientY - dragStart.current.y
      });
    } else if (draggedNode) {
      const rect = e.currentTarget.getBoundingClientRect();
      const x = (e.clientX - rect.left - pan.x) / zoom;
      const y = (e.clientY - rect.top - pan.y) / zoom;
      setPositions(prev => ({
        ...prev,
        [draggedNode]: { x, y }
      }));
    }
  };

  const handleMouseUp = () => {
    isDraggingCanvas.current = false;
    setDraggedNode(null);
  };

  const handleZoom = (factor) => {
    setZoom(prev => Math.min(Math.max(prev * factor, 0.4), 2.5));
  };

  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  return (
    <div className="graph-panel">
      <div className="graph-toolbar">
        <span className="graph-title-badge">MINDMAP: {graphType.toUpperCase()}</span>
        <div className="toolbar-btns">
          <button className="tb-btn" onClick={() => handleZoom(1.25)} title="Zoom In">+</button>
          <button className="tb-btn" onClick={() => handleZoom(0.8)} title="Zoom Out">-</button>
          <button className="tb-btn" onClick={handleReset} title="Reset Position">⟲</button>
        </div>
      </div>

      <div 
        className="graph-canvas-container"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <svg className="graph-svg" width="100%" height="100%">
          <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
            </pattern>
            <marker id="arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--cyan)" />
            </marker>
          </defs>
          <rect id="grid-overlay" width="100%" height="100%" fill="url(#grid)" />

          <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
            {/* Edges */}
            {edges.map((e, idx) => {
              const start = positions[e.source];
              const end = positions[e.target];
              if (!start || !end) return null;
              
              // Draw line
              return (
                <g key={idx}>
                  <line
                    x1={start.x}
                    y1={start.y}
                    x2={end.x}
                    y2={end.y}
                    stroke="var(--cyan)"
                    strokeWidth="1.5"
                    strokeOpacity="0.4"
                    markerEnd="url(#arrow)"
                  />
                  {e.label && e.label !== "sub" && e.label !== "next" && (
                    <text
                      x={(start.x + end.x) / 2}
                      y={(start.y + end.y) / 2 - 5}
                      fill="var(--muted)"
                      fontSize="9"
                      textAnchor="middle"
                      className="edge-label"
                    >
                      {e.label}
                    </text>
                  )}
                </g>
              );
            })}

            {/* Nodes */}
            {nodes.map((node) => {
              const pos = positions[node.id] || { x: 100, y: 100 };
              const isRoot = graphType === "hierarchical" && pos.level === 0;
              
              return (
                <g 
                  key={node.id}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  className={`node-group ${isRoot ? "node-root-group" : ""}`}
                  onMouseDown={(e) => {
                    e.stopPropagation();
                    setDraggedNode(node.id);
                  }}
                  style={{ cursor: "grab" }}
                >
                  <rect
                    x="-65"
                    y="-18"
                    width="130"
                    height="36"
                    rx="8"
                    className={`graph-node-rect ${isRoot ? "node-rect-root" : ""}`}
                  />
                  <text
                    y="3"
                    textAnchor="middle"
                    fill="#ffffff"
                    fontSize="10"
                    fontWeight="500"
                    className="graph-node-text"
                  >
                    {node.label.length > 20 ? node.label.slice(0, 18) + "..." : node.label}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>
      </div>
    </div>
  );
};

// ── SINGLE CHAT MESSAGE BUBBLE ──
const MessageBubble = ({ msg, onGenerateMindmap, activeJob }) => {
  const isUser = msg.role === "user";
  
  return (
    <div className={`msg-row ${isUser ? "msg-user" : "msg-ai"}`}>
      {!isUser && (
        <div className="avatar avatar-ai">
          <svg width="14" height="14" viewBox="0 0 32 32" fill="none">
            <polygon points="16,2 30,10 30,22 16,30 2,22 2,10" stroke="var(--cyan)" strokeWidth="1.5" fill="none"/>
            <circle cx="16" cy="16" r="4" fill="var(--cyan)"/>
          </svg>
        </div>
      )}

      <div className={`bubble ${isUser ? "bubble-user" : "bubble-ai"}`}>
        {/* State Indicators */}
        {msg.status === "loading" && (
          <div className="bubble-dots">
            <span className="dot" style={{ animationDelay: "0ms" }}/>
            <span className="dot" style={{ animationDelay: "180ms" }}/>
            <span className="dot" style={{ animationDelay: "360ms" }}/>
          </div>
        )}

        {msg.status === "generating" && msg.content === "" && (
          <div className="bubble-generating">
            <span className="spinner-sm"/>
            <span>{msg.lang === "ta" ? "பதில் உருவாகிறது…" : "Scanning RAG database…"}</span>
          </div>
        )}

        {msg.status === "error" && (
          <div className="bubble-error">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {msg.content}
          </div>
        )}

        {/* Content Body */}
        {!isUser && (msg.content || msg.status === "done") && (
          <>
            <div className="lang-chip">{msg.lang === "ta" ? "தமிழ்" : "EN"}</div>
            {msg.fallback_applied && (
              <div className="fallback-indicator">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
                </svg>
                {msg.lang === "ta" 
                  ? "விடை ஆங்கில புத்தகத்திலிருந்து பெறப்பட்டது (தற்காலிக மாற்று)" 
                  : "Answer retrieved from Tamil medium (Fallback applied)"}
              </div>
            )}
            <p className="answer-text">{msg.content}</p>

            {/* Source citations drawer */}
            {msg.sources && msg.sources.length > 0 && (
              <div className="citations-list">
                <span className="citation-title">📚 CHUNKS:</span>
                {msg.sources.map((src, sIdx) => (
                  <div key={sIdx} className="citation-card" title={`Score: ${src.score.toFixed(3)}`}>
                    <span className="citation-badge">Chunk #{sIdx + 1}</span>
                    <p className="citation-body">"{src.text}"</p>
                  </div>
                ))}
              </div>
            )}

            {/* Action buttons (Mindmap Generator) */}
            {!isUser && msg.status === "done" && (
              <div className="bubble-actions">
                <button 
                  className={`btn-mindmap ${activeJob ? "btn-disabled" : ""}`}
                  onClick={() => onGenerateMindmap(msg.content)}
                  disabled={activeJob}
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
                    <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
                  </svg>
                  {activeJob ? "Generating..." : "Generate Mindmap"}
                </button>
              </div>
            )}
          </>
        )}

        {isUser && <p className="user-text">{msg.content}</p>}
      </div>

      {isUser && (
        <div className="avatar avatar-user">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
      )}
    </div>
  );
};

// ── MAIN APP CORE ──
export default function App() {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const [lang, setLang] = useState("en");
  const [busy, setBusy] = useState(false);
  const [sessionId] = useState(() => "session_" + Math.random().toString(36).substring(2, 15));

  // RAG filter states
  const [classId, setClassId] = useState(null);
  const [term, setTerm] = useState(null);
  const [includePrevYears, setIncludePrevYears] = useState(false);
  const [fallbackAllowed, setFallbackAllowed] = useState(false);

  // Mindmap background job tracking
  const [activeMindmap, setActiveMindmap] = useState(null);
  const [mindmapStatus, setMindmapStatus] = useState(null); // 'pending' | 'completed' | 'failed'
  const [mindmapJobId, setMindmapJobId] = useState(null);

  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  const busyRef = useRef(false);

  const sampleQuestions = {
    en: [
      "What is photosynthesis?",
      "Explain the process of cell division.",
      "How does gravity affect orbital motion?",
      "What are the main components of human blood?"
    ],
    ta: [
      "ஒளிச்சேர்க்கை என்றால் என்ன?",
      "செல் பிரிதல் செயல்முறையை விளக்குக.",
      "ஈர்ப்பு விசை எவ்வாறு சுற்றுப்பாதையை பாதிக்கிறது?",
      "மனித இரத்தத்தின் முக்கிய கூறுகள் யாவை?"
    ]
  };

  // Scroll to bottom on messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Mindmap Job Polling
  useEffect(() => {
    if (!mindmapJobId) return;

    let intervalId = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:5000/mindmap/status/${mindmapJobId}`);
        if (!res.ok) return;

        const info = await res.json();
        if (info.status === "completed" && info.data) {
          clearInterval(intervalId);
          setActiveMindmap(info.data);
          setMindmapStatus("completed");
          setMindmapJobId(null);
        } else if (info.status === "failed") {
          clearInterval(intervalId);
          setMindmapStatus("failed");
          setMindmapJobId(null);
        }
      } catch (err) {
        console.error("Error checking mindmap job status:", err);
      }
    }, 2000);

    return () => clearInterval(intervalId);
  }, [mindmapJobId]);

  const handleSubmit = async () => {
    const q = query.trim();
    if (!q || busyRef.current) return;
    busyRef.current = true;
    setBusy(true);
    setQuery("");

    const userMsg = { role: "user", content: q, status: "done", time: new Date().toLocaleTimeString() };
    const aiMsg = { 
      role: "ai", 
      content: "", 
      status: "loading", 
      lang: lang === "ta" ? "tamil" : "english",
      sources: [],
      time: new Date().toLocaleTimeString() 
    };

    setMessages(prev => [...prev, userMsg, aiMsg]);

    try {
      const response = await fetch("http://localhost:5000/query/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          query: q, 
          language: lang === "ta" ? "tamil" : "english", 
          sessionId,
          class_id: classId,
          term,
          preferred_medium: lang === "ta" ? "tamil" : "english",
          include_previous_years: includePrevYears,
          fallback_language_allowed: fallbackAllowed
        })
      });

      if (!response.ok) throw new Error("Gateway connection failed.");

      // Read SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let finished = false;
      let buffer = "";

      setMessages(prev => {
        if (!prev.length) return prev;
        const lastMsg = prev[prev.length - 1];
        const updatedLastMsg = { ...lastMsg, status: "generating" };
        return [...prev.slice(0, -1), updatedLastMsg];
      });

      while (!finished) {
        const { value, done } = await reader.read();
        finished = done;
        if (value) {
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop(); // keep last incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const cleanJSON = line.substring(6).trim();
              if (cleanJSON === "[DONE]") {
                finished = true;
                break;
              }
              try {
                const parsed = JSON.parse(cleanJSON);
                
                if (parsed.sources) {
                  setMessages(prev => {
                    if (!prev.length) return prev;
                    const lastMsg = prev[prev.length - 1];
                    const updatedLastMsg = {
                      ...lastMsg,
                      sources: parsed.sources,
                      fallback_applied: parsed.fallback_applied,
                      resolved_medium: parsed.resolved_medium
                    };
                    return [...prev.slice(0, -1), updatedLastMsg];
                  });
                }
                if (parsed.token) {
                  setMessages(prev => {
                    if (!prev.length) return prev;
                    const lastMsg = prev[prev.length - 1];
                    const updatedLastMsg = {
                      ...lastMsg,
                      content: lastMsg.content + parsed.token
                    };
                    return [...prev.slice(0, -1), updatedLastMsg];
                  });
                }
                if (parsed.error) {
                  throw new Error(parsed.error);
                }
              } catch (e) {
                // Ignore incomplete JSON buffers
              }
            }
          }
        }
      }

      setMessages(prev => {
        if (!prev.length) return prev;
        const lastMsg = prev[prev.length - 1];
        const updatedLastMsg = { ...lastMsg, status: "done" };
        return [...prev.slice(0, -1), updatedLastMsg];
      });

    } catch (err) {
      setMessages(prev => {
        if (!prev.length) return prev;
        const lastMsg = prev[prev.length - 1];
        const updatedLastMsg = { ...lastMsg, status: "error", content: err.message };
        return [...prev.slice(0, -1), updatedLastMsg];
      });
    } finally {
      busyRef.current = false;
      setBusy(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  // Trigger Mindmap generation
  const handleGenerateMindmap = async (text) => {
    setActiveMindmap(null);
    setMindmapStatus("pending");
    setMindmapJobId(null);

    try {
      const res = await fetch("http://localhost:5000/mindmap/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, language: lang === "ta" ? "tamil" : "english" })
      });
      if (!res.ok) throw new Error("Failed to enqueue mindmap generation");

      const info = await res.json();
      setMindmapJobId(info.jobId);
    } catch (err) {
      console.error(err);
      setMindmapStatus("failed");
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="app-root">
      <div className="bg-orb bg-orb-1" />
      <div className="bg-orb bg-orb-2" />
      <div className="bg-orb bg-orb-3" />
      <div className="scanlines" />

      <div className="main-layout">
        
        {/* LEFT COLUMN: CHAT WINDOW */}
        <div className="chat-column">
          <header className="header">
            <div className="header-left">
              <div className="logo-mark">
                <svg width="24" height="24" viewBox="0 0 32 32" fill="none">
                  <polygon points="16,2 30,10 30,22 16,30 2,22 2,10" stroke="var(--cyan)" strokeWidth="2" fill="none"/>
                  <polygon points="16,8 24,13 24,19 16,24 8,19 8,13" stroke="var(--cyan)" strokeWidth="1.2" fill="var(--cyan)" fillOpacity="0.15"/>
                  <circle cx="16" cy="16" r="3.5" fill="var(--cyan)"/>
                </svg>
              </div>
              <div>
                <h1 className="app-title">SCIQUERY v2.0</h1>
                <p className="app-subtitle">Local Service-Oriented RAG Stack</p>
              </div>
            </div>
            <div className="header-right">
              <div className={`status-pill ${busy ? "status-active" : "status-idle"}`}>
                <span className="status-dot"/>
                {busy ? "STREAMING" : "READY"}
              </div>
            </div>
          </header>

          <div className="chat-feed">
            {messages.length === 0 && (
              <div className="welcome">
                <div className="welcome-glow">
                  <svg width="60" height="60" viewBox="0 0 32 32" fill="none">
                    <polygon points="16,2 30,10 30,22 16,30 2,22 2,10" stroke="var(--cyan)" strokeWidth="1" fill="var(--cyan)" fillOpacity="0.05"/>
                    <circle cx="16" cy="16" r="5" fill="var(--cyan)" fillOpacity="0.15"/>
                  </svg>
                </div>
                <h2 className="welcome-title">Ask your Science Textbook</h2>
                <p className="welcome-sub">Toggle translation language at the bottom input bar.</p>
                <div className="chips-grid">
                  {sampleQuestions[lang].map((q, idx) => (
                    <button key={idx} className="chip" onClick={() => { setQuery(q); inputRef.current?.focus(); }}>
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <MessageBubble 
                key={i} 
                msg={msg} 
                onGenerateMindmap={handleGenerateMindmap}
                activeJob={!!mindmapJobId}
              />
            ))}
            <div ref={bottomRef}/>
          </div>

          {/* RAG Filter Controls Row */}
          <div className="filter-controls-row">
            <div className="filter-group">
              <button
                className={`filter-toggle-btn ${includePrevYears ? "active" : ""}`}
                onClick={() => setIncludePrevYears(!includePrevYears)}
                disabled={busy}
                title="Search previous year materials as a tertiary backup tier"
              >
                PYQs
              </button>
              <button
                className={`filter-toggle-btn ${fallbackAllowed ? "active" : ""}`}
                onClick={() => setFallbackAllowed(!fallbackAllowed)}
                disabled={busy}
                title="Fallback to other medium if preferred medium lacks search results"
              >
                Fallback
              </button>
            </div>
          </div>

          <div className="input-bar">
            <div className="lang-toggle" title="Switch language">
              <button className={`lang-btn ${lang === "en" ? "lang-active" : ""}`} onClick={() => setLang("en")}>EN</button>
              <button className={`lang-btn ${lang === "ta" ? "lang-active lang-ta" : ""}`} onClick={() => setLang("ta")}>த</button>
            </div>

            <textarea
              ref={inputRef}
              className="chat-input"
              placeholder={lang === "ta" ? "அறிவியல் கேள்வியை இங்கே கேளுங்கள்…" : "Ask any science textbook question…"}
              value={query}
              rows={1}
              disabled={busy}
              onChange={e => {
                setQuery(e.target.value);
                e.target.style.height = "auto";
                e.target.style.height = Math.min(e.target.scrollHeight, 100) + "px";
              }}
              onKeyDown={handleKey}
            />

            <button className="send-btn" onClick={handleSubmit} disabled={!query.trim() || busy}>
              {busy ? <span className="spinner"/> : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2.01 21 23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* RIGHT COLUMN: INTERACTIVE MINDMAP CANVAS */}
        <div className="visualizer-column">
          <div className="visualizer-header">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--cyan)" strokeWidth="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l-7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            </svg>
            <span>INTERACTIVE SCIENCE VISUALIZER</span>
          </div>

          <div className="visualizer-body">
            {mindmapStatus === "pending" && (
              <div className="vis-loader">
                <span className="spinner-large"/>
                <p>Generating interactive mindmap nodes...</p>
                <p className="vis-sub">Classifying concept structural boundaries using local Keras networks</p>
              </div>
            )}

            {mindmapStatus === "failed" && (
              <div className="vis-error">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" strokeWidth="1.5">
                  <polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/>
                  <line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <p>Failed to generate graph structure.</p>
                <button className="btn-retry" onClick={() => setMindmapStatus(null)}>Clear</button>
              </div>
            )}

            {mindmapStatus === "completed" && activeMindmap && (
              <MindmapGraph graphData={activeMindmap} />
            )}

            {!mindmapStatus && !activeMindmap && (
              <div className="vis-empty">
                <div className="vis-welcome-icon">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="1">
                    <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/>
                  </svg>
                </div>
                <h3>No Active Visualization</h3>
                <p>Ask a science question and click "Generate Mindmap" under the answer bubble to extract and explore interactive graph entities.</p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
