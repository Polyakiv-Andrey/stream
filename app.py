from flask import Flask, jsonify, render_template, request
import uuid

app = Flask(__name__)
streams = {}

@app.route('/start_stream', methods=['POST'])
def start_stream():
    user_id = str(uuid.uuid4())
    streams[user_id] = {'is_streaming': True, 'sdp': None}
    return jsonify({'message': 'Stream started', 'uuid': user_id}), 200

@app.route('/offer', methods=['POST'])
def offer():
    data = request.json
    stream_id = data['streamId']
    streams[stream_id]['sdp'] = data['sdp']
    return jsonify({}), 200

@app.route('/offer/<stream_id>', methods=['GET'])
def get_offer(stream_id):
    if stream_id not in streams or not streams[stream_id]['is_streaming']:
        return "Stream is not started", 404
    return jsonify(streams[stream_id]['sdp'])

@app.route('/answer', methods=['POST'])
def answer():
    data = request.json
    stream_id = data['streamId']
    # Зберігаємо SDP відповіді для подальшого використання
    streams[stream_id]['answer'] = data['sdp']
    return jsonify({}), 200

@app.route('/ice_candidate', methods=['POST'])
def ice_candidate():
    candidate = request.json
    # Обробка ICE кандидата (можна додати до відповідного стріму)
    return '', 204

@app.route('/start_stream_page')
def start_stream_page():
    return render_template('startStream.html')

@app.route('/view_stream_page')
def view_stream_page():
    return render_template('watchStream.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
