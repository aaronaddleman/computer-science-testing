import random
import json
import os

class MCPService:
    def __init__(self):
        self.question_bank = {}
        self.current_questions = {}
        self._load_questions()

    def _load_questions(self):
        """Load questions from JSON files in the questions directory."""
        questions_dir = os.path.join(os.path.dirname(__file__), 'questions')
        for filename in os.listdir(questions_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(questions_dir, filename)
                with open(file_path, 'r') as f:
                    topic_data = json.load(f)
                    topic = topic_data['topic']
                    self.question_bank[topic] = topic_data['questions']

    def generate_question(self, topic):
        if topic not in self.question_bank:
            return None
        
        # Randomly select a question from the bank
        question = random.choice(self.question_bank[topic])
        
        # Store the current question (in a real implementation, this would be session-specific)
        self.current_questions[topic] = question
        
        # Return question without the correct answer and explanation
        return {
            "id": question["id"],
            "question": question["question"],
            "options": question["options"]
        }

    def validate_answer(self, topic, question_id, answer):
        if topic not in self.question_bank:
            return {"correct": False, "message": "Invalid question"}

        # Find the question with the matching ID
        matching_questions = [q for q in self.question_bank[topic] if q["id"] == question_id]
        if not matching_questions:
            return {"correct": False, "message": "Invalid question"}

        question = matching_questions[0]
        is_correct = answer == question["correct_answer"]
        
        return {
            "correct": is_correct,
            "explanation": question["explanation"]
        } 