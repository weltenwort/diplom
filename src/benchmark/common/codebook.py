#import hashlib
import numpy
import pathlib
import scipy.spatial.distance as distance
import scipy.cluster.vq as vq
import scipy.cluster.hierarchy as hierarchy

from .diskcache import CodebookDiskCache
#from . import dict_to_filename


class Codebook(object):
    def __init__(self, storage, size, stopword_ratio=0.05, cluster_method="kmeans"):
        #self._directory = directory
        self._size = size
        self._stopword_ratio = stopword_ratio
        self._cluster_method = cluster_method

        self.storage = storage
        self.observations = []
        self.document_count = 0
        self.codewords = numpy.asarray([])
        self.frequencies = numpy.asarray([])
        self.stopwords = numpy.asarray([])

    def __cmp__(self, other):
        return self.storage.__cmp__(other.storage)

    def __repr__(self):
        return "Codebook(storage='{}', size={}, stopword_ratio={})".format(
                self.storage, self._size, self._stopword_ratio,
                )

    @classmethod
    def load_from_config(cls, config):
        codebook = cls.create_from_config(config)
        codebook.load()
        return codebook

    @classmethod
    def load_from_path(cls, path):
        codebook = cls.create_from_path(path, size=0)
        codebook.load()
        return codebook

    @classmethod
    def create_from_config(cls, config):
        codebook = cls(
                storage=CodebookDiskCache.from_config(config),
                size=config["codebook"]["codebook_size"],
                stopword_ratio=config["codebook"].get("stopword_ratio", 0.05),
                )
        return codebook

    @classmethod
    def create_from_path(cls, path, *args, **kwargs):
        codebook = cls(CodebookDiskCache(path), *args, **kwargs)
        return codebook

    #@classmethod
    #def hash_from_dict_key(cls, dictionary, prefix="cache_", **kwargs):
        #directory = hashlib.sha1(dict_to_filename(dictionary)).hexdigest()
        #return cls("".join([str(prefix), directory]), **kwargs)

    @property
    def name(self):
        return self.storage.id

    @property
    def modification_date(self):
        return self.storage.modification_date

    def add_observations(self, observations, new_document=True):
        self.observations += observations
        if new_document:
            self.document_count += 1

    def cluster(self):
        self.storage.clear()

        observations = vq.whiten(numpy.array(self.observations))
        if self._cluster_method == "kmeans":
            codebook, code = vq.kmeans2(observations, self._size,\
                minit="points")
        elif self._cluster_method == "hierarchy_single":
            distances = distance.pdist(observations, "euclidean")
            cluster_hierarchy = hierarchy.linkage(distances,
                    method="single",
                    metric="euclidean",
                    )
            code = hierarchy.fcluster(cluster_hierarchy,
                    t=self._size,
                    criterion="maxclust",
                    )

        self.codewords = codebook
        signature = numpy.bincount(code, minlength=self._size)
        #signature_sum = float(numpy.sum(signature))
        #self.frequencies = numpy.clip(signature / signature_sum, 0.0, 1.0)
        self.frequencies = numpy.log(float(self.document_count) / signature)
        if self._stopword_ratio > 0:
            #signature = self.quantize(self.observations, use_stopwords=False)
            self.stopwords = self.find_stopwords([signature, ])

    def save(self):
        self.storage.set("size", self._size)
        self.storage.set("stopword_ratio", self._stopword_ratio)
        self.storage.set("document_count", self.document_count)
        self.storage.set("codewords", self.codewords)
        self.storage.set("frequencies", self.frequencies)
        self.storage.set("stopwords", self.stopwords)

    def load(self):
        if not self.exists():
            raise IOError("Codebook does not exist in strage {}".format(self.storage))
        self._size = self.storage.get("size")
        self._stopword_ratio = self.storage.get("stopword_ratio", 0)
        self.document_count = self.storage.get("document_count", 0)
        self.codewords = numpy.asarray(self.storage.get("codewords", []))
        self.frequencies = numpy.asarray(self.storage.get("frequencies", []))
        self.stopwords = numpy.asarray(self.storage.get("stopwords", []))

    def exists(self):
        try:
            self.storage.get("size")
        except KeyError:
            return False
        else:
            return True

    def quantize(self, observations, use_stopwords=True, use_weights=False):
        observations = vq.whiten(numpy.asarray(observations))
        code = vq.vq(observations, self.codewords)[0]
        signature = numpy.bincount(code, minlength=self._size)
        if use_stopwords and len(self.stopwords) > 0:
            signature[self.stopwords] = 0  # set stopword bins to 0
        if use_weights:
            signature_sum = float(numpy.sum(signature))
            signature = signature / signature_sum * self.frequencies
        return signature

    def find_stopwords(self, signatures):
        number = self._size * self._stopword_ratio
        signatures_sum = numpy.sum(signatures, axis=0)
        sorted_signatures_sum_indices = numpy.argsort(signatures_sum)
        return sorted_signatures_sum_indices[-number:]


class CodebookManager(object):
    def __init__(self, directory):
        self.directory = directory

    def get_codebooks(self):
        codebooks = set()

        path = pathlib.Path(self.directory)
        for child in path:
            if child.is_dir():
                try:
                    codebook = Codebook.load_from_path(str(child))
                    codebooks.add(codebook)
                except IOError:
                    pass

        return codebooks
