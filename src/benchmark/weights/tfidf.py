import numpy
#import sys


def execute(signature, codebook):
    #total_term_count = float(numpy.sum(signature))
    max_term_count = float(numpy.max(signature))
    tf = signature / max_term_count
    idf = numpy.log(float(codebook.document_count) / codebook.document_frequencies)
    return signature * (tf * idf)
