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
        
        # Load all topic questions from JSON files
        self.topics = {
            'binary-search-tree': [],
            'sorting-algorithms': [],
            'graph-algorithms': [],
            'dynamic-programming': []
        }
        
        questions_dir = os.path.join(os.path.dirname(__file__), 'questions')
        for filename in os.listdir(questions_dir):
            if filename.endswith('.json'):
                with open(os.path.join(questions_dir, filename), 'r') as f:
                    data = json.load(f)
                    topic = data['topic']
                    if topic in self.topics:
                        self.topics[topic] = data['questions']

    def test_home_page_topics(self):
        """Test if home page contains all topic links"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for topic links
        response_text = response.data.decode()
        expected_topics = [
            '/algo/binary-search-tree/info',
            '/algo/sorting-algorithms/info',
            '/algo/graph-algorithms/info',
            '/algo/dynamic-programming/info'
        ]
        for topic_url in expected_topics:
            self.assertIn(topic_url, response_text)

    def test_info_pages(self):
        """Test if info pages for all topics load correctly"""
        for topic in self.topics.keys():
            response = self.app.get(f'/algo/{topic}/info')
            self.assertEqual(response.status_code, 200, f"Info page for {topic} failed to load")
            response_text = response.data.decode()
            self.assertIn('Start Test', response_text)

    def test_test_pages(self):
        """Test if test pages for all topics load with valid questions"""
        for topic in self.topics.keys():
            response = self.app.get(f'/algo/{topic}/test')
            self.assertEqual(response.status_code, 200, f"Test page for {topic} failed to load")
            
            # Verify that we got a valid question from our question bank
            response_text = response.data.decode()
            found_valid_question = False
            
            for question in self.topics[topic]:
                if question['question'] in response_text:
                    # Found a valid question, verify its options are present
                    for option in question['options']:
                        self.assertIn(option, response_text)
                    found_valid_question = True
                    break
            
            self.assertTrue(found_valid_question, f"No valid question found in response for {topic}")

    def test_answer_validation_all_topics(self):
        """Test answer validation for each topic"""
        for topic, questions in self.topics.items():
            # Test 3 random questions from each topic
            test_questions = random.sample(questions, min(3, len(questions)))
            
            for question in test_questions:
                # Test correct answer
                response = self.app.post('/api/validate-answer',
                    json={
                        'topic': topic,
                        'question_id': question['id'],
                        'answer': question['correct_answer']
                    })
                
                self.assertEqual(response.status_code, 200, 
                    f"Failed to validate correct answer for {topic}, question {question['id']}")
                data = json.loads(response.data)
                self.assertTrue(data['correct'], 
                    f"Question {question['id']} in {topic} failed with correct answer")
                self.assertEqual(data['explanation'], question['explanation'],
                    f"Explanation mismatch for {topic}, question {question['id']}")

                # Test incorrect answer
                wrong_answer = (question['correct_answer'] + 1) % len(question['options'])
                response = self.app.post('/api/validate-answer',
                    json={
                        'topic': topic,
                        'question_id': question['id'],
                        'answer': wrong_answer
                    })
                
                self.assertEqual(response.status_code, 200,
                    f"Failed to validate incorrect answer for {topic}, question {question['id']}")
                data = json.loads(response.data)
                self.assertFalse(data['correct'],
                    f"Question {question['id']} in {topic} incorrectly marked wrong answer as correct")

    def test_invalid_questions(self):
        """Test validation with invalid questions for each topic"""
        for topic in self.topics.keys():
            response = self.app.post('/api/validate-answer',
                json={
                    'topic': topic,
                    'question_id': 'invalid-id',
                    'answer': 0
                })
            
            self.assertEqual(response.status_code, 200,
                f"Invalid question test failed for topic {topic}")
            data = json.loads(response.data)
            self.assertFalse(data['correct'],
                f"Invalid question incorrectly marked as correct for topic {topic}")
            self.assertIn('message', data,
                f"Error message missing for invalid question in topic {topic}")

if __name__ == '__main__':
    unittest.main() 