#!/usr/bin/env python
# -*- coding: utf-8 -*-

import http.client
import urllib.request, urllib.parse, urllib.error
import base64
import sys
import json
import argparse

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
            'returnFaceAttributes': 'age,gender'
    })

    f = open(image, "rb")
    body = f.read()
    f.close

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/detect?%s" % params, body, headers)
        response = conn.getresponse()
        faceId = ""
        gender = ""
        age = ""
        if response.status == 200:
            res_body = response.read().decode("utf-8")
            results = json.loads(res_body)
            if results:
                # Get faceId
                faceId = results[0]["faceId"]
                # Get gender
                gender = results[0]["faceAttributes"]["gender"]
                # Get age
                age = results[0]["faceAttributes"]["age"]
            else:
                print("No face detected.")
        else:
            print("detect_face")
            print(response.status, response.reason)
        conn.close()
        return faceId, gender, age
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
    faceId, gender, age = detect_face(args.key, args.image_file)

    if faceId:
        candidate = identify_person(args.key, faceId, args.group_id)
        if candidate:
            personId = candidate[0]["personId"]
            person_name = get_person(args.key, personId, args.group_id)
            print("Detected person is '%s', Confidence: %f" % (person_name, candidate[0]["confidence"]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--group_id', type=str, default='me_counter_group_id')
    parser.add_argument('--key', type=str, default='cddfbe29b3b84bef974323d654a90685')
    parser.add_argument('--image_file', type=str)
    arguments = parser.parse_args()
    main(arguments)
