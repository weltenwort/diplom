#import numpy
import scipy.spatial.distance


def execute(signature1, signature2, data):
    distance = scipy.spatial.distance.cdist(
            signature1.reshape((1, -1)),
            signature2.reshape((1, -1)),
            "cosine",
            )
    return distance[0][0]
