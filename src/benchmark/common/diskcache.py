import base64
import collections
import pickle
import shutil

import numpy
import pathlib
from . import dict_to_filename


class DiskCache(object):
    def __init__(self, cache_directory):
        self._cache_directory = pathlib.Path.cwd().join(cache_directory)

    @classmethod
    def from_dict_key(cls, dictionary, prefix="cache_"):
        return cls("".join([prefix, dict_to_filename(dictionary)]))

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

    def serialize(self, value, fp):
        pickle.dump(value, fp, protocol=pickle.HIGHEST_PROTOCOL)

    def deserialize(self, fp):
        return pickle.load(fp)

    def set(self, key, value):
        """Set entry ``key`` to ``value``.

        >>> import tempfile
        >>> tmpdir = tempfile.mkdtemp()
        >>> d = DiskCache(tmpdir)
        >>> d.set("a", 3)
        >>> d.get("a")
        3
        >>> d.clear()
        """
        filepath = self._key_to_path(key)
        self._ensure_parents(filepath)
        with filepath.open("wb") as fp:
            self.serialize(value, fp)

    def set_dict(self, dict_key, dict_value, recursive=False):
        dict_key = self._ensure_list(dict_key)
        for key, value in dict_value.iteritems():
            key = dict_key + self._ensure_list(key)
            if recursive and isinstance(value, dict):
                self.set_dict(key, value)
            else:
                self.set(key, value)

    def get(self, key, default=None):
        filepath = self._key_to_path(key)
        if filepath.exists():
            with filepath.open("rb") as fp:
                return self.deserialize(fp)
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


class NumpyDiskCache(DiskCache):
    def serialize(self, value, fp):
        if isinstance(value, dict):
            numpy.savez_compressed(fp, **value)
        else:
            numpy.save(fp, value)

    def deserialize(self, fp):
        return numpy.load(fp)
