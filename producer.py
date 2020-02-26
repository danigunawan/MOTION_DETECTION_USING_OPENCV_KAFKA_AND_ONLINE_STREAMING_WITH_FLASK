import sys
import time
import cv2
from kafka import KafkaProducer
import numpy as np

# Codec Definition And Creation Of VideoWriter Object

fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out = cv2.VideoWriter('motiondetect.avi', fourcc, 60.0, (1920,1080),isColor=False)

# MOG2 Segmentation
foreground = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
topic = "kafka_video"


def publish_video(video_file):
    
    # run producer.py
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    # define VideoCapture
    cap = cv2.VideoCapture(video_file)
   
    print('publishing video...')

    while(cap.isOpened()):
        success, camframe = cap.read()

        # make sure it works
        if not success:
            print('bad read')
            break

        # Convert Image to JPG
        ret, buffer = cv2.imencode('.jpg', camframe)

        # Break them up into bytes for kafka

        producer.send(topic, buffer.tobytes())

        time.sleep(0.2)
    cap.release()
    print('end of stream')


def publish_camera():

    # Run producer.py
    producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    camera.set(cv2.CAP_PROP_FPS, 6)

    try:
        while(True):
            success, camframe = camera.read()
            grayframe = cv2.cvtColor(camframe, cv2.COLOR_BGR2GRAY)
            blurframe = cv2.GaussianBlur(camframe, (5, 5), 0)

            # Capture Motion
            motionframe = foreground.apply(grayframe)
            detect = (np.sum(motionframe))//255
            if detect>30:
                print ("Object in motion size = ", detect)
                # Save Stream to .avi .file
                out.write(grayframe)
            ret, buffer = cv2.imencode('.jpg', grayframe)
            producer.send(topic, buffer.tobytes())

            # Give Some time for processing
            time.sleep(0.2)
    except:
        print('\nWe are done.')
        sys.exit(1)

    camera.release()
    out.release()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        publish_video(video_path)
    else:
        print('We Are Live !')
publish_camera()
