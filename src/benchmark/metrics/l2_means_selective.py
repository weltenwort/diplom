#import numpy
import scipy.spatial.distance


def execute(features1, features2, data):
    distance = 0
    for feature_group_name, means1 in features1["means"].iteritems():
        std_devs1 = features1["std_devs"][feature_group_name]
        means2 = features2["means"][feature_group_name]
        mask = means1 > (std_devs1 / 2.0)
        #logging.debug(mask)
        distance += scipy.spatial.distance.cdist(
                means1[mask].reshape((1, -1)),
                means2[mask].reshape((1, -1)),
                )
    return distance
