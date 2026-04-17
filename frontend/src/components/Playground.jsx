import React, { useState } from 'react';
import SandboxRenderer from './SandboxRenderer';
import CodeDisplay from './CodeDisplay';

const Playground = () => {
  const [prompt, setPrompt] = useState(
    'Generate an HTML + TailwindCSS visualization showing the Bubble Sort process on 5 bars with step-by-step transitions and Next/Reset buttons.'
  );
  const [visualizationCode, setVisualizationCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const problemExamples = [
    'Visualize the Bubble Sort process using colored bars.',
    'Show the Depth-First Search traversal on a tree in HTML + Tailwind.',
    'Create a Binary Search visualization with dynamic highlighting.',
    'Visualize a queue animation using boxes and enqueue/dequeue buttons.'
  ];

  const handleVisualize = async () => {
    if (!prompt) {
      setError('Please enter a problem description.');
      return;
    }

    setVisualizationCode('');
    setError('');
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/code/vis/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });

      const data = await res.json();
      if (res.ok && data.visualization) {
        setVisualizationCode(data.visualization);
      } else {
        setError(data.error || 'Failed to generate visualization.');
      }
    } catch (err) {
      setError(err.message || 'Network error.');
    }

    setIsLoading(false);
  };

  return (
    // ✅ Full viewport width
    <div className="min-h-screen w-screen bg-gray-100 p-4 sm:p-6 md:p-8 font-sans">
      {/* ✅ Removed max-w-6xl — now full width */}
      <div className="w-full">
        {/* Header */}
        <header className="text-center mb-8 md:mb-12 px-2">
          <h1 className="text-4xl md:text-5xl font-extrabold text-indigo-800 tracking-tight">
            AI Visualization Playground
          </h1>
          <p className="mt-3 text-lg md:text-xl text-gray-600 px-2">
            Generate interactive <span className="font-semibold text-indigo-600">HTML + TailwindCSS</span> visualizations for algorithms or logic flows.
          </p>
        </header>

        {/* Input Area — full width with max-w for readability */}
        <div className="bg-white p-5 md:p-6 rounded-2xl shadow-xl border border-indigo-100 max-w-4xl mx-auto">
          <h2 className="text-xl md:text-2xl font-bold text-indigo-700 mb-4">Describe Your Visualization</h2>
          <textarea
            className="w-full p-4 border  border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-indigo-600 h-28 md:h-32 resize-none"
            placeholder="E.g., Show how bubble sort swaps adjacent elements with animations..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoading}
          />

          <div className="flex flex-col sm:flex-row justify-between items-center mt-4 gap-3">
            <button
              onClick={handleVisualize}
              disabled={isLoading}
              className={`px-6 py-3 w-full sm:w-auto font-semibold text-white rounded-xl shadow-md transition duration-300 ${isLoading
                  ? 'bg-indigo-400 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700 hover:scale-[1.02] active:scale-[0.98]'
                }`}
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <svg
                    className="animate-spin h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  <span>Generating...</span>
                </div>
              ) : (
                'Generate Visualization'
              )}
            </button>

            <div className="text-sm text-gray-500 text-center sm:text-left">
              Try:
              {problemExamples.map((ex, index) => (
                <span
                  key={index}
                  onClick={() => setPrompt(ex)}
                  className="cursor-pointer underline text-indigo-500 hover:text-indigo-700 ml-2"
                >
                  {index + 1}
                </span>
              ))}
            </div>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-100 text-red-700 border border-red-300 rounded-lg">
              {error}
            </div>
          )}
        </div>

        {/* Output — FULL WIDTH */}
        <div className="mt-8 w-full px-2">
          <SandboxRenderer code={visualizationCode} isLoading={isLoading} />
        </div>

        <div className="mt-8 w-full px-2">
          <CodeDisplay code={visualizationCode} />
        </div>

        <footer className="mt-16 text-center text-sm text-gray-500 border-t pt-6 pb-8 px-2">
          <p>Powered by AI-generated HTML + Tailwind visualizations.</p>
        </footer>
      </div>
    </div>
  );
};

export default Playground;