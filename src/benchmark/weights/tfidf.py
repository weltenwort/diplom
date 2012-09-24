import numpy


def execute(signature, codebook):
    total_term_count = float(numpy.sum(signature))
    tf = signature / total_term_count
    idf = numpy.log(float(codebook.document_count) / codebook.inverted_index)
    return tf * idf
