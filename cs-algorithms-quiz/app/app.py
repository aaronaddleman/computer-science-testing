from flask import Flask, render_template, request, jsonify
from mcp_service import MCPService

app = Flask(__name__)
mcp_service = MCPService()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/algo/binary-search-tree/info')
def binary_search_tree_info():
    return render_template('binary_search_tree_info.html')

@app.route('/algo/binary-search-tree/test')
def binary_search_tree_test():
    question = mcp_service.generate_question('binary-search-tree')
    return render_template('binary_search_tree_test.html', question=question)

@app.route('/api/validate-answer', methods=['POST'])
def validate_answer():
    data = request.get_json()
    topic = data.get('topic')
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    result = mcp_service.validate_answer(topic, question_id, answer)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True) 