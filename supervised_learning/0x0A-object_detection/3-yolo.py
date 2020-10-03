#!/usr/bin/env python3
"""
This file contain the Yolo class
"""
import tensorflow.keras as K
import numpy as np


class Yolo():
    """
    Yolo that uses the Yolo v3 algorithm to perform object detection
    """

    def __init__(self, model_path, classes_path, class_t, nms_t, anchors):
        """
        model: the Darknet Keras model
        class_names: a list of the class names for the model
        class_t: the box score threshold for the initial filtering step
        nms_t: the IOU threshold for non-max suppression
        anchors: the anchor boxes
        """
        self.model = K.models.load_model(model_path)
        with open(classes_path, 'r') as f:
            data = f.read()
        self.class_names = data.split()
        self.class_t = class_t
        self.nms_t = nms_t
        self.anchors = anchors

    def process_outputs(self, outputs, image_size):
        """
        Process Outputs
        :param outputs: is a list of numpy.ndarrays containing the predictions
        from the Darknet model for a single image
        :param image_size: is a numpy.ndarray containing the image’s original
        size [image_height, image_width]
        :return: tuple of (boxes, box_confidences, box_class_probs)
        """
        boxes = []
        box_confidences = []
        box_class_probs = []
        for i, output in enumerate(outputs):
            grid_height = output.shape[0]
            grid_width = output.shape[1]
            anchor_boxes = output.shape[2]
            boxs = output[..., :4]
            t_x = boxs[..., 0]
            t_y = boxs[..., 1]
            t_w = boxs[..., 2]
            t_h = boxs[..., 3]
            c_x = np.arange(grid_width).reshape(1, grid_width)
            c_x = np.repeat(c_x, grid_height, axis=0)
            c_x = np.repeat(c_x[..., np.newaxis], anchor_boxes, axis=2)
            c_y = np.arange(grid_width).reshape(1, grid_width)
            c_y = np.repeat(c_y, grid_height, axis=0).T
            c_y = np.repeat(c_y[..., np.newaxis], anchor_boxes, axis=2)
            b_x = (self.sigmoid(t_x) + c_x) / grid_width
            b_y = (self.sigmoid(t_y) + c_y) / grid_height
            anchor_width = self.anchors[i, :, 0]
            anchor_height = self.anchors[i, :, 1]
            image_width = self.model.input.shape[1].value
            image_height = self.model.input.shape[2].value
            b_w = (anchor_width * np.exp(t_w)) / image_width
            b_h = (anchor_height * np.exp(t_h)) / image_height
            x_1 = b_x - b_w / 2
            y_1 = b_y - b_h / 2
            x_2 = x_1 + b_w
            y_2 = y_1 + b_h
            x_1 *= image_size[1]
            y_1 *= image_size[0]
            x_2 *= image_size[1]
            y_2 *= image_size[0]
            boxs[..., 0] = x_1
            boxs[..., 1] = y_1
            boxs[..., 2] = x_2
            boxs[..., 3] = y_2
            boxes.append(boxs)
            box_confidence = output[..., 4:5]
            box_confidence = self.sigmoid(box_confidence)
            box_confidences.append(box_confidence)
            classes = output[..., 5:]
            classes = self.sigmoid(classes)
            box_class_probs.append(classes)

        return (boxes, box_confidences, box_class_probs)

    def sigmoid(self, array):
        """
        Sigmoid
        """
        return 1. / (1. + np.exp(-array))

    def filter_boxes(self, boxes, box_confidences, box_class_probs):
        """
        filtered_boxes: a numpy.ndarray of shape (?, 4) containing all of the
        filtered bounding boxes:
        box_classes: a numpy.ndarray of shape (?,) containing the class number
        that each box in filtered_boxes predicts, respectively
        box_scores: a numpy.ndarray of shape (?) containing the box scores
        for each box in filtered_boxes, respectively
        """
        box_scores = []
        box_classes = []
        filtered_boxes = []
        for i, (box_confidence, box_class_prob, box) in enumerate(
                zip(box_confidences, box_class_probs, boxes)):
            box_scores_per_ouput = box_confidence * box_class_prob
            max_box_scores = np.max(box_scores_per_ouput, axis=3)
            max_box_scores = max_box_scores.reshape(-1)
            max_box_classes = np.argmax(box_scores_per_ouput, axis=3)
            max_box_classes = max_box_classes.reshape(-1)
            box = box.reshape(-1, 4)
            index_list = np.where(max_box_scores < self.class_t)
            max_box_scores_filtered = np.delete(max_box_scores, index_list)
            max_box_classes_filtered = np.delete(max_box_classes, index_list)
            filtered_box = np.delete(box, index_list, axis=0)
            box_scores.append(max_box_scores_filtered)
            box_classes.append(max_box_classes_filtered)
            filtered_boxes.append(filtered_box)
        box_scores = np.concatenate(box_scores)
        box_classes = np.concatenate(box_classes)
        filtered_boxes = np.concatenate(filtered_boxes, axis=0)
        return (filtered_boxes, box_classes, box_scores)

    def non_max_suppression(self, filtered_boxes, box_classes, box_scores):
        """
        box_predictions: a numpy.ndarray of shape (?, 4) containing all of the
        predicted bounding boxes ordered by class and box score
        predicted_box_classes: a numpy.ndarray of shape (?,) containing the
        class number for box_predictions ordered by class and box score,
        respectively
        predicted_box_scores: a numpy.ndarray of shape (?) containing the
        box scores for box_predictions ordered by class and box score,
        srespectively
        """
        box_predictions = []
        predicted_box_classes = []
        predicted_box_scores = []
        for box_class in np.unique(box_classes):
            indices = np.where(box_classes == box_class)[0]
            filtered_boxes_subset = filtered_boxes[indices]
            box_classes_subset = box_classes[indices]
            box_scores_subset = box_scores[indices]
            x1 = filtered_boxes_subset[:, 0]
            y1 = filtered_boxes_subset[:, 1]
            x2 = filtered_boxes_subset[:, 2]
            y2 = filtered_boxes_subset[:, 3]
            box_areas = (x2 - x1 + 1) * (y2 - y1 + 1)
            ranked = np.argsort(box_scores_subset)[::-1]
            pick = []
            while len(ranked) > 0:
                pick.append(ranked[0])
                xx1 = np.maximum(x1[ranked[0]], x1[ranked[1:]])
                yy1 = np.maximum(y1[ranked[0]], y1[ranked[1:]])
                xx2 = np.minimum(x2[ranked[0]], x2[ranked[1:]])
                yy2 = np.minimum(y2[ranked[0]], y2[ranked[1:]])
                inter_areas = (np.maximum(0, xx2 - xx1 + 1) *
                               np.maximum(0, yy2 - yy1 + 1))
                union_areas = (box_areas[ranked[0]] + box_areas[ranked[1:]]
                               - inter_areas)
                IOU = inter_areas / union_areas
                updated_indices = np.where(IOU <= self.nms_t)[0]
                ranked = ranked[updated_indices + 1]
            pick = np.array(pick)
            box_predictions.append(filtered_boxes_subset[pick])
            predicted_box_classes.append(box_classes_subset[pick])
            predicted_box_scores.append(box_scores_subset[pick])
        box_predictions = np.concatenate(box_predictions)
        predicted_box_classes = np.concatenate(predicted_box_classes)
        predicted_box_scores = np.concatenate(predicted_box_scores)
        return (box_predictions, predicted_box_classes, predicted_box_scores)
