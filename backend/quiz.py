# backend/quiz.py
"""
AI Study Memory Assistant - Quiz Generation & Tracking System
This file handles:
- Generating quiz questions (smart selection based on weak topics)
- Tracking quiz answers and performance
- Recording mistakes to update memory
- Providing feedback to users
"""

from memory import UserMemory
import random

class QuizGenerator:
    """
    Generates personalized quizzes focused on user's weak topics.
    Also tracks performance and updates memory based on results.
    """
    
    def __init__(self, memory):
        """
        Initialize quiz generator with memory reference.
        
        Args:
            memory: UserMemory instance for accessing and updating user data
        """
        self.memory = memory
        
        # Quiz question database organized by topic and difficulty
        # Format: topic -> difficulty -> list of questions
        self.question_database = {
            "Operating Systems": {
                "beginner": [
                    {
                        "id": 1,
                        "text": "What is a process?",
                        "options": [
                            "A file on the disk",
                            "An instance of a program being executed",
                            "A thread of execution",
                            "A memory location"
                        ],
                        "correct": 1,
                        "explanation": "A process is an instance of a program that is being executed. It includes the program code, data, and execution state."
                    },
                    {
                        "id": 2,
                        "text": "What does the CPU scheduler do?",
                        "options": [
                            "Manages memory allocation",
                            "Decides which process runs on the CPU at any given time",
                            "Handles disk I/O operations",
                            "Manages network communication"
                        ],
                        "correct": 1,
                        "explanation": "The CPU scheduler decides which process gets to use the CPU, and for how long. This ensures fair resource distribution."
                    },
                    {
                        "id": 3,
                        "text": "What is context switching?",
                        "options": [
                            "Changing the program's data",
                            "Switching between different files",
                            "Saving the state of one process and loading another onto the CPU",
                            "Changing network connections"
                        ],
                        "correct": 2,
                        "explanation": "Context switching is when the OS saves the current state of a process and loads another process onto the CPU."
                    }
                ],
                "intermediate": [
                    {
                        "id": 4,
                        "text": "What is thrashing in virtual memory?",
                        "options": [
                            "Rapid disk movement",
                            "Excessive page faults causing the system to spend more time paging than executing",
                            "Memory corruption",
                            "CPU overheating"
                        ],
                        "correct": 1,
                        "explanation": "Thrashing occurs when a system spends more time handling page faults and swapping pages than actually executing user programs."
                    }
                ]
            },
            "Databases": {
                "beginner": [
                    {
                        "id": 5,
                        "text": "What is a primary key?",
                        "options": [
                            "The first column in a table",
                            "A unique identifier for each row in a table",
                            "A password for accessing the database",
                            "The main table in the database"
                        ],
                        "correct": 1,
                        "explanation": "A primary key is a unique identifier that ensures each row in a table can be uniquely identified. No two rows can have the same primary key."
                    },
                    {
                        "id": 6,
                        "text": "What does SQL stand for?",
                        "options": [
                            "Standard Query List",
                            "Structured Query Language",
                            "System Query Layout",
                            "Stored Query Language"
                        ],
                        "correct": 1,
                        "explanation": "SQL stands for Structured Query Language. It's used to interact with relational databases."
                    },
                    {
                        "id": 7,
                        "text": "What is normalization?",
                        "options": [
                            "Making data look normal",
                            "Process of organizing data to reduce redundancy",
                            "Backing up data regularly",
                            "Encrypting sensitive data"
                        ],
                        "correct": 1,
                        "explanation": "Normalization is the process of organizing database design to reduce data redundancy and improve data integrity."
                    }
                ],
                "intermediate": [
                    {
                        "id": 8,
                        "text": "What is the difference between INNER JOIN and LEFT JOIN?",
                        "options": [
                            "INNER JOIN is faster",
                            "INNER JOIN returns only matching rows, LEFT JOIN includes all rows from left table",
                            "LEFT JOIN is more secure",
                            "They are the same thing"
                        ],
                        "correct": 1,
                        "explanation": "INNER JOIN returns only rows that have matches in both tables. LEFT JOIN returns all rows from the left table and matching rows from the right table."
                    }
                ]
            },
            "Networking": {
                "beginner": [
                    {
                        "id": 9,
                        "text": "What does TCP stand for?",
                        "options": [
                            "Transfer Code Protocol",
                            "Transmission Control Protocol",
                            "Transfer Control Process",
                            "Transmission Code Protocol"
                        ],
                        "correct": 1,
                        "explanation": "TCP stands for Transmission Control Protocol. It ensures reliable delivery of data packets in order."
                    },
                    {
                        "id": 10,
                        "text": "What is an IP address?",
                        "options": [
                            "A person's identification number",
                            "A unique identifier for a device on a network",
                            "A type of internet service",
                            "A security protocol"
                        ],
                        "correct": 1,
                        "explanation": "An IP address (Internet Protocol address) is a unique numerical label assigned to each device connected to a computer network."
                    },
                    {
                        "id": 11,
                        "text": "What does DNS do?",
                        "options": [
                            "Encrypts data during transmission",
                            "Translates domain names into IP addresses",
                            "Manages file storage",
                            "Filters spam emails"
                        ],
                        "correct": 1,
                        "explanation": "DNS (Domain Name System) translates human-readable domain names (like google.com) into IP addresses that computers can understand."
                    }
                ]
            },
            "Data Structures": {
                "beginner": [
                    {
                        "id": 12,
                        "text": "What is the time complexity of binary search?",
                        "options": [
                            "O(n)",
                            "O(log n)",
                            "O(n²)",
                            "O(1)"
                        ],
                        "correct": 1,
                        "explanation": "Binary search has O(log n) time complexity because it eliminates half the remaining elements with each comparison."
                    },
                    {
                        "id": 13,
                        "text": "What is a stack data structure?",
                        "options": [
                            "A random access structure",
                            "Last-In-First-Out (LIFO) - last element added is first to be removed",
                            "First-In-First-Out (FIFO)",
                            "A hierarchical structure"
                        ],
                        "correct": 1,
                        "explanation": "A stack follows the LIFO principle. Think of a stack of plates: the last plate you put on top is the first one you take off."
                    }
                ]
            },
            "Web Development": {
                "beginner": [
                    {
                        "id": 14,
                        "text": "What does HTML stand for?",
                        "options": [
                            "Hyper Text Markup Language",
                            "High Tech Modern Language",
                            "Home Tool Markup Language",
                            "Hyperlinks and Text Markup Language"
                        ],
                        "correct": 0,
                        "explanation": "HTML stands for Hyper Text Markup Language. It's used to structure content on web pages."
                    },
                    {
                        "id": 15,
                        "text": "What does CSS do?",
                        "options": [
                            "Handles server requests",
                            "Manages databases",
                            "Styles and layouts web pages",
                            "Creates interactive features"
                        ],
                        "correct": 2,
                        "explanation": "CSS (Cascading Style Sheets) is used to style and layout web pages — colors, fonts, spacing, positioning, etc."
                    }
                ]
            }
        }
    
    # ===================================
    # QUIZ GENERATION
    # ===================================
    
    def generate_quiz(self, num_questions=5):
        """
        Generate a personalized quiz focused on user's weak topics.
        
        Strategy:
        1. Get weak topics from memory
        2. Prioritize weak topics for quiz selection
        3. Mix in other topics to maintain broad knowledge
        4. Return appropriate difficulty based on user level
        
        Args:
            num_questions: Number of questions to generate (default: 5)
        
        Returns: List of quiz questions
        """
        questions = []
        weak_topics = self.memory.get_weak_topics()
        all_topics = self.memory.get_all_topics()
        
        # If no weak topics yet, use all known topics
        if not weak_topics:
            weak_topics = list(self.question_database.keys())[:3]
        
        # Build question pool with priority on weak topics
        question_pool = []
        
        # Add questions from weak topics first (70% of quiz)
        weak_question_count = int(num_questions * 0.7)
        for topic in weak_topics:
            if topic in self.question_database:
                topic_questions = self.question_database[topic].get("beginner", [])
                question_pool.extend(topic_questions)
        
        # Add questions from other topics (30% of quiz)
        other_question_count = num_questions - weak_question_count
        other_topics = [t for t in self.question_database.keys() if t not in weak_topics]
        for topic in other_topics[:other_question_count]:
            if topic in self.question_database:
                topic_questions = self.question_database[topic].get("beginner", [])
                question_pool.extend(topic_questions)
        
        # Randomly select questions from pool
        if question_pool:
            selected = random.sample(question_pool, min(num_questions, len(question_pool)))
            questions = selected
        else:
            # Fallback: get any available questions
            for topic in self.question_database:
                if len(questions) < num_questions:
                    topic_questions = self.question_database[topic].get("beginner", [])
                    questions.extend(topic_questions[:num_questions - len(questions)])
        
        return questions[:num_questions]
    
    # ===================================
    # QUIZ SUBMISSION & GRADING
    # ===================================
    
    def process_submission(self, answers):
        """
        Process quiz submission, grade it, and update memory.
        
        Args:
            answers: List of answers submitted by user
            Format: [
                {"question_id": 1, "user_answer": 1, "correct_answer": 0},
                ...
            ]
        
        Returns: {
            "score": int,
            "total": int,
            "percentage": float,
            "mistakes": [...],
            "feedback": str,
            "memory_updated": bool
        }
        """
        score = 0
        total = len(answers)
        mistakes = []
        
        # Grade each answer
        for answer in answers:
            question_id = answer.get("question_id")
            user_answer = answer.get("user_answer")
            correct_answer = answer.get("correct_answer")
            question_text = answer.get("question_text", "Unknown question")
            topic = answer.get("topic", "Unknown")
            
            # Check if answer is correct
            if user_answer == correct_answer:
                score += 1
            else:
                # Record mistake
                mistakes.append({
                    "question_id": question_id,
                    "question": question_text,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer,
                    "topic": topic
                })
                
                # Update memory with mistake
                self.memory.record_mistake(
                    topic=topic,
                    question=question_text,
                    user_answer=user_answer,
                    correct_answer=correct_answer
                )
        
        # Calculate percentage
        percentage = (score / total * 100) if total > 0 else 0
        
        # Generate feedback
        feedback = self._generate_feedback(percentage, mistakes)
        
        # Update quiz stats
        self.memory.update_stats(quizzes_taken=1)
        
        return {
            "score": score,
            "total": total,
            "percentage": round(percentage, 1),
            "mistakes": mistakes,
            "feedback": feedback,
            "memory_updated": True
        }
    
    def _generate_feedback(self, percentage, mistakes):
        """
        Generate personalized feedback based on quiz performance.
        
        Args:
            percentage: Score percentage
            mistakes: List of mistakes made
        
        Returns: Feedback string
        """
        if percentage == 100:
            return "🌟 Perfect score! You're mastering these topics!"
        elif percentage >= 80:
            return "✅ Great job! You're doing really well!"
        elif percentage >= 60:
            return "📚 Good effort! Let's focus on your weak areas. Check the mistakes below."
        elif percentage >= 40:
            return "💪 You're learning! Review the topics where you struggled and try again."
        else:
            return "🎯 This is just practice! Review the explanations and try the quiz again soon."
    
    # ===================================
    # QUIZ ANALYTICS
    # ===================================
    
    def get_quiz_recommendations(self):
        """
        Generate quiz recommendations based on memory.
        
        Returns: {
            "recommended_topics": [...],
            "focus_areas": [...],
            "next_difficulty": str
        }
        """
        weak_topics = self.memory.get_weak_topics()
        mistakes = self.memory.get_recent_mistakes(10)
        total_quizzes = self.memory.memory_data["stats"]["total_quizzes_taken"]
        
        # Determine next difficulty
        if total_quizzes < 3:
            next_difficulty = "beginner"
        elif total_quizzes < 10:
            next_difficulty = "intermediate"
        else:
            next_difficulty = "advanced"
        
        # Find focus areas (topics with most mistakes)
        topic_mistakes = {}
        for mistake in mistakes:
            topic = mistake.get("topic", "Unknown")
            topic_mistakes[topic] = topic_mistakes.get(topic, 0) + 1
        
        focus_areas = sorted(topic_mistakes.items(), key=lambda x: x[1], reverse=True)
        focus_topics = [topic for topic, _ in focus_areas[:3]]
        
        return {
            "recommended_topics": weak_topics[:3] if weak_topics else ["General Learning"],
            "focus_areas": focus_topics,
            "next_difficulty": next_difficulty,
            "total_quizzes_completed": total_quizzes
        }
    
    # ===================================
    # DEBUG & TESTING
    # ===================================
    
    def debug_quiz(self, num_questions=3):
        """
        Debug function: Generate and print quiz for testing.
        
        Args:
            num_questions: Number of questions to generate
        """
        print("\n" + "="*60)
        print("🧪 QUIZ DEBUG - Sample Questions")
        print("="*60 + "\n")
        
        questions = self.generate_quiz(num_questions)
        
        for q in questions:
            print(f"Q{q['id']}: {q['text']}")
            for i, option in enumerate(q['options']):
                print(f"   {i}. {option}")
            print(f"   ✓ Correct: {q['correct']}")
            print(f"   💡 {q['explanation']}\n")
    
    def debug_submission(self):
        """
        Debug function: Test quiz submission processing.
        Simulates a student taking a quiz with some wrong answers.
        """
        print("\n" + "="*60)
        print("🧪 QUIZ SUBMISSION DEBUG")
        print("="*60 + "\n")
        
        # Simulate quiz answers (some correct, some wrong)
        answers = [
            {
                "question_id": 1,
                "question_text": "What is a process?",
                "topic": "Operating Systems",
                "user_answer": 1,  # Correct
                "correct_answer": 1
            },
            {
                "question_id": 2,
                "question_text": "What does the CPU scheduler do?",
                "topic": "Operating Systems",
                "user_answer": 0,  # Wrong
                "correct_answer": 1
            },
            {
                "question_id": 5,
                "question_text": "What is a primary key?",
                "topic": "Databases",
                "user_answer": 1,  # Correct
                "correct_answer": 1
            }
        ]
        
        print("Submitting quiz answers...")
        result = self.process_submission(answers)
        
        print(f"\n📊 RESULTS:")
        print(f"Score: {result['score']}/{result['total']}")
        print(f"Percentage: {result['percentage']}%")
        print(f"Feedback: {result['feedback']}")
        
        if result['mistakes']:
            print(f"\n❌ MISTAKES:")
            for mistake in result['mistakes']:
                print(f"  - {mistake['question']}")
                print(f"    Your answer: {mistake['user_answer']}")
                print(f"    Correct: {mistake['correct_answer']}")
        
        print(f"\n✅ Memory updated: {result['memory_updated']}")
        print("\n📚 Updated memory status:")
        self.memory.print_memory_status()


