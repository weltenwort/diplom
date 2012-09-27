import numpy
import cv


def execute(signature1, signature2, data):
    codewords = data["codewords"]
    #fsig1 = cv.fromarray(numpy.asarray([[count, ] + list(word)
        #for count, word in zip(signature1, codewords)], dtype=numpy.float32))
    #fsig2 = cv.fromarray(numpy.asarray([[count, ] + list(word)
        #for count, word in zip(signature2, codewords)], dtype=numpy.float32))
    fsig1 = numpy.empty((len(signature1), 1 + len(codewords[0])), dtype=numpy.float32)
    fsig2 = numpy.empty((len(signature2), 1 + len(codewords[0])), dtype=numpy.float32)
    for index, word in enumerate(codewords):
        fsig1[index, 0] = signature1[index]
        fsig1[index, 1:] = word
        fsig2[index, 0] = signature2[index]
        fsig2[index, 1:] = word
    distance = cv.CalcEMD2(cv.fromarray(fsig1), cv.fromarray(fsig2), cv.CV_DIST_L2)
    return distance
