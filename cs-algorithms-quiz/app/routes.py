from flask import render_template, jsonify
import json
import os
import random

def load_algorithm_data(topic):
    json_file = f'app/questions/{topic}.json'
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            return json.load(f)
    return None

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('home.html')

    @app.route('/algo/<topic>/info')
    def algorithm_info(topic):
        # Map URL-friendly topic names to template directory names
        topic_map = {
            'sorting-algorithms': 'sorting',
            'graph-algorithms': 'graph',
            'dynamic-programming': 'dp',
            'binary-search-tree': 'bst'
        }
        
        # Get the template directory name
        template_dir = topic_map.get(topic)
        if not template_dir:
            return "Topic not found", 404

        # Load the algorithm data
        data = load_algorithm_data(topic.replace('-', '_'))
        if not data:
            return "Topic data not found", 404

        # Pass both the template directory and data to the template
        return render_template('algorithm_info.html',
                             topic=data,
                             template_dir=template_dir)

    @app.route('/algo/<topic>/test')
    def topic_test(topic):
        # Load the algorithm data
        data = load_algorithm_data(topic.replace('-', '_'))
        if not data:
            return "Topic not found", 404

        # Get a random question
        questions = data.get('questions', [])
        if not questions:
            return "No questions available", 404

        question = random.choice(questions)
        return render_template('test.html',
                             topic=topic,
                             question=question,
                             topic_data=data)

    @app.route('/api/questions/<topic>')
    def get_questions(topic):
        data = load_algorithm_data(topic)
        if data and 'questions' in data:
            return jsonify(data['questions'])
        return jsonify([])

    @app.route('/quiz/<topic>')
    def quiz(topic):
        return render_template('quiz.html', topic=topic) 