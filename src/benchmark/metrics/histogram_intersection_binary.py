import numpy


def execute(signature1, signature2, data):
    binary_signature1 = numpy.zeros_like(signature1)
    binary_signature1[signature1 > 0] = 1.0
    binary_signature2 = numpy.zeros_like(signature2)
    binary_signature2[signature2 > 0] = 1.0
    s1_sum = float(numpy.sum(binary_signature1))
    s2_sum = float(numpy.sum(binary_signature2))
    if s1_sum > 0 and s2_sum > 0:
        distance = 1 - float(numpy.sum(numpy.minimum(binary_signature1, binary_signature2)))\
                / min(s1_sum, s2_sum)
    else:
        distance = 1
    return distance
