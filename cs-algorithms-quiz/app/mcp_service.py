import random
import json
import os

class MCPService:
    def __init__(self):
        self.questions_dir = os.path.join(os.path.dirname(__file__), 'questions')
        self.topics = {}
        self.load_topics()

    def load_topics(self):
        """Load all topic files from the questions directory."""
        for filename in os.listdir(self.questions_dir):
            if filename.endswith('.json'):
                # Support both hyphen and underscore formats
                topic_id = filename.replace('.json', '').replace('_', '-')
                with open(os.path.join(self.questions_dir, filename)) as f:
                    self.topics[topic_id] = json.load(f)

    def get_topic_info(self, topic_id):
        """Get topic information without questions."""
        if topic_id not in self.topics:
            return None
        topic_data = self.topics[topic_id].copy()
        topic_data.pop('questions', None)  # Remove questions from the response
        return topic_data

    def get_question_info(self, topic_id, question_id):
        """Get information about a specific question."""
        if topic_id not in self.topics:
            return None
        
        for question in self.topics[topic_id].get('questions', []):
            if question['id'] == question_id:
                return question
        return None

    def generate_question(self, topic_id):
        """Generate a random question for the given topic."""
        if topic_id not in self.topics:
            return None
        
        questions = self.topics[topic_id].get('questions', [])
        if not questions:
            return None
        
        question = random.choice(questions)
        # Include difficulty in the question data
        return {
            'id': question['id'],
            'text': question['text'],
            'options': question['options'],
            'difficulty': question.get('difficulty', 'medium')  # Default to medium if not specified
        }

    def validate_answer(self, topic_id, question_id, answer):
        """Validate the answer for a given question."""
        if topic_id not in self.topics:
            return {'correct': False, 'message': 'Invalid topic'}
        
        question = None
        for q in self.topics[topic_id].get('questions', []):
            if q['id'] == question_id:
                question = q
                break
        
        if not question:
            return {'correct': False, 'message': 'Invalid question'}
        
        correct = str(answer) == str(question['correct_answer'])
        return {
            'correct': correct,
            'message': question['explanation'] if correct else 'Incorrect answer. Try again!',
            'difficulty': question.get('difficulty', 'medium')  # Include difficulty in response
        } 