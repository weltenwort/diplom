import numpy


def execute(signature1, signature2, data):
    s1_sum = float(numpy.sum(signature1))
    s2_sum = float(numpy.sum(signature2))
    if s1_sum > 0 and s2_sum > 0:
        distance = 1 - float(numpy.sum(numpy.minimum(signature1, signature2)))\
                / min(s1_sum, s2_sum)
    else:
        distance = 1
    return distance

#def execute(signature1, signature2, data):
    #similarity = numpy.sum(numpy.minimum(signature1, signature2))
    #if similarity > 0:
        #return 1.0 / float(similarity)
    #else:
        #return 1.0
