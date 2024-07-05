import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sock import Sock
import requests
# import uuid
# from flasgger import Swagger, swag_from
# import os
# import ssl
# import urllib3
#
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
# sock = Sock(app)
#
# swagger_file_path = os.path.join(os.path.dirname(__file__), 'swagger.yaml')
# swagger = Swagger(app, template_file=swagger_file_path)
#
# API_VIDEO_KEY = 'BQgyhs1lkAsktewRaHMFAGPtsMahfdaYJ4bISSwtkQF'
# API_VIDEO_BASE_URL = 'https://ws.api.video'
#
# headers = {
#     'Accept': 'application/json',
#     'Authorization': f'Bearer ' + API_VIDEO_KEY,
#     'Content-Type': 'application/json'
# }
#
# ssl_context = ssl._create_unverified_context()
#
# registered_devices = {"1341234"}
# streams = {"1341234": {"liveStreamId": "test_stream_id", "other_data": "test_data"}}
#
#
# @app.route('/register', methods=['POST'])
# def register_device():
#     global registered_devices
#     data = request.json
#     device_id = data.get('device_id')
#
#     if not device_id:
#         return jsonify({"error": "device_id is required"}), 400
#
#     if device_id not in registered_devices:
#         registered_devices.add(device_id)
#         return jsonify({"status": "device registered"}), 201
#     else:
#         return jsonify({"status": "device already registered"}), 200
#
#
# @app.route('/start-stream', methods=['POST'])
# @swag_from('swagger.yaml', endpoint='start-stream')
# def start_stream():
#     try:
#         global registered_devices, streams
#         data = request.json
#         device_id = data.get('device_id')
#
#         if device_id not in registered_devices:
#             return jsonify({"error": "Device not registered"}), 400
#
#         stream_uuid = str(uuid.uuid4())
#         stream_name = f'stream-{stream_uuid}'
#
#         response = requests.post(
#             f'{API_VIDEO_BASE_URL}/live-streams',
#             headers=headers,
#             json={
#                 "name": stream_name,
#                 "public": False,
#                 "record": True
#             },
#             verify=False
#         )
#
#         if response.status_code == 201:
#             stream_data = response.json()
#             streams[device_id] = stream_data
#             return jsonify({
#                 "status": "stream started",
#                 "stream_data": stream_data
#             })
#         else:
#             return jsonify({"error": "Failed to start stream", "details": response.json()}), response.status_code
#     except requests.exceptions.RequestException as e:
#         return jsonify({"error": "An error occurred while starting the stream", "details": str(e)}), 500
#
#
# @app.route('/stop-stream', methods=['POST'])
# @swag_from('swagger.yaml', endpoint='stop-stream')
# def stop_stream():
#     try:
#         global streams, registered_devices
#         data = request.json
#         device_id = data.get('device_id')
#
#         if device_id not in registered_devices or device_id not in streams:
#             return jsonify({"error": "Device not registered or no stream found"}), 400
#
#         stream_id = streams[device_id]['liveStreamId']
#         response = requests.delete(
#             f'{API_VIDEO_BASE_URL}/live-streams/{stream_id}',
#             headers=headers,
#             verify=False
#         )
#
#         if response.status_code == 204:
#             streams.pop(device_id, None)
#             return jsonify({"status": "stream stopped"})
#         else:
#             return jsonify({"error": "Failed to stop stream", "details": response.json()}), response.status_code
#     except requests.exceptions.RequestException as e:
#         return jsonify({"error": "An error occurred while stopping the stream", "details": str(e)}), 500
#
#
# @app.route('/list-streams', methods=['GET'])
# @swag_from('swagger.yaml', endpoint='list-streams')
# def list_streams():
#     try:
#         response = requests.get(
#             f'{API_VIDEO_BASE_URL}/live-streams',
#             headers=headers,
#             verify=False
#         )
#
#         if response.status_code == 200:
#             streams = response.json()
#             return jsonify(streams)
#         else:
#             return jsonify({"error": "Failed to list streams", "details": response.json()}), response.status_code
#     except requests.exceptions.RequestException as e:
#         return jsonify({"error": "An error occurred while listing the streams", "details": str(e)}), 500
#
#
# @app.route('/streams', methods=['GET'])
# @swag_from('swagger.yaml', endpoint='streams-page')
# def streams_page():
#     try:
#         response = requests.get(
#             f'{API_VIDEO_BASE_URL}/live-streams',
#             headers=headers,
#             verify=False
#         )
#
#         if response.status_code == 200:
#             streams = response.json().get('liveStreams', [])
#             return render_template('streams.html', streams=streams)
#         else:
#             return render_template('error.html', message="Failed to load streams")
#     except requests.exceptions.RequestException as e:
#         return render_template('error.html', message=str(e))
#
#
# @app.route('/watch-stream/<device_id>', methods=['GET'])
# @swag_from('swagger.yaml', endpoint='watch-stream-page')
# def watch_stream_page(device_id):
#     return render_template('watch.html', device_id=device_id)
#
#
# @sock.route('/<device_id>')
# def websocket(ws, device_id):
#     global registered_devices
#     global streams
#     if device_id not in registered_devices:
#         ws.send(json.dumps({"error": "Device not registered"}))
#         return
#
#     if device_id not in streams:
#         ws.send(json.dumps({"error": "No stream found for this device"}))
#         return
#
#     stream_data = streams[device_id]
#     ws.send(json.dumps(stream_data))
#     print(f"WebSocket connected: {device_id}")
#
#     while True:
#         data = ws.receive()
#         ws.send(f"Echo: {data}")
#
#
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
import csv
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sock import Sock
import requests
import uuid
from flasgger import Swagger, swag_from
import os
import ssl
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
sock = Sock(app)

