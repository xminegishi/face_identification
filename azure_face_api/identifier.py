#!/usr/bin/env python
# -*- coding: utf-8 -*-


import cv2
import argparse
import http.client
import urllib.request, urllib.parse, urllib.error
import base64
import sys
import json

KEY_Q = 113
if sys.platform == "darwin":
    ENTER = 13
elif "linux" in sys.platform:
    ENTER = 10


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
        faceRecs = list()
        faceIds = list()
        genders = list()
        ages = list()
        emotions = list()
        if response.status == 200:
            res_body = response.read().decode("utf-8")
            results = json.loads(res_body)
            if results:
                for result in results:
                    # Get faceId
                    faceIds.append(result["faceId"])
                    # Get faceRectangle
                    faceRecs.append(result["faceRectangle"])
                    # Get gender
                    genders.append(result["faceAttributes"]["gender"])
                    # Get age
                    ages.append(result["faceAttributes"]["age"])
                    # Get emotion
                    emotions.append(result["faceAttributes"]["emotion"])
            else:
                print("No face detected.")
        else:
            print("detect_face")
            print(response.status, response.reason)
        conn.close()
        return faceIds, faceRecs, genders, ages, emotions
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
    cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
    face_cascade = cv2.CascadeClassifier("/usr/local/Cellar/opencv/3.4.0/share/OpenCV/haarcascades/haarcascade_frontalface_alt2.xml")
    # eye_cascade = cv2.CascadeClassifier("/usr/local/Cellar/opencv/3.2.0/share/OpenCV/haarcascades/haarcascade_eye.xml")
    detect_counter = 0

    while(True):
        key = cv2.waitKey(1)
        # print(key)
        if key == KEY_Q:
            break

        ret, frame = cap.read()
        if args.flip:
            frame = cv2.flip(frame, -1)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray)
        for face in faces:
            cv2.rectangle(frame, tuple([face[0], face[1]]), tuple([face[0]+face[2], face[1]+face[3]]), (0, 255, 0))
        # eyes = eye_cascade.detectMultiScale(gray)
        # for eye in eyes:
        #     cv2.rectangle(frame, tuple([eye[0], eye[1]]), tuple([eye[0]+eye[2], eye[1]+eye[3]]), (0, 255, 0))
        cv2.imshow("Webcam", frame)
        # continue

        if len(faces) == 0:
            detect_counter = 0
        else:
            detect_counter += 1
            if detect_counter < 10: continue
            detect_counter = 0
            filename = "snapshots/" + str(img_id) + ".png"
            cv2.imwrite(filename, frame)
            img_id += 1

            faceIds, faceRecs, genders, ages, emotions = detect_face(args.key, filename)

            for index, faceId in enumerate(faceIds):
                top_left = (faceRecs[index]["left"], faceRecs[index]["top"])
                bottom_right = (top_left[0]+faceRecs[index]["width"], top_left[1]+faceRecs[index]["height"])
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0))
                person_name = "Sorry... Who is it?"
                candidate = identify_person(args.key, faceId, args.group_id)
                if candidate:
                    personId = candidate[0]["personId"]
                    person_name = get_person(args.key, personId, args.group_id)
                    confidence = candidate[0]["confidence"]
                    print("Detected person is '%s', Confidence: %f" % (person_name, confidence))
                    prob = "Confidence: " + str(confidence)
                    cv2.putText(frame, prob, (top_left[0], top_left[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, person_name, (top_left[0], top_left[1]-18), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))

                gender = ("gender: %s" % genders[index])
                age = ("age: %s" % ages[index])
                happiness = ("happiness: %s" % emotions[index]["happiness"])
                anger = ("anger: %s" % emotions[index]["anger"])
                sadness = ("sadness: %s" % emotions[index]["sadness"])
                fear = ("fear: %s" % emotions[index]["fear"])
                surprise =  ("surprise: %s" % emotions[index]["surprise"])
                neutral = ("neutral: %s" % emotions[index]["neutral"])
                cv2.putText(frame, gender, (top_left[0], bottom_right[1]+10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, age, (top_left[0]+100, bottom_right[1]+10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, happiness, (top_left[0], bottom_right[1]+22), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, anger, (top_left[0], bottom_right[1]+34), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, sadness, (top_left[0], bottom_right[1]+46), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, fear, (top_left[0], bottom_right[1]+58), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, surprise, (top_left[0], bottom_right[1]+70), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
                cv2.putText(frame, neutral, (top_left[0], bottom_right[1]+82), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0))
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
