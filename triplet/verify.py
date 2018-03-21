#!/usr/bin/env python
# -*- coding: utf-8 -*-


import model as M
import argparse
import tensorflow as tf
import numpy as np
# import time


def triplet_loss(y_true, y_pred, alpha = 0.2):
    """
    Implementation of the triplet loss

    Arguments:
    y_true -- true labels, required when you define a loss in Keras, you don't need it in this function.
    y_pred -- python list containing three objects:
            anchor -- the encodings for the anchor images, of shape (None, 128)
            positive -- the encodings for the positive images, of shape (None, 128)
            negative -- the encodings for the negative images, of shape (None, 128)

    Returns:
    loss -- real number, value of the loss
    """

    anchor, positive, negative = y_pred[0], y_pred[1], y_pred[2]

    # Compute the (encoding) distance between the anchor and the positive.
    pos_dist = tf.reduce_sum(tf.square(tf.subtract(anchor, positive)), axis=-1)
    # Compute the (encoding) distance between the anchor and the negative.
    neg_dist = tf.reduce_sum(tf.square(tf.subtract(anchor, negative)), axis=-1)
    # Subtract the two previous distances and add alpha.
    basic_loss = tf.add(tf.subtract(pos_dist, neg_dist), alpha)
    # Take the maximum of basic_loss and 0.0. Sum over the training examples.
    loss = tf.reduce_sum(tf.maximum(basic_loss, 0.0))

    return loss


def verify(image_path, identity, database, model):
    """
    Function that verifies if the person on the "image_path" image is "identity".

    Arguments:
    image_path -- path to an image
    identity -- string, name of the person you'd like to verify the identity. Has to be a resident of the Happy house.
    database -- python dictionary mapping names of allowed people's names (strings) to their encodings (vectors).
    model -- your Inception model instance in Keras

    Returns:
    dist -- distance between the image_path and the image of "identity" in the database.
    """

    # Compute the encoding for the image.
    encoding = M.img_to_encoding(image_path, model)

    # Compute distance with identity's image
    dist = np.linalg.norm(database[identity] - encoding)

    return dist


def main(args):
    identity = args.identity
    image = args.image
    people = args.people
    dist_thold = args.dist_thold

    FRmodel = M.inc_v2.faceRecoModel(input_shape=(3, 96, 96))
    # print("Total Params:", FRmodel.count_params())
    # FRmodel.compile(optimizer = 'adam', loss = triplet_loss, metrics = ['accuracy'])
    # start_time = time.time()
    M.load_weights_from_FaceNet(FRmodel)
    # elapsed_time = time.time() - start_time
    # print("Elapsed time(load weights):{0}".format(elapsed_time) + "[sec]")

    database = {}
    # start_time = time.time()
    for person in people:
        path = "registered_images/" + person + ".png"
        database[person] = M.img_to_encoding(path, FRmodel)
    # elapsed_time = time.time() - start_time
    # print("Elapsed time(make database):{0}".format(elapsed_time) + "[sec]")

    # start_time = time.time()
    distance = verify(image, identity, database, FRmodel)

    if distance < dist_thold:
        print("It's %s. Distance: %f" % (str(identity), distance))
    else:
        print("It's NOT %s. Distance: %f" % (str(identity), distance))
    # elapsed_time = time.time() - start_time
    # print("Elapsed time(compute distance and judge):{0}".format(elapsed_time) + "[sec]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--identity', type=str)
    parser.add_argument('--dist-thold', type=float, default=0.6)
    parser.add_argument('--image', type=str)
    parser.add_argument('--people', type=str, nargs='+')
    arguments = parser.parse_args()
    main(arguments)
