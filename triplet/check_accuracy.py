#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy as np
import model as M
import os


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
    avg_min_dist = 100

    # Loop over the database dictionary's names and encodings.
    for (name, db_encodings) in database.items():
        dist = 0
        avg_dist = 0
        for db_encoding in db_encodings:
            # Compute L2 distance between the target "encoding" and the current "emb" from the database.
            dist = np.linalg.norm(db_encoding - encoding)
            # print('distance: %f' % dist)
            if dist < min_dist:
                min_dist = dist
                identity = name
            avg_dist += dist

        # Average distance
        avg_dist = avg_dist / len(db_encodings)
        # print('average distance: %f' % avg_dist)
        # If this distance is less than the min_dist, then set min_dist to dist, and identity to name.
        if avg_dist < avg_min_dist:
            avg_min_dist = avg_dist
            avg_identity = name

    return min_dist, avg_min_dist, identity, avg_identity


def main(args):
    members = args.members
    faces = args.faces
    thold = args.thold
    db_images = "registered_images/"

    FRmodel = M.inc_v2.faceRecoModel(input_shape=(3, 96, 96))
    M.load_weights_from_FaceNet(FRmodel)

    database = {}
    for member in members:
        member_list = []
        for x in os.listdir(db_images):
            path = db_images + x
            if os.path.isfile(path) and (member in x):
                member_list.append(M.img_to_encoding(path, FRmodel))
        database[member] = member_list

    for face in faces:
        filename = "accuracy_check/" + face + ".png"

        min_dist, avg_min_dist, identity, avg_identity = who_is_it(filename, database, FRmodel)
        print('\nface of %s' % face)
        print('Single minimum distance: %f, Single identity: %s' % (min_dist, identity))
        print('Average minimum distance: %f, Average identity: %s' % (avg_min_dist, avg_identity))
        if (min_dist + avg_min_dist) < thold:
            print("It's %s!" % avg_identity)
        else:
            print("It doesn't match anybody.")
        print('----------')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--members', type=str, nargs='+')
    parser.add_argument('--faces', type=str, nargs='+')
    parser.add_argument('--thold', type=float, default=1.4)
    arguments = parser.parse_args()
    main(arguments)
