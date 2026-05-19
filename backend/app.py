# backend/app.py
"""
AI Study Memory Assistant - Flask Backend Server
Main application file that serves the API and coordinates all systems.

This file handles:
- Flask HTTP server setup
- CORS configuration for frontend communication
- API endpoints for chat, memory, and quiz
- Integration of memory.py, ai_logic.py, and quiz.py
- Error handling and data validation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from memory import UserMemory
from ai_logic import AILogic
from quiz import QuizGenerator
import json
import re
import sys
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ===================================
# FLASK APP INITIALIZATION
# ===================================

app = Flask(__name__)

# Enable CORS (Cross-Origin Resource Sharing) for frontend
# This allows requests from http://localhost:5173 (Vite dev server)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# ===================================
# GLOBAL INSTANCES (Shared across requests)
# ===================================

# Initialize user memory (persists to memory.json)
user_memory = UserMemory(user_id="default", memory_file="memory.json")

# Initialize AI logic with memory
ai_logic = AILogic(user_memory)

# Initialize quiz generator with memory
quiz_generator = QuizGenerator(user_memory)

# Cache Gemini recommendations so the memory dashboard can refresh often
# without making a model call on every poll.
recommendations_cache = {
    "signature": None,
    "recommendations": None
}

print("\n✅ All systems initialized!")
print(f"   📚 Memory: {user_memory.memory_file}")
print(f"   🤖 AI Logic: Ready")
print(f"   📝 Quiz System: Ready\n")

# ===================================
# HELPER FUNCTIONS
# ===================================

def success_response(data, message="Success"):
    """
    Create a successful JSON response.
    
    Args:
        data: The response data
        message: Status message
    
    Returns: (dict, status_code)
    """
    return {
        "success": True,
        "message": message,
        "data": data
    }, 200


def error_response(error_message, status_code=400):
    """
    Create an error JSON response.
    
    Args:
        error_message: Description of the error
        status_code: HTTP status code
    
    Returns: (dict, status_code)
    """
    return {
        "success": False,
        "error": error_message
    }, status_code


def validate_request_data(required_fields):
    """
    Decorator to validate incoming JSON request data.
    
    Args:
        required_fields: List of required field names
    
    Returns: Decorator function
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            # Check if request has JSON data
            if not request.is_json:
                return error_response("Request must be JSON", 400)
            
            data = request.get_json()
            
            # Check for required fields
            for field in required_fields:
                if field not in data:
                    return error_response(f"Missing required field: {field}", 400)
            
            return f(*args, **kwargs)
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


def useful_topics(topics):
    """Filter placeholder topics before sending personalization hints to the UI."""
    ignored_topics = {"unknown", "general", "general learning", ""}
    return [
        topic for topic in topics
        if str(topic).strip().lower() not in ignored_topics
    ]


def get_ai_recommendations(memory_summary):
    """Use Gemini to phrase personalized study recommendations when available."""
    if not ai_logic.llm_client.is_available():
        return memory_summary.get("study_recommendations", [])
    
    signature_payload = {
        "weak_topics": memory_summary.get("weak_topics", []),
        "strongest_topics": memory_summary.get("strongest_topics", []),
        "quiz_accuracy": memory_summary.get("quiz_accuracy", 0),
        "difficulty_performance": memory_summary.get("difficulty_performance", {}),
        "recent_mistakes": memory_summary.get("recent_mistakes", [])[-3:],
    }
    signature = json.dumps(signature_payload, sort_keys=True)
    
    if recommendations_cache["signature"] == signature:
        return recommendations_cache["recommendations"]
    
    prompt = f"""
You are a study coach for an AI Study Memory Assistant.
Use this learning analytics data:
{json.dumps(signature_payload, indent=2)}

Return ONLY valid JSON:
{{"recommendations": ["short recommendation 1", "short recommendation 2", "short recommendation 3"]}}

Make the recommendations specific, encouraging, and useful for the next study action.
"""
    
    try:
        raw_response = ai_logic.llm_client.generate_response(prompt)
        payload_text = raw_response.strip()
        payload_text = re.sub(r"^```(?:json)?", "", payload_text, flags=re.IGNORECASE).strip()
        payload_text = re.sub(r"```$", "", payload_text).strip()
        payload = json.loads(payload_text)
        recommendations = payload.get("recommendations", [])
        if isinstance(recommendations, list) and recommendations:
            cleaned = [str(item).strip() for item in recommendations if str(item).strip()]
            recommendations_cache["signature"] = signature
            recommendations_cache["recommendations"] = cleaned[:4]
            return recommendations_cache["recommendations"]
    except Exception as exc:
        print(f"Gemini recommendations failed, using analytics recommendations: {exc}")
    
    return memory_summary.get("study_recommendations", [])

