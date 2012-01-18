import glob
import imp
import inspect
import json
#import logging
import multiprocessing
import os

from bunch import Bunch
from matplotlib import pyplot
import stream


class DescriptorEnvironment(object):
    def __init__(self, directory):
        self.directory = directory

    @classmethod
    def get_descriptor_files(cls, directory):
        pattern = os.path.join(os.path.abspath(directory), "*.py")
        return sorted(glob.iglob(pattern))

    @classmethod
    def load_descriptor_module(cls, filename):
        basename = os.path.splitext(os.path.basename(filename))[0]
        descriptor_module = imp.load_source(
                "descriptor_{}".format(basename),
                filename,
                )
        return descriptor_module

    @classmethod
    def get_descriptor_modules(cls, directory):
        return [cls.load_descriptor_module(m)\
                for m in cls.get_descriptor_files(directory)]

    def get_descriptor(self, descriptor_name):
        for descriptor_module in self.get_descriptor_modules(self.directory):
            if descriptor_module.DESCRIPTOR_NAME == descriptor_name:
                return descriptor_module
        raise NameError("No such descriptor: {}".format(descriptor_name))

    def apply_descriptor(self, descriptor_name, **parameters):
        parameters.setdefault("angles", 12)
        parameters.setdefault("scales", 4)
        parameters = Bunch(**parameters)
        descriptor = self.get_descriptor(descriptor_name).apply_descriptor

        def apply_descriptor_inner(data):
            data.parameters = parameters
            data.descriptor_name = descriptor_name
            features = descriptor(data.image, data.parameters)
            data.features = features
            #data.coefficients = coefficients
            return data

        return stream.map(apply_descriptor_inner)


class BaseDescriptor(object):
    name = "DescriptorName"

    def __init__(self, **parameters):
        parameters.setdefault("angles", 12)
        parameters.setdefault("scales", 4)
        self.parameters = Bunch(**parameters)

    def apply(self, image, reporter=None):
        raise NotImplementedError()

    @classmethod
    def is_descriptor(cls, other):
        return other is not cls \
                and inspect.isclass(other) \
                and issubclass(other, BaseDescriptor)

    @classmethod
    def get_descriptor_files(cls, directory):
        pattern = os.path.join(os.path.abspath(directory), "*.py")
        return sorted(glob.iglob(pattern))

    @classmethod
    def load_descriptor_file(cls, filename):
        basename = os.path.splitext(os.path.basename(filename))[0]
        return imp.load_source(
                "descriptor_{}".format(basename),
                filename,
                )

    @classmethod
    def get_descriptor_classes(cls, module):
        return [v for k, v in inspect.getmembers(module, cls.is_descriptor)]

    @classmethod
    def get_descriptors(cls, directory):
        descriptors = []

        for descriptor_filename in cls.get_descriptor_files(directory):
            descriptor_module = cls.load_descriptor_file(descriptor_filename)
            descriptors += cls.get_descriptor_classes(descriptor_module)

        return descriptors

    @classmethod
    def get_descriptor(cls, directory, descriptor_name):
        for descriptor in cls.get_descriptors(directory):
            if descriptor.name == descriptor_name:
                return descriptor
        raise NameError("No such descriptor: {}".format(descriptor_name))


class DescriptorResult(object):
    def __init__(self, features, coefficients, parameters={}, artifacts={}):
        self.features = features
        self.coefficients = coefficients
        self.parameters = Bunch(**parameters) if isinstance(parameters, dict) else parameters
        self.artifacts = artifacts

    def serialize(self):
        return json.dumps({
            "features": self.features,
            "parameters": self.parameters.__dict__,
            })

    def get_artifacts(self, group=None):
        if group is not None:
            return self.artifacts.get(group, [])
        else:
            artifacts = []
            for group_name, group_values in self.artifacts.iteritems():
                artifacts += group_values
            return artifacts

    def create_artifact_images(self, directory,
            filename_pattern="scale{scale}_angle{angle}",
            reporter=None):
        os.mkdir(directory)
        if reporter:
            reporter.info("Creating image artifacts in '{}'...".format(directory))

        angles = [1] + [self.parameters.angles] * (self.parameters.scales - 1)

        if reporter:
            reporter.on_create_image_artifacts_start(sum([
                angles[s] for s in range(self.parameters.scales)
                ]))

        def process_artifact_result(args):
            scale, angle, filename = args
            self.artifacts.setdefault("images", {})\
                    .setdefault(scale, {})[angle] = filename
            if reporter:
                reporter.on_create_image_artifacts()

        pool = multiprocessing.Pool()
        for scale in range(self.parameters.scales):
            for angle in range(angles[scale]):
                label = filename_pattern.format(
                    scale=scale,
                    angle=angle,
                    )
                filename = os.path.join(directory, "{}.png".format(label))
                pool.apply_async(create_artifact_image,
                        args=(self.coefficients(scale, angle), scale, angle, filename),
                        callback=process_artifact_result,
                        )
        pool.close()
        pool.join()

        if reporter:
            reporter.on_create_image_artifacts_stop()


def create_artifact_image(data, scale, angle, filename):
    fig = pyplot.figure()
    axes = fig.gca()
    #cl_image = cl(scale, angle)

    mappable = axes.imshow(data)
    fig.colorbar(mappable, ax=axes)

    #logging.info(u"Writing image '{}'...".format(filename))
    fig.savefig(filename, format="png")
    return (scale, angle, filename)
    #result_queue.put((scale, angle, filename))
