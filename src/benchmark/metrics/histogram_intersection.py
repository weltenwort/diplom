import numpy


def execute(signature1, signature2, data):
    max_similarity = numpy.sum(signature1)
    similarity = numpy.sum(numpy.minimum(signature1, signature2))
    distance = max_similarity - similarity
    return distance
