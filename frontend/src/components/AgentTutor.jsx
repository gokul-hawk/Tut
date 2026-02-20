import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { BookOpen, BrainCircuit, FileText, Send, MonitorPlay, Moon, Sun, Copy, Check, Eye } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useLocation, useNavigate } from 'react-router-dom';
import { sendMessage, getTutorWelcome } from "../services/chatService";
import VisualizerRenderer from './VisualizerRenderer';

const DJANGO_BASE_URL = "http://127.0.0.1:8000/api";

// ─────────────── API FUNCTIONS (Internal) ───────────────

const callSummaryApi = async (messages) => {
    const tokenData = localStorage.getItem("user");
    const token = tokenData ? JSON.parse(tokenData).access : null;
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const url = `${DJANGO_BASE_URL}/chat/summarize/`;
    try {
        const response = await axios.post(url, { messages }, { headers });
        return response.data.summary;
    } catch (error) {
        if (error.response) {
            throw new Error(error.response.data.error || error.response.statusText);
        } else {
            throw new Error("Failed to connect to summary backend.");
        }
    }
};

const callResetApi = async (topic) => {
    const tokenData = localStorage.getItem("user");
    const token = tokenData ? JSON.parse(tokenData).access : null;
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    try {
        await axios.post(`${DJANGO_BASE_URL}/chat/reset_session/`, {}, { headers });
        console.log("Session reset for new topic:", topic);
    } catch (e) {
        console.error("Failed to reset session:", e);
    }
};

const callAgentApi = async (data) => {
    const tokenData = localStorage.getItem("user");
    const token = tokenData ? JSON.parse(tokenData).access : null;
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const url = `${DJANGO_BASE_URL}/chat/`;

    try {
        await axios.post(url, data, { headers });
    } catch (error) {
        console.error("Failed to connect to agent backend:", error);
    }
};


