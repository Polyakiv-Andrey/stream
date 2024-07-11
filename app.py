# import json
# from flask import Flask, request, jsonify, render_template
# from flask_cors import CORS
# from flask_sock import Sock
# import requests
# import uuid
# import ssl
# import urllib3
#
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
# sock = Sock(app)
#
# API_VIDEO_KEY = 'BQgyhs1lkAsktewRaHMFAGPtsMahfdaYJ4bISSwtkQF'
# API_VIDEO_BASE_URL = 'https://ws.api.video'
#
# headers = {
#     'Accept': 'application/json',
#     'Authorization': 'Bearer ' + API_VIDEO_KEY,
#     'Content-Type': 'application/json'
# }
#
# ssl_context = ssl._create_unverified_context()
#
# registered_devices = set()
# streams = {}
# websockets = {}
#
#
# @app.route('/register', methods=['POST'])
# def register_device():
#     data = request.json
#     device_id = str(data.get('device_id'))
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
# @sock.route('/<device_id>')
# def websocket(ws, device_id):
#     global registered_devices, streams, websockets
#
#     if device_id not in registered_devices:
#         ws.send(json.dumps({"error": "Device not registered"}))
#         return
#
#     if device_id not in websockets:
#         websockets[device_id] = []
#
#     websockets[device_id].append(ws)
#     print(f"WebSocket connected: {device_id}")
#
#     try:
#         while True:
#             message = ws.receive()
#             if not message:
#                 continue
#
#             try:
#                 message_data = json.loads(message)
#             except json.JSONDecodeError:
#                 ws.send(json.dumps({"error": "Invalid JSON format"}))
#                 continue
#
#             msg_type = message_data.get('type')
#             msg_data = message_data.get('data', {})
#
#             print(f"Received message: {message_data}")
#
#             if msg_type == 'control':
#                 action = msg_data.get('action')
#                 if action == 'start':
#                     settings = msg_data.get('settings', {})
#                     response = start_stream(device_id, settings)
#                 elif action == 'stop':
#                     response = stop_stream(device_id)
#                 elif action == 'resolution':
#                     resolution = msg_data.get('value')
#                     response = set_resolution(device_id, resolution)
#                 else:
#                     response = {"error": "Unknown action"}
#
#                 broadcast_to_device(device_id, json.dumps(response))
#             else:
#                 ws.send(json.dumps({"error": "Invalid message type"}))
#     finally:
#         websockets[device_id].remove(ws)
#         if not websockets[device_id]:
#             del websockets[device_id]
#
#
# def broadcast_to_device(device_id, message):
#     if device_id in websockets:
#         for ws in websockets[device_id]:
#             ws.send(message)
#
#
# def start_stream(device_id, settings):
#     if device_id not in registered_devices:
#         return {"error": f"Device not registered {registered_devices}"}
#
#     stream_uuid = str(uuid.uuid4())
#     stream_name = f'stream-{stream_uuid}'
#
#     try:
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
#             streams[device_id] = stream_data['liveStreamId']
#             stream_key = stream_data['streamKey']
#             print(f"Stream started: {stream_data}")
#             settings["streamKey"] = stream_key
#             settings["stream_data"] = stream_data
#             return {"type": "control", "data": {"action": "start", "settings": {"resolution": settings.get("resolution"), "streamKey": stream_key, "stream_data": stream_data}}}
#         else:
#             return {"error": "Failed to start stream", "details": response.json()}
#     except requests.exceptions.RequestException as e:
#         return {"error": "An error occurred while starting the stream", "details": str(e)}
#
#
# def stop_stream(device_id):
#     if device_id not in registered_devices:
#         return {"error": "Device not registered"}
#
#     stream_id = streams.get(device_id)
#     if not stream_id:
#         return {"error": "No stream found for this device"}
#
#     try:
#         response = requests.delete(
#             f'{API_VIDEO_BASE_URL}/live-streams/{stream_id}',
#             headers=headers,
#             verify=False
#         )
#
#         if response.status_code == 204:
#             del streams[device_id]
#             print(f"Stream stopped for device: {device_id}")
#             return {"type": "control", "data": {"action": "stop"}}
#         else:
#             return {"error": "Failed to stop stream", "details": response.json()}
#     except requests.exceptions.RequestException as e:
#         return {"error": "An error occurred while stopping the stream", "details": str(e)}
#
#
# def set_resolution(device_id, resolution):
#     try:
#         if resolution is None:
#             return {"error": "Resolution value is required"}
#
#         message = {
#             "type": "control",
#             "data": {
#                 "action": "resolution",
#                 "value": resolution
#             }
#         }
#         broadcast_to_device(device_id, json.dumps(message))
#         print(f"Resolution set to: {resolution}")
#         return message
#     except Exception as e:
#         return {"error": "Failed to set resolution", "details": str(e)}
#
#
# @app.route('/streams', methods=['GET'])
# def streams_page():
#     global registered_devices
#     try:
#         streams_list = [{"device_id": device_id} for device_id in registered_devices]
#         return render_template('streams.html', streams=streams_list)
#     except requests.exceptions.RequestException as e:
#         return render_template('error.html', message=str(e))
#
#
# @app.route('/watch-stream/<device_id>', methods=['GET'])
# def watch_stream_page(device_id):
#     return render_template('watch.html', device_id=device_id)
#
#
# @app.route('/devices', methods=['GET'])
# def get_devices():
#     devices = []
#     for device_id in registered_devices:
#         devices.append({
#             "device_id": device_id,
#             "online": device_id in websockets and len(websockets[device_id]) > 0
#         })
#     return jsonify(devices), 200
#
#
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sock import Sock
import requests
import uuid
import ssl
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
sock = Sock(app)

