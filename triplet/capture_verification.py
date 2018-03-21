#!/usr/bin/env python
# -*- coding: utf-8 -*-


import cv2
import argparse
import random
import numpy as np
import model as M

KEY_Q = 113
# DOOR_UPPER_LEFT = (240, 100)
# DOOR_LOWER_RIGHT = (440, 300)

DOOR_UPPER_LEFT = (400, 250)
DOOR_LOWER_RIGHT = (1000, 650)
DETECTION_FREQUENCY = 10


def random_string(length=5, seq="0123456789abcdefghijklmnopqrstuvwxyz"):
    sr = random.SystemRandom()
    return ''.join([sr.choice(seq) for i in range(length)])


def verify(image_path, identity, database, model):
    """
    Function that verifies if the person on the "image_path" image is "identity".

    Arguments:
    image_path -- path to an image
    identity -- string, name of the person you'd like to verify the identity. Has to be a resident of the Happy house.
    database -- python dictionary mapping names of allowed people's names (strings) to their encodings (vectors).
    model -- the Inception model instance in Keras

    Returns:
    dist -- distance between the image_path and the image of "identity" in the database.
    """

    # Compute the encoding for the image.
    encoding = M.img_to_encoding(image_path, model)

    # Compute distance with identity's image
    dist = np.linalg.norm(database[identity] - encoding)

    return dist


def main(args):
    url = args.url
    sf = args.sf
    mn = args.mn
    identity = args.identity
    members = args.members
    dist_thold = args.dist_thold

    FRmodel = M.inc_v2.faceRecoModel(input_shape=(3, 96, 96))
    M.load_weights_from_FaceNet(FRmodel)

    database = {}
    for member in members:
        path = "registered_images/" + member + ".png"
        database[member] = M.img_to_encoding(path, FRmodel)

    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        print("Can not open the video stream.")
        return

    cv2.namedWindow("Web camera", cv2.WINDOW_NORMAL)
    face_cascade = cv2.CascadeClassifier("/usr/local/Cellar/opencv/3.4.0/share/OpenCV/haarcascades/haarcascade_frontalface_alt.xml")
    frequency = DETECTION_FREQUENCY

    while(True):
        key = cv2.waitKey(50)
        # print(key)
        if key == KEY_Q:
            break

        ret, frame = cap.read()
        cv2.rectangle(frame, DOOR_UPPER_LEFT, DOOR_LOWER_RIGHT, color=(0, 0, 255), thickness=3)
        frequency -= 1
        if frequency == 0:
            frequency = DETECTION_FREQUENCY
            gray = cv2.cvtColor(frame[DOOR_UPPER_LEFT[1]:DOOR_LOWER_RIGHT[1], DOOR_UPPER_LEFT[0]:DOOR_LOWER_RIGHT[0]], cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, sf, mn)
            for face in faces:
                face_upper_left = (face[0]+DOOR_UPPER_LEFT[0], face[1]+DOOR_UPPER_LEFT[1])
                face_lower_right = (face[0]+face[2]+DOOR_UPPER_LEFT[0], face[1]+face[3]+DOOR_UPPER_LEFT[1])
                cv2.rectangle(frame, face_upper_left, face_lower_right, color=(0, 255, 0), thickness=2)
                filename = "snapshots/" + random_string() + ".png"
                cv2.imwrite(filename, frame[face_upper_left[1]:face_lower_right[1], face_upper_left[0]:face_lower_right[0]])

                distance = verify(filename, identity, database, FRmodel)
                if distance > dist_thold:
                    print("It's NOT %s(%s). Distance: %f" % (str(identity), filename, distance))
                else:
                    print("It's %s(%s). Distance: %f" % (str(identity), filename, distance))

        cv2.imshow("Web camera", frame)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str)
    parser.add_argument('--sf', type=float, default=1.10, help="scaleFactor")
    parser.add_argument('--mn', type=int, default=3, help="minNeighbors")
    parser.add_argument('--identity', type=str)
    parser.add_argument('--dist-thold', type=float, default=0.6)
    parser.add_argument('--members', type=str, nargs='+')
    arguments = parser.parse_args()
    main(arguments)
