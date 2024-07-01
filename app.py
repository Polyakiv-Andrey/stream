from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import requests
import uuid
from flasgger import Swagger, swag_from
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5000", "http://localhost:5000"]}})
socketio = SocketIO(app, cors_allowed_origins=["http://127.0.0.1:5000", "http://localhost:5000"])

swagger_file_path = os.path.join(os.path.dirname(__file__), 'swagger.yaml')
swagger = Swagger(app, template_file=swagger_file_path)

API_VIDEO_KEY = 'BQgyhs1lkAsktewRaHMFAGPtsMahfdaYJ4bISSwtkQF'
API_VIDEO_BASE_URL = 'https://ws.api.video'

headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {API_VIDEO_KEY}',
    'Content-Type': 'application/json'
}

@app.route('/start-stream', methods=['POST'])
@swag_from('swagger.yaml', endpoint='start-stream')
def start_stream():
    try:
        stream_uuid = str(uuid.uuid4())
        stream_name = f'stream-{stream_uuid}'

        response = requests.post(
            f'{API_VIDEO_BASE_URL}/live-streams',
            headers=headers,
            json={
                "name": stream_name,
                "public": False,
                "record": True
            }
        )

        if response.status_code == 201:
            stream_data = response.json()
            stream_data["stream_uuid"] = stream_uuid
            return jsonify({
                "status": "stream started",
                "stream_data": stream_data
            })
        else:
            return jsonify({"error": "Failed to start stream", "details": response.json()}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "An error occurred while starting the stream", "details": str(e)}), 500

@app.route('/stop-stream/<stream_id>', methods=['POST'])
@swag_from('swagger.yaml', endpoint='stop-stream')
def stop_stream(stream_id):
    try:
        response = requests.delete(
            f'{API_VIDEO_BASE_URL}/live-streams/{stream_id}',
            headers=headers
        )

        if response.status_code == 204:
            return jsonify({"status": "stream stopped"})
        else:
            return jsonify({"error": "Failed to stop stream", "details": response.json()}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "An error occurred while stopping the stream", "details": str(e)}), 500

@app.route('/list-streams', methods=['GET'])
@swag_from('swagger.yaml', endpoint='list-streams')
def list_streams():
    try:
        response = requests.get(
            f'{API_VIDEO_BASE_URL}/live-streams',
            headers=headers
        )

        if response.status_code == 200:
            streams = response.json()
            return jsonify(streams)
        else:
            return jsonify({"error": "Failed to list streams", "details": response.json()}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "An error occurred while listing the streams", "details": str(e)}), 500

@app.route('/streams', methods=['GET'])
@swag_from('swagger.yaml', endpoint='streams-page')
def streams_page():
    try:
        response = requests.get(
            f'{API_VIDEO_BASE_URL}/live-streams',
            headers=headers
        )

        if response.status_code == 200:
            streams = response.json().get('liveStreams', [])
            return render_template('streams.html', streams=streams)
        else:
            return render_template('error.html', message="Failed to load streams")
    except requests.exceptions.RequestException as e:
        return render_template('error.html', message=str(e))

@app.route('/watch-stream/<stream_id>', methods=['GET'])
@swag_from('swagger.yaml', endpoint='watch-stream-page')
def watch_stream_page(stream_id):
    try:
        response = requests.get(
            f'{API_VIDEO_BASE_URL}/live-streams/{stream_id}',
            headers=headers
        )

        if response.status_code == 200:
            stream_data = response.json()
            return render_template('watch.html', stream=stream_data)
        else:
            return render_template('error.html', message="Failed to load stream")
    except requests.exceptions.RequestException as e:
        return render_template('error.html', message=str(e))

@socketio.on('start_stream')
def handle_start_stream(data):
    try:
        stream_uuid = str(uuid.uuid4())
        stream_name = f'stream-{stream_uuid}'

        response = requests.post(
            f'{API_VIDEO_BASE_URL}/live-streams',
            headers=headers,
            json={
                "name": stream_name,
                "public": False,
                "record": True
            }
        )

        if response.status_code == 201:
            stream_data = response.json()
            stream_data["stream_uuid"] = stream_uuid
            emit('stream_started', stream_data)
        else:
            emit('error', {"error": "Failed to start stream", "details": response.json()})
    except requests.exceptions.RequestException as e:
        emit('error', {"error": "An error occurred while starting the stream", "details": str(e)})

@socketio.on('stop_stream')
def handle_stop_stream(data):
    try:
        stream_id = data.get('stream_id')
        response = requests.delete(
            f'{API_VIDEO_BASE_URL}/live-streams/{stream_id}',
            headers=headers
        )

        if response.status_code == 204:
            emit('stream_stopped', {"status": "stream stopped"})
        else:
            emit('error', {"error": "Failed to stop stream", "details": response.json()})
    except requests.exceptions.RequestException as e:
        emit('error', {"error": "An error occurred while stopping the stream", "details": str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    # import eventlet
    #
    # eventlet.monkey_patch()
    # socketio.run(app, debug=True, host='0.0.0.0', port=5000)
