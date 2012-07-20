import numpy
import cv


#def execute(signature1, signature2, data):
    #distance = 1 - float(numpy.sum(numpy.minimum(signature1, signature2)))\
            #/ float(numpy.sum(signature2))
    #return distance

def execute(signature1, signature2, data):
    codewords = data["codewords"]
    fsig1 = cv.fromarray(numpy.asarray([[count, ] + list(word)
        for count, word in zip(signature1, codewords)], dtype=numpy.float32))
    fsig2 = cv.fromarray(numpy.asarray([[count, ] + list(word)
        for count, word in zip(signature2, codewords)], dtype=numpy.float32))
    distance = cv.CalcEMD2(fsig1, fsig2, cv.CV_DIST_L2)
    return distance


def dist_func(a, b):
    return numpy.sin(numpy.arccos(numpy.inner(a, b) / (numpy.linalg.norm(a) * numpy.linalg.norm(b))))


def calculate_codeword_angular_distances(codewords):
    """

    >>> codewords = [numpy.array([1, 0]), numpy.array([1, 1]), numpy.array([0, 1]), numpy.array([-1, 0])]
    >>> d = calculate_codeword_angular_distances(codewords)
    >>> d.shape
    (4, 4)
    >>> numpy.allclose(d, numpy.array([
    ...     [0.0, 0.7, 1.0, 0.0],
    ...     [0.7, 0.0, 0.7, 0.7],
    ...     [1.0, 0.7, 0.0, 1.0],
    ...     [0.0, 0.7, 1.0, 0.0],
    ...     ]), atol=0.01)
    True
    """
    distances = numpy.empty([len(codewords), len(codewords)])
    for y_index, word_1 in enumerate(codewords):
        word_1 = word_1.reshape([-1, 2])
        for x_index, word_2 in enumerate(codewords):
            word_2 = word_2.reshape([-1, 2])
            d = numpy.sum(dist_func(a, b) for a, b in zip(word_1, word_2))
            distances[y_index, x_index] = d
    return distances
