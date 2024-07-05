# import csv
# import json
# from flask import Flask, request, jsonify, render_template
# from flask_cors import CORS
# from flask_sock import Sock
# import requests
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
# # File path
# REGISTERED_DEVICES_FILE = '/app/registered_devices.csv'
#
# def read_registered_devices():
#     if not os.path.isfile(REGISTERED_DEVICES_FILE):
#         return set()
#     with open(REGISTERED_DEVICES_FILE, mode='r') as file:
#         reader = csv.reader(file)
#         return set(row[0] for row in reader)
#
# def write_registered_device(device_id):
#     with open(REGISTERED_DEVICES_FILE, mode='a', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([device_id])
#
# registered_devices = read_registered_devices()
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
#         write_registered_device(device_id)
#         return jsonify({"status": "device registered"}), 201
#     else:
#         return jsonify({"status": "device already registered"}), 200
#
# @app.route('/start-stream', methods=['POST'])
# @swag_from('swagger.yaml', endpoint='start-stream')
# def start_stream():
#     try:
#         global registered_devices
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
#             return jsonify({
#                 "status": "stream started",
#                 "stream_data": stream_data
#             })
#         else:
#             return jsonify({"error": "Failed to start stream", "details": response.json()}), response.status_code
#     except requests.exceptions.RequestException as e:
#         return jsonify({"error": "An error occurred while starting the stream", "details": str(e)}), 500
#
# @app.route('/stop-stream', methods=['POST'])
# @swag_from('swagger.yaml', endpoint='stop-stream')
# def stop_stream():
#     try:
#         data = request.json
#         device_id = data.get('device_id')
#
#         if device_id not in registered_devices:
#             return jsonify({"error": "Device not registered or no stream found"}), 400
#
#         stream_id = request.json.get('stream_id')
#         if stream_id:
#             response = requests.delete(
#                 f'{API_VIDEO_BASE_URL}/live-streams/{stream_id}',
#                 headers=headers,
#                 verify=False
#             )
#
#             if response.status_code == 204:
#                 return jsonify({"status": "stream stopped"})
#             else:
#                 return jsonify({"error": "Failed to stop stream", "details": response.json()}), response.status_code
#         else:
#             return jsonify({"error": "No stream found for this device"}), 400
#     except requests.exceptions.RequestException as e:
#         return jsonify({"error": "An error occurred while stopping the stream", "details": str(e)}), 500
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
# @app.route('/watch-stream/<device_id>', methods=['GET'])
# @swag_from('swagger.yaml', endpoint='watch-stream-page')
# def watch_stream_page(device_id):
#     return render_template('watch.html', device_id=device_id)
#
# @sock.route('/<device_id>')
# def websocket(ws, device_id):
#     global registered_devices
#     if device_id not in registered_devices:
#         ws.send(json.dumps({"error": "Device not registered"}))
#         return
#
#     print(f"WebSocket connected: {device_id}")
#
#     while True:
#         data = ws.receive()
#         if data:
#             ws.send(data)
#
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

import json
import csv
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

REGISTERED_DEVICES_FILE = '/app/registered_devices.csv'
streams = {}

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


registered_devices = read_registered_devices()


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


@sock.route('/<device_id>')
def websocket(ws, device_id):
    global registered_devices
    global streams
    if device_id not in registered_devices:
        ws.send(json.dumps({"error": "Device not registered"}))
        return

    print(f"WebSocket connected: {device_id}")

    while True:
        message = ws.receive()
        if not message:
            continue

        message_data = json.loads(message)
        msg_type = message_data.get('type')
        msg_data = message_data.get('data', {})

        if msg_type == 'control':
            command = msg_data.get('value')
            if command == 'start':
                response = start_stream(device_id)
            elif command == 'stop':
                response = stop_stream(device_id)
            elif command == 'resolution':
                response = set_resolution(device_id, msg_data.get('resolution'))
            else:
                response = {"error": "Unknown command"}

            ws.send(json.dumps(response))
        else:
            ws.send(json.dumps({"error": "Invalid message type"}))


def start_stream(device_id):
    global registered_devices
    global streams

    if device_id not in registered_devices:
        return {"error": "Device not registered"}

    stream_uuid = str(uuid.uuid4())
    stream_name = f'stream-{stream_uuid}'

    try:
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
            streams[device_id] = stream_data['liveStreamId']
            return {
                "status": "stream started",
                "stream_data": stream_data
            }
        else:
            return {"error": "Failed to start stream", "details": response.json()}
    except requests.exceptions.RequestException as e:
        return {"error": "An error occurred while starting the stream", "details": str(e)}


def stop_stream(device_id):
    global registered_devices
    global streams

    if device_id not in registered_devices:
        return {"error": "Device not registered"}

    stream_id = streams.get(device_id)
    if not stream_id:
        return {"error": "No stream found for this device"}

    try:
        response = requests.delete(
            f'{API_VIDEO_BASE_URL}/live-streams/{stream_id}',
            headers=headers,
            verify=False
        )

        if response.status_code == 204:
            del streams[device_id]
            return {"status": "stream stopped"}
        else:
            return {"error": "Failed to stop stream", "details": response.json()}
    except requests.exceptions.RequestException as e:
        return {"error": "An error occurred while stopping the stream", "details": str(e)}


def set_resolution(device_id, resolution):
    global registered_devices

    if device_id not in registered_devices:
        return {"error": "Device not registered"}

    # Placeholder function to handle setting resolution
    # The actual implementation will depend on the streaming service API

    return {"status": "resolution set", "resolution": resolution}


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
            stream = response.json().get('liveStreams', [])
            return render_template('streams.html', streams=stream)
        else:
            return render_template('error.html', message="Failed to load streams")
    except requests.exceptions.RequestException as e:
        return render_template('error.html', message=str(e))


@app.route('/watch-stream/<device_id>', methods=['GET'])
@swag_from('swagger.yaml', endpoint='watch-stream-page')
def watch_stream_page(device_id):
    return render_template('watch.html', device_id=device_id)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
