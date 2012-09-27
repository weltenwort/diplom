#import hashlib
import numpy
import pathlib
#import scipy.spatial.distance as distance
import scipy.cluster.vq as vq
#import scipy.cluster.hierarchy as hierarchy

from .diskcache import CodebookDiskCache
from . import load
#from . import dict_to_filename


class Codebook(object):
    def __init__(self, storage, size, stopword_ratio=0.05, cluster_method="kmeans"):
        #self._directory = directory
        self.size = size
        self._stopword_ratio = stopword_ratio
        self._cluster_method = cluster_method

        self.storage = storage
        self.observations = []
        self.document_indices = []
        self.document_count = 0
        self.codewords = numpy.asarray([])
        self.signature = numpy.asarray([])
        self.inverted_index = []
        #self.frequencies = numpy.asarray([])
        #self.stopwords = numpy.asarray([])

        self._df_cache = None

    def __cmp__(self, other):
        return cmp(self.storage, other.storage)

    def __repr__(self):
        return "Codebook(storage='{}', size={})".format(
                self.storage, self.size,
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

    @property
    def document_frequencies(self):
        if self._df_cache is None:
            self._df_cache = numpy.asarray([len(s) for s in self.inverted_index])
        return self._df_cache

    def add_observations(self, observations, new_document=True):
        self.observations += observations
        if new_document:
            self.document_indices += [self.document_count] * len(observations)
            self.document_count += 1
        else:
            self.document_indices += [self.document_count - 1] * len(observations)

    def cluster(self, empty_retries=10):
        self.storage.clear()

        observations = vq.whiten(numpy.array(self.observations))
        #if self._cluster_method == "kmeans":
        for x in range(empty_retries):
            try:
                codebook, code = vq.kmeans2(observations, self.size, minit="points", missing="raise")
            except vq.ClusterError:
                if x >= (empty_retries - 1):
                    raise vq.ClusterError("Empty cluster after {} tries.".format(empty_retries))
            else:
                break
        #elif self._cluster_method == "hierarchy_single":
            #distances = distance.pdist(observations, "euclidean")
            #cluster_hierarchy = hierarchy.linkage(distances,
                    #method="single",
                    #metric="euclidean",
                    #)
            #code = hierarchy.fcluster(cluster_hierarchy,
                    #t=self.size,
                    #criterion="maxclust",
                    #)

        self.codewords = codebook
        self.signature = numpy.bincount(code, minlength=self.size)
        iindex = [set() for _ in range(len(self.codewords))]
        for document_index, term_index in zip(self.document_indices, code):
            iindex[term_index].add(document_index)
        self.inverted_index = iindex

        #signature_sum = float(numpy.sum(signature))
        #self.frequencies = numpy.clip(signature / signature_sum, 0.0, 1.0)
        #self.frequencies = numpy.log(float(self.document_count) / signature)
        #if self._stopword_ratio > 0:
            #signature = self.quantize(self.observations, use_stopwords=False)
            #self.stopwords = self.find_stopwords([signature, ])

    def save(self):
        self.storage.set("size", self.size)
        self.storage.set("stopword_ratio", self._stopword_ratio)
        self.storage.set("document_count", self.document_count)
        self.storage.set("codewords", self.codewords)
        self.storage.set("signature", self.signature)
        self.storage.set("inverted_index", self.inverted_index)
        #self.storage.set("frequencies", self.frequencies)
        #self.storage.set("stopwords", self.stopwords)

    def load(self):
        if not self.exists():
            raise IOError("Codebook does not exist in storage {}".format(self.storage))
        self.size = self.storage.get("size")
        self._stopword_ratio = self.storage.get("stopword_ratio", 0)
        self.document_count = self.storage.get("document_count", 0)
        self.codewords = numpy.asarray(self.storage.get("codewords", []))
        self.signature = numpy.asarray(self.storage.get("signature", []))
        self.inverted_index = self.storage.get("inverted_index", [])
        #self.frequencies = numpy.asarray(self.storage.get("frequencies", []))
        #self.stopwords = numpy.asarray(self.storage.get("stopwords", []))

    def exists(self):
        try:
            self.storage.get("size")
        except KeyError:
            return False
        else:
            return True

    def quantize(self, observations, use_stopwords=True, use_weights="weights.tfidf"):
        if len(observations) > 0:
            observations = vq.whiten(numpy.asarray(observations))
            code = vq.vq(observations, self.codewords)[0]
            signature = numpy.bincount(code, minlength=self.size)
            if use_stopwords:
                if len(self.stopwords) > 0:
                    signature[self.stopwords] = 0  # set stopword bins to 0
            if use_weights is not None:
                #signature_sum = float(numpy.sum(signature))
                #signature = signature / signature_sum * self.frequencies
                signature = load(use_weights).execute(signature, codebook=self)
            return signature
        else:
            return numpy.zeros(self.size)

    def find_stopwords(self, signatures):
        number = self.size * self._stopword_ratio
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
