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
                    topic = data['topic'].lower().replace(' ', '-')
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
        topics = ['binary-search-tree', 'sorting-algorithms', 'graph-algorithms', 'dynamic-programming']
        for topic in topics:
            response = self.app.get(f'/algo/{topic}/info')
            response_text = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Take Quiz', response_text)

    def test_test_pages(self):
        """Test if test pages for all topics load with valid questions"""
        def html_encode(text):
            """Helper function to encode text similar to HTML"""
            return text.replace("'", "&#39;").replace('"', "&quot;")
            
        for topic in self.topics.keys():
            response = self.app.get(f'/algo/{topic}/test')
            self.assertEqual(response.status_code, 200, f"Test page for {topic} failed to load")
            
            # Verify that we got a valid question from our question bank
            response_text = response.data.decode()
            found_valid_question = False
            
            for question in self.topics[topic]:
                # Check for question text and difficulty
                question_text_html = html_encode(question['question'])
                if question_text_html in response_text:
                    # Found a valid question, verify its options and difficulty are present
                    for option in question['options']:
                        # Handle HTML-encoded characters
                        option_html = html_encode(option)
                        self.assertIn(option_html, response_text,
                            f"Option '{option}' not found in HTML for question {question['id']}")
                    
                    difficulty = question.get('difficulty', 'medium')  # Default to medium if not specified
                    self.assertIn(difficulty.upper(), response_text,  # Check for difficulty level in uppercase
                        f"Difficulty '{difficulty}' not found in HTML for question {question['id']}")
                    found_valid_question = True
                    break
            
            self.assertTrue(found_valid_question, 
                f"No valid question found in response for {topic}. Response text: {response_text[:200]}...")

    def test_answer_validation_all_topics(self):
        """Test answer validation for all questions in each topic"""
        required_fields = ['id', 'category', 'question', 'options', 'correct_answer', 'explanation', 'difficulty']
        valid_difficulties = ['easy', 'medium', 'hard']
        
        for topic, questions in self.topics.items():
            # Test every question in the topic
            for question in questions:
                # Validate question structure
                for field in required_fields:
                    self.assertIn(field, question, 
                        f"Question {question.get('id', 'unknown')} in {topic} missing required field: {field}")
                
                # Validate difficulty value
                self.assertIn(question['difficulty'].lower(), valid_difficulties,
                    f"Question {question['id']} in {topic} has invalid difficulty: {question['difficulty']}")
                
                # Validate options
                self.assertGreater(len(question['options']), 1,
                    f"Question {question['id']} in {topic} has too few options")
                self.assertLess(question['correct_answer'], len(question['options']),
                    f"Question {question['id']} in {topic} has invalid correct_answer index")
                
                # Test correct answer
                response = self.app.post('/api/validate-answer',
                    json={
                        'topic': topic,
                        'question_id': question['id'],
                        'answer': question['options'][question['correct_answer']],
                        'response_time': 1.0
                    })
                
                self.assertEqual(response.status_code, 200, 
                    f"Failed to validate correct answer for {topic}, question {question['id']}")
                data = json.loads(response.data)
                self.assertTrue(data['correct'], 
                    f"Question {question['id']} in {topic} failed with correct answer")
                self.assertIn('message', data,
                    f"Message missing for {topic}, question {question['id']}")
                self.assertEqual(data['message'], question['explanation'],
                    f"Explanation mismatch for correct answer in {topic}, question {question['id']}")
                self.assertEqual(data['difficulty'], question['difficulty'].lower(),
                    f"Difficulty mismatch in response for {topic}, question {question['id']}")

                # Test all incorrect answers
                wrong_options = [opt for i, opt in enumerate(question['options']) if i != question['correct_answer']]
                for wrong_answer in wrong_options:
                    response = self.app.post('/api/validate-answer',
                        json={
                            'topic': topic,
                            'question_id': question['id'],
                            'answer': wrong_answer,
                            'response_time': 1.0
                        })
                    
                    self.assertEqual(response.status_code, 200,
                        f"Failed to validate incorrect answer for {topic}, question {question['id']}")
                    data = json.loads(response.data)
                    self.assertFalse(data['correct'],
                        f"Question {question['id']} in {topic} incorrectly marked wrong answer as correct")
                    self.assertIn('message', data,
                        f"Message missing for incorrect answer in {topic}, question {question['id']}")
                    self.assertEqual(data['difficulty'], question['difficulty'].lower(),
                        f"Difficulty mismatch in response for {topic}, question {question['id']}")

    def test_invalid_questions(self):
        """Test validation with invalid questions for each topic"""
        for topic in self.topics.keys():
            response = self.app.post('/api/validate-answer',
                json={
                    'topic': topic,
                    'question_id': 'invalid-id',
                    'answer': 'invalid',
                    'response_time': 1.0
                })
            
            self.assertEqual(response.status_code, 200,
                f"Invalid question test failed for topic {topic}")
            data = json.loads(response.data)
            self.assertFalse(data['correct'],
                f"Invalid question incorrectly marked as correct for topic {topic}")
            self.assertIn('message', data,
                f"Error message missing for invalid question in topic {topic}")

    def test_single_header_presence(self):
        """Test to ensure there is exactly one header element on each page with correct navigation."""
        # Test the home page
        response = self.app.get('/')
        assert response.status_code == 200
        html = response.data.decode()
        
        # Check header count on home page
        assert html.count('<header class="header">') == 1, "Should have exactly one header element on home page"
        assert '<h1 class="site-title"><a href="/">CS Algorithms Quiz</a></h1>' in html
        assert '<nav class="main-nav">' in html
        assert '<a href="/">Home</a>' in html
        assert html.count('<nav class="main-nav">') == 1, "Should have exactly one navigation element on home page"
        assert html.count('<h1 class="site-title">') == 1, "Should have exactly one site title on home page"
        
        # Test all topic info pages
        topics = ['binary-search-tree', 'sorting-algorithms', 'graph-algorithms', 'dynamic-programming']
        for topic in topics:
            # Test info page
            response = self.app.get(f'/algo/{topic}/info')
            assert response.status_code == 200, f"Info page for {topic} should return 200"
            html = response.data.decode()
            
            # Check header count on info page
            assert html.count('<header class="header">') == 1, f"Should have exactly one header element on {topic} info page"
            assert '<h1 class="site-title"><a href="/">CS Algorithms Quiz</a></h1>' in html, f"Site title missing on {topic} info page"
            assert '<nav class="main-nav">' in html, f"Navigation missing on {topic} info page"
            assert '<a href="/">Home</a>' in html, f"Home link missing on {topic} info page"
            assert f'<a href="/algo/{topic}/test">Take Quiz</a>' in html, f"Quiz link missing on {topic} info page"
            assert html.count('<nav class="main-nav">') == 1, f"Should have exactly one navigation element on {topic} info page"
            assert html.count('<h1 class="site-title">') == 1, f"Should have exactly one site title on {topic} info page"
            
            # Test test page
            response = self.app.get(f'/algo/{topic}/test')
            assert response.status_code == 200, f"Test page for {topic} should return 200"
            html = response.data.decode()
            
            # Check header count on test page
            assert html.count('<header class="header">') == 1, f"Should have exactly one header element on {topic} test page"
            assert '<h1 class="site-title"><a href="/">CS Algorithms Quiz</a></h1>' in html, f"Site title missing on {topic} test page"
            assert '<nav class="main-nav">' in html, f"Navigation missing on {topic} test page"
            assert '<a href="/">Home</a>' in html, f"Home link missing on {topic} test page"
            assert html.count('<nav class="main-nav">') == 1, f"Should have exactly one navigation element on {topic} test page"
            assert html.count('<h1 class="site-title">') == 1, f"Should have exactly one site title on {topic} test page"

if __name__ == '__main__':
    unittest.main() 