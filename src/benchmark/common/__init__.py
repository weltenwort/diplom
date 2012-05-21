from __future__ import print_function

import argparse
import base64
import collections
import contextlib
import datetime
import glob
import importlib
import json
import os
import pickle
import shutil
import sys

import numpy
import pathlib
import scipy.stats


def load(module_name):
    return importlib.import_module(module_name)


def glob_list(pathnames):
    return [l for p in pathnames for l in glob.glob(p)]


def ensure_list(value):
    if isinstance(value, basestring):
        return [value, ]
    elif isinstance(value, collections.Iterable):
        return list(value)
    else:
        return [value, ]


def dict_to_filename(obj, exclude=()):
    parts = []
    for key, value in sorted(obj.iteritems(), key=lambda x: x[0]):
        if not key in exclude:
            parts.append("(")
            parts.append(str(key))
            parts.append(":")
            if isinstance(value, dict):
                parts.append(dict_to_filename(value, exclude))
            else:
                parts.append(str(value))
            parts.append(")")
    return "".join(parts)


class RDict(collections.defaultdict):
    def __init__(self, *args, **kwargs):
        super(RDict, self).__init__(RDict, *args, **kwargs)

    @classmethod
    def from_dict(cls, d):
        if isinstance(d, dict):
            return cls((k, cls.from_dict(v)) for k, v in d.iteritems())
        elif isinstance(d, (list, tuple)):
            return type(d)(cls.from_dict(v) for v in d)
        else:
            return d

    def to_dict(self, d=None):
        if d is None:
            d = self
        if isinstance(d, dict):
            return dict((k, self.to_dict(v)) for k, v in d.iteritems())
        elif isinstance(d, (list, tuple)):
            return type(d)(self.to_dict(v) for v in d)
        else:
            return d


class DiskCache(object):
    def __init__(self, cache_directory):
        self._cache_directory = pathlib.Path.cwd().join(cache_directory)

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
        if filepath.exists:
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
        if filepath.exists:
            filepath.unlink()

    def clear(self):
        shutil.rmtree(str(self._cache_directory))


class Logger(object):
    def __init__(self, default_format=["{message}", ], stream=sys.stderr):
        self.default_format = default_format
        self.stream = stream

        self.reset()

    def reset(self):
        self.format_stack = [self.default_format, ]

    def log(self, message, **kwargs):
        print(" ".join([segment.format(message=message, **kwargs) for segment\
                in self.format_stack[-1]]),
                file=self.stream)

    @contextlib.contextmanager
    def section(self, prefix="::"):
        old_format = self.format_stack[-1]
        if prefix:
            new_format = old_format[:-1] + [prefix, old_format[-1], ]

        self.format_stack.append(new_format)
        yield self
        self.format_stack.pop()

    def loop(self, iterable, entry_message="Looping over {count} items...",\
            item_prefix="iteration"):
        item_count = len(iterable)
        if entry_message:
            self.log(entry_message.format(count=item_count))
        for index, item in enumerate(iterable):
            with self.section(prefix="[{0}:{1:{2}}/{3}]".format(
                item_prefix, index + 1, len(str(item_count)), item_count)):
                yield item


class BenchmarkBase(object):
    def __init__(self):
        self.logger = Logger()

    def get_argv_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--config", action="store", dest="config",\
                required=True)
        parser.add_argument("-s", "--study", action="store", dest="study",\
                required=True)
        return parser

    def load_json(self, filename):
        with open(filename, "r") as fp:
            return json.load(fp)

    def load_config(self, args):
        return self.load_json(args.config)

    def load_study(self, args):
        return self.load_json(args.study)

    def __call__(self, argv=None):
        argv = argv if argv is not None else sys.argv[1:]
        args = self.get_argv_parser().parse_args(argv)

        config = self.load_config(args)
        self.study = self.load_study(args)

        self.logger.reset()
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            start_time = datetime.datetime.now()
            correlations, mean_correlation = self.execute(config, args)
            stop_time = datetime.datetime.now()
        finally:
            sys.stdout = old_stdout
        print(json.dumps(dict(
            correlations=correlations,
            mean_correlation=mean_correlation,
            datetime=str(start_time),
            duration=(stop_time - start_time).total_seconds(),
            config=config,
            ), indent=4))

    def execute(self, config):
        pass

    def get_benchmark_for_distances(self, distances):
        benchmark = {}
        for query_image, images in distances.iteritems():
            benchmark_row = []
            distance_row = []
            for image, distance in images.iteritems():
                benchmark_row.append(self.study[query_image][image])
                distance_row.append(distance)
            benchmark[query_image] = dict(
                    benchmark=benchmark_row,
                    distances=distance_row,
                    )
        return benchmark

    def correlate_to_study(self, distances, data):
        benchmark_data = self.get_benchmark_for_distances(distances)
        results = {query_image: scipy.stats.kendalltau(image_set["benchmark"],\
                image_set["distances"])[0] for query_image, image_set\
                in benchmark_data.iteritems()}
        return results, numpy.mean(results.values())
