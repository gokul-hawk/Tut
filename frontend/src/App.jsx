
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import authService from './services/authService';
import Login from './components/Login';
import Register from './components/Register';
import Playground from './components/Playground';
import Quiz from './components/Quiz';
import PythonRunner from './components/Coding';
import Dashboard from './components/Dashboard';
import TutorApp from './components/Chat/TutorApp';
import Debugger from './components/Debugger';
import AgentQuiz from './components/AgentQuiz';
import AgentCode from './components/AgentCode';
import AgentDebugger from './components/AgentDebugger';
import AgentTutor from './components/AgentTutor';
import KnowledgeGraph from './components/KnowledgeGraph'; // Import

import ChatWidget from './components/EmbeddableChat/ChatWidget'; // Import

// Test Page for Widget
const TestWidgetPage = () => (

  <ChatWidget />

);

// A wrapper component to protect routes
const PrivateRoute = ({ children }) => {
  const user = authService.getCurrentUser();
  return user ? children : <Navigate to="/login" />;
};

function App() {

  return (<React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/test-widget" element={<TestWidgetPage />} /> {/* NEW TEST ROUTE */}
        <Route path="/Playground" element={<Playground />} />
        <Route path="/coding" element={<PythonRunner />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path='/quiz' element={<Quiz />} />
        <Route path='/agent-quiz' element={<AgentQuiz />} />
        <Route path='/agent-code' element={<AgentCode />} />
        <Route path='/agent-debugger' element={<AgentDebugger />} />
        <Route path='/agent-tutor' element={<AgentTutor />} />
        <Route path='/knowledge-map' element={
          <div style={{ display: 'flex', height: '100vh', width: '100vw' }}>
             <Dashboard /> {/* Hacky Reuse: Dashboard renders left/right/center. Center is Chat. We want to replace Center? */}
             {/* Better: KnowledgeGraph is a standalone page or overlay. Let's make it a standalone route first. */}
             {/* Actually, I should probably render KnowledgeGraph INSIDE Dashboard layout if possible, or just standalone for clarity. */}
          </div>
        } />
        {/* Let's try standalone first to avoid layout conflicts */}
        <Route path='/map' element={<KnowledgeGraph />} />
        <Route path='/coding' element={<PythonRunner />} />
        <Route path='/tutor' element={<TutorApp />} />
        <Route path='/debugger' element={<Debugger />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>);

}

export default App;