// ─────────────── MARKDOWN STYLING COMPONENTS ───────────────
const MarkdownComponents = {
    // Headers
    h1: ({ node, ...props }) => <h1 className="text-2xl font-extrabold bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent mt-6 mb-4 pb-2 border-b border-indigo-100 dark:border-indigo-900/30" {...props} />,
    h2: ({ node, ...props }) => <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mt-5 mb-3" {...props} />,
    h3: ({ node, ...props }) => <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-200 mt-4 mb-2" {...props} />,

    // Text
    p: ({ node, ...props }) => <div className="text-slate-700 dark:text-slate-300 leading-7 mb-4 last:mb-0" {...props} />,
    strong: ({ node, ...props }) => <strong className="font-bold text-slate-900 dark:text-white" {...props} />,
    em: ({ node, ...props }) => <em className="italic text-slate-600 dark:text-slate-400" {...props} />,

    // Lists
    ul: ({ node, ...props }) => <ul className="list-disc pl-5 space-y-1 mb-4 text-slate-700 dark:text-slate-300 marker:text-indigo-500" {...props} />,
    ol: ({ node, ...props }) => <ol className="list-decimal pl-5 space-y-1 mb-4 text-slate-700 dark:text-slate-300 marker:text-indigo-500 font-medium" {...props} />,
    li: ({ node, ...props }) => <li className="pl-1" {...props} />,

    // Code
    code: ({ node, inline, className, children, ...props }) => {
        const [copied, setCopied] = useState(false);
        const codeText = String(children).replace(/\n$/, '');

        const handleCopy = () => {
            navigator.clipboard.writeText(codeText);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        };

        if (inline) {
            return (
                <code className="text-pink-600 dark:text-pink-400 font-semibold px-1 rounded-sm" {...props}>
                    {children}
                </code>
            );
        }

        return (
            <div className="relative my-5 group rounded-xl overflow-hidden shadow-lg border border-slate-700/50 bg-[#1e1e1e]">
                <div className="flex items-center justify-between px-4 py-2 bg-[#2d2d2d] border-b border-white/10">
                    <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
                        <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
                        <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
                    </div>
                    <button onClick={handleCopy} className="text-xs text-slate-400 hover:text-white transition-colors flex items-center gap-1">
                        {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                        {copied ? "Copied!" : "Copy"}
                    </button>
                </div>
                <pre className="p-4 overflow-x-auto text-sm font-mono text-emerald-400 leading-relaxed scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                    <code className={className} {...props}>
                        {children}
                    </code>
                </pre>
            </div>
        );
    },

    // Blockquotes
    blockquote: ({ node, ...props }) => (
        <div className="border-l-4 border-indigo-500 pl-4 py-2 my-4 bg-indigo-50 dark:bg-indigo-900/10 italic text-slate-700 dark:text-slate-300 rounded-r-lg">
            {props.children}
        </div>
    ),

    // Tables
    table: ({ node, ...props }) => (
        <div className="overflow-x-auto my-6 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm bg-white dark:bg-zinc-900/50">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700" {...props} />
        </div>
    ),
    thead: ({ node, ...props }) => <thead className="bg-slate-100 dark:bg-slate-800" {...props} />,
    th: ({ node, ...props }) => <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider border-b border-slate-200 dark:border-slate-700" {...props} />,
    tbody: ({ node, ...props }) => <tbody className="bg-transparent divide-y divide-slate-100 dark:divide-slate-800" {...props} />,
    tr: ({ node, ...props }) => <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors" {...props} />,
    td: ({ node, ...props }) => <td className="px-6 py-4 text-sm text-slate-700 dark:text-slate-300 whitespace-nowrap" {...props} />,

    // Links
    a: ({ node, ...props }) => <a className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 underline underline-offset-2 decoration-indigo-300 dark:decoration-indigo-700 transition-colors" target="_blank" rel="noopener noreferrer" {...props} />,

    // Horizontal Rule
    hr: ({ node, ...props }) => <hr className="my-8 border-slate-200 dark:border-slate-800" {...props} />
};

// ─────────────── PANELS ───────────────
const KeyConceptsPanel = () => {
    const [concepts, setConcepts] = useState([]);
    const [loading, setLoading] = useState(true);

    // Helper inside panel
    const getAuthHeaders = () => {
        const tokenData = localStorage.getItem("user");
        const token = tokenData ? JSON.parse(tokenData).access : null;
        return token ? { Authorization: `Bearer ${token}` } : {};
    };

    useEffect(() => {
        axios.get(`${DJANGO_BASE_URL}/chat/key_concepts/`, { headers: getAuthHeaders() })
            .then((res) => {
                setConcepts(res.data);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Key concepts error", err);
                setConcepts(["Error loading concepts."]);
                setLoading(false);
            });
    }, []);

    return (
        <div className="h-full flex flex-col p-6 animate-fade-in bg-white dark:bg-slate-900">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-indigo-100 dark:bg-indigo-500/10 rounded-xl text-indigo-600 dark:text-indigo-400 shadow-sm">
                    <BookOpen className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-lg text-slate-800 dark:text-slate-100 tracking-tight">Key Concepts</h3>
            </div>

            {loading ? (
                <div className="flex-1 flex items-center justify-center text-slate-400 text-sm italic">
                    <div className="flex flex-col items-center gap-2">
                        <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                        Loading library...
                    </div>
                </div>
            ) : (
                <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800">
                    {concepts.length === 0 ? (
                        <div className="text-center py-10 px-4 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl">
                            <p className="text-slate-500 text-sm">No concepts recorded yet.</p>
                        </div>
                    ) : (
                        concepts.map((c, i) => (
                            <div key={i} className="group p-4 bg-white dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-xl hover:border-indigo-400 dark:hover:border-indigo-500/50 hover:shadow-md transition-all duration-300 cursor-default">
                                <div className="flex gap-3">
                                    <div className="mt-1 w-1.5 h-1.5 rounded-full bg-indigo-400 group-hover:scale-125 transition-transform shrink-0" />
                                    <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{c}</p>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
};

const QuizPanel = ({ messages, onQuizComplete, autoStart }) => {
    const [quiz, setQuiz] = useState([]);
    const [loading, setLoading] = useState(false);
    const [answers, setAnswers] = useState({});
    const [showResult, setShowResult] = useState(false);
    const mounted = useRef(false);

    const getCorrectAnswer = (q) => q.correct_answer ?? q.answer ?? q.correct ?? null;

    useEffect(() => {
        if (autoStart && !mounted.current && messages.length > 0) {
            mounted.current = true;
            generateQuiz();
        }
    }, [autoStart, messages]);

    const generateQuiz = async () => {
        setLoading(true);
        setShowResult(false);
        setAnswers({});
        const tokenData = localStorage.getItem("user");
        const token = tokenData ? JSON.parse(tokenData).access : null;
        const headers = token ? { "Authorization": `Bearer ${token}` } : {};

        try {
            const res = await axios.post(`${DJANGO_BASE_URL}/chat/generate_quiz/`, { messages }, { headers });
            setQuiz(res.data.quiz || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleOptionClick = (qIndex, option) => {
        if (showResult) return;
        setAnswers(prev => ({ ...prev, [qIndex]: option }));
    };

    return (
        <div className="h-full flex flex-col p-6 animate-fade-in bg-white dark:bg-slate-900">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-amber-100 dark:bg-amber-500/10 rounded-xl text-amber-600 dark:text-amber-400 shadow-sm">
                    <BrainCircuit className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-lg text-slate-800 dark:text-slate-100 tracking-tight">Knowledge Check</h3>
            </div>

            <button
                onClick={generateQuiz}
                disabled={loading}
                className="w-full mb-6 py-3.5 px-4 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-semibold rounded-xl shadow-lg shadow-amber-500/20 active:scale-98 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2 group"
            >
                {loading ? (
                    <>
                        <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                        <span>Crafting Quiz...</span>
                    </>
                ) : (
                    <>
                        <MonitorPlay className="w-4 h-4" />
                        <span>Generate Quiz</span>
                    </>
                )}
            </button>

            <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800">
                {quiz.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-48 text-center px-4 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl bg-slate-50/50 dark:bg-slate-900/50">
                        <div className="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-3 text-slate-400">
                            <BrainCircuit className="w-6 h-6" />
                        </div>
                        <p className="text-slate-500 text-sm font-medium">No active quiz.</p>
                        <p className="text-slate-400 text-xs mt-1">Generate one from your chat context.</p>
                    </div>
                ) : (
                    <div className="space-y-6 pb-4">
                        {quiz.map((q, i) => (
                            <div key={i} className="p-5 bg-white dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm">
                                <p className="text-sm font-semibold text-slate-900 dark:text-white mb-4 flex gap-2">
                                    <span className="flex-shrink-0 w-6 h-6 bg-slate-100 dark:bg-slate-700 text-slate-500 text-[10px] font-bold flex items-center justify-center rounded-lg">{i + 1}</span>
                                    {q.question}
                                </p>
                                <div className="space-y-2.5">
                                    {q.options.map((opt, j) => {
                                        const isSelected = answers[i] === opt;
                                        const correctAns = getCorrectAnswer(q);
                                        const isCorrect = showResult && opt === correctAns;
                                        const isWrong = showResult && isSelected && opt !== correctAns;

                                        let baseClass = "w-full text-left p-3 text-xs rounded-xl border transition-all duration-200 relative group ";
                                        if (showResult) {
                                            if (isCorrect) baseClass += "bg-emerald-50 dark:bg-emerald-900/20 border-emerald-500/50 text-emerald-700 dark:text-emerald-300 font-medium";
                                            else if (isWrong) baseClass += "bg-red-50 dark:bg-red-900/20 border-red-500/50 text-red-700 dark:text-red-300 font-medium";
                                            else baseClass += "bg-slate-50 dark:bg-slate-900/30 border-slate-100 dark:border-slate-800 opacity-50";
                                        } else {
                                            if (isSelected) baseClass += "bg-indigo-50 dark:bg-indigo-900/20 border-indigo-500 text-indigo-700 dark:text-indigo-300 shadow-sm ring-1 ring-indigo-500/20";
                                            else baseClass += "bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700/50 hover:border-indigo-300 dark:hover:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-700/50";
                                        }

                                        return (
                                            <button key={j} onClick={() => handleOptionClick(i, opt)} disabled={showResult} className={baseClass}>
                                                <div className="flex items-center justify-between">
                                                    <span>{opt}</span>
                                                    {isCorrect && <Check className="w-4 h-4 text-emerald-500" />}
                                                    {isWrong && <div className="w-4 h-4 rounded-full border border-red-500 flex items-center justify-center text-[10px] text-red-500">✕</div>}
                                                </div>
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                        ))}

                        {!showResult && (
                            <button onClick={() => {
                                setShowResult(true);
                                // Calculate Score and Notify Parent
                                let correctCount = 0;
                                quiz.forEach((q, i) => {
                                    const correctAns = q.correct_answer ?? q.answer ?? q.correct;
                                    if (answers[i] === correctAns) correctCount++;
                                });
                                if (onQuizComplete) {
                                    onQuizComplete({ correct: correctCount, total: quiz.length });
                                }
                            }} className="w-full py-3.5 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold rounded-xl shadow-lg shadow-emerald-500/20 transition-all active:scale-98">
                                Submit & Check Answers
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

const NotesPanel = ({ messages }) => {
    const [summary, setSummary] = useState("");
    const [loading, setLoading] = useState(false);

    const handleGenerateSummary = async () => {
        setSummary("");
        setLoading(true);
        try {
            const botMessages = messages.filter((m) => m.sender === "bot").map(m => m.text);
            const data = await callSummaryApi(botMessages);
            setSummary(data || "No summary available.");
        } catch (err) {
            setSummary("Error: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const downloadNotes = () => {
        const blob = new Blob([summary], { type: "text/plain" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "tutor_summary.txt";
        link.click();
    };

    return (
        <div className="h-full flex flex-col p-6 animate-fade-in bg-white dark:bg-slate-900">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-emerald-100 dark:bg-emerald-500/10 rounded-xl text-emerald-600 dark:text-emerald-400 shadow-sm">
                    <FileText className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-lg text-slate-800 dark:text-slate-100 tracking-tight">Smart Summary</h3>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-6">
                <button onClick={handleGenerateSummary} disabled={loading} className="col-span-1 py-2.5 px-3 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl shadow transition-all flex justify-center items-center gap-2">
                    {loading ? <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <MonitorPlay className="w-3.5 h-3.5" />}
                    {loading ? "Thinking..." : "Generate"}
                </button>
                <button onClick={downloadNotes} disabled={!summary || loading} className="col-span-1 py-2.5 px-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-xl shadow-sm transition-all disabled:opacity-50 flex justify-center items-center gap-2">
                    <FileText className="w-3.5 h-3.5" />
                    Download
                </button>
            </div>

            <div className="flex-1 overflow-y-auto bg-slate-50/50 dark:bg-slate-900/30 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800">
                {summary ? (
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={MarkdownComponents}
                    >
                        {summary}
                    </ReactMarkdown>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-slate-400">
                        <FileText className="w-10 h-10 mb-3 opacity-20" />
                        <p className="text-xs font-medium">Generate a summary to review your session.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

// ─────────────── CHAT AREA ───────────────
const ChatArea = ({ messages, setMessages, setVisualizationContent, setActiveTab, setAutoStartQuiz }) => {
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const chatEndRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;
        const userMsg = input.trim();
        setMessages(prev => [...prev, { sender: "user", text: userMsg }]);
        setInput("");
        setLoading(true);

        try {
            const data = await sendMessage(userMsg);

            // 1. Handle Visualization
            if (data.visualization) {
                setVisualizationContent(data.visualization);
                setActiveTab("visualizer");
            }

            // 2. Handle Completion (Agent Flow) -- CUSTOM AGENT HANDLER
            if (data.is_complete) {
                console.log("Topic Complete! Triggering Quiz...");

                // Show completion message
                setMessages(prev => [...prev, { sender: "bot", text: `${data.reply}\n\n🎉 Topic Covered! Let's take a quick quiz to verify your mastery.` }]);

                // Enforce Quiz Flow
                setVisualizationContent(null); // Clear vis to focus on quiz
                setActiveTab("quiz");

                // Signal AgentTutor to auto-start the quiz in the panel
                // We need to pass this state down.
                // Note: The parent component needs to manage this state trigger.
                // Since this function is inside ChatArea, and setActiveTab is passed down,
                // we might need a setAutoStartQuiz callback? 
                // Yes, ChatArea needs setAutoStartQuiz prop.
                if (typeof setAutoStartQuiz === 'function') {
                    setAutoStartQuiz(true);
                }
            }

            // 3. Handle Direct Actions (if any)
            if (data.action && data.action.type === 'SWITCH_TAB') {
                setTimeout(() => {
                    const targetView = data.action.view;
                    const topic = data.action.topic || "Unknown";
                    if (targetView === 'code') navigate(`/agent-code?topic=${encodeURIComponent(topic)}`);
                    if (targetView === 'debugger') navigate(`/agent-debugger?topic=${encodeURIComponent(topic)}`);
                }, 1500);
            }

            const isClarifying = data.awaiting_reply;
            setMessages(prev => [...prev, { sender: "bot", text: data.reply, meta: { clarifying: isClarifying } }]);
        } catch (err) {
            setMessages(prev => [...prev, { sender: "bot", text: `Error: ${err.message}` }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="h-full flex flex-col relative bg-slate-50/50 dark:bg-slate-950/50">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-8 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800">
                {messages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"} animate-slide-up group`}>
                        {/* Avatar placeholder if needed, for now just bubble */}
                        <div className={`max-w-[85%] lg:max-w-[75%] rounded-2xl p-6 shadow-sm relative overflow-hidden ${msg.sender === "user"
                            ? "bg-gradient-to-br from-indigo-600 to-violet-600 text-white rounded-br-sm shadow-indigo-500/10"
                            : "bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-sm shadow-slate-200/50 dark:shadow-none"
                            } ${msg.sender === "bot" && msg.meta?.clarifying ? "ring-2 ring-indigo-400/50 dark:ring-indigo-500/30 bg-indigo-50/50 dark:bg-indigo-900/10" : ""}`}>

                            {/* Content */}
                            <div className={`${msg.sender === "user" ? "text-white/90" : ""}`}>
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    components={msg.sender === "user" ? {
                                        // User message overrides (simpler styling)
                                        p: ({ node, ...props }) => <p className="leading-relaxed whitespace-pre-wrap" {...props} />,
                                        code: ({ node, ...props }) => <code className="bg-white/20 px-1 py-0.5 rounded text-sm font-mono" {...props} />,
                                    } : MarkdownComponents}
                                >
                                    {msg.text.replace(/\\n/g, '\n')}
                                </ReactMarkdown>
                            </div>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start animate-fade-in">
                        <div className="bg-white dark:bg-slate-900 px-5 py-4 rounded-2xl rounded-tl-sm border border-slate-100 dark:border-slate-800 shadow-sm flex items-center space-x-1.5">
                            <div className="w-2 h-2 bg-indigo-500/80 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                            <div className="w-2 h-2 bg-indigo-500/80 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                            <div className="w-2 h-2 bg-indigo-500/80 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                        </div>
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-6">
                <div className="relative flex items-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl shadow-slate-200/40 dark:shadow-black/20 focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-500 transition-all duration-300">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Discuss a topic or ask a question..."
                        className="flex-1 bg-transparent border-none focus:ring-0 px-6 py-4 text-slate-800 dark:text-slate-100 placeholder-slate-400 font-medium"
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || loading}
                        className="m-2 p-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-all disabled:opacity-50 disabled:scale-95 shadow-md shadow-indigo-600/20 active:scale-90"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
                <p className="text-center text-[10px] text-slate-400 mt-2 font-medium">AI can make mistakes. Please verify important information.</p>
            </div>
        </div>
    );
};

// ─────────────── SIDEBAR ───────────────
const Sidebar = ({ activeTab, setActiveTab, darkMode, toggleTheme }) => {
    const tabs = [
        { id: "concepts", label: "Concepts", icon: BookOpen },
        { id: "visualizer", label: "Visualizer", icon: Eye },
        { id: "quiz", label: "Quiz", icon: BrainCircuit },
        { id: "notes", label: "Notes", icon: FileText },
    ];

    return (
        <div className="w-20 bg-slate-900 border-r border-slate-800 flex flex-col items-center py-6 z-20 shadow-2xl">
            <div className="mb-8 p-3 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-600/30">
                <MonitorPlay className="w-6 h-6 text-white" />
            </div>

            <div className="flex-1 flex flex-col gap-6 w-full px-2">
                {tabs.map((t) => {
                    const isActive = activeTab === t.id;
                    return (
                        <button
                            key={t.id}
                            onClick={() => setActiveTab(t.id)}
                            className={`group relative w-full flex flex-col items-center justify-center gap-1 p-3 rounded-xl transition-all duration-300 ${isActive ? "bg-white/10 text-white" : "text-slate-400 hover:text-white hover:bg-white/5"
                                }`}
                        >
                            <t.icon className={`w-6 h-6 transition-all ${isActive ? "scale-110" : "group-hover:scale-110"}`} />
                            <span className="text-[10px] font-medium opacity-80">{t.label}</span>
                            {isActive && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-indigo-500 rounded-r-full" />}
                        </button>
                    );
                })}
            </div>

            <button onClick={toggleTheme} className="p-3 text-slate-400 hover:text-indigo-400 transition-colors">
                {darkMode ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
            </button>
        </div>
    );
};

// ─────────────── MAIN LAYOUT ───────────────
// Helper for headers
const getAuthHeaders = () => {
    const tokenData = localStorage.getItem("user");
    const token = tokenData ? JSON.parse(tokenData).access : null;
    return token ? { Authorization: `Bearer ${token}` } : {};
};

export default function AgentTutor() {
    const location = useLocation();
    const navigate = useNavigate();
    const initialMessageProcessed = useRef(false);

    // Get state from navigation (Orchestrator or Router)
    const { initialMessage, topic } = location.state || {};


    const [activeTab, setActiveTab] = useState("concepts");
    const [messages, setMessages] = useState([]);
    const [darkMode, setDarkMode] = useState(() => localStorage.getItem("theme") === "dark");
    const [visualizationContent, setVisualizationContent] = useState(null);
    const [isRegenerating, setIsRegenerating] = useState(false);
    const [autoStartQuiz, setAutoStartQuiz] = useState(false);

    const handleRegenerate = async () => {
        setIsRegenerating(true);
        try {
            // No topic implies "use active session topic"
            const res = await axios.post(`${DJANGO_BASE_URL}/chat/regenerate_visualization/`, {}, { headers: getAuthHeaders() });
            if (res.data.visualization) {
                setVisualizationContent(res.data.visualization);
            }
        } catch (err) {
            console.error("Regeneration failed", err);
        } finally {
            setIsRegenerating(false);
        }
    };

    useEffect(() => {
        // If agent mode provided specific messages, verify/load them
        if (initialMessage) {
            setMessages([{ sender: "bot", text: initialMessage }]);
        }

        if (darkMode) document.documentElement.classList.add("dark");
        else document.documentElement.classList.remove("dark");
        localStorage.setItem("theme", darkMode ? "dark" : "light");
    }, [initialMessage, darkMode]);

    // Auto-Start (Copied from original AgentTutor)
    useEffect(() => {
        if (initialMessageProcessed.current) return;

        const initSession = async () => {
            // Only reset and auto-start if we differ from standard Orchestrator flow (i.e. if we have a topic but no roadmap yet)
            if (topic && !initialMessage) {
                await callResetApi(topic);
                // Send the topic as the first message to kickstart the tutor
                await callAgentApi({ message: topic });
            }
            initialMessageProcessed.current = true;
        };

        if (topic) {
            initSession();
        }
    }, [topic, initialMessage]);

    // HANDLER: Quiz Completion -> Backend Score Update
    const handleQuizComplete = async (stats) => {
        console.log("Quiz Complete! Stats:", stats);
        try {
            const tokenData = localStorage.getItem("user");
            const token = tokenData ? JSON.parse(tokenData).access : null;
            const headers = token ? { "Authorization": `Bearer ${token}` } : {};

            const res = await axios.post(
                "http://localhost:8000/api/main-agent/report_success/",
                {
                    source: "tutor",
                    quiz_stats: stats
                },
                { headers }
            );

            // Show success message from backend
            setMessages(prev => [...prev, { sender: "bot", text: `Quiz Result: ${stats.correct}/${stats.total}\n\n${res.data.reply}` }]);

            // Handle Action (Navigation)
            if (res.data.action) {
                const action = res.data.action;
                setTimeout(() => {
                    if (action.view === 'code') navigate(`/agent-code?topic=${encodeURIComponent(action.data?.topic)}`);
                    if (action.view === 'tutor') {
                        // Refresh Tutor (New Topic)
                        navigate('/agent-tutor', { state: { initialMessage: res.data.reply } });
                        // Force reload if same route? modify key?
                        // For now, react-router handles state updates well.
                    }
                }, 2000);
            }

        } catch (e) {
            console.error("Quiz Report Error:", e);
            setMessages(prev => [...prev, { sender: "bot", text: "Error submitting quiz result." }]);
        }
    };


    return (
        <div className="flex w-screen h-screen bg-white dark:bg-slate-950 font-sans overflow-hidden">
            {/* 1. LEFT SIDEBAR */}
            <Sidebar
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                darkMode={darkMode}
                toggleTheme={() => setDarkMode(!darkMode)}
            />

            {/* 2. CENTER CHAT */}
            <div className="flex-1 flex flex-col min-w-0">
                <header className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 backdrop-blur-sm z-10 w-full">
                    <div className="flex items-center justify-between w-full">
                        <h1 className="text-xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
                            Agent Tutor
                        </h1>
                        {topic && <span className="text-sm px-3 py-1 bg-red-100 dark:bg-red-900/20 text-red-600 rounded-full">{topic}</span>}
                    </div>
                </header>
                <div className="flex-1 overflow-hidden relative">
                    <ChatArea messages={messages} setMessages={setMessages} setVisualizationContent={setVisualizationContent} setActiveTab={setActiveTab} setAutoStartQuiz={setAutoStartQuiz} />
                </div>
            </div>

            {/* 3. RIGHT TOOLS PANEL */}
            <div className="w-96 flex-shrink-0 border-l border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col relative shadow-xl z-20">
                <div className="flex-1 overflow-hidden">
                    {activeTab === "concepts" && <KeyConceptsPanel />}
                    {activeTab === "visualizer" && <VisualizerRenderer htmlContent={visualizationContent} onRegenerate={handleRegenerate} isRegenerating={isRegenerating} />}
                    {activeTab === "concepts" && <KeyConceptsPanel />}
                    {activeTab === "visualizer" && <VisualizerRenderer htmlContent={visualizationContent} onRegenerate={handleRegenerate} isRegenerating={isRegenerating} />}
                    {activeTab === "quiz" && <QuizPanel messages={messages} onQuizComplete={handleQuizComplete} autoStart={autoStartQuiz} />}
                    {activeTab === "notes" && <NotesPanel messages={messages} />}
                    {activeTab === "notes" && <NotesPanel messages={messages} />}
                </div>
            </div>
        </div>
    );
}
