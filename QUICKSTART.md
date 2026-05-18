# 🚀 Quick Start Guide - AI Study Memory Assistant

## Step 1: Install Dependencies

### Backend (Python)
```bash
cd backend
pip install -r requirements.txt
```

Optional: add `GEMINI_API_KEY` to a root `.env` file if you want live Gemini answers.

### Frontend (Node.js)
```bash
cd frontend
npm install
```

---

## Step 2: Start Backend Server

```bash
cd backend
python app.py
```

**✅ You should see:**
```
🚀 Starting AI Study Memory Assistant Backend...
📡 Server running at http://localhost:5000
✅ CORS enabled for frontend communication
 * Running on http://127.0.0.1:5000
```

**⚠️ Keep this terminal open!**

---

## Step 3: Start Frontend (New Terminal)

```bash
cd frontend
npm run dev
```

**✅ You should see:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

---

## Step 4: Open in Browser

Go to: **http://localhost:5173/**

You should see:
- 🧠 AI Study Memory Assistant header
- 💬 📊 📝 three tabs (Chat, Memory, Quiz)
- Chat interface is active by default

---

## 🎮 First-Time Demo (2 minutes)

Before each demo, click **Reset Demo** in the header so the walkthrough starts from a clean memory state.

### Tab 1: Chat 💬

**Ask about Operating Systems 3 times:**

1. Type: `What is a process?`
   - Hit Enter → AI gives generic response
   - **Notice: No memory applied yet**

2. Type: `Can you explain context switching?`
   - Hit Enter → Still generic
   - **Notice: No badge showing memory**

3. Type: `How do threads work?`
   - Hit Enter → **NOW IT'S PERSONALIZED!**
   - **Notice: 🧠 Memory Applied badge appears!**
   - Response starts with: "I noticed you've asked about OS several times..."

### Tab 2: Memory 🧠

Click the 🧠 tab to see:
- **⚠️ Weak Topics section** - "Operating Systems" now appears!
- **📊 Your Progress** - Shows "3" questions asked
- **Real-time sync** - Refreshes every 3 seconds

### Tab 3: Quiz 📝

Click the 📝 tab to see:
1. Click **"📝 Standard (5 Q)"** button
2. Answer the quiz (mostly Operating Systems questions)
3. Get your score
4. See **❌ Mistakes review** 
5. After submitting, go back to **Memory tab**
   - **Mistakes now show** in "Recent Mistakes" section!

### Final: Back to Chat 💬

Ask about OS again:
- **Response is EVEN MORE personalized!**
- AI mentions the quiz mistakes
- Shows you're learning!

---

## ⚡ Quick Troubleshooting

### Backend not starting?
```bash
# Check if port 5000 is in use
# On Windows:
netstat -ano | findstr :5000

# On Mac/Linux:
lsof -i :5000

# Try different port:
python app.py --port 5001
# Then update BACKEND_URL in Chat.jsx, Memory.jsx, Quiz.jsx
```

### Frontend not connecting?
```
Check browser console (F12):
- "Connection refused" = Backend not running
- "CORS error" = Flask not started with CORS

Solution: Start backend first, then frontend
```

### Components not showing?
```
Make sure files exist:
✓ frontend/src/components/Chat.jsx
✓ frontend/src/components/Memory.jsx
✓ frontend/src/components/Quiz.jsx
✓ frontend/src/styles/Chat.css
✓ frontend/src/styles/Memory.css
✓ frontend/src/styles/Quiz.css
```

---

## 📊 Testing the Memory System

### Test 1: Topic Detection
```
Chat:
- Ask "What is an array?"           → Data Structures detected
- Ask "How do arrays work?"         → Still data structures
- Ask "Can you compare arrays?"     → Counts toward weak topic
→ After 3 mentions: ⚠️ Shows in Memory
```

### Test 2: Personalization
```
Chat:
- First question: Generic response (no 🧠 badge)
- Third+ question: Personalized response (🧠 badge appears!)
```

