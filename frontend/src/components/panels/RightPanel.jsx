import React from 'react';
import { useNavigate } from 'react-router-dom';
import './RightPanel.css';

const RightPanel = () => {
    const navigate = useNavigate();

    return (
        <div className="right-panel overflow-y">
            <h3>Tools</h3>
            <div className="tools-grid overflow-y-auto">
                <button className="tool-button" onClick={() => navigate('/debugger')}>
                    Debugging Zone
                </button>
                <button className="tool-button" onClick={() => navigate('/quiz')}>
                    Concept-Explorer
                </button>
                <button className="tool-button" onClick={() => navigate('/coding')}>
                    Coding Challenges
                </button>
                <button className="tool-button" onClick={() => navigate('/tutor')}>
                    Tutor
                </button>
            </div>
        </div>
    );
};

export default RightPanel;
