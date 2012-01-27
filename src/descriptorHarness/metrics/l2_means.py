import numpy


def apply_metric(features1, features2):
    feature_name = "means"
    distance = 0
    for feature_group in features1[feature_name]:
        f1 = features1[feature_name][feature_group]
        f2 = features2[feature_name][feature_group]
        diff = numpy.asarray(f1) - numpy.asarray(f2)
        squares = numpy.power(diff, 2)
        distance += numpy.sum(squares)
    return distance