# ===================================
# API ENDPOINTS
# ===================================

@app.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    Returns server status and information.
    """
    return success_response({
        "status": "online",
        "server": "AI Study Memory Assistant",
        "version": "1.0.0",
        "features": ["chat", "memory", "quiz"],
        "backend_url": "http://localhost:5000"
    }, "Backend server is running!")


@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """
    POST /api/chat
    
    Main chat endpoint. Receives user message, generates personalized AI response.
    
    REQUEST JSON:
    {
        "message": "What is a process?"
    }
    
    RESPONSE JSON:
    {
        "success": true,
        "data": {
            "response": "Personalized AI response here...",
            "topics_detected": ["Operating Systems"],
            "memory_applied": true,
            "personalization_level": "personalized"
        }
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return error_response("Request must be JSON", 400)
        
        data = request.get_json()
        user_message = data.get("message", "").strip()
        
        # Validate message
        if not user_message:
            return error_response("Message cannot be empty", 400)
        
        if len(user_message) > 5000:
            return error_response("Message too long (max 5000 characters)", 400)
        
        # Generate AI response with memory awareness
        response_data = ai_logic.generate_response(user_message)
        
        # Return success response
        return success_response(
            {
                "response": response_data["response"],
                "topics_detected": response_data["topics_detected"],
                "memory_applied": response_data["memory_applied"],
                "personalization_level": response_data["personalization_level"],
                "response_source": response_data["response_source"],
            },
            "Response generated successfully"
        )
    
    except Exception as e:
        print(f"❌ Error in /chat: {str(e)}")
        traceback.print_exc()
        return error_response(f"Server error: {str(e)}", 500)


@app.route('/api/memory', methods=['GET'])
def get_memory():
    """
    GET /api/memory
    
    Returns user's memory summary (weak topics, stats, mistakes, etc).
    Frontend polls this every 3 seconds to update the Memory dashboard.
    
    RESPONSE JSON:
    {
        "success": true,
        "data": {
            "weak_topics": ["Operating Systems"],
            "total_questions": 5,
            "total_quizzes_taken": 1,
            "topics_covered": 2,
            "recent_mistakes": [...],
            "user_preferences": {...},
            "all_topics": [...]
        }
    }
    """
    try:
        # Get memory summary
        memory_summary = user_memory.get_memory_summary()
        memory_summary["study_recommendations"] = get_ai_recommendations(memory_summary)
        
        return success_response(
            memory_summary,
            "Memory summary retrieved"
        )
    
    except Exception as e:
        print(f"❌ Error in /memory: {str(e)}")
        traceback.print_exc()
        return error_response(f"Server error: {str(e)}", 500)


@app.route('/api/quiz', methods=['GET'])
def generate_quiz():
    """
    GET /api/quiz?num_questions=5&difficulty=beginner
    
    Generates a personalized Gemini-powered quiz focused on weak topics,
    recent mistakes, chat history, and memory data.
    
    QUERY PARAMETERS:
    - num_questions: Number of questions (default: 5, min: 1, max: 20)
    - difficulty: beginner, intermediate, or advanced
    
    RESPONSE JSON:
    {
        "success": true,
        "data": {
            "questions": [
                {
                    "id": 1,
                    "text": "What is a process?",
                    "options": ["A", "B", "C", "D"],
                    "correct": 1,
                    "topic": "Operating Systems"
                },
                ...
            ],
            "total_questions": 5,
            "weak_topics": ["Operating Systems"],
            "difficulty": "beginner",
            "quiz_source": "gemini",
            "personalization_note": "AI-generated from weak topics, mistakes, and chat history"
        }
    }
    """
    try:
        # Get query parameters
        num_questions = request.args.get('num_questions', 5, type=int)
        difficulty = request.args.get('difficulty', 'beginner').strip().lower()
        
        # Validate
        if num_questions < 1 or num_questions > 20:
            return error_response("num_questions must be between 1 and 20", 400)
        
        if difficulty not in QuizGenerator.VALID_DIFFICULTIES:
            return error_response("difficulty must be beginner, intermediate, or advanced", 400)
        
        # Generate quiz
        questions = quiz_generator.generate_quiz(num_questions, difficulty)
        
        # Format response
        formatted_questions = []
        for q in questions:
            formatted_questions.append({
                "id": q["id"],
                "text": q["text"],
                "options": q["options"],
                "correct": q["correct"],  # Note: This is the correct answer index
                "explanation": q.get("explanation", ""),
                "topic": q.get("topic", "Unknown"),
                "difficulty": q.get("difficulty", difficulty),
                "source": q.get("source", "local")
            })
        
        quiz_source = "gemini" if any(q.get("source") == "gemini" for q in questions) else "local"
        
        return success_response(
            {
                "questions": formatted_questions,
                "total_questions": len(formatted_questions),
                "weak_topics": useful_topics(user_memory.get_weak_topics()),
                "difficulty": difficulty,
                "quiz_source": quiz_source,
                "personalization_note": "AI-generated from weak topics, mistakes, and chat history"
                if quiz_source == "gemini"
                else "Local fallback quiz focused on weak topics and review"
            },
            "Quiz generated successfully"
        )
    
    except Exception as e:
        print(f"❌ Error in /quiz (GET): {str(e)}")
        traceback.print_exc()
        return error_response(f"Server error: {str(e)}", 500)


@app.route('/api/quiz', methods=['POST'])
def submit_quiz():
    """
    POST /api/quiz
    
    Submits quiz answers, grades them, and updates memory.
    Records mistakes and updates weak topic tracking.
    
    REQUEST JSON:
    {
        "answers": [
            {
                "question_id": 1,
                "question_text": "What is a process?",
                "topic": "Operating Systems",
                "user_answer": 1,
                "correct_answer": 1
            },
            ...
        ]
    }
    
    RESPONSE JSON:
    {
        "success": true,
        "data": {
            "score": 3,
            "total": 5,
            "percentage": 60,
            "feedback": "Good effort!",
            "mistakes": [...],
            "memory_updated": true,
            "recommendations": {...}
        }
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return error_response("Request must be JSON", 400)
        
        data = request.get_json()
        answers = data.get("answers", [])
        
        # Validate answers
        if not isinstance(answers, list) or len(answers) == 0:
            return error_response("Answers must be a non-empty list", 400)
        
        # Process submission (grades and updates memory)
        result = quiz_generator.process_submission(answers)
        
        # Get recommendations
        recommendations = quiz_generator.get_quiz_recommendations()
        
        # Return success response
        return success_response(
            {
                "score": result["score"],
                "total": result["total"],
                "percentage": result["percentage"],
                "feedback": result["feedback"],
                "mistakes": result["mistakes"],
                "memory_updated": result["memory_updated"],
                "recommendations": recommendations
            },
            "Quiz submitted and graded successfully"
        )
    
    except Exception as e:
        print(f"❌ Error in /quiz (POST): {str(e)}")
        traceback.print_exc()
        return error_response(f"Server error: {str(e)}", 500)


@app.route('/api/memory/reset', methods=['POST'])
def reset_memory():
    """
    POST /api/memory/reset
    
    ADMIN ENDPOINT: Resets user memory to fresh state.
    Useful for demos and testing.
    
    WARNING: This deletes all learning history!
    
    RESPONSE JSON:
    {
        "success": true,
        "message": "Memory reset to fresh state"
    }
    """
    try:
        global user_memory, ai_logic, quiz_generator, recommendations_cache
        
        # Delete memory file
        import os
        if os.path.exists(user_memory.memory_file):
            os.remove(user_memory.memory_file)
        
        # Reinitialize fresh instances
        user_memory = UserMemory(user_id="default", memory_file="memory.json")
        ai_logic = AILogic(user_memory)
        quiz_generator = QuizGenerator(user_memory)
        recommendations_cache = {"signature": None, "recommendations": None}
        
        print("🔄 Memory reset to fresh state")
        
        return success_response(
            {"reset_time": user_memory.memory_data["created_at"]},
            "Memory reset to fresh state"
        )
    
    except Exception as e:
        print(f"❌ Error in /memory/reset: {str(e)}")
        traceback.print_exc()
        return error_response(f"Server error: {str(e)}", 500)


@app.route('/api/debug/status', methods=['GET'])
def debug_status():
    """
    GET /api/debug/status
    
    DEBUG ENDPOINT: Returns detailed system status.
    Shows current state of memory, topics, mistakes, etc.
    
    Useful for troubleshooting and understanding what AI "remembers".
    """
    try:
        weak_topics = user_memory.get_weak_topics()
        all_topics = user_memory.get_all_topics()
        recent_mistakes = user_memory.get_recent_mistakes(5)
        stats = user_memory.memory_data["stats"]
        
        return success_response(
            {
                "weak_topics": weak_topics,
                "all_topics": all_topics,
                "total_topics": len(all_topics),
                "stats": stats,
                "recent_mistakes": recent_mistakes,
                "memory_file": user_memory.memory_file,
                "preferences": user_memory.get_preferences()
            },
            "Debug status retrieved"
        )
    
    except Exception as e:
        print(f"❌ Error in /debug/status: {str(e)}")
        traceback.print_exc()
        return error_response(f"Server error: {str(e)}", 500)


# ===================================
# ERROR HANDLERS
# ===================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors (endpoint not found)."""
    return error_response(
        f"Endpoint not found. Available endpoints: /api/chat, /api/memory, /api/quiz",
        404
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors (internal server error)."""
    print(f"❌ 500 Internal Server Error: {str(error)}")
    return error_response("Internal server error", 500)


# ===================================
# STARTUP & SHUTDOWN
# ===================================

def print_startup_banner():
    """Print startup banner with endpoint information."""
    print("\n" + "="*70)
    print("🚀 AI STUDY MEMORY ASSISTANT BACKEND")
    print("="*70)
    print("\n📡 SERVER RUNNING AT: http://localhost:5000")
    print("\n📚 AVAILABLE ENDPOINTS:")
    print("  GET  /                  - Health check")
    print("  POST /api/chat          - Chat with AI (memory-aware)")
    print("  GET  /api/memory        - Get memory summary")
    print("  GET  /api/quiz          - Generate quiz")
    print("  POST /api/quiz          - Submit quiz answers")
    print("  POST /api/memory/reset  - Reset memory (testing only)")
    print("  GET  /api/debug/status  - Debug status (testing only)")
    print("\n🔗 CORS ENABLED FOR: http://localhost:5173, http://localhost:3000")
    print("\n✅ Ready to receive requests from frontend!")
    print("="*70 + "\n")


# ===================================
# MAIN EXECUTION
# ===================================

if __name__ == '__main__':
    print_startup_banner()
    
    # Print current memory status
    user_memory.print_memory_status()
    
    # Start Flask server
    print("⏳ Starting Flask server...\n")
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False
    )
