import dlib
from PIL import Image
from skimage import io
import boto3

bucket_name = 'bucket-cloud-photo'
session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net'
)

# Create client
mq = boto3.client(
    service_name='sqs',
    endpoint_url='https://message-queue.api.cloud.yandex.net'
)

from flask import Flask

app = Flask(__name__)


def detect_faces(image):
    # Create a face detector
    face_detector = dlib.get_frontal_face_detector()

    # Run detector and get bounding boxes of the faces on image.
    detected_faces = face_detector(image, 1)
    face_frames = [(x.left(), x.top(),
                    x.right(), x.bottom()) for x in detected_faces]

    return face_frames


def crop_faces():
    pictures = []
    for key in s3.list_objects(Bucket=bucket_name)['Contents']:
        pictures.append(key['Key'])

    for picture in pictures:
        # Load image
        get_object_response = s3.get_object(Bucket=bucket_name, Key=picture)
        img = get_object_response['Body'].read()
        out_file = open(picture, "wb")  # open for [w]riting as [b]inary
        out_file.write(img)
        out_file.close()
        image = io.imread(picture)

        # Detect faces
        detected_faces = detect_faces(image)

        # Crop faces and plot
        for n, face_rect in enumerate(detected_faces):
            if 'face' not in picture:
                name = picture.split(".")[0] + "_" + "face" + n.__str__() + ".jpg"
                if name not in pictures:
                    face = Image.fromarray(image).crop(face_rect)
                    face.save(name)
                    s3.upload_file(name, bucket_name, picture.split(".")[0] + "_" + "face" + n.__str__() + ".jpg")
                    mq.send_message(
                        QueueUrl='https://message-queue.api.cloud.yandex.net/b1gs4a51unfsngpt0hke/dj60000000046uo806dt/queue-21-37',
                        MessageBody=name
                    )


@app.route('/')
def hello_world():
    crop_faces()
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
