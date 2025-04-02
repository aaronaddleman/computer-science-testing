import random

class MCPService:
    def __init__(self):
        # Initialize question bank
        self.question_bank = {
            "binary-search-tree": [
                {
                    "id": "bst-1",
                    "question": "What is the time complexity of searching in a balanced binary search tree?",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                    "correct_answer": 1,
                    "explanation": "In a balanced BST, each comparison eliminates half of the remaining nodes."
                },
                {
                    "id": "bst-2",
                    "question": "Which traversal of a binary search tree visits nodes in ascending order?",
                    "options": ["Preorder", "Inorder", "Postorder", "Level-order"],
                    "correct_answer": 1,
                    "explanation": "Inorder traversal visits left subtree, root, then right subtree, producing sorted output in BST."
                },
                {
                    "id": "bst-3",
                    "question": "What is the space complexity of a binary search tree with n nodes?",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                    "correct_answer": 2,
                    "explanation": "Each node requires constant space, and there are n nodes in total."
                }
            ]
        }
        self.current_questions = {}  # Store current question for each user session

    def generate_question(self, topic):
        if topic not in self.question_bank:
            return None
        
        # For testing purposes, always return the first question
        question = self.question_bank[topic][0]
        
        # Store the current question (in a real implementation, this would be session-specific)
        self.current_questions[topic] = question
        
        # Return question without the correct answer and explanation
        return {
            "id": question["id"],
            "question": question["question"],
            "options": question["options"]
        }

    def validate_answer(self, topic, question_id, answer):
        # Get the current question for this topic
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