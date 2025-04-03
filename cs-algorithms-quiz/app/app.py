from flask import Flask, render_template, request, jsonify
from mcp_service import MCPService
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)
mcp_service = MCPService()

# Define Prometheus metrics
TOTAL_QUESTIONS = Counter('quiz_questions_total', 'Total number of questions attempted', ['topic', 'difficulty'])
CORRECT_ANSWERS = Counter('quiz_correct_answers_total', 'Total number of correct answers', ['topic', 'difficulty'])
INCORRECT_ANSWERS = Counter('quiz_incorrect_answers_total', 'Total number of incorrect answers', ['topic', 'difficulty'])

# Response time metrics
RESPONSE_TIME = Histogram('quiz_response_time_seconds',
    'Time taken to answer questions',
    ['topic', 'difficulty', 'correct'],
    buckets=[1, 5, 10, 20, 30, 60, float("inf")])  # buckets in seconds

# Question generation time
QUESTION_GENERATION_TIME = Histogram('quiz_question_generation_seconds',
    'Time taken to generate questions',
    ['topic'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0])

# Define valid topics and their template mappings
TOPIC_TEMPLATES = {
    'binary-search-tree': {
        'info': 'algorithm_info.html',
        'test': 'algorithm_test.html'
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

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

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
    
    start_time = time.time()
    template = TOPIC_TEMPLATES[topic]['test']
    question = mcp_service.generate_question(topic)
    generation_time = time.time() - start_time
    
    if question is None:
        return "No questions available", 404
    
    # Record question generation time
    QUESTION_GENERATION_TIME.labels(topic=topic).observe(generation_time)
    
    topic_data = mcp_service.get_topic_info(topic)
    return render_template(template, topic=topic_data, question=question)

@app.route('/api/validate-answer', methods=['POST'])
def validate_answer():
    data = request.get_json()
    topic = data.get('topic')
    question_id = data.get('question_id')
    answer = data.get('answer')
    response_time = data.get('response_time', 0)  # Time taken to answer in seconds
    
    if topic not in TOPIC_TEMPLATES:
        return jsonify({"correct": False, "message": "Invalid topic"})
    
    # Get question details including difficulty
    question_info = mcp_service.get_question_info(topic, question_id)
    if not question_info:
        return jsonify({"correct": False, "message": "Invalid question"})
    
    difficulty = question_info.get('difficulty', 'medium')  # Default to medium if not specified
    
    # Increment total questions counter with difficulty
    TOTAL_QUESTIONS.labels(topic=topic, difficulty=difficulty).inc()
    
    result = mcp_service.validate_answer(topic, question_id, answer)
    is_correct = result.get('correct', False)
    
    # Record metrics with difficulty
    if is_correct:
        CORRECT_ANSWERS.labels(topic=topic, difficulty=difficulty).inc()
    else:
        INCORRECT_ANSWERS.labels(topic=topic, difficulty=difficulty).inc()
    
    # Record response time
    RESPONSE_TIME.labels(
        topic=topic,
        difficulty=difficulty,
        correct=str(is_correct).lower()
    ).observe(response_time)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 