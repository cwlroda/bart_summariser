import json
import flask
from flask import Flask, request, render_template
from core.bart_flask import Bart

app = Flask(__name__)

def init(request):
    file = open('config.json', 'r')
    config = json.load(file)
    
    config['input']['text'] = request.json['input_text']
    config['input']['documents'] = request.json['documents']
    config['params']['num_words'] = int(request.json['num_words'])
    config['params']['summary_length'] = float(request.json['percentage'])/100
    config['params']['num_beams'] = int(request.json['num_beams'])
    config['params']['no_repeat_ngram_size'] = int(request.json['no_repeat_ngram_size'])
    config['params']['repetition_penalty'] = float(request.json['repetition_penalty'])
    config['params']['length_penalty'] = float(request.json['length_penalty'])
    config['params']['min_length_buffer'] = int(request.json['min_buffer'])
    config['params']['max_length_buffer'] = int(request.json['max_buffer'])
    #config['params']['num_return_sequences'] = request.json['num_return_sequences']
    
    file.close()
    
    file = open('config.json', 'w')
    json.dump(config, file, ensure_ascii=False, indent=4)
    file.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        init(request)
        summariser = Bart()
        
        output, documents = summariser.run()
        
        response = {}
        response['response'] = {
            'summary': str(output),
            'documents': documents
        }
        
        return flask.jsonify(response)
    
    except Exception as ex:
        res = dict({'message': str(ex)})
        print(res)
        return app.response_class(response=json.dumps(res), status=500, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=False,
            port=8000,
            use_reloader=False)