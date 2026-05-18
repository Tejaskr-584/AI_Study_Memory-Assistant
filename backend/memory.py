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
                return json.load(f)
        
        # Otherwise, create fresh memory structure
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
                "topics_covered": 0
            }
        }
    
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
                "last_discussed": None
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
            if data["is_weak"]:
                weak_topics.append(topic)
        return weak_topics
    
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
        return list(self.memory_data["topics"].keys())
    
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
        
        return {
            "weak_topics": weak_topics,
            "total_questions": self.memory_data["stats"]["total_questions_asked"],
            "total_quizzes_taken": self.memory_data["stats"]["total_quizzes_taken"],
            "topics_covered": self.memory_data["stats"]["topics_covered"],
            "recent_mistakes": recent_mistakes,
            "user_preferences": self.memory_data["preferences"],
            "all_topics": self.get_all_topics(),
            "chat_history_length": len(self.memory_data["chat_history"])
        }
    
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
