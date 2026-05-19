# AI Study Memory Assistant

AI Study Memory Assistant is an adaptive learning companion that remembers weak topics, tracks quiz mistakes, and uses that learning history to make future study help more personalized.

The project combines a React frontend, a Flask backend, a lightweight memory engine, adaptive quizzes, and optional Gemini-powered responses.

---

## Features

- Memory-aware study chat
- Optional Gemini API integration for natural answers
- Fallback response engine when no API key is configured
- Weak-topic detection from repeated questions and quiz mistakes
- Personalized quiz generation
- Recent mistake tracking
- Real-time memory dashboard
- Demo reset flow for clean presentations
- Fixed chat layout with internal message scrolling

---

## How It Works

```text
Chat -> Memory -> Quiz -> Mistake Tracking -> Personalized Learning
```

1. The student asks study questions.
2. The backend detects topics and stores learning activity.
3. Repeated topics or quiz mistakes become weak areas.
4. Quizzes prioritize those weak areas.
5. Future answers use memory context to adapt explanations.
6. If Gemini is configured, answers can cover topics beyond the built-in fallback set.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | Flask |
| AI | Gemini API optional, fallback engine built in |
| Memory | JSON-based local memory |
| Styling | CSS |
| Testing | Python unittest |

---

## Project Structure

```text
.
├── backend/
│   ├── app.py
│   ├── ai_logic.py
│   ├── llm_client.py
│   ├── memory.py
│   ├── quiz.py
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── styles/
│   │   ├── api.js
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── .env.example
├── QUICKSTART.md
└── README.md
```

---

## Setup

Clone the repository, then install backend and frontend dependencies.

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs on:

```text
http://127.0.0.1:5000
```

### Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Frontend runs on:

```text
http://127.0.0.1:5173
```

---

## Gemini Setup

Gemini is optional. The app still works without it using the fallback response engine.

To enable Gemini:

1. Copy `.env.example` to `.env`.
2. Add your Gemini API key.

Example:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Do not commit `.env` or real API keys.

---

## Demo Flow

Use this flow for a hackathon demo:

1. Click **Reset Demo**.
2. Ask repeated questions about one topic:

```text
What is a process?
Explain context switching.
How do threads work?
```

3. Open the Memory tab and show the weak topic.
4. Take a quiz.
5. Submit at least one wrong answer.
6. Return to Memory and show the mistake history.
7. Ask a new topic outside the fallback set, such as:

```text
Explain photosynthesis simply.
```

If Gemini is configured, the app should answer naturally.

---

## Testing

Run backend tests:

```bash
python -m unittest backend.tests.test_app
```

Build the frontend:

```bash
cd frontend
npm run build
```

---

## Current Limitations

- Memory is stored locally in JSON.
- There is no user authentication yet.
- Quiz questions are from a local question bank.
- Topic detection is lightweight and keyword-based.
- Gemini requires a valid API key.

---

## Future Improvements

- User accounts and cloud memory storage
- SQLite or database-backed persistence
- Better semantic topic detection
- Larger quiz question bank
- Spaced repetition scheduling
- Analytics dashboard
- Voice input
- Mobile app polish

---

## Goal

The goal of this project is to show a complete adaptive learning loop where the assistant does not only answer questions, but also remembers learning patterns and helps students improve over time.
