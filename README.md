# 🧠 AI Study Memory Assistant

A hackathon-ready AI-powered study companion that **remembers what you struggle with** and **personalizes responses** to help you learn better.

## 🎯 Core Features

### 1. **Memory-Aware Chat** 💬
- Ask questions about any study topic
- AI detects topics and remembers weak areas
- Responses become personalized after 3+ questions on same topic
- Clear indication when memory is being applied ("🧠 Memory Applied")

### 2. **Learning Memory Dashboard** 🧠
- Real-time display of weak topics
- Statistics (questions asked, quizzes taken, topics covered)
- Recent mistakes for learning reinforcement
- Progress tracking with visual bar
- Live sync every 3 seconds

### 3. **Personalized Quizzes** 📝
- Auto-generated questions based on weak topics (70% weak, 30% review)
- Choose quiz difficulty (3, 5, or 10 questions)
- Real-time question navigation with progress tracking
- Detailed results with mistake review
- Automatic memory updates from quiz performance

## 🚀 Quick Start

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- pip (Python package manager)

### Backend Setup (Flask)

```bash
# Navigate to backend folder
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run Flask server
python app.py
```

**Expected Output:**
```
🚀 Starting AI Study Memory Assistant Backend...
📡 Server running at http://localhost:5000
✅ CORS enabled for frontend communication
```

### Frontend Setup (React + Vite)

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### Access the App

Open your browser and go to: **http://localhost:5173/**

### Optional Gemini Setup

To enable real model responses, create a `.env` file from `.env.example` and set:

```bash
GEMINI_API_KEY=your_api_key_here
```

Without a key, the app automatically keeps using the built-in fallback response engine.

---

## 📊 Project Structure

```
hackathon-devanovate/
│
├── backend/
│   ├── app.py              # Flask server & API endpoints
│   ├── memory.py           # Memory management system
│   ├── ai_logic.py         # AI personalization engine
│   ├── quiz.py             # Quiz generation & tracking
│   └── memory.json         # Persistent memory storage (auto-created)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main app with tab navigation
│   │   ├── App.css         # Global styling
│   │   ├── main.jsx        # React entry point
│   │   ├── index.css       # Base styles
│   │   │
│   │   ├── components/
│   │   │   ├── Chat.jsx    # Chat interface
│   │   │   ├── Memory.jsx  # Memory dashboard
│   │   │   └── Quiz.jsx    # Quiz system
│   │   │
│   │   └── styles/
│   │       ├── Chat.css
│   │       ├── Memory.css
│   │       └── Quiz.css
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
└── README.md (this file)
```

---

## 🎮 Demo Walkthrough

### Demo Scenario: User Learns About Operating Systems

**Minute 1-3: Building Memory**
```
Chat Tab:
User: "What is a process?"
AI: [Generic explanation - no memory]

User: "Can you explain context switching?"
AI: [Still generic - OS mentions: 2]

User: "How do threads work?"
AI: "🧠 I noticed you've asked about OS several times!
    Let me explain more simply..."
    [Beginner-friendly explanation]
    [🧠 Memory Applied badge GLOWS]
```

**Switch to Memory Tab:**
```
📊 Progress Stats:
- Questions Asked: 3
- Quizzes Taken: 0
- Topics Covered: 1

⚠️ Weak Topics:
[Operating Systems]  ← Marked after 3 mentions

📚 Recent Mistakes:
[None yet - user hasn't taken quiz]
```

**Switch to Quiz Tab:**
```
📝 Start Quiz: "Standard (5 Questions)"
↓
Quiz focuses on OS (70% weak topic priority)
Questions appear with real-time progress bar

User gets 3/5 correct
Mistakes on context switching & memory management

Results Page:
Score: 60%
❌ 3 mistakes recorded
Memory automatically updated!
```

**Switch back to Memory Tab:**
```
📊 Updated Stats:
- Questions Asked: 8
- Quizzes Taken: 1
- Recent Mistakes: 3 ← Now visible!

❌ Mistakes Review:
Shows exactly what user got wrong
```

**Back to Chat Tab:**
```
User: "Explain memory management in OS"
AI: "You struggled with memory management in the quiz.
    Let me explain this in simpler terms..."
    [Even MORE personalized]
    [🧠 Memory Applied - DOUBLE GLOW]
```

**Judge sees:** Complete learning loop with visible memory behavior! 🎉

---

## 🔧 Technology Stack

### Backend
- **Flask** - Web framework
- **Flask-CORS** - Cross-Origin requests
- **Python** - Core logic
- **JSON** - Memory storage

### Frontend
- **React** - UI library
- **Vite** - Build tool & dev server
- **CSS3** - Styling with animations
- **Fetch API** - Backend communication

### AI/Memory
- **Hindsight** - Memory concept (hackathon theme)
- **Cascadeflow** - Runtime intelligence (hackathon theme)
- Compatible architecture for future integration

---

## 📡 API Endpoints

### Chat
```
POST /api/chat
Input: {"message": "What is a process?"}
Output: {
  "response": "AI response with memory awareness",
  "topics_detected": ["Operating Systems"],
  "memory_applied": true/false
}
```

### Memory
```
GET /api/memory
Output: {
  "weak_topics": ["Operating Systems"],
  "total_questions": 8,
  "total_quizzes_taken": 1,
  "recent_mistakes": [...],
  "user_preferences": {...}
}
```