### Test 3: Quiz Integration
```
Quiz:
- Take quiz (system focuses on weak topics)
- Get some wrong
- Go to Memory → See mistakes recorded
- Back to Chat → Responses reference quiz performance
```

---

## 🎯 What to Show Judges

1. **Chat with Memory** 💬
   - Same topic asked 3x → Shows personalization progression
   - 🧠 Badge glows when memory applies

2. **Real-Time Memory Sync** 🔄
   - Chat updates → Memory dashboard updates (3s lag)
   - Shows live learning tracking

3. **Quiz + Memory Loop** 📚
   - Take quiz → Mistakes appear in Memory
   - Chat responses reference quiz mistakes
   - Complete closed loop!

4. **Beautiful UI** 🎨
   - Dark theme with gradients
   - Smooth animations
   - Professional design
   - Responsive (works on mobile too)

---

## 📁 File Structure Quick Reference

```
hackathon-devanovate/
├── README.md                          ← Full documentation
├── QUICKSTART.md                      ← This file
│
├── backend/
│   ├── app.py                         ← Flask server
│   ├── memory.py                      ← Memory system
│   ├── ai_logic.py                    ← AI personalization
│   ├── quiz.py                        ← Quiz generator
│   └── memory.json                    ← Auto-created on first run
│
└── frontend/
    └── src/
        ├── App.jsx                    ← Main app component
        ├── App.css                    ← Global styles
        ├── components/
        │   ├── Chat.jsx
        │   ├── Memory.jsx
        │   └── Quiz.jsx
        └── styles/
            ├── Chat.css
            ├── Memory.css
            └── Quiz.css
```

---

## 💡 Tips for Best Demo

1. **Start Fresh** - Delete `backend/memory.json` before each demo for clean slate

2. **Show Progression** - Build up 3+ questions on one topic to show memory trigger

3. **Use Variety** - Ask about different topics to show system's versatility

4. **Take Quiz** - Shows how mistakes integrate with memory system

5. **Highlight Personalization** - Point out 🧠 badge and beginner explanations

6. **Show Real-Time** - Switch between tabs to demonstrate live sync

---

## 🔧 Advanced: Modify Questions

Edit `backend/quiz.py` → Find `self.question_database`:
```python
"Your Topic": {
    "beginner": [
        {
            "id": 999,
            "text": "Your question?",
            "options": ["A", "B", "C", "D"],
            "correct": 0,
            "explanation": "Why A is correct..."
        }
    ]
}
```

---

## 🎓 Key Files to Understand

### For Judges Evaluating Backend:
- `backend/app.py` - Clean Flask API
- `backend/memory.py` - Smart memory detection (3+ mentions = weak)
- `backend/ai_logic.py` - Personalization logic
- `backend/quiz.py` - Smart quiz generation

### For Judges Evaluating Frontend:
- `frontend/src/App.jsx` - Tab navigation (clean architecture)
- `frontend/src/components/Chat.jsx` - Real-time backend communication
- `frontend/src/components/Memory.jsx` - Live data refresh (3s sync)
- `frontend/src/components/Quiz.jsx` - Complete quiz flow

---

## ❓ FAQ

**Q: How long until memory kicks in?**  
A: After user asks 3 questions about same topic (or 2 mistakes)

**Q: Does memory persist?**  
A: Yes! In `backend/memory.json` file

**Q: Can I change the theme?**  
A: Yes! Edit CSS files in `frontend/src/styles/`

**Q: What topics are pre-loaded?**  
A: Operating Systems, Databases, Networking, Data Structures, Web Dev, Python

**Q: Can I add more topics?**  
A: Yes! Edit `backend/ai_logic.py` and `backend/quiz.py`

---

## ✨ You're All Set!

Now you're ready to:
1. ✅ Run the backend
2. ✅ Run the frontend  
3. ✅ Demo the memory system
4. ✅ Impress the judges!

**Good luck! 🚀**
