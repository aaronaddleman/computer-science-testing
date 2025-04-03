import unittest
import json
import os
import random
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.app.testing = True
        
        # Load questions from JSON file
        questions_file = os.path.join(os.path.dirname(__file__), 'questions', 'binary_search_tree.json')
        with open(questions_file, 'r') as f:
            data = json.load(f)
            self.all_questions = {q['id']: q for q in data['questions']}
            
        # Select 10 random questions for testing
        question_ids = list(self.all_questions.keys())
        self.test_questions = {
            qid: self.all_questions[qid] 
            for qid in random.sample(question_ids, min(10, len(question_ids)))
        }

    def test_home_page(self):
        """Test if home page loads and contains expected content"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Computer Science Algorithms', response.data)
        self.assertIn(b'Binary Search Tree', response.data)

    def test_info_page(self):
        """Test if BST info page loads"""
        response = self.app.get('/algo/binary-search-tree/info')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Binary Search Tree', response.data)
        self.assertIn(b'Start Test', response.data)

    def test_test_page(self):
        """Test if BST test page loads with a valid question"""
        response = self.app.get('/algo/binary-search-tree/test')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Binary Search Tree Test', response.data)
        
        # Verify that we got a valid question from our question bank
        response_text = response.data.decode()
        found_valid_question = False
        for question_id, question_data in self.all_questions.items():
            if question_data['question'] in response_text:
                # Found a valid question, verify its options are present
                for option in question_data['options']:
                    self.assertIn(option, response_text)
                found_valid_question = True
                break
        
        self.assertTrue(found_valid_question, "No valid question found in response")

    def test_random_questions(self):
        """Test 10 random questions with both correct and incorrect answers"""
        for question_id, question_data in self.test_questions.items():
            # Test correct answer
            response = self.app.post('/api/validate-answer',
                json={
                    'topic': 'binary-search-tree',
                    'question_id': question_id,
                    'answer': question_data['correct_answer']
                })
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(isinstance(data, dict))
            self.assertIn('correct', data)
            self.assertTrue(data['correct'], f"Question {question_id} failed with correct answer")
            self.assertIn('explanation', data)
            self.assertEqual(data['explanation'], question_data['explanation'])

            # Test incorrect answer
            wrong_answer = (question_data['correct_answer'] + 1) % len(question_data['options'])
            response = self.app.post('/api/validate-answer',
                json={
                    'topic': 'binary-search-tree',
                    'question_id': question_id,
                    'answer': wrong_answer
                })
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(isinstance(data, dict))
            self.assertIn('correct', data)
            self.assertFalse(data['correct'], f"Question {question_id} incorrectly marked wrong answer as correct")
            self.assertIn('explanation', data)

    def test_invalid_question(self):
        """Test validation with invalid question ID"""
        response = self.app.post('/api/validate-answer',
            json={
                'topic': 'binary-search-tree',
                'question_id': 'invalid-id',
                'answer': 0
            })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('correct', data)
        self.assertEqual(data['correct'], False)
        self.assertIn('message', data)

if __name__ == '__main__':
    unittest.main() 