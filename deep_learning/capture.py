#!/usr/bin/env python
# -*- coding: utf-8 -*-


import cv2
import argparse

KEY_Q = 113


def main(args):
    cap = cv2.VideoCapture(args.url)

    if not cap.isOpened():
        print("Can not open the video stream.")
        return

    while(True):
        ret, frame = cap.read()

        cv2.imshow("Webcam", frame)

        key = cv2.waitKey(1)
        if key == KEY_Q:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str)
    arguments = parser.parse_args()
    main(arguments)
