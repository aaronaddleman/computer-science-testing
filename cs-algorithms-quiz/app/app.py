from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/algo/binary-search-tree/info')
def binary_search_tree_info():
    return render_template('binary_search_tree_info.html')

@app.route('/algo/binary-search-tree/test')
def binary_search_tree_test():
    return render_template('binary_search_tree_test.html')

if __name__ == '__main__':
    app.run(debug=True) 