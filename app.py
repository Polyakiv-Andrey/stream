import cv2
from flask import Flask, Response, jsonify, render_template
import threading
import uuid

from services import find_working_camera

app = Flask(__name__)
streams = {}


@app.route('/start_stream', methods=['POST'])
def start_stream():
    user_id = str(uuid.uuid4())

    if user_id not in streams:
        streams[user_id] = {'cap': None, 'is_streaming': False}

    if not streams[user_id]['is_streaming']:
        camera_index = find_working_camera()
        if camera_index is None:
            return "Cannot open stream", 500
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            return "Cannot open stream", 500
        streams[user_id]['cap'] = cap
        streams[user_id]['is_streaming'] = True
        threading.Thread(target=generate_frames, args=(user_id,)).start()

    return jsonify({'message': 'Stream started', 'uuid': user_id}), 200


@app.route('/video_feed/<user_id>')
def video_feed(user_id):
    if user_id not in streams or not streams[user_id]['is_streaming']:
        return "Stream is not started", 404
    return Response(generate(user_id), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/start_stream_page')
def start_stream_page():
    return render_template('startStream.html')


@app.route('/view_stream_page')
def view_stream_page():
    return render_template('watchStream.html')


def generate(user_id):
    cap = streams[user_id]['cap']
    while streams[user_id]['is_streaming']:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        print("Frame captured")
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Failed to encode frame")
            break
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        print("Frame sent")


def generate_frames(user_id):
    cap = streams[user_id]['cap']
    while streams[user_id]['is_streaming']:
        ret, frame = cap.read()
        if not ret:
            streams[user_id]['is_streaming'] = False
            break


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
