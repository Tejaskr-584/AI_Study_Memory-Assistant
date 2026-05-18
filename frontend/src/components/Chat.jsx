// frontend/src/components/Chat.jsx
/**
 * AI Study Memory Assistant - Chat Component
 * 
 * This component handles:
 * - Displaying chat messages
 * - Sending user messages to backend
 * - Receiving AI responses
 * - Showing memory-applied indicators
 * - Loading states
 */

import React, { useState, useRef, useEffect } from 'react';
import { BACKEND_URL } from '../api';
import '../styles/Chat.css';

const Chat = () => {
  // ===================================
  // STATE MANAGEMENT
  // ===================================

  // Array of messages: [{role: 'user'|'assistant', content: '...', memoryApplied: bool}]
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Welcome to AI Study Memory Assistant. Ask a study question and I will adapt as your learning history builds.",
      memoryApplied: false
    }
  ]);

  // Current text being typed in input field
  const [inputValue, setInputValue] = useState('');

  // Whether a request is in progress
  const [isLoading, setIsLoading] = useState(false);

  // Error message if request fails
  const [error, setError] = useState('');

  // Reference to scroll to latest message
  const messagesEndRef = useRef(null);

  // ===================================
  // AUTO-SCROLL TO LATEST MESSAGE
  // ===================================

  /**
   * Effect hook: Auto-scroll chat to bottom when new messages arrive
   * Creates smooth scrolling experience
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // ===================================
  // API COMMUNICATION
  // ===================================

  /**
   * Send message to backend and get AI response
   * Handles:
   * - Sending to /chat endpoint
   * - Receiving personalized response
   * - Tracking if memory was applied
   * - Error handling
   */
  const sendMessage = async () => {
    // Don't send empty messages
    if (!inputValue.trim()) {
      return;
    }

    // Don't send while already loading
    if (isLoading) {
      return;
    }

    // Clear error messages
    setError('');

    try {
      // Step 1: Add user message to chat
      const userMessage = {
        role: 'user',
        content: inputValue,
        memoryApplied: false
      };

      setMessages(prev => [...prev, userMessage]);
      setInputValue(''); // Clear input field
      setIsLoading(true); // Show loading state

      // Step 2: Send to backend
      const response = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: inputValue
        })
      });

      // Step 3: Handle response
      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const payload = await response.json();
      const data = payload.data;

      // Step 4: Add AI response to chat
      // Include memoryApplied flag to show indicator
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        memoryApplied: data.memory_applied || false,
        topicsDetected: data.topics_detected || [],
        personalizationLevel: data.personalization_level || 'generic'
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      // Error handling: show user-friendly message
      console.error('Error:', err);
      
      const errorMessage = {
        role: 'assistant',
        content: `❌ Connection error: Could not reach backend. Make sure the Flask server is running at ${BACKEND_URL}`,
        memoryApplied: false
      };

      setMessages(prev => [...prev, errorMessage]);
      setError(err.message);

    } finally {
      // Always stop loading, whether success or error
      setIsLoading(false);
    }
  };

  // ===================================
  // EVENT HANDLERS
  // ===================================

  /**
   * Handle Enter key to send message
   * Shift+Enter for new line (if needed in future)
   */
  const handleKeyPress = (e) => {
    // Send on Enter, but allow Shift+Enter for new lines
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  /**
   * Clear entire chat history
   * Useful for starting fresh conversation
   */
  const clearChat = () => {
    if (window.confirm('Are you sure? This will clear all messages.')) {
      setMessages([
        {
          role: 'assistant',
          content: "Chat cleared. Ready for a fresh start.",
          memoryApplied: false
        }
      ]);
    }
  };

  // ===================================
  // RENDER FUNCTIONS
  // ===================================

  /**
   * Render individual message with special styling for memory-applied messages
   */
  const renderMessage = (message, index) => {
    const isUser = message.role === 'user';

    return (
      <div key={index} className={`message-container ${isUser ? 'user' : 'assistant'}`}>
        {/* Message bubble */}
        <div className={`message-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}`}>
          <p className="message-text">{message.content}</p>

          {/* Memory-applied indicator for assistant messages */}
          {!isUser && message.memoryApplied && (
            <div className="memory-indicator">
              <span className="memory-badge">🧠 Memory Applied</span>
            </div>
          )}

        </div>
      </div>
    );
  };

  // ===================================
  // MAIN COMPONENT RENDER
  // ===================================

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <h1>💬 Study Chat</h1>
        <button className="clear-btn" onClick={clearChat} title="Clear chat">
          🗑️ Clear
        </button>
      </div>

      {/* Messages area */}
      <div className="messages-area">
        {/* Render all messages */}
        {messages.map((message, index) => renderMessage(message, index))}

        {/* Loading indicator while waiting for response */}
        {isLoading && (
          <div className="message-container assistant">
            <div className="message-bubble assistant-bubble loading">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        {/* Auto-scroll reference point */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="input-area">
        {/* Error message if connection fails */}
        {error && (
          <div className="error-banner">
            ⚠️ {error}
          </div>
        )}

        {/* Input field + Send button */}
        <div className="input-container">
          <textarea
            className="message-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about your studies... 📚"
            disabled={isLoading}
            rows="2"
          />
          <button
            className="send-button"
            onClick={sendMessage}
            disabled={isLoading || !inputValue.trim()}
            title="Send message (Enter)"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>

        {/* Hint text */}
        <p className="input-hint">Press Enter to send</p>
      </div>
    </div>
  );
};

export default Chat;
