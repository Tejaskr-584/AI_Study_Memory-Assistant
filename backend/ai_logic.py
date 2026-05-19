# backend/ai_logic.py
"""
AI Study Memory Assistant - AI Logic & Response Generation
This file handles:
- Topic detection (identifying what subject is being discussed)
- Memory application (personalizing responses based on weak topics)
- Response generation with memory awareness
"""

from memory import UserMemory
from llm_client import GeminiClient
import random
import re

class AILogic:
    """
    Handles AI response generation with memory awareness.
    This is where the "magic" happens - responses change based on what AI remembers!
    """
    
    def __init__(self, memory, llm_client=None):
        """
        Initialize AI logic with memory reference.
        
        Args:
            memory: UserMemory instance for accessing stored data
        """
        self.memory = memory
        self.llm_client = llm_client or GeminiClient()
        
        # Dictionary of topics with keywords to detect them
        # When user message contains these keywords, we know what topic they're asking about
        self.topic_keywords = {
            "Operating Systems": [
                "process", "processes", "thread", "threads", "kernel", "os", "operating system",
                "memory management", "context switch", "context switching", "interrupt", "scheduling",
                "cpu", "processor", "system call"
            ],
            "Databases": [
                "database", "databases", "sql", "query", "queries", "table", "tables", "schema", "index",
                "join", "transaction", "acid", "relationship", "primary key",
                "foreign key", "normalization", "db"
            ],
            "Networking": [
                "network", "tcp", "ip", "http", "dns", "port", "socket",
                "packet", "protocol", "router", "server", "client", "bandwidth",
                "latency", "firewall", "encryption"
            ],
            "Data Structures": [
                "array", "arrays", "list", "queue", "queues", "stack", "stacks", "tree", "trees", "graph", "graphs", "hash",
                "linked list", "binary tree", "heap", "algorithm", "complexity",
                "time complexity", "space complexity", "big o"
            ],
            "Web Development": [
                "html", "css", "javascript", "react", "vue", "angular",
                "frontend", "backend", "api", "rest", "dom", "component",
                "state", "props", "hook", "async", "promise"
            ],
            "Python": [
                "python", "pip", "virtual environment", "venv", "django",
                "flask", "pandas", "numpy", "list comprehension", "decorator",
                "function", "class", "import", "module"
            ],
            "Mathematics": [
                "math", "mathematics", "geometry", "triangle", "area", "perimeter",
                "side", "sides", "cm", "meter", "metre", "equilateral", "isosceles",
                "scalene", "base", "height"
            ]
        }
        
        # Generic explanations (used before memory kicks in)
        self.generic_responses = {
            "Operating Systems": "An operating system is software that manages computer hardware and provides services to applications. It handles processes, memory, and device management.",
            "Databases": "A database is an organized collection of structured data stored on a computer. It allows efficient data retrieval and updates.",
            "Networking": "Computer networking involves connecting computers to share data. Key protocols include TCP/IP for communication.",
            "Data Structures": "Data structures are ways to organize and store data efficiently. Different structures serve different purposes.",
            "Web Development": "Web development involves building applications that run in browsers. It typically includes frontend (client-side) and backend (server-side) components.",
            "Python": "Python is a popular programming language known for simplicity and readability. It's widely used in web development, data science, and automation."
            ,
            "Mathematics": "Mathematics uses formulas and logical steps to solve problems. Tell me the given values, and I can calculate the answer step by step."
        }

        # Direct answers for common study concepts. These are used before the
        # broader topic fallback so the app answers the actual question asked.
        self.concept_responses = {
            "Operating Systems": {
                "process": "A process is a program that is currently running. It includes the program code, the data it uses, and the current execution state managed by the operating system.",
                "thread": "A thread is the smallest unit of execution inside a process. Multiple threads in the same process share memory but can run different tasks.",
                "context switch": "Context switching is when the operating system saves the state of one running process or thread and loads another so the CPU can switch between tasks.",
                "memory management": "Memory management is how the operating system allocates, tracks, and frees RAM so programs can run without interfering with one another.",
            },
            "Databases": {
                "primary key": "A primary key is a column, or set of columns, that uniquely identifies each row in a table.",
                "foreign key": "A foreign key is a column that links one table to the primary key of another table, creating a relationship between them.",
                "normalization": "Normalization is the process of organizing database tables to reduce repeated data and improve consistency.",
                "join": "A join combines rows from two or more tables using a related column, such as matching customer IDs across tables.",
            },
            "Networking": {
                "tcp": "TCP is a reliable transport protocol that delivers data in order and checks that packets arrive correctly.",
                "dns": "DNS translates human-readable domain names like example.com into IP addresses that computers use to locate servers.",
                "ip": "An IP address is a numerical address that identifies a device on a network.",
                "http": "HTTP is the protocol browsers and servers use to request and send web content.",
            },
            "Data Structures": {
                "array": "An array stores items in contiguous positions and lets you access elements quickly by index.",
                "stack": "A stack is a Last-In, First-Out structure, like a pile of plates where the last item added is removed first.",
                "queue": "A queue is a First-In, First-Out structure, like a line where the first item added is removed first.",
                "linked list": "A linked list stores items as nodes, where each node points to the next one instead of being stored contiguously.",
            },
            "Web Development": {
                "html": "HTML defines the structure and content of a web page.",
                "css": "CSS controls the visual presentation of a web page, including layout, colors, spacing, and typography.",
                "javascript": "JavaScript adds behavior and interactivity to web pages.",
                "react": "React is a JavaScript library for building user interfaces from reusable components.",
            },
            "Python": {
                "decorator": "A decorator is a function that wraps another function to extend or modify its behavior without changing the original code directly.",
                "list comprehension": "A list comprehension is a compact way to create a list from an iterable in one expression.",
                "class": "A class is a blueprint for creating objects with related data and behavior.",
                "function": "A function is a reusable block of code that performs a task and can accept inputs or return outputs.",
            },
            "Mathematics": {
                "triangle": "For a triangle, area depends on the information given. If base and height are known, area = 1/2 × base × height. If all three sides are equal, it is an equilateral triangle and area = (√3 / 4) × side².",
            },
        }
        
        # Beginner-friendly explanations (used when topic is weak)
        self.beginner_responses = {
            "Operating Systems": "Since you've asked about OS before, let me explain more simply! Think of an operating system like a manager at a restaurant. It directs requests from apps (customers) to hardware (kitchen). A process is just one task your computer is running.",
            "Databases": "You've been learning databases! Let's keep it simple: A database is like a smart filing cabinet. SQL is the language you use to ask questions like 'Show me all red books' or 'Update this record'.",
            "Networking": "Networking might seem complex, but here's the easy version: Imagine sending a letter. TCP/IP is like the postal system - TCP ensures the whole letter arrives, IP is the address.",
            "Data Structures": "You're working on data structures! Quick recap: Arrays are like rows in a table. Linked lists are like a treasure hunt (each item points to the next). Pick the right one for your problem!",
            "Web Development": "Building websites! Remember: HTML is the structure (skeleton), CSS is the style (clothes), JavaScript is the behavior (thinking). React makes it easier to manage complex sites.",
            "Python": "Python is so readable! Instead of complex syntax, Python reads almost like English. That's why you might find it easier than other languages when you're building something."
            ,
            "Mathematics": "Let's solve it step by step. In math, first identify the shape, then choose the correct formula, then substitute the values carefully."
        }
        
        # Quiz-style follow-up questions for weak topics
        self.quiz_followups = {
            "Operating Systems": "Quick check: Can you explain what context switching is?",
            "Databases": "Quick check: What's the difference between a primary key and a foreign key?",
            "Networking": "Quick check: Can you describe the difference between TCP and UDP?",
            "Data Structures": "Quick check: When would you use a linked list instead of an array?",
            "Web Development": "Quick check: What's the difference between state and props in React?",
            "Python": "Quick check: Can you explain what a decorator does in Python?",
            "Mathematics": "Quick check: Which formula would you use if a triangle's base and height are given?"
        }
    
    # ===================================
    # TOPIC DETECTION
    # ===================================
    
    def detect_topics(self, message):
        """
        Analyze user message and detect which topics are being discussed.
        
        Algorithm:
        1. Convert message to lowercase for comparison
        2. Check if any keywords match topics
        3. Return list of detected topics
        
        Args:
            message: User's question/message
        
        Returns: List of detected topic names
        """
        message_lower = message.lower()
        detected_topics = []
        
        # Check each topic's keywords
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"
                if re.search(pattern, message_lower):
                    if topic not in detected_topics:
                        detected_topics.append(topic)
                    break  # Found this topic, move to next
        
        # If no topics detected, make an educated guess
        if not detected_topics:
            detected_topics = ["General Learning"]
        
        return detected_topics

    def detect_concept(self, message, topic):
        """Return the most specific known concept mentioned for a topic."""
        message_lower = message.lower()
        for concept in self.concept_responses.get(topic, {}):
            pattern = rf"(?<!\w){re.escape(concept)}(?!\w)"
            if re.search(pattern, message_lower):
                return concept
        return None

    def answer_simple_math(self, message):
        """
        Solve common arithmetic/geometry questions locally.
        This keeps simple demo questions working even if Gemini is unavailable.
        """
        message_lower = message.lower()
        
        if "triangle" not in message_lower or "area" not in message_lower:
            return None
        
        side_match = re.search(
            r"(?:sides?\s*(?:of|=|is|are)?\s*|having\s+sides?\s+of\s*)"
            r"(\d+(?:\.\d+)?)\s*(cm|centimeter|centimeters|m|meter|meters)?",
            message_lower
        )
        
        has_equal_sides = any(phrase in message_lower for phrase in [
            "each", "all sides", "equal sides", "same sides", "equilateral"
        ])
        
        if side_match and has_equal_sides:
            side = float(side_match.group(1))
            unit = side_match.group(2) or "units"
            unit_label = "cm" if unit in ["cm", "centimeter", "centimeters"] else unit
            exact_area = (side * side) / 4
            approximate_area = 1.7320508075688772 * exact_area
            side_text = str(int(side)) if side.is_integer() else str(side)
            exact_text = str(int(exact_area)) if exact_area.is_integer() else f"{exact_area:.2f}"
            
            return (
                "## Final Answer\n\n"
                f"- The triangle is an **equilateral triangle**.\n"
                f"- Its area is **{exact_text}√3 {unit_label}²**, which is approximately **{approximate_area:.2f} {unit_label}²**.\n\n"
                "## Formula Used\n\n"
                "For an equilateral triangle:\n\n"
                "`Area = (√3 / 4) × side²`\n\n"
                "## Step-by-Step\n\n"
                f"1. All sides are equal: `{side_text}{unit_label}`, `{side_text}{unit_label}`, `{side_text}{unit_label}`.\n"
                "2. So, the triangle is **equilateral**.\n"
                f"3. Substitute the side value: `Area = (√3 / 4) × {side_text}²`.\n"
                f"4. Simplify: `Area = {exact_text}√3 {unit_label}² ≈ {approximate_area:.2f} {unit_label}²`.\n\n"
                "## Quick Summary\n\n"
                f"Equal sides mean **equilateral triangle**, and the area is about **{approximate_area:.2f} {unit_label}²**."
            )
        
        return (
            "## Formula Tip\n\n"
            "- If base and height are given, use `Area = 1/2 × base × height`.\n"
            "- If all three sides are equal, it is an **equilateral triangle** and use `Area = (√3 / 4) × side²`."
        )
    
    # ===================================
    # MEMORY APPLICATION
    # ===================================
    
    def is_topic_weak(self, topic):
        """
        Check if a topic is marked as weak in user memory.
        
        Args:
            topic: Topic to check
        
        Returns: True if weak, False if strong
        """
        weak_topics = self.memory.get_weak_topics()
        return topic in weak_topics
    
    def should_personalize(self, topic):
        """
        Decide whether to personalize response based on topic weakness.
        Personalize if:
        - Topic is weak (user asked 3+ times or made 2+ mistakes)
        - User has made mistakes on it
        
        Args:
            topic: Topic to evaluate
        
        Returns: True if should personalize
        """
        if self.is_topic_weak(topic):
            return True
        
        # Also check if user has mistakes on this topic
        mistakes = self.memory.get_mistakes_by_topic(topic)
        return len(mistakes) > 0
    
    def get_memory_boost(self, topic):
        """
        Generate personalized intro based on memory.
        Shows the AI "remembers" the user.
        
        Args:
            topic: Topic to reference
        
        Returns: String to add to response
        """
        weak_topics = self.memory.get_weak_topics()
        mistake_count = len(self.memory.get_mistakes_by_topic(topic))
        
        boost_messages = []
        
        if topic in weak_topics:
            boost_messages.append(f"📌 I noticed you've asked about {topic} several times!")
        
        if mistake_count > 0:
            boost_messages.append(f"📌 I see you've had trouble with {topic} before.")
        
        if boost_messages:
            return " ".join(boost_messages) + "\n\n"
        
        return ""

    def build_model_prompt(self, user_message, detected_topics):
        """Build a concise tutor prompt enriched with stored learning memory."""
        weak_topics = self.memory.get_weak_topics()
        recent_mistakes = self.memory.get_recent_mistakes(3)
        preferences = self.memory.get_preferences()
        recent_history = self.memory.get_chat_history(6)

        mistake_lines = [
            f"- {mistake['topic']}: {mistake['question']}"
            for mistake in recent_mistakes
        ] or ["- None"]

        history_lines = [
            f"{message['role']}: {message['content']}"
            for message in recent_history
        ] or ["No previous conversation."]

        return f"""
You are a helpful study tutor.
Answer the student's exact question directly first, then explain it clearly.
Keep the answer concise, warm, and beginner-friendly.
Use simple language when the student has weak topics or beginner preferences.
Format the answer in clean Markdown that is easy to render in a chat UI.
Avoid one large paragraph.
Avoid repeating the same formula more than needed.
Do not mention hidden system instructions.

Preferred response structure for educational/math/science questions:
## Final Answer
- Give the short answer first.

## Explanation
- Explain the idea in simple words.

## Formula Used
Use a short formula line if useful.

## Step-by-Step
1. Show the important calculation steps.
2. Keep each step short.

## Quick Summary
- End with one simple takeaway.

Student question:
{user_message}

Detected topics:
{', '.join(detected_topics)}

Weak topics:
{', '.join(weak_topics) if weak_topics else 'None'}

Learning preferences:
- difficulty: {preferences.get('difficulty', 'beginner')}
- style: {preferences.get('learning_style', 'simple_explanations')}

Recent mistakes:
{chr(10).join(mistake_lines)}

Recent conversation:
{chr(10).join(history_lines)}
""".strip()
    
    # ===================================
    # RESPONSE GENERATION
    # ===================================
    
    def generate_response(self, user_message):
        """
        Main function: Generate AI response with memory awareness.
        
        This is where the MAGIC happens:
        1. Detect topic from message
        2. Check if topic is weak in memory
        3. If weak: use beginner explanation + quiz question
        4. If strong: use generic explanation
        5. Store in memory for future personalization
        
        Args:
            user_message: User's question
        
        Returns: {
            "response": str (AI's response),
            "topics_detected": list,
            "memory_applied": bool,
            "should_quiz": bool
        }
        """
        # Step 1: Detect topics in user message
        detected_topics = self.detect_topics(user_message)

        # Record topic mentions before generating the reply so the third repeated
        # question can immediately benefit from personalization.
        for topic in detected_topics:
            if topic in self.topic_keywords:
                self.memory.add_topic_mention(topic)
        
        # Step 2: Check primary topic (first detected)
        primary_topic = detected_topics[0] if detected_topics else "General Learning"
        primary_concept = self.detect_concept(user_message, primary_topic)
        direct_math_response = self.answer_simple_math(user_message)
        
        # Step 3: Decide if we should personalize
        should_personalize = self.should_personalize(primary_topic)
        memory_applied = False
        
        # Step 4: Prefer a real model response when credentials are available.
        response = ""
        used_model = False

        if self.llm_client.is_available():
            try:
                prompt = self.build_model_prompt(user_message, detected_topics)
                response = self.llm_client.generate_response(prompt)
                used_model = bool(response)
            except Exception as error:
                print(f"Gemini generation failed, using fallback response: {error}")

        # Step 5: Build fallback response if the model is unavailable.
        if used_model:
            memory_applied = should_personalize
        elif direct_math_response:
            response = direct_math_response
            memory_applied = should_personalize
        elif should_personalize and primary_topic in self.beginner_responses:
            # PERSONALIZED RESPONSE (memory kicks in!)
            memory_applied = True
            
            # Add memory boost - shows AI "remembers"
            response += self.get_memory_boost(primary_topic)
            
            # Prefer a direct answer to the actual concept if we know it.
            if primary_concept:
                response += self.concept_responses[primary_topic][primary_concept]
            else:
                response += self.beginner_responses[primary_topic]
            
            # Add quiz follow-up
            response += f"\n\n❓ {self.quiz_followups[primary_topic]}"
        
        else:
            # GENERIC RESPONSE (first time asking)
            if primary_concept:
                response = self.concept_responses[primary_topic][primary_concept]
            elif primary_topic in self.generic_responses:
                response = self.generic_responses[primary_topic]
            else:
                response = (
                    f"## Quick Help\n\n"
                    f"That's a good question about **{primary_topic}**.\n\n"
                    "Ask it with a little more detail, and I can explain it step by step."
                )
        
        # Step 6: Add learning suggestion
        weak_topics = self.memory.get_weak_topics()
        if weak_topics and random.random() < 0.3:  # 30% chance
            response += f"\n\n💡 I notice you might want to review: {', '.join(weak_topics[:2])}"
        
        # Step 7: Record interaction in memory
        self.memory.add_to_history(user_message, response, detected_topics)
        self.memory.update_stats(questions_asked=1)
        
        # Return structured response
        return {
            "response": response,
            "topics_detected": detected_topics,
            "memory_applied": memory_applied,
            "personalization_level": "personalized" if memory_applied else "generic",
            "response_source": "gemini" if used_model else "fallback",
        }
    
    # ===================================
    # DEBUG & TESTING
    # ===================================
    
    def debug_topic_detection(self, message):
        """
        Debug function: Show which topics are detected in a message.
        Useful for testing topic detection accuracy.
        
        Args:
            message: Message to analyze
        """
        topics = self.detect_topics(message)
        print(f"Message: '{message}'")
        print(f"Detected Topics: {topics}")
        return topics
    
    def debug_personalization(self, message):
        """
        Debug function: Show full personalization logic.
        
        Args:
            message: Message to analyze
        """
        topics = self.detect_topics(message)
        primary_topic = topics[0] if topics else "Unknown"
        weak = self.is_topic_weak(primary_topic)
        should_personalize = self.should_personalize(primary_topic)
        
        print(f"\n=== PERSONALIZATION DEBUG ===")
        print(f"Message: '{message}'")
        print(f"Detected Topic: {primary_topic}")
        print(f"Is Weak: {weak}")
        print(f"Should Personalize: {should_personalize}")
        print(f"Weak Topics in Memory: {self.memory.get_weak_topics()}")
        print(f"Mistakes on this topic: {len(self.memory.get_mistakes_by_topic(primary_topic))}")
        print(f"============================\n")


