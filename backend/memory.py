# backend/memory.py
"""
AI Study Memory Assistant - User Memory Management System
This file handles all memory operations:
- Storing weak topics
- Tracking mistakes
- Recalling chat history
- Detecting learning patterns
"""

import json
import os
from datetime import datetime
from collections import defaultdict

class UserMemory:
    """
    Manages user learning memory. Stores topics, mistakes, and preferences.
    Data persists in JSON file for future sessions.
    """
    
    def __init__(self, user_id="default", memory_file="memory.json"):
        """
        Initialize memory system.
        
        Args:
            user_id: Unique user identifier (default: "default")
            memory_file: JSON file to store memory (created in backend folder)
        """
        self.user_id = user_id
        self.memory_file = memory_file
        self.memory_data = self._load_or_create_memory()
    
    # ===================================
    # MEMORY LOADING & SAVING
    # ===================================
    
    def _load_or_create_memory(self):
        """
        Load existing memory from JSON file, or create new if doesn't exist.
        Returns: dict with all user memory data
        """
        # If memory file exists, load it
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return self._ensure_memory_shape(json.load(f))
        
        # Otherwise, create fresh memory structure
        return self._default_memory()
    
    def _default_memory(self):
        """Create the full memory shape used by new users."""
        return {
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "topics": {},  # Store topics and their stats
            "mistakes": [],  # Track quiz mistakes
            "chat_history": [],  # Full conversation history
            "preferences": {
                "difficulty": "beginner",
                "learning_style": "simple_explanations"
            },
            "stats": {
                "total_questions_asked": 0,
                "total_quizzes_taken": 0,
                "topics_covered": 0,
                "total_quiz_questions": 0,
                "total_correct_answers": 0,
                "current_streak": 0,
                "best_streak": 0,
                "last_quiz_date": None,
                "difficulty_performance": {
                    "beginner": {"correct": 0, "total": 0},
                    "intermediate": {"correct": 0, "total": 0},
                    "advanced": {"correct": 0, "total": 0}
                }
            }
        }
    
    def _ensure_memory_shape(self, data):
        """
        Upgrade older memory.json files without deleting existing history.
        This keeps the app compatible with saved demo data.
        """
        defaults = self._default_memory()
        data.setdefault("user_id", defaults["user_id"])
        data.setdefault("created_at", defaults["created_at"])
        data.setdefault("topics", {})
        data.setdefault("mistakes", [])
        data.setdefault("chat_history", [])
        data.setdefault("preferences", defaults["preferences"])
        data.setdefault("stats", {})
        
        for key, value in defaults["preferences"].items():
            data["preferences"].setdefault(key, value)
        
        for key, value in defaults["stats"].items():
            data["stats"].setdefault(key, value)
        
        for difficulty, value in defaults["stats"]["difficulty_performance"].items():
            data["stats"]["difficulty_performance"].setdefault(difficulty, value)
        
        for topic_data in data["topics"].values():
            topic_data.setdefault("mention_count", 0)
            topic_data.setdefault("mistake_count", 0)
            topic_data.setdefault("is_weak", False)
            topic_data.setdefault("difficulty_level", "beginner")
            topic_data.setdefault("last_discussed", None)
            topic_data.setdefault("quiz_correct", 0)
            topic_data.setdefault("quiz_total", 0)
            topic_data.setdefault("mastery_level", 0)
        
        return data
    
    def _save_memory(self):
        """Save current memory to JSON file."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory_data, f, indent=2)
        print(f"✅ Memory saved to {self.memory_file}")
    
    # ===================================
    # TOPIC MANAGEMENT
    # ===================================
    
    def add_topic_mention(self, topic, is_mistake=False):
        """
        Record when user discusses a topic.
        Tracks how many times they ask about it.
        
        Args:
            topic: Subject being discussed (e.g., "Operating Systems")
            is_mistake: True if user made an error on this topic
        """
        # If topic doesn't exist, create it
        if topic not in self.memory_data["topics"]:
            self.memory_data["topics"][topic] = {
                "mention_count": 0,
                "mistake_count": 0,
                "is_weak": False,
                "difficulty_level": "beginner",
                "last_discussed": None,
                "quiz_correct": 0,
                "quiz_total": 0,
                "mastery_level": 0
            }
        
        # Increment mention count
        self.memory_data["topics"][topic]["mention_count"] += 1
        
        # If mistake, increment mistake count
        if is_mistake:
            self.memory_data["topics"][topic]["mistake_count"] += 1
        
        # Update last discussed timestamp
        self.memory_data["topics"][topic]["last_discussed"] = datetime.now().isoformat()
        
        # Check if topic is now weak (after 3+ mentions or 2+ mistakes)
        self._detect_weak_topic(topic)
        
        self._save_memory()

    def record_quiz_result(self, score, total, difficulty, topic_results):
        """
        Store quiz-level analytics after grading.
        
        Args:
            score: Number of correct answers
            total: Total submitted answers
            difficulty: beginner, intermediate, or advanced
            topic_results: dict like {"Operating Systems": {"correct": 2, "total": 3}}
        """
        stats = self.memory_data["stats"]
        difficulty = difficulty if difficulty in stats["difficulty_performance"] else "beginner"
        
        stats["total_quiz_questions"] += total
        stats["total_correct_answers"] += score
        stats["last_quiz_date"] = datetime.now().isoformat()
        
        if score == total and total > 0:
            stats["current_streak"] += 1
        else:
            stats["current_streak"] = 0
        stats["best_streak"] = max(stats["best_streak"], stats["current_streak"])
        
        difficulty_stats = stats["difficulty_performance"][difficulty]
        difficulty_stats["correct"] += score
        difficulty_stats["total"] += total
        
        for topic, result in topic_results.items():
            if topic not in self.memory_data["topics"]:
                self.add_topic_mention(topic)
            
            topic_data = self.memory_data["topics"][topic]
            topic_data["quiz_correct"] += result.get("correct", 0)
            topic_data["quiz_total"] += result.get("total", 0)
            topic_data["mastery_level"] = self._calculate_topic_mastery(topic_data)
            topic_data["is_weak"] = topic_data["mastery_level"] < 55 or topic_data["mistake_count"] >= 2
        
        stats["topics_covered"] = len(self.memory_data["topics"])
        self._save_memory()
    
    def _calculate_topic_mastery(self, topic_data):
        """Estimate mastery from quiz accuracy and mistake pressure."""
        quiz_total = topic_data.get("quiz_total", 0)
        quiz_correct = topic_data.get("quiz_correct", 0)
        mistake_count = topic_data.get("mistake_count", 0)
        mention_count = topic_data.get("mention_count", 0)
        
        if quiz_total == 0:
            base = min(mention_count * 12, 45)
        else:
            base = (quiz_correct / quiz_total) * 100
        
        penalty = min(mistake_count * 8, 35)
        return max(0, min(100, round(base - penalty)))
    
    def _detect_weak_topic(self, topic):
        """
        Determine if a topic should be marked as 'weak'.
        A topic is weak if:
        - User asked about it 3+ times, OR
        - User made 2+ mistakes on it
        
        Args:
            topic: Topic to evaluate
        """
        topic_data = self.memory_data["topics"][topic]
        
        # Mark as weak if conditions met
        if topic_data["mention_count"] >= 3 or topic_data["mistake_count"] >= 2:
            topic_data["is_weak"] = True
        else:
            topic_data["is_weak"] = False
    
    def get_weak_topics(self):
        """
        Get list of topics user struggles with.
        Returns: List of weak topic names
        """
        weak_topics = []
        for topic, data in self.memory_data["topics"].items():
            if data["is_weak"] and self._is_useful_topic(topic):
                weak_topics.append(topic)
        return weak_topics
    
    def _is_useful_topic(self, topic):
        """Hide placeholder topics from analytics and recommendations."""
        return str(topic).strip().lower() not in {"", "unknown", "general", "general learning"}
    
    def get_topic_stats(self, topic):
        """
        Get detailed stats for a specific topic.
        Returns: dict with mention count, mistake count, last discussed date
        """
        if topic in self.memory_data["topics"]:
            return self.memory_data["topics"][topic]
        return None
    
    def get_all_topics(self):
        """Get all topics user has discussed."""
        return [
            topic for topic in self.memory_data["topics"].keys()
            if self._is_useful_topic(topic)
        ]
    
    # ===================================
    # MISTAKE TRACKING
    # ===================================
    
    def record_mistake(self, topic, question, user_answer, correct_answer):
        """
        Record a quiz mistake so we can learn from it.
        
        Args:
            topic: What subject was the question about
            question: The quiz question text
            user_answer: What user answered
            correct_answer: What correct answer was
        """
        mistake = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "question": question,
            "user_answer": user_answer,
            "correct_answer": correct_answer
        }
        
        # Add to mistakes list
        self.memory_data["mistakes"].append(mistake)
        
        # Update topic mistake count
        self.add_topic_mention(topic, is_mistake=True)
        
        self._save_memory()
    
    def get_recent_mistakes(self, num_mistakes=5):
        """
        Get user's most recent mistakes.
        Used to show learning progress.
        
        Args:
            num_mistakes: How many recent mistakes to return (default: 5)
        
        Returns: List of recent mistakes
        """
        return self.memory_data["mistakes"][-num_mistakes:]
    
    def get_mistakes_by_topic(self, topic):
        """
        Get all mistakes for a specific topic.
        Useful for showing user their common errors.
        
        Args:
            topic: Topic to filter by
        
        Returns: List of mistakes for that topic
        """
        return [m for m in self.memory_data["mistakes"] if m["topic"] == topic]
    
    # ===================================
    # CHAT HISTORY
    # ===================================
    
    def add_to_history(self, user_message, assistant_response, detected_topics=None):
        """
        Store conversation in history for context.
        This helps AI remember what we talked about.
        
        Args:
            user_message: What user said
            assistant_response: What AI responded
            detected_topics: List of topics mentioned in this exchange
        """
        if detected_topics is None:
            detected_topics = []
        
        # Record user message
        self.memory_data["chat_history"].append({
            "role": "user",
            "content": user_message,
            "topics": detected_topics,
            "timestamp": datetime.now().isoformat()
        })
        
        # Record assistant response
        self.memory_data["chat_history"].append({
            "role": "assistant",
            "content": assistant_response,
            "topics": detected_topics,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_memory()
    
    def get_chat_history(self, num_messages=10):
        """
        Get recent chat history.
        Used for context in AI responses.
        
        Args:
            num_messages: How many recent messages to return
        
        Returns: List of recent messages
        """
        return self.memory_data["chat_history"][-num_messages:]
    
    def get_conversation_context(self, topic):
        """
        Get all previous conversations about a specific topic.
        Helps AI understand what was already explained.
        
        Args:
            topic: Topic to search for
        
        Returns: List of messages mentioning this topic
        """
        context = []
        for message in self.memory_data["chat_history"]:
            if topic in message.get("topics", []):
                context.append(message)
        return context
    
    # ===================================
    # PREFERENCES
    # ===================================
    
    def update_preferences(self, difficulty=None, learning_style=None):
        """
        Update user learning preferences.
        AI will adapt explanations based on these.
        
        Args:
            difficulty: "beginner", "intermediate", or "advanced"
            learning_style: "simple_explanations", "detailed", "with_examples"
        """
        if difficulty:
            self.memory_data["preferences"]["difficulty"] = difficulty
        if learning_style:
            self.memory_data["preferences"]["learning_style"] = learning_style
        
        self._save_memory()
    
    def get_preferences(self):
        """Get user's current learning preferences."""
        return self.memory_data["preferences"]
    
    # ===================================
    # STATISTICS & SUMMARY
    # ===================================
    
    def update_stats(self, questions_asked=0, quizzes_taken=0):
        """
        Update user statistics.
        
        Args:
            questions_asked: Increment total questions by this amount
            quizzes_taken: Increment total quizzes by this amount
        """
        if questions_asked > 0:
            self.memory_data["stats"]["total_questions_asked"] += questions_asked
        if quizzes_taken > 0:
            self.memory_data["stats"]["total_quizzes_taken"] += quizzes_taken
        
        # Update topics covered count
        self.memory_data["stats"]["topics_covered"] = len(self.memory_data["topics"])
        
        self._save_memory()
    
    def get_memory_summary(self):
        """
        Get a summary of user's memory.
        Used by frontend to display stats and weak topics.
        
        Returns: {
            "weak_topics": [...],
            "total_questions": int,
            "recent_mistakes": [...],
            "user_preferences": {...},
            "stats": {...}
        }
        """
        weak_topics = self.get_weak_topics()
        recent_mistakes = self.get_recent_mistakes(5)
        stats = self.memory_data["stats"]
        total_quiz_questions = stats.get("total_quiz_questions", 0)
        total_correct_answers = stats.get("total_correct_answers", 0)
        quiz_accuracy = round((total_correct_answers / total_quiz_questions) * 100, 1) if total_quiz_questions else 0
        
        return {
            "weak_topics": weak_topics,
            "total_questions": self.memory_data["stats"]["total_questions_asked"],
            "total_quizzes_taken": self.memory_data["stats"]["total_quizzes_taken"],
            "topics_covered": len(self.get_all_topics()),
            "quiz_accuracy": quiz_accuracy,
            "learning_streak": stats.get("current_streak", 0),
            "best_streak": stats.get("best_streak", 0),
            "strongest_topics": self.get_strongest_topics(),
            "weakest_topics_detailed": self.get_weakest_topics_detailed(),
            "topic_mastery": self.get_topic_mastery_levels(),
            "difficulty_performance": self.get_difficulty_performance(),
            "improvement_trend": self.get_improvement_trend(),
            "recent_activity": self.get_recent_activity(),
            "study_recommendations": self.get_study_recommendations(),
            "recent_mistakes": recent_mistakes,
            "user_preferences": self.memory_data["preferences"],
            "all_topics": self.get_all_topics(),
            "chat_history_length": len(self.memory_data["chat_history"])
        }
    
    def get_strongest_topics(self):
        """Return topics with the highest mastery scores."""
        topics = self.get_topic_mastery_levels()
        return sorted(topics, key=lambda item: item["mastery"], reverse=True)[:3]
    
    def get_weakest_topics_detailed(self):
        """Return weak topics with useful demo-friendly metadata."""
        topics = self.get_topic_mastery_levels()
        weak = [topic for topic in topics if topic["is_weak"] or topic["mastery"] < 60]
        return sorted(weak, key=lambda item: item["mastery"])[:3]
    
    def get_topic_mastery_levels(self):
        """Build topic mastery cards for the frontend dashboard."""
        mastery = []
        for topic, data in self.memory_data["topics"].items():
            if not self._is_useful_topic(topic):
                continue
            mastery.append({
                "topic": topic,
                "mastery": data.get("mastery_level", self._calculate_topic_mastery(data)),
                "mentions": data.get("mention_count", 0),
                "mistakes": data.get("mistake_count", 0),
                "quiz_total": data.get("quiz_total", 0),
                "quiz_correct": data.get("quiz_correct", 0),
                "is_weak": data.get("is_weak", False)
            })
        return sorted(mastery, key=lambda item: item["mastery"], reverse=True)
    
    def get_difficulty_performance(self):
        """Return accuracy grouped by selected quiz difficulty."""
        performance = {}
        for difficulty, data in self.memory_data["stats"]["difficulty_performance"].items():
            total = data.get("total", 0)
            correct = data.get("correct", 0)
            performance[difficulty] = {
                "correct": correct,
                "total": total,
                "accuracy": round((correct / total) * 100, 1) if total else 0
            }
        return performance
    
    def get_improvement_trend(self):
        """Simple trend summary from recent mistake volume and quiz accuracy."""
        recent_mistakes = len(self.get_recent_mistakes(5))
        accuracy = self.get_memory_summary_quiz_accuracy()
        if accuracy >= 80 and recent_mistakes <= 2:
            return "improving"
        if recent_mistakes >= 4:
            return "needs_revision"
        return "steady"
    
    def get_memory_summary_quiz_accuracy(self):
        """Helper to avoid repeating quiz accuracy math."""
        stats = self.memory_data["stats"]
        total = stats.get("total_quiz_questions", 0)
        correct = stats.get("total_correct_answers", 0)
        return round((correct / total) * 100, 1) if total else 0
    
    def get_recent_activity(self):
        """Create a lightweight activity timeline from chats and mistakes."""
        activity = []
        for message in self.memory_data["chat_history"][-6:]:
            activity.append({
                "type": "chat",
                "title": "Asked a study question" if message.get("role") == "user" else "Received explanation",
                "topics": message.get("topics", []),
                "timestamp": message.get("timestamp")
            })
        for mistake in self.memory_data["mistakes"][-5:]:
            activity.append({
                "type": "mistake",
                "title": f"Missed a question in {mistake.get('topic', 'Unknown')}",
                "topics": [mistake.get("topic", "Unknown")],
                "timestamp": mistake.get("timestamp")
            })
        return sorted(activity, key=lambda item: item.get("timestamp") or "", reverse=True)[:6]
    
    def get_study_recommendations(self):
        """Generate personalized recommendations from memory analytics."""
        weak_topics = self.get_weakest_topics_detailed()
        strong_topics = self.get_strongest_topics()
        difficulty_perf = self.get_difficulty_performance()
        recommendations = []
        
        if weak_topics:
            recommendations.append(f"You should revise {weak_topics[0]['topic']} again.")
        if strong_topics:
            recommendations.append(f"Your strongest topic is {strong_topics[0]['topic']}.")
        if difficulty_perf["beginner"]["accuracy"] >= 75 and difficulty_perf["intermediate"]["total"] == 0:
            recommendations.append("Try intermediate-level quizzes next.")
        if self.get_memory_summary_quiz_accuracy() >= 70:
            recommendations.append("You are improving. Keep mixing chat revision with quizzes.")
        if not recommendations:
            recommendations.append("Start with a beginner quiz so the assistant can learn your strengths.")
        
        return recommendations[:4]
    
    def print_memory_status(self):
        """
        Print human-readable memory status (for debugging).
        Shows what the AI remembers about the user.
        """
        print("\n" + "="*50)
        print("📚 USER MEMORY STATUS")
        print("="*50)
        print(f"User ID: {self.user_id}")
        print(f"Total Topics: {len(self.get_all_topics())}")
        print(f"Weak Topics: {self.get_weak_topics()}")
        print(f"Total Questions Asked: {self.memory_data['stats']['total_questions_asked']}")
        print(f"Total Quizzes Taken: {self.memory_data['stats']['total_quizzes_taken']}")
        print(f"Recent Mistakes: {len(self.get_recent_mistakes(10))}")
        print(f"Chat History Length: {len(self.memory_data['chat_history'])}")
        print(f"Preferences: {self.memory_data['preferences']}")
        print("="*50 + "\n")


# ===================================
# HELPER FUNCTION FOR TESTING
# ===================================

def demo_memory():
    """
    Quick demo to show memory system working.
    Run this to test memory.py independently.
    """
    print("🧪 Testing Memory System...\n")
    
    # Create memory instance
    mem = UserMemory("demo_user")
    
    # Add some topics
    print("➕ Adding topic mentions...")
    mem.add_topic_mention("Operating Systems")
    mem.add_topic_mention("Operating Systems")
    mem.add_topic_mention("Operating Systems")
    mem.add_topic_mention("Databases")
    
    # Record a mistake
    print("❌ Recording a mistake...")
    mem.record_mistake(
        topic="Operating Systems",
        question="What is a process?",
        user_answer="A file on disk",
        correct_answer="An instance of a running program"
    )
    
    # Add to chat history
    print("💬 Adding chat history...")
    mem.add_to_history(
        "What is a process?",
        "A process is an instance of a program being executed.",
        ["Operating Systems"]
    )
    
    # Display memory status
    mem.print_memory_status()
    
    # Show summary
    summary = mem.get_memory_summary()
    print("📊 Memory Summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    # This runs when memory.py is executed directly
    demo_memory()
