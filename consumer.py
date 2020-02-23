import datetime
from flask import Flask, Response
from kafka import KafkaConsumer


# Start consumer.py
topic = "kafka_video"

consumer = KafkaConsumer(
    topic,
    bootstrap_servers = ['127.0.0.1:9092']
)

# Get The Flask App Ready for view

app = Flask(__name__)
@app.route('/video', methods=['GET'])

def video():
    return Response(
        get_video_stream(),
        mimetype = 'multipart/x-mixed-replace; boundary=frame')

def get_video_stream():
    for msg in consumer:
        yield(b'--frame\r\n'
              b'Content-Type: image/jpg\r\n\r\n' + msg.value + b'\r\n\r\n')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)