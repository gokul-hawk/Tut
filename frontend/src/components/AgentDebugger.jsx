import React, { useState, useEffect } from 'react';
import CodeEditor from './CodeEditor'; // Reuse
import axios from 'axios';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';

const AgentDebugger = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const location = useLocation();
    const topic = searchParams.get("topic") || location.state?.topic;

    const [challenge, setChallenge] = useState(null);
    const [loading, setLoading] = useState(true);
    const [userExplanation, setUserExplanation] = useState("");
    const [verifying, setVerifying] = useState(false);
    const [feedback, setFeedback] = useState(null);
    const [error, setError] = useState(null);
    const [attempts, setAttempts] = useState(0);

    // Pyodide State
    const [editorCode, setEditorCode] = useState("");
    const [pyodide, setPyodide] = useState(null);
    const [isRunning, setIsRunning] = useState(false);
    const [runOutput, setRunOutput] = useState(null);

    // Init Pyodide
    useEffect(() => {
        const initPyodide = async () => {
            try {
                if (window.loadPyodide && !pyodide) {
                    const pyodideInstance = await window.loadPyodide({
                        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.28.3/full/"
                    });
                    setPyodide(pyodideInstance);
                }
            } catch (err) { console.error("Pyodide Error", err); }
        };
        initPyodide();
    }, []);

    // Auto-Fetch
    useEffect(() => {
        if (topic) {
            handleTopicSubmit(topic);
        } else {
            setLoading(false);
            setError("No topic provided.");
        }
    }, [topic]);

    const handleTopicSubmit = async (selectedTopic) => {
        setLoading(true);
        try {
            const userData = JSON.parse(localStorage.getItem("user"));
            const token = userData?.access;
            const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};

            const response = await axios.get(`http://localhost:8000/api/debugger/get-challenge/?topic=${selectedTopic}&count=1`, config);
            const challenges = Array.isArray(response.data) ? response.data : [response.data];

            if (challenges.length > 0) {
                setChallenge(challenges[0]);
                setEditorCode(challenges[0].buggy_code);
            }
        } catch (err) {
            console.error(err);
            setError("Failed to load debug challenge.");
        } finally {
            setLoading(false);
        }
    };

    const handleRunCode = async () => {
        if (!pyodide) return;
        setIsRunning(true);
        setRunOutput(null);
        try {
            await pyodide.runPythonAsync(`
                import sys
                import io
                sys.stdout = io.StringIO()
            `);
            await pyodide.runPythonAsync(editorCode);
            const stdout = pyodide.runPython("sys.stdout.getvalue()");
            setRunOutput(stdout);
        } catch (err) {
            setRunOutput(String(err));
        } finally {
            setIsRunning(false);
        }
    };

    const handleSubmit = async () => {
        if (!challenge || !userExplanation.trim()) return;
        setVerifying(true);
        try {
            const userData = JSON.parse(localStorage.getItem("user"));
            const token = userData?.access;
            const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};

            const response = await axios.post(`http://localhost:8000/api/debugger/verify/`, {
                challenge_id: challenge.id,
                user_explanation: userExplanation
            }, config);

            setFeedback(response.data);

            if (response.data.is_correct) {
                await reportSuccess();
            } else {
                setAttempts(prev => prev + 1);
            }
        } catch (err) {
            console.error(err);
            setError("Verification failed.");
        } finally {
            setVerifying(false);
        }
    };

    const reportSuccess = async () => {
        try {
            const userData = JSON.parse(localStorage.getItem("user"));
            const token = userData?.access;
            const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};

            const res = await axios.post(
                "http://localhost:8000/api/main-agent/report_success/",
                {
                    failed_topics: [],
                    source: "debug",
                    debug_stats: {
                        attempts: attempts + 1, // Current successful attempt
                        explanation_len: userExplanation.length,
                        passed: true
                    }
                },
                config
            );

            if (res.data.action) {
                setTimeout(() => {
                    if (res.data.action.view === 'code') navigate(`/agent-code?topic=${encodeURIComponent(res.data.action.data.topic)}`);
                    if (res.data.action.view === 'debugger') navigate(`/agent-debugger?topic=${encodeURIComponent(res.data.action.data.topic)}`);
                    if (res.data.action.view === 'tutor') navigate('/agent-tutor', { state: { initialMessage: res.data.reply } });
                    if (res.data.action.view === 'Gaps') navigate(`/agent-quiz?topic=${encodeURIComponent(res.data.action.data.topic)}`);
                    if (res.data.action.view === 'dashboard') navigate('/');
                }, 2000);
            } else {
                // No explicit action (e.g., Teaching Phase), go to Tutor to read the reply
                setTimeout(() => {
                    navigate('/agent-tutor', { state: { initialMessage: res.data.reply } });
                }, 2000);
            }
        } catch (e) {
            console.error("Failed to report success", e);
        }
    };

    if (loading) return <div className="h-screen flex items-center justify-center bg-gray-900 text-white">Loading Agent Mission...</div>;

    return (
        <div className="h-screen w-screen bg-gray-950 text-gray-200 p-4 font-sans flex flex-col">
            <header className="flex justify-between items-center mb-4 border-b border-gray-800 pb-2">
                <h1 className="text-xl font-bold text-red-400">🐞 Agent Debugger: {topic}</h1>
            </header>

            <div className="flex-1 grid grid-cols-2 gap-4 h-full overflow-hidden">
                {/* Left: Code */}
                <div className="flex flex-col bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
                    <div className="flex justify-end p-2 bg-gray-800">
                        <button onClick={handleRunCode} className="bg-green-600 px-3 py-1 rounded text-white text-sm hover:bg-green-700">Test Run</button>
                    </div>
                    <div className="flex-1 relative">
                        <CodeEditor code={editorCode} setCode={setEditorCode} />
                    </div>
                    <div className="h-32 bg-black/40 p-2 font-mono text-xs overflow-auto border-t border-gray-800">
                        {runOutput || challenge?.error_output || "No output"}
                    </div>
                </div>

                {/* Right: Interaction */}
                <div className="flex flex-col gap-4">
                    <div className="bg-gray-900 p-4 rounded-xl border border-gray-800">
                        <h3 className="font-bold text-indigo-400 mb-2">The Bug</h3>
                        <p className="text-sm text-gray-400">{challenge?.description}</p>
                    </div>

                    <div className="bg-gray-900 p-4 rounded-xl border border-gray-800 flex-1 flex flex-col">
                        <label className="text-sm font-bold text-gray-400 mb-2">Explain & Fix</label>
                        <textarea
                            className="flex-1 bg-gray-950 border border-gray-700 rounded p-2 text-sm resize-none mb-2"
                            placeholder="Why is this failing?"
                            value={userExplanation}
                            onChange={(e) => setUserExplanation(e.target.value)}
                        />
                        <button
                            onClick={handleSubmit}
                            disabled={verifying}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded font-bold transition"
                        >
                            {verifying ? "Checking..." : "Submit Diagnosis"}
                        </button>
                    </div>

                    {feedback && (
                        <div className={`p-4 rounded-xl border ${feedback.is_correct ? 'bg-green-900/30 border-green-800' : 'bg-red-900/30 border-red-800'}`}>
                            <h3 className={`font-bold ${feedback.is_correct ? 'text-green-400' : 'text-red-400'}`}>
                                {feedback.is_correct ? "Success!" : "Not quite..."}
                            </h3>
                            <p className="text-sm mt-1">{feedback.feedback}</p>
                            {feedback.is_correct && <p className="text-xs mt-2 text-green-300 animate-pulse">Reporting to Agent...</p>}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
export default AgentDebugger;
