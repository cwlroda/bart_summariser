import flask
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    pass

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000, use_reloader=False)