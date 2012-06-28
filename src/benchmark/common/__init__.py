from __future__ import print_function

import argparse
import collections
import contextlib
import datetime
import glob
import importlib
import itertools
import json
import os
import sys

import numpy
import scipy.stats


def load(module_name):
    return importlib.import_module(module_name)


def glob_list(pathnames):
    return [l for p in pathnames for l in glob.glob(p)]


def augment_list(seq, *args):
    l = len(seq)
    return [seq, ] + [[arg, ] * l for arg in args]


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
            item_prefix="iteration", item_count=None):
        if item_count is None:
            try:
                item_count = len(iterable)
            except TypeError:
                item_count = "n"

        if entry_message:
            self.log(entry_message.format(count=item_count))
        for index, item in enumerate(iterable):
            with self.section(prefix="[{0}:{1:{2}}/{3}]".format(
                item_prefix, index + 1, len(str(item_count)), item_count)):
                yield item

    def async_loop(self, f, *iterables, **kwargs):
        from IPython.parallel import Client
        rc = Client()
        lview = rc.load_balanced_view()
        return self.loop(lview.map_async(f, *iterables),\
                item_count=len(iterables[0]), **kwargs)

    def sync_loop(self, f, *iterables, **kwargs):
        return self.loop(itertools.imap(f, *iterables),\
                item_count=len(iterables[0]), **kwargs)


class ApplicationBaseMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['_subcommands'] = [attr for attr in attrs.itervalues()
            if hasattr(attr, '_subcommand')]
        return super(ApplicationBaseMetaclass, cls).__new__(cls, name, bases,\
                attrs)


class ApplicationBase(object):
    __metaclass__ = ApplicationBaseMetaclass
    DEFAULT_COMMAND = "--help"

    def __init__(self):
        self.logger = Logger()

    def get_argv_parser(self):
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers(dest='subcommand',\
                title='subcommands', metavar='')

        for command in sorted(self._subcommands,\
                key=lambda c: c._subcommand[0]):
            name, about_args, about_kwargs = command._subcommand
            subparser = subparsers.add_parser(name, *about_args,\
                    **about_kwargs)

            subparser.set_defaults(func=command)

            subparser.add_argument("-c", "--config", action="store",\
                    dest="config", required=True)
            try:
                class_arguments = self._arguments
            except AttributeError:
                pass
            else:
                # Add arguments in the order they were declared.
                for arg_args, arg_kwargs in reversed(class_arguments):
                    subparser.add_argument(*arg_args, **arg_kwargs)

            try:
                arguments = command._arguments
            except AttributeError:
                pass
            else:
                # Add arguments in the order they were declared.
                for arg_args, arg_kwargs in reversed(arguments):
                    subparser.add_argument(*arg_args, **arg_kwargs)

        return parser

    def parse_argv(self, argv=None):
        argv = argv if argv is not None else sys.argv[1:]
        if len(argv) == 0 or ("--help" not in argv and argv[0] not in\
                [s._subcommand[0] for s in self._subcommands]):
            argv = [self.DEFAULT_COMMAND, ] + argv
        return self.get_argv_parser().parse_args(argv)

    def load_json(self, filename):
        with open(filename, "r") as fp:
            return json.load(fp)

    def load_config(self, args):
        return self.load_json(args.config)

    def __call__(self, argv=None):
        args = self.parse_argv(argv)
        config = self.load_config(args)

        self.logger.reset()
        self.dispatch_subcommand(args, config)

    def dispatch_subcommand(self, args, config, **kwargs):
        return args.func(self, args, config, **kwargs)

    @staticmethod
    def subcommand(*args, **kwargs):
        def decor(fn):
            pargs = list(args)
            try:
                name = pargs.pop(0)
            except IndexError:
                try:
                    name = kwargs.pop('name')
                except KeyError:
                    name = fn.__name__
            fn._subcommand = (name, pargs, kwargs)
            return fn
        return decor

    @staticmethod
    def argument(*args, **kwargs):
        def decor(fn):
            try:
                arguments = fn._arguments
            except AttributeError:
                arguments = fn._arguments = list()
            arguments.append((args, kwargs))
            return fn
        return decor


@ApplicationBase.argument("-s", "--study", action="store", dest="study",\
                required=True)
class BenchmarkBase(ApplicationBase):
    DEFAULT_COMMAND = "execute"

    def load_study(self, args):
        return self.load_json(args.study)

    def dispatch_subcommand(self, args, config, **kwargs):
        study = self.load_study(args)
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            start_time = datetime.datetime.now()
            correlations, mean_correlation = super(BenchmarkBase, self)\
                    .dispatch_subcommand(args, config, study=study)
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

    def get_benchmark_for_distances(self, distances, study):
        benchmark = {}
        for query_image, images in distances.iteritems():
            benchmark_row = []
            distance_row = []
            for image, distance in images.iteritems():
                benchmark_row.append(study[query_image][image])
                distance_row.append(distance)
            benchmark[query_image] = dict(
                    benchmark=benchmark_row,
                    distances=distance_row,
                    )
        return benchmark

    def correlate_to_study(self, distances, study):
        benchmark_data = self.get_benchmark_for_distances(distances, study)
        results = {query_image: scipy.stats.kendalltau(image_set["benchmark"],\
                image_set["distances"])[0] for query_image, image_set\
                in benchmark_data.iteritems()}
        return results, numpy.mean(results.values())
