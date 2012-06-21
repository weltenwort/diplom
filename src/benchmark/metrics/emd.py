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