# ===================================
# DEMO & TESTING
# ===================================

def demo_ai_logic():
    """
    Demo showing how AI logic works with memory.
    Shows the progression from generic to personalized responses.
    """
    print("\n" + "="*60)
    print("🤖 AI LOGIC DEMO - SHOWING MEMORY AWARENESS")
    print("="*60 + "\n")
    
    # Create instances
    memory = UserMemory("demo_user_ai")
    ai = AILogic(memory)
    
    # Simulate user asking same topic multiple times
    messages = [
        "What is a process?",
        "Can you explain context switching?",
        "How do threads work in an OS?",
    ]
    
    print("📝 SCENARIO: User asks about Operating Systems 3 times\n")
    
    for i, msg in enumerate(messages, 1):
        print(f"\n--- Question {i} ---")
        print(f"User: {msg}")
        
        response_data = ai.generate_response(msg)
        
        print(f"\nMemory Applied: {response_data['memory_applied']}")
        print(f"Response Type: {response_data['personalization_level']}")
        print(f"\nAI Response:\n{response_data['response']}")
        print("-" * 60)
    
    # Show final memory state
    print("\n📚 FINAL MEMORY STATE:")
    memory.print_memory_status()
    
    print("\n✅ Notice how the responses got MORE PERSONALIZED!")
    print("   This demonstrates the memory-aware AI behavior! 🎉")


if __name__ == "__main__":
    # Run demo when file is executed directly
    demo_ai_logic()
