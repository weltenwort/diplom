import numpy


def apply_metric(features1, features2):
    distance = 0
    for scale in features1:
        for angle in features1[scale]:
            f1 = features1[scale][angle]
            f2 = features2[scale][angle]
            mean_diff = numpy.asarray(f1["means"]) - numpy.asarray(f2["means"])
            squares = numpy.power(mean_diff, 2)
            distance += numpy.sum(squares)
    return distance
