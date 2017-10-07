#!/usr/bin/env python
# -*- coding: utf-8 -*-

import http.client
import urllib.request, urllib.parse, urllib.error
import base64
import json
import sys
import argparse

def main(args):
    headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': args.key
    }

    personGroupId = args.group_id
    body = ""

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("GET", "/face/v1.0/persongroups/%s/persons" % personGroupId, body, headers)
        response = conn.getresponse()

        print(response.status, response.reason)
        res_body = response.read()
        for person in json.loads(res_body):
            print(person)

        conn.close()
    except Exception as e:
        print(e.args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--group_id', type=str, default='me_counter_group_id')
    parser.add_argument('--key', type=str, default='cddfbe29b3b84bef974323d654a90685')
    arguments = parser.parse_args()
    main(arguments)
