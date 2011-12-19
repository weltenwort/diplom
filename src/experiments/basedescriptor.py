import glob
import imp
import inspect
import os

from matplotlib.cbook import Bunch


class BaseDescriptor(object):
    name = "DescriptorName"

    def __init__(self, **parameters):
        self.parameters = Bunch(**parameters)

    def apply(self, image):
        raise NotImplemented()

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
    def __init__(self, features, coefficients, artifacts={}):
        self.features = features
        self.coefficients = coefficients
        self.artifacts = artifacts

    def get_artifacts(self, group=None):
        if group is not None:
            return self.artifacts.get(group, [])
        else:
            artifacts = []
            for group_name, group_values in self.artifacts.iteritems():
                artifacts += group_values
            return artifacts
