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


def who_is_it(image_path, database, model):
    """
    Find who is the person on the image_path image.

    Arguments:
    image_path -- path to an image
    database -- database containing image encodings along with the name of the person on the image
    model -- the Inception model instance in Keras

    Returns:
    min_dist -- the minimum distance between image_path encoding and the encodings from the database
    identity -- string, the name prediction for the person on image_path
    """

    # Compute the target "encoding" for the image.
    encoding = M.img_to_encoding(image_path, model)

    # Initialize "min_dist" to a large value, say 100.
    min_dist = 100

    # Loop over the database dictionary's names and encodings.
    for (name, db_enc) in database.items():

        # Compute L2 distance between the target "encoding" and the current "emb" from the database.
        dist = np.linalg.norm(db_enc - encoding)

        # If this distance is less than the min_dist, then set min_dist to dist, and identity to name.
        if dist < min_dist:
            min_dist = dist
            identity = name

    return min_dist, identity


def main(args):
    url = args.url
    sf = args.sf
    mn = args.mn
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

                min_dist, identity = who_is_it(filename, database, FRmodel)
                if min_dist > 1:
                    print ("Sorry... Who is it(%s)." % (filename))
                    cv2.putText(frame, "Who is it", (face_upper_left[0], face_upper_left[1]-12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    cv2.imshow("Who is it", frame)
                elif min_dist > dist_thold:
                    print ("Not sure... It might be %s(%s). Distance: %f" % (identity, filename, min_dist))
                    cv2.putText(frame, "Maybe... " + identity, (face_upper_left[0], face_upper_left[1]-12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    cv2.imshow("Maybe... " + identity, frame)
                else:
                    print ("It's %s(%s). Distance: %f" % (identity, filename, min_dist))
                    cv2.putText(frame, identity, (face_upper_left[0], face_upper_left[1]-12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    cv2.imshow(identity, frame)

        cv2.imshow("Web camera", frame)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str)
    parser.add_argument('--sf', type=float, default=1.10, help="scaleFactor")
    parser.add_argument('--mn', type=int, default=3, help="minNeighbors")
    parser.add_argument('--dist-thold', type=float, default=0.6)
    parser.add_argument('--members', type=str, nargs='+')
    arguments = parser.parse_args()
    main(arguments)
