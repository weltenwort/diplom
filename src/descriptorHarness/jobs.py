#import base64
import glob
import logging
import os
import pickle
import re

from bunch import Bunch
import numpy
from pyct import fdct2
from scipy.misc import imread, imsave

import utils


class DictBackend(object):
    pass


class FileBackend(object):
    pass


def ensure_list(data):
    if isinstance(data, basestring):
        return [data, ]
    else:
        return list(data)


def format_path(path, *args, **kwargs):
    path = ensure_list(path)
    return os.path.join(*[c.format(*args, **kwargs) for c in path])


class Job(object):
    def __init__(self):
        pass

    def __call__(self, item):
        logging.debug("Executing job {}...".format(self))
        result = self.execute(item)

        return result

    def execute(self, item):
        raise NotImplementedError()


class CompositeJob(Job):
    def __init__(self, jobs=None):
        self.jobs = jobs or []

    def execute(self, item):
        for job in self.jobs:
            #logging.debug("Executing job {} with item {}...".format(job, item)) # NOQA
            item = job(item)

        return item


class FileIOJob(Job):
    def __init__(self, job_directory, parameters=None,\
            read=True, write=True):
        super(FileIOJob, self).__init__()

        self.parameters = parameters or {}
        self.job_directory = job_directory
        self.read = read
        self.write = write

    def read_parameter(self, parameter_name, item):
        parameter = self.parameters[parameter_name]
        filename = parameter.format_filename(
                job_directory=self.job_directory,
                parameter_name=parameter_name,
                item=item,
                )
        parameter.ensure_directory(filename)
        return parameter.read(filename)

    def write_parameter(self, parameter_name, item, value):
        parameter = self.parameters[parameter_name]
        filename = parameter.format_filename(
                job_directory=self.job_directory,
                parameter_name=parameter_name,
                item=item,
                )
        parameter.ensure_directory(filename)
        parameter.write(filename, value)

    def list_files(self, parameter_name=None):
        if parameter_name is None:
            parameter_name = self.parameters.keys()[0]

        parameter = self.parameters[parameter_name]
        filename = parameter.format_filename(
                job_directory=self.job_directory,
                parameter_name=parameter_name,
                item=dict(
                    id="*",
                    )
                )
        return glob.glob(filename)

    def list_ids(self, parameter_name=None):
        sentinel = "LISTIDSENTINEL"
        if parameter_name is None:
            parameter_name = self.parameters.keys()[0]

        parameter = self.parameters[parameter_name]
        filename = parameter.format_filename(
                job_directory=self.job_directory,
                parameter_name=parameter_name,
                item=dict(
                    id=sentinel,
                    )
                )
        filename_expression = re.compile(re.escape(filename)\
                .replace(sentinel, "(.+)"))
        item_ids = [filename_expression.match(filename).group(1) for filename\
                in self.list_files(parameter_name)]

        return item_ids

    def execute(self, item):
        for parameter_name in self.parameters:
            if parameter_name in item:
                if self.write:
                    #logging.debug("Writing parameter '{}': {}".format(parameter_name, item[parameter_name])) # NOQA
                    self.write_parameter(parameter_name, item,\
                            item[parameter_name])
            else:
                if self.read:
                    #logging.debug("Reading parameter '{}'...".format(parameter_name)) # NOQA
                    item[parameter_name] = self.read_parameter(parameter_name,\
                            item)

        return item


class JobParameter(object):
    def __init__(self,\
            filename_pattern=["{job_directory}", "{parameter_name}",
                "{item.id}"]):
        self.filename_pattern = filename_pattern

    def format_filename(self, *args, **kwargs):
        return format_path(self.filename_pattern, *args, **kwargs)

    def ensure_directory(self, filename):
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except OSError:
                pass

    def read(self, filename):
        with open(filename, "r") as f:
            return pickle.load(f)

    def write(self, filename, value):
        with open(filename, "w") as f:
            return pickle.dump(value, f)


class JobNpzParameter(JobParameter):
    def read(self, filename):
        with open(filename, "r") as f:
            return numpy.load(f)

    def write(self, filename, value):
        with open(filename, "w") as f:
            numpy.savez(f, **value)


class JobImageParameter(JobParameter):
    def read(self, filename):
        return imread(filename, flatten=True)

    def write(self, filename, value):
        imsave(filename, value)


class ImageReaderJob(FileIOJob):
    def __init__(self, job_directory):
        super(ImageReaderJob, self).__init__(job_directory,
                parameters=dict(
                    image=JobImageParameter(filename_pattern=[
                        "{item[source_image_filename]}",
                        ]),
                    ),
                read=True,
                write=False,
                )


class ParameterPersistenceJob(FileIOJob):
    def __init__(self, job_directory, read=True, write=True):
        super(ParameterPersistenceJob, self).__init__(job_directory,
                parameters=dict(
                    parameters=JobParameter(filename_pattern=[
                        "{job_directory}",
                        "parameters.pickle",
                        ]),
                    ),
                read=read,
                write=write,
                )


class CurveletPersistenceJob(FileIOJob):
    def __init__(self, job_directory, read=True, write=True):
        super(CurveletPersistenceJob, self).__init__(job_directory,
                parameters=dict(
                    coefficients=JobNpzParameter(filename_pattern=[
                        "{job_directory}",
                        "{parameter_name}",
                        "{item[id]}.coefficients",
                        ]),
                    ),
                read=read,
                write=write,
                )


class CurveletTransformationJob(Job):
    def __init__(self):
        super(CurveletTransformationJob, self).__init__()

    def execute(self, item):
        inputs = Bunch.fromDict(item)

        transformation = fdct2(
                inputs.image.shape,
                inputs.parameters.scales,
                inputs.parameters.angles,
                True,
                norm=True,
                )

        coefficients = transformation.fwd(inputs.image)
        coefficient_map = {}

        angles = [1] + [inputs.parameters.angles]\
                * (inputs.parameters.scales - 1)
        for scale in range(inputs.parameters.scales):
            for angle in range(angles[scale]):
                coefficient_map["{},{}".format(scale, angle)] =\
                        coefficients(scale, angle)

        item["coefficients"] = coefficient_map
        return item


class FeatureExtractionJob(Job):
    def execute(self, item):
        feature_extractor = utils.import_module(\
                item["parameters"]["feature_extractor"]).apply_descriptor
        item["features"] = feature_extractor(item["coefficients"],\
                item["parameters"])
        return item


class FeaturePersistenceJob(FileIOJob):
    def __init__(self, job_directory, read=True, write=True):
        super(FeaturePersistenceJob, self).__init__(job_directory,
                parameters=dict(
                    features=JobParameter(filename_pattern=[
                        "{job_directory}",
                        "{parameter_name}",
                        "{item[id]}.features",
                        ])
                    ),
                read=read,
                write=write,
                )


class FeatureComparisonJob(Job):
    def execute(self, item):
        """Compares two features.

        :argument item: a dict containing the following keys:
            metric
                The name of the module containing the metric
            query_features
                The features of the query image
            comparison_features
                The features of the image to compare the query to
        :return: `item` augmented with the following keys:
            distance
                The distance between the query and comparison images computed
                using the given metric
        """
        inputs = Bunch.fromDict(item)

        metric = utils.import_module(inputs.metric).apply_metric
        distance = metric(inputs.query_features.features,\
                inputs.comparison_features.features)

        item["distance"] = distance
        return item
