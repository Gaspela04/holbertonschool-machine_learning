#!/usr/bin/env python3
"""
Pipeline
"""

import tensorflow.compat.v2 as tf


def create_masks(inputs, target):
    """
    inputs is a tf.Tensor of shape (batch_size, seq_len_in) that contains the
    input sentence
    target is a tf.Tensor of shape (batch_size, seq_len_out) that contains the
    target sentence
    """
    encoder_mask = tf.cast(tf.math.equal(inputs, 0), tf.float32)
    encoder_mask = encoder_mask[:, tf.newaxis, tf.newaxis, :]
    decoder_mask = tf.cast(tf.math.equal(inputs, 0), tf.float32)
    decoder_mask = decoder_mask[:, tf.newaxis, tf.newaxis, :]

    size = target.shape[1]

    look_ahead_mask = 1 - tf.linalg.band_part(tf.ones((size, size)), -1, 0)
    decoder_target = tf.cast(tf.math.equal(target, 0), tf.float32)
    decoder_target = decoder_target[:, tf.newaxis, tf.newaxis, :]
    combined_mask = tf.maximum(decoder_target, look_ahead_mask)

    return (encoder_mask, combined_mask, decoder_mask)
