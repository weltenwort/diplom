import base64
import collections
import contextlib
import datetime
import gzip
import hashlib
import pickle
import shutil

import Image
import numpy
import scipy.misc
import pathlib
from . import dict_to_filename


class BaseDiskCache(object):
    METADATA_KEY = "__metadata__"
    CACHE_TYPE = "generic"

    def __init__(self, cache_directory):
        self._cache_directory = pathlib.Path(cache_directory)

        self.initialize()

    def __cmp__(self, other):
        return self.modification_date.__cmp__(other.modification_date)

    @property
    def id(self):
        return self._cache_directory

    @property
    def modification_date(self):
        if self._cache_directory.exists():
            return datetime.datetime.fromtimestamp(self._cache_directory.st_mtime)

    @classmethod
    def from_dict_key(cls, dictionary, prefix="cache_"):
        return cls("".join([str(prefix), dict_to_filename(dictionary)]))

    @classmethod
    def hash_from_dict_key(cls, dictionary, prefix="cache_", **kwargs):
        directory = hashlib.sha1(dict_to_filename(dictionary)).hexdigest()
        return cls("".join([str(prefix), directory]), **kwargs)

    def initialize(self):
        if self._cache_directory.exists():
            if self.contains([self.METADATA_KEY, "cache_type"]):
                if not self.get_metadata("cache_type") == self.CACHE_TYPE:
                    raise IOError("Could not initialize cache at location '{}': incompatible cache type")
            else:
                raise IOError("Could not initialize cache at location '{}': directory is not a cache".format(self._cache_directory))
        else:
            self.update_metadata(dict(
                cache_type=self.CACHE_TYPE,
                creation_date=datetime.datetime.now(),
                ))

    def set_metadata(self, key, value):
        self.set([self.METADATA_KEY, key], value, serializer=PickleSerializerMixin)

    def update_metadata(self, data):
        for key, value in data.iteritems():
            self.set([self.METADATA_KEY, key], value, serializer=PickleSerializerMixin)

    def get_metadata(self, key, default=None):
        return self.get([self.METADATA_KEY, key], default, serializer=PickleSerializerMixin)

    def remove_metadata(self, key):
        self.remove([self.METADATA_KEY, key])

    def _key_to_path(self, key):
        path = pathlib.Path(*self._ensure_list(key))
        return self._cache_directory.join(path)

    def _ensure_parents(self, path):
        parent = path.parent()
        if not parent.exists():
            parent.mkdir(parents=True)

    def _ensure_list(self, value):
        encode = lambda x: base64.urlsafe_b64encode(str(x))
        if isinstance(value, basestring):
            return [encode(value), ]
        elif isinstance(value, collections.Iterable):
            return [encode(x) for x in value]
        else:
            return [encode(value), ]

    def set(self, key, value, serializer=None):
        """Set entry ``key`` to ``value``.

        >>> import tempfile
        >>> tmpdir = tempfile.mkdtemp()
        >>> d = DiskCache(tmpdir)
        >>> d.set("a", 3)
        >>> d.get("a")
        3
        >>> d.clear()
        """
        if serializer is None:
            serializer = self
        filepath = self._key_to_path(key)
        self._ensure_parents(filepath)
        with self.open(str(filepath), "wb") as fp:
            serializer.serialize(value, fp)

    #def set_dict(self, dict_key, dict_value, recursive=False, serializer=None):
        #dict_key = self._ensure_list(dict_key)
        #for key, value in dict_value.iteritems():
            #key = dict_key + self._ensure_list(key)
            #if recursive and isinstance(value, dict):
                #self.set_dict(key, value, recursive=recursive, serializer=serializer)
            #else:
                #self.set(key, value, serializer=serializer)

    def get(self, key, default=None, serializer=None):
        if serializer is None:
            serializer = self
        filepath = self._key_to_path(key)
        if filepath.exists():
            with self.open(str(filepath), "rb") as fp:
                return serializer.deserialize(fp)
        else:
            if default is None:
                raise KeyError("Key '{}' not found in cache.".format(key))
            else:
                return default

    def contains(self, key):
        filepath = self._key_to_path(key)
        return filepath.exists() and filepath.is_file()

    def remove(self, key):
        filepath = self._key_to_path(key)
        if filepath.exists():
            filepath.unlink()

    def clear(self):
        if self._cache_directory.exists() and self._cache_directory.is_file():
            shutil.rmtree(str(self._cache_directory))


class FileBackendMixin(object):
    @contextlib.contextmanager
    def open(self, filename, mode):
        with open(filename, mode) as fp:
            yield fp


class GzipBackendMixin(object):
    @contextlib.contextmanager
    def open(self, filename, mode):
        with gzip.open(filename, mode) as fp:
            yield fp


class PickleSerializerMixin(object):
    @classmethod
    def serialize(cls, value, fp):
        pickle.dump(value, fp, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def deserialize(cls, fp):
        return pickle.load(fp)


class NumpySerializerMixin(object):
    @classmethod
    def serialize(cls, value, fp):
        numpy.save(fp, value)

    @classmethod
    def deserialize(cls, fp):
        return numpy.load(fp)


class PngSerializerMixin(object):
    @classmethod
    def serialize(cls, value, fp):
        Image.fromarray(value).save(fp, format="PNG")

    @classmethod
    def deserialize(cls, fp):
        return scipy.misc.fromimage(Image.open(fp))


class DiskCache(BaseDiskCache, FileBackendMixin, PickleSerializerMixin):
    pass


class NullCache(DiskCache):
    def __init__(self, *args, **kwargs):
        pass

    @property
    def id(self):
        return hash(self)

    @property
    def modification_date(self):
        return datetime.datetime.now()

    def set(self, key, value):
        pass

    def get(self, key, default=None):
        return default

    def clear(self):
        pass

    def remove(self, key):
        pass

    def contains(self, key):
        return False


class ConfigDiskCache(BaseDiskCache):
    CONFIG_KEYS = []
    PREFIX = "cache_"

    @classmethod
    def from_config(cls, config, prefix=None, root_directory="."):
        if prefix is None:
            prefix = cls.PREFIX
        dictionary = {key: value for key, value in config.iteritems() if key in cls.CONFIG_KEYS}
        directory = hashlib.sha1(dict_to_filename(dictionary)).hexdigest()
        return cls(str(pathlib.Path(str(root_directory)).join("".join([str(prefix), directory]))))


class ReaderDiskCache(ConfigDiskCache, GzipBackendMixin, NumpySerializerMixin):
    CACHE_TYPE = "gzip_numpy"
    CONFIG_KEYS = ["readers"]
    PREFIX = "rcache_"


class FeatureDiskCache(ConfigDiskCache, GzipBackendMixin, PickleSerializerMixin):
    CACHE_TYPE = "gzip_pickle"
    CONFIG_KEYS = ReaderDiskCache.CONFIG_KEYS + ["curvelets", "features"]
    PREFIX = "fcache_"


class CodebookDiskCache(ConfigDiskCache, FileBackendMixin, PickleSerializerMixin):
    CACHE_TYPE = "gzip_pickle"
    CONFIG_KEYS = FeatureDiskCache.CONFIG_KEYS + ["codebook"]
    PREFIX = "ccache_"