API_VIDEO_KEY = 'BQgyhs1lkAsktewRaHMFAGPtsMahfdaYJ4bISSwtkQF'
API_VIDEO_BASE_URL = 'https://ws.api.video'

headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + API_VIDEO_KEY,
    'Content-Type': 'application/json'
}

ssl_context = ssl._create_unverified_context()

registered_devices = set()
streams = {}
websockets = {}


@app.route('/register', methods=['POST'])
def register_device():
    data = request.json
    device_id = str(data.get('device_id'))

    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    if device_id not in registered_devices:
        registered_devices.add(device_id)
        return jsonify({"status": "device registered"}), 201
    else:
        return jsonify({"status": "device already registered"}), 200


@sock.route('/<device_id>')
def websocket(ws, device_id):
    global registered_devices, streams, websockets

    if device_id not in registered_devices:
        ws.send(json.dumps({"error": "Device not registered"}))
        return

    if device_id not in websockets:
        websockets[device_id] = set()

    websockets[device_id].add(ws)
    print(f"WebSocket connected: {device_id}")

    try:
        while True:
            message = ws.receive()
            if not message:
                continue

            try:
                message_data = json.loads(message)
            except json.JSONDecodeError:
                ws.send(json.dumps({"error": "Invalid JSON format"}))
                continue

            msg_type = message_data.get('type')
            msg_data = message_data.get('data', {})

            print(f"Received message: {message_data}")

            if msg_type == 'control':
                action = msg_data.get('action')
                if action == 'start':
                    settings = msg_data.get('settings', {})
                    response = start_stream(device_id, settings)
                elif action == 'stop':
                    response = stop_stream(device_id)
                elif action == 'resolution':
                    resolution = msg_data.get('value')
                    response = set_resolution(device_id, resolution)
                else:
                    response = {"error": "Unknown action"}

                broadcast_to_device(device_id, json.dumps(response))
            else:
                ws.send(json.dumps({"error": "Invalid message type"}))
    finally:
        websockets[device_id].remove(ws)
        if not websockets[device_id]:
            del websockets[device_id]


def broadcast_to_device(device_id, message):
    if device_id in websockets:
        sent_to = []
        for ws in websockets[device_id]:
            print(ws)
            if ws not in sent_to:
                ws.send(message)
                sent_to.append(ws)


def start_stream(device_id, settings):
    if device_id not in registered_devices:
        return {"error": f"Device not registered {registered_devices}"}

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
            stream_key = stream_data['streamKey']
            print(f"Stream started: {stream_data}")
            settings["streamKey"] = stream_key
            settings["stream_data"] = stream_data
            return {"type": "control", "data": {"action": "start", "settings": {"resolution": settings.get("resolution"), "streamKey": stream_key, "stream_data": stream_data}}}
        else:
            return {"error": "Failed to start stream", "details": response.json()}
    except requests.exceptions.RequestException as e:
        return {"error": "An error occurred while starting the stream", "details": str(e)}


def stop_stream(device_id):
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
            print(f"Stream stopped for device: {device_id}")
            return {"type": "control", "data": {"action": "stop"}}
        else:
            return {"error": "Failed to stop stream", "details": response.json()}
    except requests.exceptions.RequestException as e:
        return {"error": "An error occurred while stopping the stream", "details": str(e)}


def set_resolution(device_id, resolution):
    try:
        if resolution is None:
            return {"error": "Resolution value is required"}

        message = {
            "type": "control",
            "data": {
                "action": "resolution",
                "value": resolution
            }
        }
        # broadcast_to_device(device_id, json.dumps(message))
        print(f"Resolution set to: {resolution}")
        return message
    except Exception as e:
        return {"error": "Failed to set resolution", "details": str(e)}


@app.route('/streams', methods=['GET'])
def streams_page():
    global registered_devices
    try:
        streams_list = [{"device_id": device_id} for device_id in registered_devices]
        return render_template('streams.html', streams=streams_list)
    except requests.exceptions.RequestException as e:
        return render_template('error.html', message=str(e))


@app.route('/watch-stream/<device_id>', methods=['GET'])
def watch_stream_page(device_id):
    return render_template('watch.html', device_id=device_id)


@app.route('/devices', methods=['GET'])
def get_devices():
    devices = []
    for device_id in registered_devices:
        devices.append({
            "device_id": device_id,
            "online": device_id in websockets and len(websockets[device_id]) > 0
        })
    return jsonify(devices), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