# ===================================
# DEMO & TESTING
# ===================================

def demo_quiz_system():
    """
    Demo showing complete quiz system workflow.
    """
    print("\n" + "="*70)
    print("📝 QUIZ SYSTEM DEMO - COMPLETE WORKFLOW")
    print("="*70 + "\n")
    
    # Create instances
    memory = UserMemory("demo_quiz_user")
    quiz = QuizGenerator(memory)
    
    # Add some memory history
    print("STEP 1: Adding learning history to memory...")
    memory.add_topic_mention("Operating Systems")
    memory.add_topic_mention("Operating Systems")
    memory.add_topic_mention("Operating Systems")
    memory.add_topic_mention("Databases")
    print("✅ History added\n")
    
    # Generate personalized quiz
    print("STEP 2: Generating personalized quiz...")
    questions = quiz.generate_quiz(5)
    print(f"✅ Generated {len(questions)} questions")
    print(f"   (Prioritizing weak topics: {memory.get_weak_topics()})\n")
    
    # Display sample questions
    print("Sample questions:")
    for i, q in enumerate(questions[:2], 1):
        print(f"  Q{i}: {q['text']}")
    print()
    
    # Simulate submission
    print("STEP 3: Simulating quiz submission...")
    answers = [
        {
            "question_id": questions[0]["id"],
            "question_text": questions[0]["text"],
            "topic": "Operating Systems",
            "user_answer": questions[0]["correct"],  # Correct
            "correct_answer": questions[0]["correct"]
        },
        {
            "question_id": questions[1]["id"],
            "question_text": questions[1]["text"],
            "topic": "Operating Systems",
            "user_answer": 0,  # Wrong
            "correct_answer": questions[1]["correct"]
        }
    ]
    
    result = quiz.process_submission(answers)
    print(f"✅ Quiz submitted: {result['score']}/{result['total']}")
    print(f"   Feedback: {result['feedback']}\n")
    
    # Show recommendations
    print("STEP 4: Getting quiz recommendations...")
    recommendations = quiz.get_quiz_recommendations()
    print(f"✅ Recommended topics: {recommendations['recommended_topics']}")
    print(f"   Focus areas: {recommendations['focus_areas']}")
    print(f"   Next difficulty: {recommendations['next_difficulty']}\n")
    
    # Final memory state
    print("STEP 5: Final memory state...")
    memory.print_memory_status()
    
    print("✅ Demo complete! The quiz system is working with memory integration! 🎉")


if __name__ == "__main__":
    # Run demo when file is executed directly
    demo_quiz_system()
