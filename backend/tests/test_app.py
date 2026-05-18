import os
import sys
import tempfile
import unittest

BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BACKEND_DIR)

import app
from ai_logic import AILogic
from memory import UserMemory
from quiz import QuizGenerator


class FakeGeminiClient:
    def is_available(self):
        return True

    def generate_response(self, prompt):
        return "A process is a running program explained by Gemini."


class FakeUnavailableClient:
    def is_available(self):
        return False

    def generate_response(self, prompt):
        return None


class AppFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        memory_path = os.path.join(self.temp_dir.name, "memory.json")
        memory = UserMemory(memory_file=memory_path)
        app.user_memory = memory
        app.ai_logic = AILogic(memory, llm_client=FakeUnavailableClient())
        app.quiz_generator = QuizGenerator(memory)
        self.client = app.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_chat_personalizes_on_third_repeated_topic(self):
        for _ in range(2):
            response = self.client.post("/api/chat", json={"message": "What is a process?"})
            self.assertFalse(response.json["data"]["memory_applied"])

        response = self.client.post("/api/chat", json={"message": "How do threads work?"})
        self.assertTrue(response.json["data"]["memory_applied"])

    def test_quiz_submission_updates_score(self):
        quiz_response = self.client.get("/api/quiz?num_questions=1")
        question = quiz_response.json["data"]["questions"][0]

        response = self.client.post(
            "/api/quiz",
            json={
                "answers": [
                    {
                        "question_id": question["id"],
                        "question_text": question["text"],
                        "topic": question["topic"],
                        "user_answer": question["correct"],
                        "correct_answer": question["correct"],
                    }
                ]
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["score"], 1)
        self.assertEqual(response.json["data"]["total"], 1)

    def test_chat_answers_specific_concept(self):
        response = self.client.post("/api/chat", json={"message": "What is a process?"})
        self.assertIn("program that is currently running", response.json["data"]["response"])

    def test_chat_uses_model_when_available(self):
        app.ai_logic = AILogic(app.user_memory, llm_client=FakeGeminiClient())
        response = self.client.post("/api/chat", json={"message": "What is a process?"})
        self.assertEqual(response.json["data"]["response_source"], "gemini")
        self.assertIn("Gemini", response.json["data"]["response"])

    def test_topic_detection_uses_whole_words(self):
        topics = app.ai_logic.detect_topics("Explain photosynthesis simply")
        self.assertEqual(topics, ["General Learning"])


if __name__ == "__main__":
    unittest.main()
