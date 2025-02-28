import uuid
from datetime import datetime
import os
import logging
from requests import Session
from utils import load_config, get_logger, get_models, get_model, select_best_server
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

_log = get_logger()

# Get API port and binding from environment variables or use default values if not specified
api_bind = os.getenv('APP_BIND', '0.0.0.0')
_log.info(f'API binding to address: {api_bind}')
api_port = int(os.getenv('APP_PORT', 5000))
_log.info(f'API listening on port: {api_port}')

# Initialize Flask application and load system configuration
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = os.getenv('MAX_CONTENT_LENGTH', 250 * 1024 * 1024)  # 25MB max
app.logger.setLevel(logging.INFO)
CORS(app, resources={r"/*": {"origins": "*"}})

config = load_config('config.yml')
available_models = get_models(config)

available_response_format = ['json', 'text', 'srt', 'verbose_json', 'vtt']
response_format_mapping = {
    'srt': 'text/plain',
    'vtt': 'text/plain',
    'text': 'text/plain',
    'json': 'application/json',
    'verbose_json': 'application/json',
}


@app.route('/')
@app.route('/index')
@app.route('/models', methods=['GET'])
def models():
    _log.debug('Received a GET request to retrieve available models.')
    result = {"object": "list", "data": available_models}
    return jsonify(result), 200, {'Content-Type': 'application/json'}


@app.route('/models/<model>', methods=['GET'])
def model(model: str):
    _log.debug('Received a GET request to retrieve a model.')
    result = get_model(config, model)
    if result is None:
        _log.error(message := 'No model found with provided id')
        return jsonify({'message': message}), 404
    return jsonify(result), 200, {'Content-Type': 'application/json'}


@app.route('/audio/transcriptions', methods=['POST'], defaults={"response_format": "json"})
@app.route('/audio/translations', methods=['POST'], defaults={"language": "en", "response_format": "json"})
def transcriptions(language: str = None, response_format: str = None):
    _log.debug('Received a POST request to transcribe an audio file.')

    # Check if 'file' attribute is present in the request
    if 'file' not in request.files:
        _log.error(message := 'No file attribute provided in the request')
        return jsonify({'message': message}), 400

    file = request.files['file']
    # Check if the file is empty or None
    if file.filename == '' or file is None:
        _log.error(message := 'File attribute is empty')
        return jsonify({'message': message}), 400

    # Check if model parameter is provided and validate it
    if 'model' not in request.form:
        _log.error(message := 'No model provided in the request')
        return jsonify({'message': message}), 400

    model = request.form['model']
    if model not in config['models'].keys():
        _log.warning(message := f'Requested model "{model}" is not available.')
        return jsonify({'message': message}), 400

    # Collect form data for transcription
    data = {}
    if 'language' in request.form:
        _log.debug(f'language: {request.form["language"]}')
        data['language'] = request.form['language']
    if language is not None:
        _log.debug(f'language: {language}')
        data['language'] = language
    if 'prompt' in request.form:
        _log.debug(f'prompt: {request.form["prompt"]}')
        data['prompt'] = request.form['prompt']
    if response_format is not None:
        _log.debug(f'response_format: {response_format}')
        data['response_format'] = response_format
    if 'response_format' in request.form:
        _log.debug(f'response_format: {request.form["response_format"]}')
        data['response_format'] = request.form['response_format']
    if 'temperature' in request.form:
        _log.debug(f'temperature: {request.form["temperature"]}')
        data['temperature'] = request.form['temperature']
    if 'temperature_inc' in request.form:
        _log.debug(f'temperature_inc: {request.form["temperature_inc"]}')
        data['temperature'] = request.form['temperature']
    if 'timestamp_granularities' in request.form:
        _log.debug(f'timestamp_granularities: {request.form["timestamp_granularities"]}')
        data['timestamp_granularities'] = request.form['timestamp_granularities']

    try:

        # Get uniq ID of request
        request_id = str(uuid.uuid4())

        # Select a random server from model's endpoints list
        endpoint = select_best_server(config['models'][model]['endpoints'])

        # Init requests session
        session = Session()

        # Send POST request to the chosen server with uploaded file and data
        _log.info({"uuid": request_id, "name": "transcriptions", "type": "request",
                   'timestamp': int(datetime.utcnow().timestamp()),
                   "endpoint": endpoint['base_url'], "model": model, "data": data})
        response = session.post(url=endpoint['base_url'], files={'file': file}, data=data)

        # Send response
        _log.debug({"uuid": request_id, "name": "transcriptions", "type": "response",
                    'timestamp': int(datetime.utcnow().timestamp()),
                    'status_code': response.status_code, 'content': response.content})

        content_type = response_format_mapping[response_format]
        return response.content, response.status_code, {'Content-Type': content_type}

    except Exception as e:
        _log.exception(e)
        return jsonify({'message': 'An error occurred while processing the audio file.'}), 500


if __name__ == "__main__":
    app.run(host=api_bind, port=api_port, debug=True, use_reloader=True)
