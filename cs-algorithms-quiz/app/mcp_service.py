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
        
        # Randomly select a question from the bank
        question = random.choice(self.question_bank[topic])
        
        # Store the current question (in a real implementation, this would be session-specific)
        self.current_questions[topic] = question
        
        # Return question without the correct answer
        return {
            "id": question["id"],
            "question": question["question"],
            "options": question["options"]
        }

    def validate_answer(self, topic, question_id, answer):
        # Get the current question for this topic
        current_question = self.current_questions.get(topic)
        
        if not current_question or current_question["id"] != question_id:
            return {"correct": False, "message": "Invalid question"}
        
        is_correct = answer == current_question["correct_answer"]
        
        return {
            "correct": is_correct,
            "explanation": current_question["explanation"]
        } 