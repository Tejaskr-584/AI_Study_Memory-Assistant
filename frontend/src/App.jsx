// frontend/src/App.jsx
/**
 * AI Study Memory Assistant - Main App Component
 * 
 * Integrates all components:
 * - Chat: Ask questions and get AI responses
 * - Memory: View learning profile and weak topics
 * - Quiz: Practice with personalized questions
 */

import { useState } from 'react'
import Chat from './components/Chat'
import Memory from './components/Memory'
import Quiz from './components/Quiz'
import { BACKEND_URL } from './api'
import './App.css'

function App() {
  // ===================================
  // STATE MANAGEMENT
  // ===================================

  // Active tab: 'chat', 'memory', or 'quiz'
  const [activeTab, setActiveTab] = useState('chat')
  const [appVersion, setAppVersion] = useState(0)
  const [resetState, setResetState] = useState('idle')

  // ===================================
  // RENDER FUNCTIONS
  // ===================================

  /**
   * Render the active component based on selected tab
   */
  const renderActiveComponent = () => {
    switch (activeTab) {
      case 'chat':
        return <Chat key={`chat-${appVersion}`} />
      case 'memory':
        return <Memory key={`memory-${appVersion}`} />
      case 'quiz':
        return <Quiz key={`quiz-${appVersion}`} />
      default:
        return <Chat />
    }
  }

  const resetDemo = async () => {
    try {
      setResetState('loading')
      const response = await fetch(`${BACKEND_URL}/api/memory/reset`, { method: 'POST' })

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`)
      }

      setActiveTab('chat')
      setAppVersion((version) => version + 1)
      setResetState('done')
      window.setTimeout(() => setResetState('idle'), 1800)
    } catch (error) {
      console.error('Failed to reset demo:', error)
      setResetState('error')
      window.setTimeout(() => setResetState('idle'), 2200)
    }
  }

  // ===================================
  // MAIN COMPONENT RENDER
  // ===================================

  return (
    <div className="app">
      {/* Header with logo and title */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1 className="app-title">🧠 AI Study Memory Assistant</h1>
            <p className="app-subtitle">
              An AI that remembers what you struggle with and adapts to help you learn better
            </p>
          </div>
          <button
            className={`reset-demo-button ${resetState}`}
            onClick={resetDemo}
            disabled={resetState === 'loading'}
            title="Reset demo memory"
          >
            {resetState === 'loading' && 'Resetting...'}
            {resetState === 'done' && 'Demo Reset'}
            {resetState === 'error' && 'Reset Failed'}
            {resetState === 'idle' && 'Reset Demo'}
          </button>
        </div>
      </header>

      {/* Tab navigation */}
      <nav className="tab-navigation">
        <div className="tabs-container">
          <button
            className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
            title="Chat with AI"
          >
            <span className="tab-icon">💬</span>
            <span className="tab-label">Chat</span>
          </button>

          <button
            className={`tab-button ${activeTab === 'memory' ? 'active' : ''}`}
            onClick={() => setActiveTab('memory')}
            title="View your learning profile"
          >
            <span className="tab-icon">🧠</span>
            <span className="tab-label">Memory</span>
          </button>

          <button
            className={`tab-button ${activeTab === 'quiz' ? 'active' : ''}`}
            onClick={() => setActiveTab('quiz')}
            title="Take personalized quiz"
          >
            <span className="tab-icon">📝</span>
            <span className="tab-label">Quiz</span>
          </button>
        </div>
      </nav>

      {/* Main content area */}
      <main className="app-main">
        <div className="content-container">
          {renderActiveComponent()}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <p className="footer-text">
            Built for AI Agent Hackathon 2026 • React + Flask + adaptive memory demo
          </p>
          <div className="footer-links">
            <a href="#" className="footer-link">GitHub</a>
            <a href="#" className="footer-link">Docs</a>
            <a href="#" className="footer-link">API</a>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
