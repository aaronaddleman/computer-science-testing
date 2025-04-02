import unittest
import json
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.app.testing = True
        
        # Known test data from our question bank
        self.test_questions = {
            "bst-1": {
                "question": "What is the time complexity of searching in a balanced binary search tree?",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                "correct_answer": 1
            },
            "bst-2": {
                "question": "Which traversal of a binary search tree visits nodes in ascending order?",
                "options": ["Preorder", "Inorder", "Postorder", "Level-order"],
                "correct_answer": 1
            },
            "bst-3": {
                "question": "What is the space complexity of a binary search tree with n nodes?",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                "correct_answer": 2
            }
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
        for question_id, question_data in self.test_questions.items():
            if question_data['question'].encode() in response.data:
                # Found a valid question, verify its options are present
                for option in question_data['options']:
                    self.assertIn(option.encode(), response.data)
                break
        else:
            self.fail("No valid question found in response")

    def test_answer_validation(self):
        """Test answer validation for each known question"""
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
            self.assertIn('explanation', data)

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