#!/usr/bin/env python
# -*- coding: utf-8 -*-

import http.client
import urllib.request, urllib.parse, urllib.error
import base64
import sys
import argparse

def main(args):
    headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': args.key,
            'cache-control': 'no-cache'
    }

    personGroupId = args.group_id
    personId = args.person_id

    body = ("{'url':'%s'}" % args.image_url)

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/%s/persons/%s/persistedFaces" % (personGroupId, personId), body, headers)
        response = conn.getresponse()

        print(response.status, response.reason)
        res_body = response.read()
        print(res_body)

        conn.close()
    except Exception as e:
        print(e.args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--group_id', type=str, default='me_counter_group_id')
    parser.add_argument('--person_id', type=str)
    parser.add_argument('--key', type=str, default='cddfbe29b3b84bef974323d654a90685')
    parser.add_argument('--image_url', type=str)
    arguments = parser.parse_args()
    main(arguments)
