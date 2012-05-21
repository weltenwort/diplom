#import numpy
import scipy.spatial.distance


def execute(features1, features2, data):
    feature_name = "means"
    distance = 0
    for feature_group in features1[feature_name]:
        distance += scipy.spatial.distance.cdist(
                features1[feature_name][feature_group].reshape((1, -1)),
                features2[feature_name][feature_group].reshape((1, -1)),
                )
    return distance[0][0]
