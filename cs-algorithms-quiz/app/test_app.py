import unittest
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        # Test the home page
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Computer Science Algorithms', response.data)

    def test_binary_search_tree_info_page(self):
        # Test the Binary Search Tree info page
        response = self.app.get('/algo/binary-search-tree/info')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Binary Search Tree', response.data)

    def test_binary_search_tree_test_page(self):
        # Test the Binary Search Tree test page
        response = self.app.get('/algo/binary-search-tree/test')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Binary Search Tree Test', response.data)

if __name__ == '__main__':
    unittest.main() 