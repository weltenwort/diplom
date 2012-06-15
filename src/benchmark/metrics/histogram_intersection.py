import numpy


#def execute(signature1, signature2, data):
    #distance = 1 - float(numpy.sum(numpy.minimum(signature1, signature2)))\
            #/ float(numpy.sum(signature2))
    #return distance

def execute(signature1, signature2, data):
    similarity = numpy.sum(numpy.minimum(signature1, signature2))
    if similarity > 0:
        return 1.0 / float(similarity)
    else:
        return 1.0
