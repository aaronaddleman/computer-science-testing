from flask import Flask, render_template, request, jsonify
from mcp_service import MCPService

app = Flask(__name__)
mcp_service = MCPService()

# Define valid topics and their template mappings
TOPIC_TEMPLATES = {
    'binary-search-tree': {
        'info': 'binary_search_tree_info.html',
        'test': 'binary_search_tree_test.html'
    },
    'sorting-algorithms': {
        'info': 'algorithm_info.html',
        'test': 'algorithm_test.html'
    },
    'graph-algorithms': {
        'info': 'algorithm_info.html',
        'test': 'algorithm_test.html'
    },
    'dynamic-programming': {
        'info': 'algorithm_info.html',
        'test': 'algorithm_test.html'
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/algo/<topic>/info')
def topic_info(topic):
    if topic not in TOPIC_TEMPLATES:
        return "Topic not found", 404
    
    template = TOPIC_TEMPLATES[topic]['info']
    topic_data = mcp_service.get_topic_info(topic)
    return render_template(template, topic=topic_data)

@app.route('/algo/<topic>/test')
def topic_test(topic):
    if topic not in TOPIC_TEMPLATES:
        return "Topic not found", 404
    
    template = TOPIC_TEMPLATES[topic]['test']
    question = mcp_service.generate_question(topic)
    if question is None:
        return "No questions available", 404
    
    topic_data = mcp_service.get_topic_info(topic)
    return render_template(template, topic=topic_data, question=question)

@app.route('/api/validate-answer', methods=['POST'])
def validate_answer():
    data = request.get_json()
    topic = data.get('topic')
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    if topic not in TOPIC_TEMPLATES:
        return jsonify({"correct": False, "message": "Invalid topic"})
    
    result = mcp_service.validate_answer(topic, question_id, answer)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True) 