swagger_file_path = os.path.join(os.path.dirname(__file__), 'swagger.yaml')
swagger = Swagger(app, template_file=swagger_file_path)

API_VIDEO_KEY = 'BQgyhs1lkAsktewRaHMFAGPtsMahfdaYJ4bISSwtkQF'
API_VIDEO_BASE_URL = 'https://ws.api.video'

headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer ' + API_VIDEO_KEY,
    'Content-Type': 'application/json'
}

ssl_context = ssl._create_unverified_context()

# File paths
REGISTERED_DEVICES_FILE = '/app/registered_devices.csv'
STREAMS_FILE = '/app/streams.csv'

def read_registered_devices():
    if not os.path.isfile(REGISTERED_DEVICES_FILE):
        return set()
    with open(REGISTERED_DEVICES_FILE, mode='r') as file:
        reader = csv.reader(file)
        return set(row[0] for row in reader)

def write_registered_device(device_id):
    with open(REGISTERED_DEVICES_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([device_id])

def read_streams():
    if not os.path.isfile(STREAMS_FILE):
        return {}
    with open(STREAMS_FILE, mode='r') as file:
        reader = csv.reader(file)
        return {rows[0]: json.loads(rows[1]) for rows in reader}

def write_stream_to_csv(device_id, stream_data):
    with open(STREAMS_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([device_id, json.dumps(stream_data)])

registered_devices = read_registered_devices()
streams = read_streams()

@app.route('/register', methods=['POST'])
def register_device():
    global registered_devices
    data = request.json
    device_id = data.get('device_id')

    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    if device_id not in registered_devices:
        registered_devices.add(device_id)
        write_registered_device(device_id)
        return jsonify({"status": "device registered"}), 201
    else:
        return jsonify({"status": "device already registered"}), 200

@app.route('/start-stream', methods=['POST'])
@swag_from('swagger.yaml', endpoint='start-stream')
def start_stream():
    try:
        global registered_devices, streams
        data = request.json
        device_id = data.get('device_id')

        if device_id not in registered_devices:
            return jsonify({"error": "Device not registered"}), 400

        stream_uuid = str(uuid.uuid4())
        stream_name = f'stream-{stream_uuid}'

        response = requests.post(
            f'{API_VIDEO_BASE_URL}/live-streams',
            headers=headers,
            json={
                "name": stream_name,
                "public": False,
                "record": True
            },
            verify=False
        )

        if response.status_code == 201:
            stream_data = response.json()
            streams[device_id] = stream_data
            write_stream_to_csv(device_id, stream_data)
            return jsonify({
                "status": "stream started",
                "stream_data": stream_data
            })
        else:
            return jsonify({"error": "Failed to start stream", "details": response.json()}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "An error occurred while starting the stream", "details": str(e)}), 500

@app.route('/stop-stream', methods=['POST'])
@swag_from('swagger.yaml', endpoint='stop-stream')
def stop_stream():
    try:
        global streams, registered_devices
        data = request.json
        device_id = data.get('device_id')

        if device_id not in registered_devices or device_id not in streams:
            return jsonify({"error": "Device not registered or no stream found"}), 400

        stream_id = streams[device_id]['liveStreamId']
        response = requests.delete(
            f'{API_VIDEO_BASE_URL}/live-streams/{stream_id}',
            headers=headers,
            verify=False
        )

        if response.status_code == 204:
            streams.pop(device_id, None)
            # write_streams_to_csv(streams)  # Update CSV after removing stream
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
            headers=headers,
            verify=False
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
            headers=headers,
            verify=False
        )

        if response.status_code == 200:
            streams = response.json().get('liveStreams', [])
            return render_template('streams.html', streams=streams)
        else:
            return render_template('error.html', message="Failed to load streams")
    except requests.exceptions.RequestException as e:
        return render_template('error.html', message=str(e))

@app.route('/watch-stream/<device_id>', methods=['GET'])
@swag_from('swagger.yaml', endpoint='watch-stream-page')
def watch_stream_page(device_id):
    return render_template('watch.html', device_id=device_id)

@sock.route('/<device_id>')
def websocket(ws, device_id):
    global registered_devices
    global streams
    if device_id not in registered_devices:
        ws.send(json.dumps({"error": "Device not registered"}))
        return

    # if device_id not in streams:
    #     ws.send(json.dumps({"error": "No stream found for this device"}))
    #     return

    stream_data = streams[device_id]
    ws.send(json.dumps(stream_data))
    print(f"WebSocket connected: {device_id}")

    while True:
        data = ws.receive()
        ws.send(f"Echo: {data}")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
