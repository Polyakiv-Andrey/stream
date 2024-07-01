from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import uuid
from flasgger import Swagger, swag_from

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)


API_VIDEO_KEY = 'BQgyhs1lkAsktewRaHMFAGPtsMahfdaYJ4bISSwtkQF'
API_VIDEO_BASE_URL = 'https://ws.api.video'

headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {API_VIDEO_KEY}',
    'Content-Type': 'application/json'
}

@app.route('/start-stream', methods=['POST'])
@swag_from({
    'responses': {
        200: {
            'description': 'Stream started successfully',
            'examples': {
                'application/json': {
                    "status": "stream started",
                    "stream_data": {
                        "stream_uuid": "generated-uuid",
                        "id": "stream-id",
                        "name": "stream-name",
                        "public": False,
                        "record": True
                    }
                }
            }
        },
        400: {
            'description': 'Stream name is required',
        },
        500: {
            'description': 'Failed to start stream',
        }
    },
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'type': 'json',
            'required': True,
            'schema': {
                'stream_name': {
                    'type': 'string',
                    'description': 'The name of the stream',
                }
            }
        }
    ]
})
def start_stream():
    data = request.json
    stream_name = data.get('stream_name')

    if not stream_name:
        return jsonify({"error": "Stream name is required"}), 400

    stream_uuid = str(uuid.uuid4())
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

@app.route('/stop-stream/<stream_id>', methods=['POST'])
@swag_from({
    'responses': {
        200: {
            'description': 'Stream stopped successfully',
        },
        500: {
            'description': 'Failed to stop stream',
        }
    },
    'parameters': [
        {
            'name': 'stream_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'The ID of the stream to stop',
        }
    ]
})
def stop_stream(stream_id):
    response = requests.delete(
        f'{API_VIDEO_BASE_URL}/live-streams/{stream_id}',
        headers=headers
    )

    if response.status_code == 204:
        return jsonify({"status": "stream stopped"})
    else:
        return jsonify({"error": "Failed to stop stream", "details": response.json()}), response.status_code

@app.route('/list-streams', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'List of streams',
            'examples': {
                'application/json': [
                    {
                        "id": "stream-id",
                        "name": "stream-name",
                        "public": False,
                        "record": True
                    }
                ]
            }
        },
        500: {
            'description': 'Failed to list streams',
        }
    }
})
def list_streams():
    response = requests.get(
        f'{API_VIDEO_BASE_URL}/live-streams',
        headers=headers
    )

    if response.status_code == 200:
        streams = response.json()
        return jsonify(streams)
    else:
        return jsonify({"error": "Failed to list streams", "details": response.json()}), response.status_code

@app.route('/streams', methods=['GET'])
def streams_page():
    response = requests.get(
        f'{API_VIDEO_BASE_URL}/live-streams',
        headers=headers
    )

    if response.status_code == 200:
        streams = response.json().get('liveStreams', [])
        return render_template('streams.html', streams=streams)
    else:
        return render_template('error.html', message="Failed to load streams")

@app.route('/watch-stream/<stream_id>', methods=['GET'])
def watch_stream_page(stream_id):
    response = requests.get(
        f'{API_VIDEO_BASE_URL}/live-streams/{stream_id}',
        headers=headers
    )

    if response.status_code == 200:
        stream_data = response.json()
        return render_template('watch.html', stream=stream_data)
    else:
        return render_template('error.html', message="Failed to load stream")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
