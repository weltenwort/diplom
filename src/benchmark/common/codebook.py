import numpy
import scipy.cluster.vq

from .diskcache import DiskCache


class Codebook(object):
    def __init__(self, directory, k, stopword_ratio=0.05):
        self._directory = directory
        self._k = k
        self._stopword_ratio = stopword_ratio

        self.storage = DiskCache(self._directory)
        self.observations = []
        self.codewords = numpy.asarray([])
        self.frequencies = numpy.asarray([])
        self.stopwords = numpy.asarray([])

    def __repr__(self):
        return "Codebook(directory='{}', k={}, stopword_ratio={})".format(
                self._directory, self._k, self._stopword_ratio,
                )

    @classmethod
    def from_cache(cls, directory):
        codebook = cls(directory, 0, 0)
        codebook.load()
        return codebook

    def add_observations(self, observations):
        self.observations += observations

    def cluster(self):
        self.storage.clear()
        observations = scipy.cluster.vq.whiten(numpy.array(self.observations))
        codebook, code = scipy.cluster.vq.kmeans2(observations, self._k,\
            minit="points")
        self.codewords = codebook
        signature = numpy.bincount(code, minlength=self._k)
        self.frequencies = numpy.clip(1.0 / signature, 0.0, 1.0)
        if self._stopword_ratio > 0:
            #signature = self.quantize(self.observations, use_stopwords=False)
            self.stopwords = self.find_stopwords([signature, ])

    def save(self):
        self.storage.set("k", self._k)
        self.storage.set("stopword_ratio", self._stopword_ratio)
        self.storage.set("codewords", self.codewords)
        self.storage.set("frequencies", self.frequencies)
        self.storage.set("stopwords", self.stopwords)

    def load(self):
        self._k = self.storage.get("k", 0)
        self._stopword_ratio = self.storage.get("stopword_ratio", 0)
        self.codewords = numpy.asarray(self.storage.get("codewords", []))
        self.frequencies = numpy.asarray(self.storage.get("frequencies", []))
        self.stopwords = numpy.asarray(self.storage.get("stopwords", []))

    def quantize(self, observations, use_stopwords=True, use_weights=False):
        observations = scipy.cluster.vq.whiten(numpy.asarray(observations))
        code = scipy.cluster.vq.vq(observations, self.codewords)[0]
        signature = numpy.bincount(code, minlength=self._k)
        if use_stopwords and len(self.stopwords) > 0:
            signature[self.stopwords] = 0  # set stopword bins to 0
        if use_weights:
            signature = signature / (self.frequencies ** 2)
        return signature

    def find_stopwords(self, signatures):
        number = self._k * self._stopword_ratio
        signatures_sum = numpy.sum(signatures, axis=0)
        sorted_signatures_sum_indices = numpy.argsort(signatures_sum)
        return sorted_signatures_sum_indices[-number:]
