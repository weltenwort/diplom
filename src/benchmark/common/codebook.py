import numpy
import scipy.cluster.vq

from .diskcache import DiskCache


class Codebook(object):
    def __init__(self, directory, k):
        self._directory = directory
        self._k = k

        self.storage = DiskCache(self._directory)
        self.observations = []
        #self.codewords = numpy.array([])
        self.load()

    def add_observations(self, observations):
        self.observations += observations

    def cluster(self):
        self.storage.clear()
        observations = scipy.cluster.vq.whiten(numpy.array(self.observations))
        codebook, distortion = scipy.cluster.vq.kmeans(observations, self._k)
        self.codewords = codebook

    def store(self):
        self.storage.set("codewords", self.codewords)

    def load(self):
        self.codewords = numpy.asarray(self.storage.get("codewords", []))

    def quantize(self, observations):
        observations = scipy.cluster.vq.whiten(numpy.asarray(observations))
        codes = scipy.cluster.vq.vq(observations, self.codewords)
        signature = numpy.bincount(codes, minlength=len(observations))
