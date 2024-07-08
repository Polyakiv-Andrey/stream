import json
import csv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sock import Sock
import requests
import uuid
import os
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
                response = set_resolution(ws, msg_data.get('resolution'))
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


def set_resolution(ws, resolution):
    try:
        message = {
            "type": "control",
            "data": {
                "value": "resolution",
                "resolution": resolution
            }
        }
        ws.send(json.dumps(message))
        return {"status": "resolution set", "resolution": resolution}
    except Exception as e:
        return {"error": "Failed to set resolution", "details": str(e)}


@app.route('/streams', methods=['GET'])
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
def watch_stream_page(device_id):
    return render_template('watch.html', device_id=device_id)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
