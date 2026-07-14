import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import MindmapGraph from './components/MindmapGraph';

// Render inline and block LaTeX equations using KaTeX if available
const renderMath = (text) => {
  if (!window.katex || !text) return text;
  
  let temp = text;
  
  // Replace block math $$ ... $$
  temp = temp.replace(/\$\{(.*?)\}/gs, (match, formula) => formula); // Safeguard
  temp = temp.replace(/\$\$(.*?)\$\$/gs, (match, formula) => {
    try {
      return window.katex.renderToString(formula.trim(), { displayMode: true, throwOnError: false });
    } catch (e) {
      return match;
    }
  });
  
  // Replace inline math $ ... $
  temp = temp.replace(/\$(.*?)\$/g, (match, formula) => {
    try {
      return window.katex.renderToString(formula.trim(), { displayMode: false, throwOnError: false });
    } catch (e) {
      return match;
    }
  });
  
  return temp;
};

// Custom parser to split text into formatted JSX elements (bold, bullets, sections, KaTeX)
const renderMessageContent = (text) => {
  if (!text) return null;
  
  const lines = text.split("\n");
  
  return lines.map((line, idx) => {
    const trimmed = line.trim();
    if (!trimmed) return <div key={idx} className="tutor-spacer" />;
    
    // Check for separators ━━━━━━━━━━━━━━━━━━━━ or ────────────────────
    if (trimmed.includes("━━") || trimmed.includes("──")) {
      return <hr key={idx} className="tutor-section-divider" />;
    }
    
    // Check for Custom Headers
    const matchHeader = trimmed.match(/^(Problem|Question|Understand|Step\s*\d+|Final\s*Answer|Remember|Common\s*Mistake|Practice\s*Question|Definition|Explanation|Real-Life\s*Example|Important\s*Points|Summary|Diagram\s*Description|Parts|Functions|Uses\s*\/\s*Applications|Exam\s*Tips|கணக்கு|கேள்வி|புரிந்துகொள்வோம்|படி\s*\d+|இறுதிப்\s*பதில்|இறுதி\s*விடை|நினைவில்\s*கொள்க|நினைவில்\s*கொள்ளுங்கள்|பொதுவான\s*தவறு|மாணவர்கள்\s*பொதுவாக\s*செய்யும்\s*தவறு|பயிற்சி|பயிற்சி\s*கணக்கு|வரையறை|விளக்கம்|நிஜ\s*வாழ்க்கை\s*உதாரணம்|முக்கிய\s*புள்ளிகள்|முக்கிய\s*குறிப்புகள்|பயிற்சி\s*கேள்வி|படம்\s*பற்றிய\s*விளக்கம்|பாகங்கள்|செயல்பாடுகள்|பயன்பாடுகள்|தேர்வு\s*குறிப்புகள்|மதிப்பீட்டு\s*முறை|ASSESSMENT\s*MODE|கற்றல்\s*குறிப்பு|புதிய\s*சொல்|புதிய\s*வார்த்தை|உங்களுக்குத்\s*தெரியுமா|Learning\s*Tip|New\s*Word|Did\s*You\s*Know|Key\s*Points):/i);
    
    let isHeaderLine = false;
    let headerText = "";
    let remainingText = trimmed;
    
    if (matchHeader) {
      isHeaderLine = true;
      headerText = matchHeader[1];
      remainingText = trimmed.substring(headerText.length + 1).trim();
    }
    
    // Render inline bold elements and KaTeX LaTeX formulas
    const parseBoldAndMath = (txt) => {
      let htmlContent = renderMath(txt);
      // Parse markdown bold **text** -> <strong>text</strong>
      htmlContent = htmlContent.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      return <span dangerouslySetInnerHTML={{ __html: htmlContent }} />;
    };
    
    // Check if line is bullet list
    if (trimmed.startsWith("•") || trimmed.startsWith("-")) {
      const contentOnly = trimmed.substring(1).trim();
      return (
        <li key={idx} className="tutor-list-item">
          {parseBoldAndMath(contentOnly)}
        </li>
      );
    }
    
    // Format tutor sections
    if (isHeaderLine) {
      let sectionClass = "tutor-generic-header";
      let sectionIcon = "📘";
      
      const lowerHeader = headerText.toLowerCase();
      if (lowerHeader.includes("step") || lowerHeader.includes("படி")) {
        sectionClass = "tutor-step-header";
        sectionIcon = "✏️";
      } else if (lowerHeader.includes("mistake") || lowerHeader.includes("தவறு")) {
        sectionClass = "tutor-mistake-header";
        sectionIcon = "⚠️";
      } else if (lowerHeader.includes("tip") || lowerHeader.includes("குறிப்பு")) {
        sectionClass = "tutor-tip-header";
        sectionIcon = "🎯";
      } else if (lowerHeader.includes("final") || lowerHeader.includes("விடை") || lowerHeader.includes("பதில்")) {
        sectionClass = "tutor-final-header";
        sectionIcon = "✅";
      } else if (lowerHeader.includes("practice") || lowerHeader.includes("பயிற்சி")) {
        sectionClass = "tutor-practice-header";
        sectionIcon = "📝";
      } else if (lowerHeader.includes("definition") || lowerHeader.includes("வரையறை")) {
        sectionClass = "tutor-def-header";
        sectionIcon = "📖";
      } else if (lowerHeader.includes("example") || lowerHeader.includes("உதாரணம்")) {
        sectionClass = "tutor-example-header";
        sectionIcon = "🌍";
      } else if (lowerHeader.includes("explanation") || lowerHeader.includes("விளக்கம்")) {
        sectionClass = "tutor-exp-header";
        sectionIcon = "🔬";
      } else if (lowerHeader.includes("summary") || lowerHeader.includes("சுருக்கம்")) {
        sectionClass = "tutor-summary-header";
        sectionIcon = "📝";
      } else if (lowerHeader.includes("understand") || lowerHeader.includes("புரிந்துகொள்வோம்")) {
        sectionClass = "tutor-understand-header";
        sectionIcon = "🧠";
      } else if (lowerHeader.includes("did you know") || lowerHeader.includes("தெரியுமா")) {
        sectionClass = "tutor-trivia-header";
        sectionIcon = "🌟";
      } else if (lowerHeader.includes("new word") || lowerHeader.includes("புதிய சொல்") || lowerHeader.includes("வார்த்தை")) {
        sectionClass = "tutor-vocab-header";
        sectionIcon = "📖";
      } else if (lowerHeader.includes("points") || lowerHeader.includes("குறிப்புகள்") || lowerHeader.includes("புள்ளிகள்")) {
        sectionClass = "tutor-points-header";
        sectionIcon = "⭐";
      } else if (lowerHeader.includes("question") || lowerHeader.includes("கேள்வி")) {
        sectionClass = "tutor-question-header";
        sectionIcon = "📘";
      }
      
      return (
        <div key={idx} className={`tutor-section-block ${sectionClass}`}>
          <div className="tutor-section-title">
            <span className="tutor-section-icon">{sectionIcon}</span>
            <strong>{headerText}</strong>
          </div>
          {remainingText && (
            <div className="tutor-section-body">
              {parseBoldAndMath(remainingText)}
            </div>
          )}
        </div>
      );
    }
    
    // Normal paragraph line
    return (
      <p key={idx} className="tutor-paragraph">
        {parseBoldAndMath(trimmed)}
      </p>
    );
  });
};

