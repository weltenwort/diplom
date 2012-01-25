import itertools
import sys

from bunch import Bunch
from scipy.misc import imread
import stream


def import_module(module_name):
    __import__(module_name)
    return sys.modules[module_name]


def load_image(flatten=True):
    def load_image_inner(image_filename):
        return Bunch(
                image_filename=image_filename,
                image=imread(image_filename, flatten=flatten),
                )
    return stream.map(load_image_inner)


class ImageLoader(stream.Stream):
    def __init__(self, flatten=True):
        super(ImageLoader, self).__init__()
        self.flatten = flatten

    def __call__(self, iterable):
        return itertools.imap(self.load_image, iterable)

    def load_image(self, image_filename):
        return Bunch(
                image_filename=image_filename,
                image=imread(image_filename, flatten=self.flatten),
                )


class ParameterWrapper(stream.Stream):
    def __init__(self, **parameters):
        super(ParameterWrapper, self).__init__()
        self.parameters = parameters

    def __call__(self, iterable):
        return itertools.imap(self.wrap, iterable)

    def wrap(self, data):
        data.update(self.parameters)
        return data


import multiprocessing
import multiprocessing.managers
import signal


class ProcessPipeline(object):
    def __init__(self, steps=[], proxy_factory=dict,\
            pool_parameters=[("default", None), ]):
        self.steps = []

        for step_info in steps:
            if callable(step_info):
                self.append_step(step_info)
            else:
                self.append_step(*step_info)

        self.proxy_factory = proxy_factory
        self.proxy = None
        self.pool_parameters = pool_parameters[:]

        class ProcessPipelineManager(multiprocessing.managers.BaseManager):
            pass
        ProcessPipelineManager.register("get_proxy", self.proxy_factory)

        self.manager = ProcessPipelineManager()
        self.pools = {name: multiprocessing.Pool(num, self.init_worker)\
                for name, num in self.pool_parameters}

    def append_step(self, step, pool_name="default"):
        self.steps.append((step, pool_name))

    @staticmethod
    def init_worker():
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def handle_interrupt(self, signum, frame):
        for pool in self.pools.values():
            pool.terminate()

    def start(self, data):
        signal.signal(signal.SIGINT, self.handle_interrupt)
        self.manager.start()
        self.proxy = self.manager.get_proxy()

        prev_result = data
        for step, pool_name in self.steps:
            prev_result = self.pools[pool_name].imap_unordered(
                    step, itertools.izip_longest(prev_result, [],\
                            fillvalue=self.proxy),
                    )

        return prev_result
