import random
import os
import logging
from load_config import load_config
from get_logger import get_logger
from requests import Session
from flask import Flask, request, jsonify

_log = get_logger()

# Port and binding
api_port = int(os.getenv('APP_PORT', 5000))
_log.info(f'API port is: {api_port}')
api_bind = os.getenv('APP_BIND', '0.0.0.0')
_log.info(f'API bind to: {api_bind}')

# Init application and dependencies
app = Flask(__name__)
app.config["APPLICATION_ROOT"] = "/v1"

# Load system config
config = load_config('config.yml')
available_models = list(config['models'].keys())


@app.route('/')
@app.route('/index')
def index():
    return "test"


@app.route('/audio/models', methods=['GET'])
def models():
    result = available_models
    return jsonify(result), 200


@app.route('/audio/transcriptions', methods=['POST'])
def transcriptions():
    _log.debug(request.__dict__)

    # Get file
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '' or file is None:
        return jsonify({'message': 'No selected file'}), 400

    # Get name of model
    if 'model' not in request.form:
        return jsonify({'message': 'No model provided'}), 400
    if request.form['model'] not in available_models:
        return jsonify({'message': 'Requested model is not available'}), 400

    # Model related settings
    data = dict()
    if 'language' in request.form:
        data['language'] = request.form['language']
        # TODO: check in language in available list
    if 'prompt' in request.form:
        data['prompt'] = request.form['prompt']
    if 'response_format' in request.form:
        data['response_format'] = request.form['response_format']
    if 'temperature' in request.form:
        data['temperature'] = request.form['temperature']
    # if 'timestamp_granularities' in request.form:
    #     data['timestamp_granularities'] = request.form['timestamp_granularities']

    # Connection settings
    model = request.form['model']
    servers = config['models'][model]
    server = random.choice(servers)

    _log.info(f"Server: {server}, Model: {model}, Data: {data}")

    try:
        session = Session()
        response = session.post(url=server, files={'file': file}, data=data)
        _log.debug(response.__dict__)

        result = response.content
        return result, 200
    except Exception as e:
        _log.exception(e)
        return jsonify({'message': 'Error processing file'}), 500


if __name__ == "__main__":
    app.run(host=api_bind, port=api_port, debug=True, use_reloader=True)