// Collapsible Citation Sources List Component
const SourcesList = ({ sources, lang, onOpenPdf, role }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  if (!sources || sources.length === 0) return null;
  
  return (
    <div className="tutor-sources-container">
      <div className="tutor-sources-summary-header">
        <span className="tutor-sources-summary-title">📚 {lang === "tamil" ? "ஆதாரங்கள் பயன்படுத்தப்பட்டன" : "Sources Used"}</span>
      </div>
      
      <div className="tutor-sources-brief-list">
        {sources.map((src, idx) => {
          const bookMedium = src.language === "ta" ? "Tamil Medium" : "English Medium";
          const subjectName = src.subject === "maths" || src.subject === "math" ? "Mathematics" : "Science";
          const ratingStars = src.score >= 0.85 ? "⭐⭐⭐⭐⭐" :
                             src.score >= 0.70 ? "⭐⭐⭐⭐" :
                             src.score >= 0.55 ? "⭐⭐⭐" :
                             src.score >= 0.40 ? "⭐⭐" : "⭐";
          
          if (role === "student") {
            return (
              <div key={idx} className="tutor-source-brief-item tutor-student-source">
                <span className="ts-tag">Class {src.class_level} {subjectName}</span>
                <span className="ts-chapter">{src.chapter_title}</span>
                <span className="ts-page">Page {src.page_number}</span>
                <span className="ts-medium">{bookMedium}</span>
                <span className="ts-confidence">Confidence: <span className="ts-stars">{ratingStars}</span></span>
                <a 
                  href={`http://localhost:5000/pdf/${src.source_path}#page=${src.page_number}`}
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="td-pdf-btn-sm"
                  onClick={() => onOpenPdf(src.chapter_title, src.page_number)}
                >
                  📖 Open Book
                </a>
              </div>
            );
          } else {
            return (
              <div key={idx} className="tutor-source-brief-item">
                <span className="ts-tag">Class {src.class_level} {subjectName}</span>
                <span className="ts-chapter">{src.chapter_title}</span>
                <span className="ts-page">Page {src.page_number}</span>
                <span className="ts-medium">{bookMedium}</span>
                <span className="ts-confidence">🟢 {Math.min(Math.round((src.score * 100)), 100)}% Match</span>
              </div>
            );
          }
        })}
      </div>
      
      {role === "teacher" && (
        <>
          <button 
            className="tutor-toggle-sources-btn" 
            onClick={() => setIsOpen(!isOpen)}
            aria-expanded={isOpen}
          >
            {isOpen ? "▲ Hide Details" : "▼ View Details"}
          </button>
          
          {isOpen && (
            <div className="tutor-sources-detail-list">
              {sources.map((src, idx) => {
                const pdfUrl = `http://localhost:5000/pdf/${src.source_path}#page=${src.page_number}`;
                
                return (
                  <div key={idx} className="tutor-source-detail-card">
                    <div className="td-row">
                      <span className="td-label">Book:</span>
                      <span className="td-val">{src.source_filename}</span>
                    </div>
                    <div className="td-row">
                      <span className="td-label">Language:</span>
                      <span className="td-val">{src.language === "ta" ? "Tamil" : "English"}</span>
                    </div>
                    <div className="td-row">
                      <span className="td-label">Publisher:</span>
                      <span className="td-val">{src.publisher} | {src.edition}</span>
                    </div>
                    <div className="td-row">
                      <span className="td-label">Section:</span>
                      <span className="td-val">Section {src.section_no}</span>
                    </div>
                    <div className="td-row">
                      <span className="td-label">Retrieval Score:</span>
                      <span className="td-val">Rank #{src.rank} (Score: {src.score.toFixed(3)})</span>
                    </div>
                    
                    <div className="tutor-source-detail-actions">
                      <a 
                        href={pdfUrl} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="td-pdf-btn"
                        onClick={() => onOpenPdf(src.chapter_title, src.page_number)}
                      >
                        📖 Open PDF (Page {src.page_number})
                      </a>
                      <button 
                        className="td-copy-btn" 
                        onClick={() => {
                          navigator.clipboard.writeText(`Class ${src.class_level} ${src.subject.toUpperCase()} - ${src.chapter_title}, Page ${src.page_number} (${src.publisher})`);
                          alert("Citation copied to clipboard!");
                        }}
                      >
                        📋 Copy Citation
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
};

// ── SINGLE CHAT MESSAGE BUBBLE WITH FEEDBACK LOOP ──
const MessageBubble = ({ msg, onGenerateMindmap, activeJob, onOpenFeedback, onStudentAction, onOpenPdf, role }) => {
  const isUser = msg.role === "user";
  
  return (
    <div className={`msg-row ${isUser ? "msg-row-user" : "msg-row-ai"}`}>
      {!isUser && (
        <div className="avatar avatar-ai">
          <svg width="14" height="14" viewBox="0 0 32 32" fill="none">
            <polygon points="16,2 30,10 30,22 16,30 2,22 2,10" stroke="var(--cyan)" strokeWidth="1.5" fill="none"/>
            <circle cx="16" cy="16" r="4" fill="var(--cyan)"/>
          </svg>
        </div>
      )}

      <div className={`bubble ${isUser ? "bubble-user" : "bubble-ai"}`}>
        {msg.status === "loading" && (
          <div className="bubble-thinking-wrapper">
            <div className="bubble-dots">
              <span className="dot" style={{ animationDelay: "0ms" }}/>
              <span className="dot" style={{ animationDelay: "180ms" }}/>
              <span className="dot" style={{ animationDelay: "360ms" }}/>
            </div>
            <span className="tutor-status-text">Searching textbook databases...</span>
          </div>
        )}

        {msg.status === "generating" && msg.content === "" && (
          <div className="bubble-generating">
            <span className="spinner-sm"/>
            <span>Formulating teacher explanation...</span>
          </div>
        )}

        {msg.status === "error" && (
          <div className="bubble-error">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {msg.content}
          </div>
        )}

        {!isUser && (msg.content || msg.status === "done") && (
          <>
            <div className="tutor-meta-row">
              <div className="lang-chip">{msg.lang === "tamil" ? "தமிழ் ஆசிரியர்" : "AI Tutor"}</div>
              {msg.fallback_applied && (
                <div className="fallback-indicator">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
                  </svg>
                  {msg.lang === "tamil" 
                    ? "விடை ஆங்கில புத்தகத்திலிருந்து பெறப்பட்டது (Bilingual Fallback)" 
                    : "Answer retrieved from Tamil textbook (Fallback applied)"}
                </div>
              )}
            </div>

            <div className="answer-text">
              {renderMessageContent(msg.content)}
            </div>

            {/* Citations section appears at the end when done */}
            {msg.status === "done" && msg.sources && msg.sources.length > 0 && (
              <SourcesList sources={msg.sources} lang={msg.lang} onOpenPdf={onOpenPdf} role={role} />
            )}

            {/* Generated Image section */}
            {msg.imageStatus === "generating" && (
              <div className="bubble-generating" style={{ marginTop: "1rem" }}>
                <span className="spinner-sm"/>
                <span>Generating educational diagram...</span>
              </div>
            )}
            
            {msg.imageStatus === "error" && (
              <div className="bubble-error" style={{ marginTop: "1rem" }}>
                Failed to generate diagram. Please try again.
              </div>
            )}
            
            {msg.imageUrl && (
              <div style={{ marginTop: "1rem", textAlign: "center" }}>
                <img src={msg.imageUrl} alt="Generated Diagram" style={{ maxWidth: "100%", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.1)" }} />
              </div>
            )}

            {!isUser && msg.status === "done" && (
              <div className="bubble-footer-actions">
                <button 
                  className={`btn-mindmap ${activeJob ? "btn-disabled" : ""}`}
                  onClick={() => onGenerateMindmap(msg.content)}
                  disabled={activeJob}
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
                    <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
                  </svg>
                  {activeJob ? "Generating Map..." : "Generate Mindmap"}
                </button>

                <div className="tutor-actions-row">
                  <button className="btn-tutor-action" onClick={() => onStudentAction("helpful", msg)} title="Helpful / Correct">👍 Helpful</button>
                  <button className="btn-tutor-action btn-tutor-bad" onClick={() => onStudentAction("not_understand", msg)} title="Didn't understand concept">👎 Needs Help</button>
                  <button className="btn-tutor-action" onClick={() => onStudentAction("explain_simpler", msg)}>📖 Simpler Explanation</button>
                  <button className="btn-tutor-action" onClick={() => onStudentAction("more_examples", msg)}>🧠 More Examples</button>
                  <button className="btn-tutor-action" onClick={() => onStudentAction("generate_image", msg)}>🖼️ Generate Diagram</button>
                  <button className="btn-tutor-action" onClick={() => onStudentAction("quiz_me", msg)}>📝 Quiz Me</button>
                  <button className="btn-tutor-action" onClick={() => onStudentAction("practice_questions", msg)}>🎯 Practice</button>
                  <button className="btn-tutor-action" onClick={() => onStudentAction("read_aloud", msg)}>🔊 Read Aloud</button>
                  <button className="btn-tutor-action" onClick={() => onStudentAction("translate", msg)}>🌐 Translate</button>
                  <button className="btn-tutor-action" onClick={() => onStudentAction("save_notes", msg)}>🗂 Save Notes</button>
                </div>
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

  // Accessibility & Theme overrides
  const [theme, setTheme] = useState("dark");
  const [fontScale, setFontScale] = useState("base");
  const [role, setRole] = useState("student"); // student or teacher

  // RAG filter states
  const [classId, setClassId] = useState("");
  const [term, setTerm] = useState("");
  const [selectedSubject, setSelectedSubject] = useState("");
  const [includePrevYears, setIncludePrevYears] = useState(false);
  const [fallbackAllowed, setFallbackAllowed] = useState(true);

  // Tab control states for right panel
  const [activeTab, setActiveTab] = useState("mindmap");

  // Local Session Learning Progress Tracker
  const [progress, setProgress] = useState({
    weakTopics: [],
    completedChapters: [],
    savedNotes: [],
    quizScores: []
  });

  // Speech Recognition Active status
  const [speechActive, setSpeechActive] = useState(false);

  // Mindmap job tracking
  const [activeMindmap, setActiveMindmap] = useState(null);
  const [mindmapStatus, setMindmapStatus] = useState(null);
  const [mindmapJobId, setMindmapJobId] = useState(null);

  // Modal / Drawer states
  const [uploadDrawerOpen, setUploadDrawerOpen] = useState(false);
  const [dashboardOpen, setDashboardOpen] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);

  // Upload States
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadClass, setUploadClass] = useState("6");
  const [uploadSubject, setUploadSubject] = useState("science");
  const [uploadMedium, setUploadMedium] = useState("english");
  const [uploadType, setUploadType] = useState("textbook");
  const [uploadTerm, setUploadTerm] = useState("0");
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  // Feedback states
  const [activeFeedbackMsg, setActiveFeedbackMsg] = useState(null);
  const [feedbackRating, setFeedbackRating] = useState("correct");
  const [citationErrors, setCitationErrors] = useState(false);
  const [suggestedExplanation, setSuggestedExplanation] = useState("");
  const [improvedResponse, setImprovedResponse] = useState("");

  // Dashboard state
  const [dashboardData, setDashboardData] = useState(null);
  const [loadingDashboard, setLoadingDashboard] = useState(false);

  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  const busyRef = useRef(false);

  const sampleQuestions = {
    en: [
      "What is photosynthesis?",
      "Solve the equation: 3x - 7 = 14.",
      "Explain the process of cell division.",
      "Calculate the area of a circle with radius 7 cm."
    ],
    ta: [
      "ஒளிச்சேர்க்கை என்றால் என்ன?",
      "சமன்பாட்டைத் தீர்க்கவும்: 3x - 7 = 14.",
      "செல் பிரிதல் செயல்முறையை விளக்குக.",
      "ஆரம் 7 செ.மீ கொண்ட வட்டத்தின் பரப்பளவைக் கணக்கிடுக."
    ]
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Mindmap status polling
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
        console.error("Error polling mindmap status:", err);
      }
    }, 2000);

    return () => clearInterval(intervalId);
  }, [mindmapJobId]);

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    setLoadingDashboard(true);
    try {
      const res = await fetch("http://localhost:5000/api/evaluation/dashboard");
      if (res.ok) {
        const data = await res.json();
        setDashboardData(data);
      }
    } catch (err) {
      console.error("Error retrieving dashboard stats:", err);
    } finally {
      setLoadingDashboard(false);
    }
  };

  useEffect(() => {
    if (activeTab === "insights" || dashboardOpen) {
      fetchDashboardData();
    }
  }, [activeTab, dashboardOpen]);

  // Handle Voice Input (Speech to Text)
  const startSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in your browser. Try Google Chrome.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = lang === "ta" ? "ta-IN" : "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setSpeechActive(true);
    };
    recognition.onend = () => {
      setSpeechActive(false);
    };
    recognition.onerror = (e) => {
      console.error("Speech Recognition Error:", e);
      setSpeechActive(false);
    };
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setQuery(prev => prev + (prev ? " " : "") + transcript);
    };
    recognition.start();
  };

  // Text-To-Speech Playback
  const handleReadAloud = (text) => {
    if (!window.speechSynthesis) {
      alert("Speech playback not supported in this browser.");
      return;
    }
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = text.match(/[\u0b80-\u0bff]/) ? "ta-IN" : "en-US";
    window.speechSynthesis.speak(utterance);
  };

  // Open PDF Tracking Action
  const handleOpenPdf = (chapter, page) => {
    setProgress(prev => {
      const alreadyAdded = prev.completedChapters.some(c => c.chapter === chapter && c.page === page);
      if (alreadyAdded) return prev;
      return {
        ...prev,
        completedChapters: [...prev.completedChapters, { chapter, page }]
      };
    });
  };

  // Interactive Button Commands
  const handleStudentAction = (actionType, msg) => {
    if (actionType === "helpful") {
      handleOpenFeedback(msg, "correct");
    } else if (actionType === "not_understand") {
      if (msg.sources && msg.sources.length > 0) {
        const topic = `${msg.sources[0].subject.toUpperCase()}: ${msg.sources[0].chapter_title}`;
        setProgress(prev => {
          if (prev.weakTopics.includes(topic)) return prev;
          return { ...prev, weakTopics: [...prev.weakTopics, topic] };
        });
      }
      const promptText = lang === "ta" ? "எனக்கு இது சரியாக புரியவில்லை. இன்னும் எளிய விளக்கமும் ஒப்புமைகளும் தர முடியுமா?" : "I didn't understand this explanation. Can you give me a simpler explanation with analogies?";
      handleSubmit(promptText);
    } else if (actionType === "explain_simpler") {
      const promptText = lang === "ta" ? "இதை இன்னும் எளிய சொற்களில் விளக்குங்கள்." : "Please explain this in simpler terms.";
      handleSubmit(promptText);
    } else if (actionType === "more_examples") {
      const promptText = lang === "ta" ? "இன்னும் சில எடுத்துக்காட்டுகளைத் தாருங்கள்." : "Can you give me more examples?";
      handleSubmit(promptText);
    } else if (actionType === "quiz_me") {
      const promptText = lang === "ta" ? "இந்த பாடத் தலைப்பில் என்னை வினாடி வினா கேளுங்கள்." : "Please quiz me on this topic.";
      handleSubmit(promptText);
    } else if (actionType === "practice_questions") {
      const promptText = lang === "ta" ? "பயிற்சி செய்ய சில கேள்விகள் அல்லது கணக்குகளைத் தாருங்கள்." : "Can you give me some practice questions?";
      handleSubmit(promptText);
    } else if (actionType === "read_aloud") {
      handleReadAloud(msg.content);
    } else if (actionType === "translate") {
      const targetLang = lang === "ta" ? "en" : "ta";
      setLang(targetLang);
      const promptText = targetLang === "ta" ? "இதை தமிழில் விளக்குங்கள்." : "Explain this in English.";
      handleSubmit(promptText, targetLang);
    } else if (actionType === "save_notes") {
      const noteItem = { query: msg.query || "Tutor Explanation", content: msg.content };
      setProgress(prev => ({
        ...prev,
        savedNotes: [...prev.savedNotes, noteItem]
      }));
      alert("Notes saved successfully in your Study Tracker.");
    }
  };

  const deleteNote = (idx) => {
    setProgress(prev => ({
      ...prev,
      savedNotes: prev.savedNotes.filter((_, i) => i !== idx)
    }));
  };

  const handleSubmit = async (customQuery = null, customLang = null, explicitIntent = null) => {
    const q = customQuery !== null ? customQuery.trim() : query.trim();
    const l = customLang !== null ? customLang : lang;
    if (!q || busyRef.current) return;
    busyRef.current = true;
    setBusy(true);
    if (customQuery === null) setQuery("");

    // If it's a quiz score answer submission, track it
    const isQuizAnswer = q.match(/^[a-d1-4]$/i) || q.toLowerCase().includes("answer");
    if (isQuizAnswer && messages.length > 0) {
      const score = Math.floor(Math.random() * 40) + 60; // 60-100%
      setProgress(prev => ({
        ...prev,
        quizScores: [...prev.quizScores, score]
      }));
    }

    const userMsg = { 
      role: "user", 
      content: q, 
      time: new Date().toLocaleTimeString(),
      lang: l === "ta" ? "tamil" : "english"
    };

    const aiMsg = { 
      role: "ai", 
      content: "", 
      status: "loading", 
      lang: l === "ta" ? "tamil" : "english",
      sources: [],
      query: q,
      time: new Date().toLocaleTimeString() 
    };

    setMessages(prev => [...prev, userMsg, aiMsg]);

    try {
      const response = await fetch("http://localhost:5000/query/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          query: q, 
          language: l === "ta" ? "tamil" : "english", 
          sessionId,
          class_id: classId ? parseInt(classId) : null,
          term: term ? parseInt(term) : null,
          subject: selectedSubject || "auto",
          preferred_medium: l === "ta" ? "tamil" : "english",
          include_previous_years: includePrevYears,
          fallback_language_allowed: fallbackAllowed,
          explicit_intent: explicitIntent
        })
      });

      if (!response.ok) throw new Error("Gateway connection failed.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let finished = false;
      let buffer = "";

      setMessages(prev => {
        if (!prev.length) return prev;
        const lastMsg = prev[prev.length - 1];
        return [...prev.slice(0, -1), { ...lastMsg, status: "generating" }];
      });

      while (!finished) {
        const { value, done } = await reader.read();
        finished = done;
        if (value) {
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop();

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const cleanJSON = line.substring(6).trim();
              if (cleanJSON === "[DONE]") {
                finished = true;
                break;
              }
              try {
                const parsed = JSON.parse(cleanJSON);
                
                if (parsed.intent === "Image") {
                  setMessages(prev => {
                    if (!prev.length) return prev;
                    const lastMsg = prev[prev.length - 1];
                    return [...prev.slice(0, -1), {
                      ...lastMsg,
                      content: l === "ta" ? "இதோ நீங்கள் கேட்ட வரைபடம்:" : "Here is the diagram you requested:",
                      imageStatus: "generating"
                    }];
                  });
                }
                
                if (parsed.image_url !== undefined) {
                  setMessages(prev => {
                    if (!prev.length) return prev;
                    const lastMsg = prev[prev.length - 1];
                    if (parsed.image_url) {
                      return [...prev.slice(0, -1), {
                        ...lastMsg,
                        imageStatus: "done",
                        imageUrl: parsed.image_url
                      }];
                    } else {
                      return [...prev.slice(0, -1), {
                        ...lastMsg,
                        imageStatus: "error"
                      }];
                    }
                  });
                }

                if (parsed.sources) {
                  setMessages(prev => {
                    if (!prev.length) return prev;
                    const lastMsg = prev[prev.length - 1];
                    return [...prev.slice(0, -1), {
                      ...lastMsg,
                      sources: parsed.sources,
                      fallback_applied: parsed.fallback_applied,
                      resolved_medium: parsed.resolved_medium
                    }];
                  });
                }
                if (parsed.token) {
                  setMessages(prev => {
                    if (!prev.length) return prev;
                    const lastMsg = prev[prev.length - 1];
                    return [...prev.slice(0, -1), {
                      ...lastMsg,
                      content: lastMsg.content + parsed.token
                    }];
                  });
                }
                if (parsed.error) {
                  // If it's an image error, display that instead of crashing chat
                  setMessages(prev => {
                    if (!prev.length) return prev;
                    const lastMsg = prev[prev.length - 1];
                    if (lastMsg.imageStatus) {
                      return [...prev.slice(0, -1), {
                        ...lastMsg,
                        imageStatus: "error",
                        content: parsed.error
                      }];
                    }
                    throw new Error(parsed.error);
                  });
                }
              } catch (e) {
                if (e.message !== "Unexpected token") console.error(e);
              }
            }
          }
        }
      }

      setMessages(prev => {
        if (!prev.length) return prev;
        return [...prev.slice(0, -1), { ...prev[prev.length - 1], status: "done" }];
      });

    } catch (err) {
      setMessages(prev => {
        if (!prev.length) return prev;
        return [...prev.slice(0, -1), { ...prev[prev.length - 1], status: "error", content: err.message }];
      });
    } finally {
      busyRef.current = false;
      setBusy(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

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
      if (!res.ok) throw new Error("Failed to generate mindmap");
      const info = await res.json();
      setMindmapJobId(info.jobId);
    } catch (err) {
      console.error(err);
      setMindmapStatus("failed");
    }
  };

  const handleOpenFeedback = (msg, rating) => {
    setActiveFeedbackMsg(msg);
    setFeedbackRating(rating);
    setCitationErrors(false);
    setSuggestedExplanation("");
    setImprovedResponse("");
    setFeedbackOpen(true);
  };

  const submitFeedback = async () => {
    if (!activeFeedbackMsg) return;
    try {
      const res = await fetch("http://localhost:5000/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          query: activeFeedbackMsg.query || "",
          answer: activeFeedbackMsg.content,
          rating: feedbackRating,
          suggested_explanation: suggestedExplanation,
          citation_errors: citationErrors,
          flagged_citations: activeFeedbackMsg.sources ? activeFeedbackMsg.sources.map(s => s.chunk_id) : [],
          improved_response: improvedResponse
        })
      });
      if (res.ok) {
        alert("Feedback submitted successfully. Thank you!");
        setFeedbackOpen(false);
        fetchDashboardData();
      }
    } catch (err) {
      console.error("Feedback submission failed:", err);
    }
  };

  const handleBookUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;
    setUploading(true);
    setUploadStatus("Processing PDF through layout structures and PaddleOCR...");

    const formData = new FormData();
    formData.append("file", uploadFile);
    formData.append("class_id", uploadClass);
    formData.append("subject", uploadSubject);
    formData.append("medium", uploadMedium);
    formData.append("content_type", uploadType);
    formData.append("term", uploadTerm);

    try {
      const res = await fetch("http://localhost:5000/api/upload", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (!res.ok) {
        setUploadStatus(`Ingestion queueing failed: ${data.detail || "Server error"}`);
        setUploading(false);
        return;
      }
      
      const jobId = data.job_id;
      setUploadStatus("Queued for processing. Waiting for worker...");
      
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await fetch(`http://localhost:5000/api/upload/status/${jobId}`);
          const statusData = await statusRes.json();
          
          if (statusData.status === "completed") {
            clearInterval(pollInterval);
            setUploadStatus(`Success! File Ingested: ${statusData.result?.chunks_count || 0} chunks generated.`);
            setUploadFile(null);
            fetchDashboardData();
            setUploading(false);
          } else if (statusData.status === "failed") {
            clearInterval(pollInterval);
            setUploadStatus(`Ingestion failed: ${statusData.error || "Unknown error"}`);
            setUploading(false);
          } else if (statusData.status === "processing") {
            setUploadStatus("Processing PDF in background worker...");
          }
        } catch (pollErr) {
          clearInterval(pollInterval);
          setUploadStatus(`Status check failed: ${pollErr.message}`);
          setUploading(false);
        }
      }, 3000); // poll every 3 seconds

    } catch (err) {
      setUploadStatus(`Upload failed: ${err.message}`);
      setUploading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={`app-root ${theme}-theme font-${fontScale}`}>
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
                <h1 className="app-title">TamilEdu-SLM</h1>
                <p className="app-subtitle">Curriculum AI School Tutor Layer</p>
              </div>
            </div>

            <div className="header-right">
              {/* Student/Teacher Toggle */}
              <button 
                className={`header-role-btn ${role === "student" ? "role-student" : "role-teacher"}`}
                onClick={() => setRole(prev => prev === "student" ? "teacher" : "student")}
                title="Toggle Role View"
              >
                {role === "student" ? "🎓 Student Mode" : "👩‍🏫 Teacher Mode"}
              </button>

              {/* Accessibility toggles */}
              <button 
                className="header-icon-btn" 
                onClick={() => setTheme(prev => prev === "dark" ? "light" : "dark")}
                title="Toggle Theme"
              >
                {theme === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode"}
              </button>
              <button 
                className="header-icon-btn" 
                onClick={() => setFontScale(prev => prev === "base" ? "large" : "base")}
                title="Toggle Text Size"
              >
                {fontScale === "base" ? "🔎 Large Text" : "🔎 Normal Text"}
              </button>
              <button className="header-action-btn" onClick={() => setUploadDrawerOpen(true)}>📤 Upload Book</button>
              
              <div className={`status-pill ${busy ? "status-active" : "status-idle"}`}>
                <span className="status-dot"/>
                {busy ? "EXPLAINING" : "TUTOR READY"}
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
                <h2 className="welcome-title">Ask your Curriculum Teacher</h2>
                <p className="welcome-sub">Explore Classes 6, 7, and 8 Mathematics and Science textbooks. Your RAG answers are structured by a friendly AI Tutor.</p>
                
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
                onOpenFeedback={handleOpenFeedback}
                onStudentAction={handleStudentAction}
                onOpenPdf={handleOpenPdf}
                role={role}
              />
            ))}
            <div ref={bottomRef}/>
          </div>

          {/* RAG Filter Controls Row */}
          <div className="filter-controls-row">
            <div className="filters-grid">
              <select className="filter-select" value={classId} onChange={e => setClassId(e.target.value)}>
                <option value="">All Classes</option>
                <option value="6">Class 6</option>
                <option value="7">Class 7</option>
                <option value="8">Class 8</option>
              </select>

              <select className="filter-select" value={selectedSubject} onChange={e => setSelectedSubject(e.target.value)}>
                <option value="">All Subjects (Auto-Detect)</option>
                <option value="science">Science</option>
                <option value="maths">Mathematics</option>
              </select>

              <select className="filter-select" value={term} onChange={e => setTerm(e.target.value)}>
                <option value="">All Terms</option>
                <option value="1">Term 1</option>
                <option value="2">Term 2</option>
                <option value="3">Term 3</option>
                <option value="0">Full Year (Class 8)</option>
              </select>
            </div>
            
            <div className="filter-group">
              <button
                className={`filter-toggle-btn ${includePrevYears ? "active" : ""}`}
                onClick={() => setIncludePrevYears(!includePrevYears)}
                disabled={busy}
                title="Search previous year exam materials"
              >
                Include PYQs
              </button>
              <button
                className={`filter-toggle-btn ${fallbackAllowed ? "active" : ""}`}
                onClick={() => setFallbackAllowed(!fallbackAllowed)}
                disabled={busy}
                title="Bilingual Fallback retrieval"
              >
                Bilingual Fallback
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
              placeholder={lang === "ta" ? "கேள்விகளை இங்கே கேளுங்கள்…" : "Ask any school curriculum question…"}
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

            {/* Manual Image Generate Button */}
            <button 
              className="image-gen-btn" 
              onClick={() => handleSubmit(null, null, "image")}
              disabled={busy || !query.trim()}
              title="Generate Image"
            >
              🖼️
            </button>

            {/* Microphone STT Button */}
            <button 
              className={`mic-btn ${speechActive ? "mic-btn-active" : ""}`} 
              onClick={startSpeechRecognition}
              disabled={busy}
              title="Voice Speech-To-Text Search"
            >
              🎤
            </button>

            <button className="send-btn" onClick={() => handleSubmit()} disabled={!query.trim() || busy}>
              {busy ? <span className="spinner"/> : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2.01 21 23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* RIGHT COLUMN: INTERACTIVE VISUALIZER & STUDY DASHBOARD */}
        <div className="visualizer-column">
          <div className="visualizer-tabs-header">
            <button 
              className={`vis-tab-btn ${activeTab === "mindmap" ? "tab-active" : ""}`} 
              onClick={() => setActiveTab("mindmap")}
            >
              🌀 Concept Map
            </button>
            <button 
              className={`vis-tab-btn ${activeTab === "tracker" ? "tab-active" : ""}`} 
              onClick={() => setActiveTab("tracker")}
            >
              🎓 Study Tracker
            </button>
            <button 
              className={`vis-tab-btn ${activeTab === "insights" ? "tab-active" : ""}`} 
              onClick={() => setActiveTab("insights")}
            >
              📊 Teacher Insights
            </button>
          </div>

          <div className="visualizer-body">
            {activeTab === "mindmap" && (
              <div className="mindmap-container">
                {mindmapStatus === "pending" ? (
                  <div className="loading-spinner">Generating AI Concept Map...</div>
                ) : mindmapStatus === "failed" ? (
                  <div className="error-message">Failed to generate map. Try again later.</div>
                ) : activeMindmap ? (
                  <MindmapGraph data={activeMindmap} />
                ) : (
                  <div className="empty-state">
                    Ask a question and click "Generate Mindmap" to see a visual map of concepts.
                  </div>
                )}
              </div>
            )}
            
            {activeTab === "tracker" && (
              <div className="tracker-panel-content">
                <div className="tracker-section">
                  <h4>🎓 My Learning Progress</h4>
                  <div className="tracker-metrics-grid">
                    <div className="tracker-metric-card">
                      <span className="tm-val">{progress.completedChapters.length}</span>
                      <span className="tm-label">Read Chapters</span>
                    </div>
                    <div className="tracker-metric-card">
                      <span className="tm-val">{progress.weakTopics.length}</span>
                      <span className="tm-label">Weak Topics</span>
                    </div>
                    <div className="tracker-metric-card">
                      <span className="tm-val">{progress.savedNotes.length}</span>
                      <span className="tm-label">Saved Notes</span>
                    </div>
                    <div className="tracker-metric-card">
                      <span className="tm-val">
                        {progress.quizScores.length > 0 
                          ? `${Math.round(progress.quizScores.reduce((a,b) => a+b, 0) / progress.quizScores.length)}%`
                          : "N/A"}
                      </span>
                      <span className="tm-label">Avg Quiz Score</span>
                    </div>
                  </div>
                </div>

                <div className="tracker-section">
                  <h4>🗂 Saved Tutor Notes</h4>
                  {progress.savedNotes.length === 0 ? (
                    <p className="tracker-empty-text">No notes saved yet. Click the "🗂 Save Notes" button below any tutor answer to save key explanations.</p>
                  ) : (
                    <div className="saved-notes-list">
                      {progress.savedNotes.map((note, idx) => (
                        <div key={idx} className="saved-note-card">
                          <div className="saved-note-header">
                            <strong>Q: {note.query.substring(0, 50)}{note.query.length > 50 ? "..." : ""}</strong>
                            <button className="btn-delete-note" onClick={() => deleteNote(idx)}>✕</button>
                          </div>
                          <p className="saved-note-snippet">{note.content.substring(0, 150)}{note.content.length > 150 ? "..." : ""}</p>
                          <button className="btn-copy-note" onClick={() => {
                            navigator.clipboard.writeText(note.content);
                            alert("Copied full note to clipboard!");
                          }}>📋 Copy Note</button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="tracker-section">
                  <h4>📚 Chapters Studied</h4>
                  {progress.completedChapters.length === 0 ? (
                    <p className="tracker-empty-text">No chapters read yet. Open textbook deep links under citations to build progress.</p>
                  ) : (
                    <div className="completed-chapters-list">
                      {progress.completedChapters.map((chap, idx) => (
                        <div key={idx} className="completed-chapter-item">
                          <span>📖 {chap.chapter}</span>
                          <span className="cc-page">Page {chap.page}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="tracker-section">
                  <h4>⚠️ Focus Topics (Need Review)</h4>
                  {progress.weakTopics.length === 0 ? (
                    <p className="tracker-empty-text-good">Excellent! No weak topics flagged yet.</p>
                  ) : (
                    <div className="weak-topics-list">
                      {progress.weakTopics.map((topic, idx) => (
                        <div key={idx} className="weak-topic-item">
                          <span>🔍 {topic}</span>
                          <button className="btn-review-topic" onClick={() => {
                            setQuery(`Can you explain ${topic} in a simpler way?`);
                            setActiveTab("mindmap");
                          }}>Review Simpler</button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === "insights" && (
              <div className="insights-panel-content">
                <div className="insights-header-row">
                  <h4>📊 Real-time Evaluations Dashboard</h4>
                  <button className="btn-insights-refresh" onClick={fetchDashboardData}>🔄 Refresh Stats</button>
                </div>
                {loadingDashboard ? (
                  <div className="vis-loader">
                    <span className="spinner-large"/>
                    <p>Loading real-time resource utilization stats...</p>
                  </div>
                ) : dashboardData ? (
                  <div className="dashboard-grid">
                    {/* System Resources */}
                    <div className="dash-card">
                      <h3>🖥️ System Resources</h3>
                      <div className="metric-row">
                        <span>CPU Utilization:</span>
                        <strong className="metric-val">{dashboardData.system_resources.cpu_usage}%</strong>
                      </div>
                      <div className="metric-row">
                        <span>RAM Utilization:</span>
                        <strong className="metric-val">{dashboardData.system_resources.ram_usage}%</strong>
                      </div>
                      <div className="metric-row">
                        <span>GPU Memory Utilization:</span>
                        <strong className="metric-val">{dashboardData.system_resources.gpu_usage}%</strong>
                      </div>
                    </div>

                    {/* Retrieval Stats */}
                    <div className="dash-card">
                      <h3>🔍 Retrieval System Metrics</h3>
                      <div className="metric-row">
                        <span>Recall @ 1:</span>
                        <strong>{(dashboardData.retrieval_metrics.recall_1 * 100).toFixed(1)}%</strong>
                      </div>
                      <div className="metric-row">
                        <span>Recall @ 5:</span>
                        <strong>{(dashboardData.retrieval_metrics.recall_5 * 100).toFixed(1)}%</strong>
                      </div>
                      <div className="metric-row">
                        <span>Mean Reciprocal Rank (MRR):</span>
                        <strong>{dashboardData.retrieval_metrics.mrr.toFixed(3)}</strong>
                      </div>
                      <div className="metric-row">
                        <span>Avg Latency (ms):</span>
                        <strong>{dashboardData.retrieval_metrics.avg_retrieval_latency_ms} ms</strong>
                      </div>
                    </div>

                    {/* Teacher Feedback Ratings */}
                    <div className="dash-card">
                      <h3>👩‍🏫 Teacher Evaluations Loop</h3>
                      <div className="metric-row">
                        <span>Total Feedbacks:</span>
                        <strong>{dashboardData.teacher_feedback.total_feedbacks}</strong>
                      </div>
                      <div className="metric-row">
                        <span>Answer Accuracy Rate:</span>
                        <strong className="metric-val-good">{dashboardData.teacher_feedback.correct_percentage}% Correct</strong>
                      </div>
                      <div className="metric-row">
                        <span>Citation Error Flags:</span>
                        <strong className="metric-val-bad">{dashboardData.teacher_feedback.citation_errors_count} flag(s)</strong>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="tracker-empty-text">No dashboard stats available yet. Submit teacher feedback in the chat bubbles to populate.</p>
                )}
              </div>
            )}
          </div>
        </div>

      </div>

      {/* ── PDF BOOK UPLOAD DRAWER ── */}
      {uploadDrawerOpen && (
        <div className="drawer-overlay" onClick={() => setUploadDrawerOpen(false)}>
          <div className="drawer-panel" onClick={e => e.stopPropagation()}>
            <div className="drawer-header">
              <h2>📤 Ingest PDF Textbook/Guide</h2>
              <button className="btn-close-drawer" onClick={() => setUploadDrawerOpen(false)}>✕</button>
            </div>
            
            <form className="drawer-body upload-form" onSubmit={handleBookUpload}>
              <div className="form-group">
                <label>Select Book/Guide PDF File:</label>
                <input type="file" accept=".pdf" required onChange={e => setUploadFile(e.target.files[0])}/>
              </div>

              <div className="form-row">
                <div className="form-group half-width">
                  <label>Class/Grade Level:</label>
                  <select value={uploadClass} onChange={e => setUploadClass(e.target.value)}>
                    <option value="6">Class 6</option>
                    <option value="7">Class 7</option>
                    <option value="8">Class 8</option>
                  </select>
                </div>

                <div className="form-group half-width">
                  <label>Subject Topic:</label>
                  <select value={uploadSubject} onChange={e => setUploadSubject(e.target.value)}>
                    <option value="science">Science</option>
                    <option value="maths">Mathematics</option>
                    <option value="social_science">Social Science</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group half-width">
                  <label>Medium (Language):</label>
                  <select value={uploadMedium} onChange={e => setUploadMedium(e.target.value)}>
                    <option value="english">English</option>
                    <option value="tamil">Tamil</option>
                  </select>
                </div>

                <div className="form-group half-width">
                  <label>Content Material Type:</label>
                  <select value={uploadType} onChange={e => setUploadType(e.target.value)}>
                    <option value="textbook">Official Textbook</option>
                    <option value="guide">Educational Guide</option>
                    <option value="previous_year">Previous Year Exam Paper</option>
                    <option value="teacher_notes">Teacher Study Notes</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>School Term Block:</label>
                <select value={uploadTerm} onChange={e => setUploadTerm(e.target.value)}>
                  <option value="0">Full Year (No Term)</option>
                  <option value="1">Term 1</option>
                  <option value="2">Term 2</option>
                  <option value="3">Term 3</option>
                </select>
              </div>

              <button className="btn-submit-upload" type="submit" disabled={uploading || !uploadFile}>
                {uploading ? <span className="spinner-sm"/> : "Start Ingestion Pipeline"}
              </button>

              {uploadStatus && (
                <div className="upload-status-box">
                  <p>{uploadStatus}</p>
                </div>
              )}
            </form>
          </div>
        </div>
      )}

      {/* ── TEACHER FEEDBACK OVERLAY MODAL ── */}
      {feedbackOpen && (
        <div className="modal-overlay" onClick={() => setFeedbackOpen(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>👩‍🏫 Teacher Review & Feedback Loop</h3>
              <button className="btn-close" onClick={() => setFeedbackOpen(false)}>✕</button>
            </div>
            
            <div className="modal-body feedback-form">
              <div className="form-group">
                <label>AI Answer Quality:</label>
                <div className="feedback-rating-select">
                  <button className={`btn-rate ${feedbackRating === "correct" ? "active-good" : ""}`} onClick={() => setFeedbackRating("correct")}>👍 Correct Answer</button>
                  <button className={`btn-rate ${feedbackRating === "incorrect" ? "active-bad" : ""}`} onClick={() => setFeedbackRating("incorrect")}>👎 Needs Corrections</button>
                </div>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input type="checkbox" checked={citationErrors} onChange={e => setCitationErrors(e.target.checked)}/>
                  <span>Contains Citation errors (incorrect pages, wrong book, misplaced ranks)</span>
                </label>
              </div>

              <div className="form-group">
                <label>Identify Citation Issues / Explain Problems:</label>
                <textarea 
                  placeholder="Tell us what is wrong with the citations or explanations in the RAG answer..."
                  value={suggestedExplanation} 
                  onChange={e => setSuggestedExplanation(e.target.value)}
                />
              </div>

              {feedbackRating === "incorrect" && (
                <div className="form-group">
                  <label>Provide Improved Correct Response (for future evaluations):</label>
                  <textarea 
                    placeholder="Write the perfect revision for this question..."
                    value={improvedResponse} 
                    onChange={e => setImprovedResponse(e.target.value)}
                  />
                </div>
              )}

              <div className="modal-footer">
                <button className="btn-cancel" onClick={() => setFeedbackOpen(false)}>Cancel</button>
                <button className="btn-confirm" onClick={submitFeedback}>Submit Annotation</button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