### Quiz
```
GET /api/quiz?num_questions=5
Output: {
  "questions": [
    {
      "id": 1,
      "text": "What is a process?",
      "options": ["A", "B", "C", "D"],
      "correct": 1,
      "topic": "Operating Systems"
    }
  ]
}

POST /api/quiz
Input: {"answers": [...]}
Output: {
  "score": 3,
  "total": 5,
  "percentage": 60,
  "mistakes": [...]
}
```

---

## 🧠 How Memory Works

### Detection (Automatic)
```
User asks multiple questions about topic X
→ System counts mentions
→ After 3+ mentions OR 2+ mistakes → Topic marked WEAK
```

### Personalization (Automatic)
```
Topic is WEAK
→ AI detects topic in new question
→ AI generates BEGINNER-FRIENDLY explanation
→ UI shows 🧠 Memory Applied badge
→ Next question gets EASIER response
```

### Updates (Automatic)
```
User takes quiz → Gets wrong answer
→ Mistake recorded in memory
→ Topic weakness score increases
→ Next quiz focuses even more on this topic
```

---

## 🎨 UI Design Philosophy

### Dark Theme with Glassmorphism
- Modern, professional look
- Easy on the eyes during long study sessions
- Gradient backgrounds (cyan/blue theme)
- Frosted glass effects on cards

### Responsive Design
- Desktop: Full 3-column tab layout
- Tablet: Optimized layout with touch-friendly buttons
- Mobile: Single-column, large tap targets

### Clear Visual Feedback
- Green badges for memory applied
- Red badges for weak topics
- Progress bars for learning journey
- Glowing animations for important states
- Color-coded quiz navigation

---

## 🚨 Troubleshooting

### Backend won't start
```
Error: ModuleNotFoundError: No module named 'flask'
Solution: pip install flask flask-cors
```

### Frontend can't connect to backend
```
Error: Cannot reach backend at http://localhost:5000
Solution: Make sure Flask is running (check terminal for http://localhost:5000)
```

### Components not showing
```
Make sure all files are in correct folders:
- frontend/src/components/Chat.jsx
- frontend/src/components/Memory.jsx
- frontend/src/components/Quiz.jsx
- frontend/src/styles/*.css
```

### Port already in use
```
Flask (default 5000): python app.py --port 5001
Vite (default 5173): npm run dev -- --port 3000
```

---

## 🎓 For Hackathon Judges

### What Makes This Special

✅ **Clear Memory Behavior** - Users see AI learn in real-time  
✅ **Before/After Personalization** - First vs later responses are noticeably different  
✅ **Beautiful UI** - Professional, hackathon-ready design  
✅ **Complete Demo Loop** - Chat → Memory → Quiz → Personalization  
✅ **Scalable Architecture** - Easy to add features  
✅ **Clean Code** - Well-commented, beginner-friendly  

### Demo Talking Points

1. **"First, I'll ask a question without memory..."** → Generic response
2. **"Now I'll ask the same topic twice more..."** → System detects weak area
3. **"Let's check the Memory dashboard..."** → Show weak topic populated
4. **"Now when I ask again..."** → 🧠 Memory Applied! Personalized response!
5. **"Take a quick quiz..."** → Focused on weak topic
6. **"Look at Memory tab..."** → Mistakes recorded, stats updated
7. **"The AI keeps learning..."** → Future interactions will be even more personalized!

---

## ✅ Demo Readiness Checklist

- Use **Reset Demo** in the header before each judge walkthrough
- Ask the same topic three times to trigger visible personalization
- Open the Memory tab to show the weak-topic update
- Take a quiz, submit at least one wrong answer, then revisit Memory
- Ask the weak topic again to show the closed learning loop

## 🧪 Testing

Run backend flow tests from the project root:

```bash
python -m unittest backend.tests.test_app
```

Build the frontend before demo day:

```bash
cd frontend
npm run build
```

## 🔮 Future Enhancements

- Richer prompt evaluation and response quality checks
- User authentication & cloud storage
- Spaced repetition algorithm
- AI conversation history analysis
- Advanced analytics dashboard
- Mobile app
- Collaborative study groups

---

## 📝 Notes for Developers

### Adding New Topics
Edit `backend/ai_logic.py` → `topic_keywords` dictionary

### Adding Quiz Questions
Edit `backend/quiz.py` → `question_database` dictionary

### Changing Colors/Theme
Edit component CSS files → `colors`, `gradients`

### Backend Port
Change `BACKEND_URL` in `frontend/src/components/*.jsx`

---

## 🏆 Credits

Built for AI Agent Hackathon 2026

- **Frontend**: React + Vite
- **Backend**: Flask
- **Memory System**: Custom JSON-based with real-time sync
- **Design**: Modern dark theme with glassmorphism
- **Architecture**: Modular, scalable, judge-friendly

---

## 📞 Support

For issues or questions:
1. Check terminal for error messages
2. Verify both servers are running
3. Check browser console (F12) for frontend errors
4. Ensure Python/Node dependencies are installed

---

## ✨ Enjoy Building!

This project demonstrates AI memory and personalization in action. Perfect for showcasing advanced concepts while keeping code clean and understandable.

Good luck at the hackathon! 🚀
