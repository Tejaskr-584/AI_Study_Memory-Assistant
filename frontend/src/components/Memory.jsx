// frontend/src/components/Memory.jsx
/**
 * AI Study Memory Assistant - Memory Display Component
 * 
 * This component displays:
 * - Weak topics (what user struggles with)
 * - Learning statistics (progress tracking)
 * - Recent mistakes (for learning)
 * - Overall progress and recommendations
 */

import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../api';
import '../styles/Memory.css';

const Memory = () => {
  // ===================================
  // STATE MANAGEMENT
  // ===================================

  // Memory data fetched from backend
  const [memoryData, setMemoryData] = useState({
    weak_topics: [],
    total_questions: 0,
    total_quizzes_taken: 0,
    topics_covered: 0,
    recent_mistakes: [],
    user_preferences: {},
    all_topics: [],
    chat_history_length: 0,
    quiz_accuracy: 0,
    learning_streak: 0,
    best_streak: 0,
    topic_mastery: [],
    difficulty_performance: {},
    recent_activity: [],
    study_recommendations: []
  });

  // Whether data is being fetched
  const [isLoading, setIsLoading] = useState(true);

  // Error message if fetch fails
  const [error, setError] = useState('');

  // ===================================
  // EFFECTS
  // ===================================

  /**
   * Effect: Fetch memory data from backend on component mount
   * and set up periodic refresh (every 3 seconds)
   */
  useEffect(() => {
    // Fetch immediately on mount
    fetchMemoryData();

    // Set up interval to refresh memory data every 3 seconds
    // This shows real-time updates as user interacts with chat
    const interval = setInterval(fetchMemoryData, 3000);

    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, []);

  // ===================================
  // API COMMUNICATION
  // ===================================

  /**
   * Fetch memory data from backend /memory endpoint
   * Shows what the AI remembers about the user
   */
  const fetchMemoryData = async () => {
    try {
      setError('');

      const response = await fetch(`${BACKEND_URL}/api/memory`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const payload = await response.json();
      setMemoryData(payload.data);
      setIsLoading(false);

    } catch (err) {
      console.error('Error fetching memory:', err);
      setError(`Cannot fetch memory data. Is backend running at ${BACKEND_URL}?`);
      setIsLoading(false);
    }
  };

  // ===================================
  // HELPER FUNCTIONS
  // ===================================

  /**
   * Calculate learning progress percentage
   * Based on questions asked and topics covered
   */
  const calculateProgressPercentage = () => {
    const maxQuestions = 50; // Arbitrary max for visualization
    return Math.min((memoryData.total_questions / maxQuestions) * 100, 100);
  };

  /**
   * Get color for topic strength indicator
   * Red = weak, Yellow = moderate, Green = strong
   */
  const getTopicColor = (topic) => {
    const weakTopics = memoryData.weak_topics || [];
    if (weakTopics.includes(topic)) {
      return '#ff6b6b'; // Red for weak topics
    }
    return '#4ecdc4'; // Teal for strong topics
  };

  const getMasteryLabel = (value) => {
    if (value >= 80) return 'Strong';
    if (value >= 55) return 'Growing';
    return 'Needs Focus';
  };

  /**
   * Format date from ISO string to readable format
   */
  const formatDate = (isoString) => {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // ===================================
  // RENDER FUNCTIONS
  // ===================================

  /**
   * Render weak topics section
   * Shows topics user struggles with and needs to focus on
   */
  const renderWeakTopics = () => {
    const weakTopics = memoryData.weak_topics || [];

    if (weakTopics.length === 0) {
      return (
        <div className="empty-state">
          <p>🌟 You haven't struggled with any topics yet! Keep learning!</p>
        </div>
      );
    }

    return (
      <div className="topics-grid">
        {weakTopics.map((topic, idx) => (
          <div key={idx} className="topic-card weak">
            <div className="topic-icon">⚠️</div>
            <h4>{topic}</h4>
            <p className="topic-hint">Focus area - Practice more on this</p>
          </div>
        ))}
      </div>
    );
  };

  /**
   * Render all known topics
   * Shows topics user has learned about
   */
  const renderAllTopics = () => {
    const allTopics = memoryData.all_topics || [];
    const weakTopics = memoryData.weak_topics || [];

    if (allTopics.length === 0) {
      return (
        <div className="empty-state">
          <p>📚 Start asking questions to build your topic list!</p>
        </div>
      );
    }

    return (
      <div className="topics-grid">
        {allTopics.map((topic, idx) => {
          const isWeak = weakTopics.includes(topic);
          return (
            <div key={idx} className={`topic-card ${isWeak ? 'weak' : 'strong'}`}>
              <div className="topic-icon">{isWeak ? '⚠️' : '✅'}</div>
              <h4>{topic}</h4>
              <p className="topic-hint">
                {isWeak ? 'Needs focus' : 'You\'re doing well!'}
              </p>
            </div>
          );
        })}
      </div>
    );
  };

  /**
   * Render recent mistakes
   * Shows what user got wrong (for learning from errors)
   */
  const renderRecentMistakes = () => {
    const mistakes = memoryData.recent_mistakes || [];

    if (mistakes.length === 0) {
      return (
        <div className="empty-state">
          <p>✅ No mistakes recorded yet. You're doing great!</p>
        </div>
      );
    }

    return (
      <div className="mistakes-list">
        {mistakes.map((mistake, idx) => (
          <div key={idx} className="mistake-card">
            <div className="mistake-header">
              <h5>{mistake.topic}</h5>
              <span className="mistake-time">{formatDate(mistake.timestamp)}</span>
            </div>
            <div className="mistake-question">
              <p><strong>Q:</strong> {mistake.question}</p>
            </div>
            <div className="mistake-answer">
              <p>
                <strong>Your answer:</strong> {mistake.user_answer}
              </p>
              <p className="correct-answer">
                <strong>Correct:</strong> {mistake.correct_answer}
              </p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  /**
   * Render statistics cards
   * Shows overall learning progress
   */
  const renderStats = () => {
    const stats = [
      {
        label: 'Questions Asked',
        value: memoryData.total_questions,
        icon: '❓',
        color: '#0099ff'
      },
      {
        label: 'Quizzes Taken',
        value: memoryData.total_quizzes_taken,
        icon: '📝',
        color: '#00d4ff'
      },
      {
        label: 'Topics Covered',
        value: memoryData.topics_covered,
        icon: '📚',
        color: '#4ecdc4'
      },
      {
        label: 'Chat Messages',
        value: memoryData.chat_history_length,
        icon: '💬',
        color: '#a8e6cf'
      },
      {
        label: 'Quiz Accuracy',
        value: `${memoryData.quiz_accuracy || 0}%`,
        icon: '✓',
        color: '#8fd694'
      },
      {
        label: 'Learning Streak',
        value: memoryData.learning_streak || 0,
        icon: '↗',
        color: '#ffc857'
      }
    ];

    return (
      <div className="stats-grid">
        {stats.map((stat, idx) => (
          <div key={idx} className="stat-card" style={{ borderColor: stat.color }}>
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-value">{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </div>
        ))}
      </div>
    );
  };

  const renderRecommendations = () => {
    const recommendations = memoryData.study_recommendations || [];

    return (
      <div className="recommendation-list">
        {recommendations.map((recommendation, idx) => (
          <div key={idx} className="recommendation-card">
            <span className="recommendation-dot"></span>
            <p>{recommendation}</p>
          </div>
        ))}
      </div>
    );
  };

  const renderTopicMastery = () => {
    const topics = memoryData.topic_mastery || [];

    if (topics.length === 0) {
      return (
        <div className="empty-state">
          <p>Take a quiz to unlock topic mastery tracking.</p>
        </div>
      );
    }

    return (
      <div className="mastery-list">
        {topics.map((topic, idx) => (
          <div key={idx} className="mastery-row">
            <div className="mastery-row-header">
              <span>{topic.topic}</span>
              <strong>{getMasteryLabel(topic.mastery)} · {topic.mastery}%</strong>
            </div>
            <div className="mastery-bar">
              <div
                className="mastery-fill"
                style={{
                  width: `${topic.mastery}%`,
                  background: topic.mastery >= 80 ? '#4ecdc4' : topic.mastery >= 55 ? '#ffc857' : '#ff6b6b'
                }}
              ></div>
            </div>
            <div className="mastery-meta">
              {topic.quiz_correct}/{topic.quiz_total} quiz answers correct · {topic.mistakes} mistakes
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderDifficultyPerformance = () => {
    const performance = memoryData.difficulty_performance || {};
    const levels = ['beginner', 'intermediate', 'advanced'];

    return (
      <div className="difficulty-performance-grid">
        {levels.map(level => {
          const data = performance[level] || { accuracy: 0, correct: 0, total: 0 };
          return (
            <div key={level} className="difficulty-performance-card">
              <div className="difficulty-name">{level}</div>
              <div className="difficulty-score">{data.accuracy}%</div>
              <div className="difficulty-subtext">{data.correct}/{data.total} correct</div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderActivityTimeline = () => {
    const activity = memoryData.recent_activity || [];

    if (activity.length === 0) {
      return (
        <div className="empty-state">
          <p>Recent chats and quiz mistakes will appear here.</p>
        </div>
      );
    }

    return (
      <div className="activity-list">
        {activity.map((item, idx) => (
          <div key={idx} className={`activity-item ${item.type}`}>
            <div>
              <strong>{item.title}</strong>
              <p>{(item.topics || []).join(', ') || 'General Learning'}</p>
            </div>
            <span>{formatDate(item.timestamp)}</span>
          </div>
        ))}
      </div>
    );
  };

  // ===================================
  // MAIN COMPONENT RENDER
  // ===================================

  if (isLoading && memoryData.total_questions === 0) {
    return (
      <div className="memory-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading your memory...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="memory-container">
      {/* Header */}
      <div className="memory-header">
        <h2>🧠 Your Learning Memory</h2>
        <p>AI remembers what you struggle with and adapts accordingly</p>
      </div>

      {/* Error message if present */}
      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* Main content sections */}
      <div className="memory-content">
        {/* STATISTICS SECTION */}
        <section className="memory-section">
          <h3 className="section-title">📊 Your Progress</h3>
          {renderStats()}

          {/* Progress bar */}
          <div className="progress-container">
            <div className="progress-label">
              <span>Learning Progress</span>
              <span className="progress-percent">{calculateProgressPercentage().toFixed(0)}%</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${calculateProgressPercentage()}%` }}
              ></div>
            </div>
          </div>
        </section>

        <section className="memory-section">
          <h3 className="section-title">Personalized Recommendations</h3>
          <p className="section-hint">
            Suggestions are generated from weak topics, quiz accuracy, and recent activity
          </p>
          {renderRecommendations()}
        </section>

        <section className="memory-section">
          <h3 className="section-title">Topic Mastery Levels</h3>
          <p className="section-hint">
            Mastery combines quiz performance, mistakes, and learning activity
          </p>
          {renderTopicMastery()}
        </section>

        <section className="memory-section">
          <h3 className="section-title">Difficulty Performance</h3>
          {renderDifficultyPerformance()}
        </section>

        {/* WEAK TOPICS SECTION */}
        <section className="memory-section">
          <h3 className="section-title">⚠️ Topics You Need to Focus On</h3>
          <p className="section-hint">
            The more you ask about a topic, the better the AI understands your learning pattern
          </p>
          {renderWeakTopics()}
        </section>

        {/* ALL TOPICS SECTION */}
        <section className="memory-section">
          <h3 className="section-title">📚 All Topics Learned</h3>
          <p className="section-hint">
            Topics you've discussed with the AI
          </p>
          {renderAllTopics()}
        </section>

        <section className="memory-section">
          <h3 className="section-title">Recent Activity Timeline</h3>
          {renderActivityTimeline()}
        </section>

        {/* RECENT MISTAKES SECTION */}
        <section className="memory-section">
          <h3 className="section-title">❌ Recent Mistakes (Learning from Errors)</h3>
          <p className="section-hint">
            Review your mistakes to improve faster
          </p>
          {renderRecentMistakes()}
        </section>

        {/* PERSONALIZATION INFO */}
        <section className="memory-section info-section">
          <h3 className="section-title">🎯 How AI Personalization Works</h3>
          <div className="info-cards">
            <div className="info-card">
              <div className="info-number">1️⃣</div>
              <h4>You Ask Questions</h4>
              <p>Chat with the AI about topics you want to learn</p>
            </div>
            <div className="info-card">
              <div className="info-number">2️⃣</div>
              <h4>AI Remembers</h4>
              <p>System detects weak topics after 3+ questions</p>
            </div>
            <div className="info-card">
              <div className="info-number">3️⃣</div>
              <h4>AI Adapts</h4>
              <p>Responses become simpler and more personalized</p>
            </div>
            <div className="info-card">
              <div className="info-number">4️⃣</div>
              <h4>You Improve</h4>
              <p>Quizzes focus on weak areas to strengthen learning</p>
            </div>
          </div>
        </section>

        {/* PREFERENCES DISPLAY */}
        <section className="memory-section">
          <h3 className="section-title">⚙️ Your Preferences</h3>
          <div className="preferences-display">
            <div className="pref-item">
              <span className="pref-label">Difficulty Level:</span>
              <span className="pref-value">
                {memoryData.user_preferences?.difficulty || 'Beginner'}
              </span>
            </div>
            <div className="pref-item">
              <span className="pref-label">Learning Style:</span>
              <span className="pref-value">
                {memoryData.user_preferences?.learning_style || 'Simple Explanations'}
              </span>
            </div>
          </div>
        </section>
      </div>

      {/* Refresh indicator */}
      <div className="refresh-indicator">
        <span className="sync-dot"></span>
        Real-time memory sync enabled
      </div>
    </div>
  );
};

export default Memory;
