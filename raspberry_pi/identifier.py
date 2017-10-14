#!/usr/bin/env python
# -*- coding: utf-8 -*-


import cv2
import argparse
import http.client
import urllib.request, urllib.parse, urllib.error
import base64
import sys
import json


def detect_face(key, image):
    headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Content-Type': 'application/octet-stream',
            'cache-control': 'no-cache'
    }

    params = urllib.parse.urlencode({
            # Request parameters
            'returnFaceId': 'ture',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender,emotion'
    })

    f = open(image, "rb")
    body = f.read()
    f.close

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/detect?%s" % params, body, headers)
        response = conn.getresponse()
        faceRec = dict()
        faceId = ""
        gender = ""
        age = ""
        emotion = dict()
        if response.status == 200:
            res_body = response.read().decode("utf-8")
            results = json.loads(res_body)
            if results:
                # Get faceRectangle
                faceRec = results[0]["faceRectangle"]
                # Get faceId
                faceId = results[0]["faceId"]
                # Get gender
                gender = results[0]["faceAttributes"]["gender"]
                # Get age
                age = results[0]["faceAttributes"]["age"]
                # Get emotion
                emotion = results[0]["faceAttributes"]["emotion"]
            else:
                print("No face detected.")
        else:
            print("detect_face")
            print(response.status, response.reason)
        conn.close()
        return faceRec, faceId, gender, age, emotion
    except Exception as e:
        print(e.args)
        raise

def identify_person(key, faceId, groupId):
    headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Content-Type': 'application/json'
    }

    body = ("{'personGroupId': '%s', 'faceIds': ['%s']}" % (groupId, faceId))

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/identify", body, headers)
        response = conn.getresponse()
        candidate = None
        if response.status == 200:
            res_body = response.read().decode("utf-8")
            results = json.loads(res_body)
            candidate = results[0]["candidates"]
            if not candidate:
                print("No candidate.")
        else:
            print("identify_person")
            print(response.status, response.reason)
        conn.close()
        return candidate
    except Exception as e:
        print(e.args)
        raise

def get_person(key, personId, groupId):
    headers = {'Ocp-Apim-Subscription-Key': key}

    body = ""

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("GET", "/face/v1.0/persongroups/%s/persons/%s" % (groupId, personId), body, headers)
        response = conn.getresponse()
        person_name = ""
        if response.status == 200:
            res_body = response.read().decode("utf-8")
            results = json.loads(res_body)
            person_name = results["name"]
        else:
            print("get_person")
            print(response.status, response.reason)
        conn.close()
        return person_name
    except Exception as e:
        print(e.args)


def main(args):
    cap = cv2.VideoCapture(0)
    img_id = 0
    cv2.namedWindow("Web camera", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Web camera", 640, 480)

    while(True):
        ret, frame = cap.read()
        if args.flip:
            frame = cv2.flip(frame, -1)
        cv2.imshow("Web camera", frame)

        key = cv2.waitKey(1)
        if key == 27:# Escape
            break
        elif key == 10:# Enter
            filename = "snapshots/" + str(img_id) + ".png"
            cv2.imwrite(filename, frame)
            img_id += 1

            faceRec, faceId, gender, age, emotion = detect_face(args.key, filename)

            if faceId:
                top_left = (faceRec["left"], faceRec["top"])
                bottom_right = (top_left[0]+faceRec["width"], top_left[1]+faceRec["height"])
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0))
                person_name = "Sorry... Who is it?"
                candidate = identify_person(args.key, faceId, args.group_id)
                if candidate:
                    personId = candidate[0]["personId"]
                    person_name = get_person(args.key, personId, args.group_id)
                    print("Detected person is '%s', Confidence: %f" % (person_name, candidate[0]["confidence"]))
                cv2.putText(frame, person_name, (top_left[0], top_left[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                happiness = ("happiness: %s" % emotion["happiness"])
                anger = ("anger: %s" % emotion["anger"])
                sadness = ("sadness: %s" % emotion["sadness"])
                fear = ("fear: %s" % emotion["fear"])
                surprise =  ("surprise: %s" % emotion["surprise"])
                neutral = ("neutral: %s" % emotion["neutral"])
                cv2.putText(frame, happiness, (top_left[0], bottom_right[1]+10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, anger, (top_left[0], bottom_right[1]+22), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, sadness, (top_left[0], bottom_right[1]+34), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, fear, (top_left[0], bottom_right[1]+46), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, surprise, (top_left[0], bottom_right[1]+58), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, neutral, (top_left[0], bottom_right[1]+70), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.imshow(str(img_id), frame)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--flip', action='store_true')
    parser.add_argument('--group_id', type=str, default='me_counter_group_id')
    parser.add_argument('--key', type=str)
    arguments = parser.parse_args()
    main(arguments)

