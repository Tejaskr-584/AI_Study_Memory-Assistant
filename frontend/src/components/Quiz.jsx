// frontend/src/components/Quiz.jsx
/**
 * AI Study Memory Assistant - Quiz Component
 * 
 * This component handles:
 * - Generating personalized quizzes
 * - Displaying questions with multiple choice options
 * - Tracking user answers
 * - Submitting and grading
 * - Showing detailed results
 */

import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../api';
import '../styles/Quiz.css';

const Quiz = () => {
  // ===================================
  // STATE MANAGEMENT
  // ===================================

  // Quiz questions from backend
  const [questions, setQuestions] = useState([]);

  // Current question index being displayed
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

  // User's selected answers {questionId: selectedOptionIndex}
  const [userAnswers, setUserAnswers] = useState({});

  // Whether quiz is in progress or showing results
  const [quizState, setQuizState] = useState('idle'); // idle, taking, results

  // Quiz results after submission
  const [quizResults, setQuizResults] = useState(null);

  // Whether data is being fetched
  const [isLoading, setIsLoading] = useState(false);

  // Error message if something goes wrong
  const [error, setError] = useState('');

  // ===================================
  // EFFECTS
  // ===================================

  /**
   * Effect: Auto-scroll to top when component mounts
   * Also initializes empty quiz
   */
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // ===================================
  // API COMMUNICATION
  // ===================================

  /**
   * Fetch quiz questions from backend
   * Backend generates personalized questions based on weak topics
   */
  const generateQuiz = async (numQuestions = 5) => {
    try {
      setError('');
      setIsLoading(true);

      const response = await fetch(`${BACKEND_URL}/api/quiz?num_questions=${numQuestions}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const payload = await response.json();
      const data = payload.data;
      setQuestions(data.questions || []);
      setUserAnswers({});
      setCurrentQuestionIndex(0);
      setQuizState('taking');

    } catch (err) {
      console.error('Error generating quiz:', err);
      setError(`Failed to load quiz. Is backend running at ${BACKEND_URL}?`);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Submit quiz answers to backend for grading
   * Backend records mistakes and updates memory
   */
  const submitQuiz = async () => {
    try {
      setError('');
      setIsLoading(true);

      // Prepare answers in format backend expects
      const answers = questions.map(q => ({
        question_id: q.id,
        question_text: q.text,
        topic: q.topic,
        user_answer: userAnswers[q.id] !== undefined ? userAnswers[q.id] : null,
        correct_answer: q.correct
      }));

      const response = await fetch(`${BACKEND_URL}/api/quiz`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ answers })
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const payload = await response.json();
      setQuizResults(payload.data);
      setQuizState('results');

    } catch (err) {
      console.error('Error submitting quiz:', err);
      setError('Failed to submit quiz answers');
    } finally {
      setIsLoading(false);
    }
  };

  // ===================================
  // EVENT HANDLERS
  // ===================================

  /**
   * Handle when user selects an answer option
   */
  const handleSelectAnswer = (optionIndex) => {
    const currentQuestion = questions[currentQuestionIndex];
    setUserAnswers({
      ...userAnswers,
      [currentQuestion.id]: optionIndex
    });
  };

  /**
   * Move to next question
   */
  const goToNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      window.scrollTo(0, 0);
    }
  };

  /**
   * Move to previous question
   */
  const goToPreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
      window.scrollTo(0, 0);
    }
  };

  /**
   * Jump to specific question
   */
  const jumpToQuestion = (index) => {
    setCurrentQuestionIndex(index);
    window.scrollTo(0, 0);
  };

  /**
   * Reset quiz to initial state
   */
  const resetQuiz = () => {
    setQuizState('idle');
    setQuestions([]);
    setCurrentQuestionIndex(0);
    setUserAnswers({});
    setQuizResults(null);
    setError('');
  };

  // ===================================
  // RENDER FUNCTIONS
  // ===================================

  /**
   * Render quiz start screen with difficulty options
   */
  const renderQuizStart = () => {
    return (
      <div className="quiz-start">
        <div className="start-content">
          <h2>📝 Start a Personalized Quiz</h2>
          <p>
            The quiz is automatically focused on your weak topics to help you improve faster!
          </p>

          <div className="quiz-info">
            <div className="info-item">
              <span className="info-icon">🎯</span>
              <div>
                <h4>Smart Focus</h4>
                <p>70% questions on weak topics, 30% review</p>
              </div>
            </div>
            <div className="info-item">
              <span className="info-icon">📊</span>
              <div>
                <h4>Track Progress</h4>
                <p>Results update your learning profile</p>
              </div>
            </div>
            <div className="info-item">
              <span className="info-icon">🧠</span>
              <div>
                <h4>Memory Learns</h4>
                <p>Mistakes are recorded to help personalize AI</p>
              </div>
            </div>
          </div>

          <div className="difficulty-selector">
            <h3>How many questions?</h3>
            <div className="difficulty-buttons">
              <button
                className="difficulty-btn quick"
                onClick={() => generateQuiz(3)}
                disabled={isLoading}
              >
                ⚡ Quick (3 Q)
              </button>
              <button
                className="difficulty-btn standard"
                onClick={() => generateQuiz(5)}
                disabled={isLoading}
              >
                📝 Standard (5 Q)
              </button>
              <button
                className="difficulty-btn full"
                onClick={() => generateQuiz(10)}
                disabled={isLoading}
              >
                🎓 Full (10 Q)
              </button>
            </div>
          </div>

          {isLoading && <div className="loading-text">⏳ Generating personalized quiz...</div>}
        </div>
      </div>
    );
  };

  /**
   * Render quiz taking interface with questions
   */
  const renderQuizTaking = () => {
    if (questions.length === 0) return null;

    const currentQuestion = questions[currentQuestionIndex];
    const isAnswered = userAnswers[currentQuestion.id] !== undefined;
    const selectedAnswer = userAnswers[currentQuestion.id];

    return (
      <div className="quiz-taking">
        {/* Progress bar */}
        <div className="quiz-progress">
          <div className="progress-bar-container">
            <div
              className="progress-fill"
              style={{
                width: `${((currentQuestionIndex + 1) / questions.length) * 100}%`
              }}
            ></div>
          </div>
          <span className="progress-text">
            Question {currentQuestionIndex + 1} of {questions.length}
          </span>
        </div>

        {/* Question navigation */}
        <div className="question-navigator">
          <h4>Questions</h4>
          <div className="navigator-buttons">
            {questions.map((q, idx) => (
              <button
                key={idx}
                className={`nav-btn ${idx === currentQuestionIndex ? 'active' : ''} 
                  ${userAnswers[q.id] !== undefined ? 'answered' : ''}`}
                onClick={() => jumpToQuestion(idx)}
                title={`Question ${idx + 1}`}
              >
                {idx + 1}
              </button>
            ))}
          </div>
        </div>

        {/* Current question */}
        <div className="question-container">
          <div className="question-header">
            <h3>{currentQuestion.text}</h3>
            <span className="question-topic">{currentQuestion.topic}</span>
          </div>

          {/* Answer options */}
          <div className="options-container">
            {currentQuestion.options.map((option, idx) => (
              <label key={idx} className="option-label">
                <input
                  type="radio"
                  name={`question-${currentQuestion.id}`}
                  value={idx}
                  checked={selectedAnswer === idx}
                  onChange={() => handleSelectAnswer(idx)}
                  className="option-radio"
                />
                <span className={`option-text ${selectedAnswer === idx ? 'selected' : ''}`}>
                  {String.fromCharCode(65 + idx)}. {option}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Navigation buttons */}
        <div className="quiz-controls">
          <button
            className="nav-button prev"
            onClick={goToPreviousQuestion}
            disabled={currentQuestionIndex === 0}
          >
            ← Previous
          </button>

          {currentQuestionIndex === questions.length - 1 ? (
            <button
              className="nav-button submit"
              onClick={submitQuiz}
              disabled={!isAnswered || isLoading}
            >
              {isLoading ? '⏳ Submitting...' : '✓ Submit Quiz'}
            </button>
          ) : (
            <button
              className="nav-button next"
              onClick={goToNextQuestion}
              disabled={!isAnswered}
            >
              Next →
            </button>
          )}
        </div>

        {/* Hint about selecting answer */}
        {!isAnswered && (
          <div className="hint">
            <p>💡 Select an answer to continue</p>
          </div>
        )}
      </div>
    );
  };

  /**
   * Render quiz results
   */
  const renderQuizResults = () => {
    if (!quizResults) return null;

    const percentage = quizResults.percentage;
    const isPerfect = percentage === 100;
    const isGood = percentage >= 80;
    const isOkay = percentage >= 60;

    return (
      <div className="quiz-results">
        {/* Score display */}
        <div className={`results-header ${isPerfect ? 'perfect' : isGood ? 'good' : isOkay ? 'okay' : 'needswork'}`}>
          <h2>Quiz Complete! 🎉</h2>
          <div className="score-display">
            <div className="score-circle">
              <span className="score-percent">{quizResults.percentage}%</span>
              <span className="score-total">{quizResults.score}/{quizResults.total}</span>
            </div>
          </div>
        </div>

        {/* Feedback */}
        <div className="feedback-box">
          <p className="feedback-message">{quizResults.feedback}</p>
        </div>

        {/* Mistakes section */}
        {quizResults.mistakes && quizResults.mistakes.length > 0 && (
          <div className="mistakes-review">
            <h3>❌ Review Your Mistakes ({quizResults.mistakes.length})</h3>
            <p className="mistakes-hint">
              Understanding these mistakes will help you improve!
            </p>

            <div className="mistakes-list">
              {quizResults.mistakes.map((mistake, idx) => (
                <div key={idx} className="mistake-review-card">
                  <div className="mistake-number">❌ Question {idx + 1}</div>
                  <div className="mistake-content">
                    <p className="mistake-q">
                      <strong>Question:</strong> {mistake.question}
                    </p>
                    <p className="mistake-topic">
                      <strong>Topic:</strong> {mistake.topic}
                    </p>
                    <div className="mistake-answers">
                      <p className="wrong-answer">
                        <strong>Your answer:</strong> {mistake.user_answer}
                      </p>
                      <p className="correct-answer">
                        <strong>✓ Correct:</strong> {mistake.correct_answer}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Success message for perfect/good scores */}
        {(isPerfect || isGood) && (
          <div className="success-message">
            <span className="success-icon">🌟</span>
            <p>Great job! Keep it up and you'll master all topics!</p>
          </div>
        )}

        {/* Action buttons */}
        <div className="results-actions">
          <button className="action-btn retake" onClick={resetQuiz}>
            📝 Take Another Quiz
          </button>
          <button className="action-btn home" onClick={resetQuiz}>
            🏠 Back to Quiz Menu
          </button>
        </div>

        {/* Memory update info */}
        <div className="memory-update-info">
          <span className="update-icon">🧠</span>
          <p>Your mistakes have been saved to memory. The AI will use this to personalize future responses!</p>
        </div>
      </div>
    );
  };

  // ===================================
  // MAIN COMPONENT RENDER
  // ===================================

  return (
    <div className="quiz-container">
      {/* Header */}
      <div className="quiz-header">
        <h1>📝 Practice Quiz</h1>
        <p>Personalized questions focused on your weak topics</p>
      </div>

      {/* Error banner */}
      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      {/* Content based on quiz state */}
      <div className="quiz-content">
        {quizState === 'idle' && renderQuizStart()}
        {quizState === 'taking' && renderQuizTaking()}
        {quizState === 'results' && renderQuizResults()}
      </div>
    </div>
  );
};

export default Quiz;
