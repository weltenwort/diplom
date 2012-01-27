#import base64
import glob
import logging
import os
import pickle
import re

from bunch import Bunch
from matplotlib import pyplot
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

        self.parameters = parameters or []
        self.job_directory = job_directory
        self.read = read
        self.write = write

    #def read_parameter(self, parameter_index, item):
        #parameter = self.parameters[parameter_index]
        #filename = parameter.format_filename(
                #job_directory=self.job_directory,
                #item=item,
                #)
        #parameter.ensure_directory(filename)
        #return parameter.read(filename)

    #def write_parameter(self, parameter_index, item):
        #parameter = self.parameters[parameter_index]
        #filename = parameter.format_filename(
                #job_directory=self.job_directory,
                #item=item,
                #)
        #parameter.ensure_directory(filename)
        #parameter.write(filename, item)

    def list_files(self, parameter_index=0):
        parameter = self.parameters[parameter_index]
        filename = parameter.format_filename(
                job_directory=self.job_directory,
                item=dict(
                    id="*",
                    )
                )
        return glob.glob(filename)

    def list_ids(self, parameter_index=0):
        sentinel = "LISTIDSENTINEL"
        parameter = self.parameters[parameter_index]
        filename = parameter.format_filename(
                job_directory=self.job_directory,
                item=dict(
                    id=sentinel,
                    )
                )
        filename_expression = re.compile(re.escape(filename)\
                .replace(sentinel, "(.+)"))
        item_ids = [filename_expression.match(filename).group(1) for filename\
                in self.list_files(parameter_index)]

        return item_ids

    def execute(self, item):
        for parameter in self.parameters:
            if self.write and parameter.should_write(item):
                parameter.write(item,
                        job_directory=self.job_directory,
                        )
            if self.read and parameter.should_read(item):
                parameter.read(item,
                        job_directory=self.job_directory,
                        )

        return item


class JobParameter(object):
    def __init__(self, parameter_name,\
            filename_pattern=["{job_directory}", "{parameter_name}",
                "{item.id}"],
            enable_read=True,
            enable_write=True,
            ):
        self.parameter_name = parameter_name
        self.filename_pattern = filename_pattern
        self.enable_read = enable_read
        self.enable_write = enable_write

    def format_filename(self, *args, **kwargs):
        kwargs.setdefault("parameter_name", self.parameter_name)
        return format_path(self.filename_pattern, *args, **kwargs)

    def ensure_directory(self, filename):
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except OSError:
                pass

    def should_read(self, item):
        return self.enable_read and self.parameter_name not in item

    def should_write(self, item):
        return self.enable_write and self.parameter_name in item

    def read(self, item, **filename_args):
        filename = self.format_filename(item=item, **filename_args)
        with open(filename, "r") as f:
            item[self.parameter_name] = pickle.load(f)

    def write(self, item, **filename_args):
        value = item[self.parameter_name]
        filename = self.format_filename(item=item, **filename_args)
        self.ensure_directory(filename)
        with open(filename, "w") as f:
            return pickle.dump(value, f)


class JobNpzParameter(JobParameter):
    def read(self, item, **filename_args):
        filename = self.format_filename(item=item, **filename_args)
        with open(filename, "r") as f:
            item[self.parameter_name] = numpy.load(f)

    def write(self, item, **filename_args):
        value = item[self.parameter_name]
        filename = self.format_filename(item=item, **filename_args)
        self.ensure_directory(filename)
        with open(filename, "w") as f:
            numpy.savez(f, **value)


class JobImageParameter(JobParameter):
    def read(self, item, **filename_args):
        filename = self.format_filename(item=item, **filename_args)
        item[self.parameter_name] = imread(filename, flatten=True)

    def write(self, item, **filename_args):
        value = item[self.parameter_name]
        filename = self.format_filename(item=item, **filename_args)
        self.ensure_directory(filename)
        imsave(filename, value)


class JobIteratorParameter(JobParameter):
    def __init__(self, each_parameter, filename_pattern=[]):
        super(JobIteratorParameter, self).__init__(
                filename_pattern=filename_pattern,
                )
        self.each_parameter = each_parameter

    def read(self, item, **filename_args):
        raise NotImplementedError()

    def write(self, item, **filename_args):
        value = item[self.parameter_name]
        filename = self.format_filename(item=item, **filename_args)

        self.ensure_directory(filename)
        for key in value:
            #current_filename = self.each_parameter.format_filename(
                    #iter_filename=filename,
                    #iter_key=key,
                    #)
            #self.each_parameter.ensure_directory(current_filename)
            self.each_parameter.write(value[key],
                    iter_filename=filename,
                    iter_key=key
                    )


class JobCoefficientPlotParameter(JobParameter):
    def read(self, item, **filename_args):
        raise NotImplementedError()

    def write(self, item, **filename_args):
        value = item[self.parameter_name]
        filename = self.format_filename(item=item, **filename_args)
        self.ensure_directory(filename)

        fig = pyplot.figure()
        axes = fig.gca()
        mappable = axes.imshow(value)
        fig.colorbar(mappable, ax=axes)
        fig.savefig(filename, format="png")


class JobFeaturePlotParameter(JobParameter):
    def __init__(self, feature_name, filename_pattern=[]):
        super(JobFeaturePlotParameter, self).__init__(
                filename_pattern=filename_pattern,
                )
        self.feature_name = feature_name

    def read(self, item, **filename_args):
        raise NotImplementedError()

    def write(self, item, **filename_args):
        value = item[self.parameter_name]
        filename = self.format_filename(item=item, **filename_args)
        self.ensure_directory(filename)

        pass
        #print self.feature_name, value[self.feature_name]


class ImageReaderJob(FileIOJob):
    def __init__(self, job_directory):
        super(ImageReaderJob, self).__init__(job_directory,
                parameters=[
                    JobImageParameter("image", filename_pattern=[
                        "{item[source_image_filename]}",
                        ]),
                    ],
                read=True,
                write=False,
                )


class ParameterPersistenceJob(FileIOJob):
    def __init__(self, job_directory, read=True, write=True):
        super(ParameterPersistenceJob, self).__init__(job_directory,
                parameters=[
                    JobParameter("parameters", filename_pattern=[
                        "{job_directory}",
                        "parameters.pickle",
                        ]),
                    ],
                read=read,
                write=write,
                )


class CurveletPersistenceJob(FileIOJob):
    def __init__(self, job_directory, read=True, write=True):
        super(CurveletPersistenceJob, self).__init__(job_directory,
                parameters=[
                    JobNpzParameter("coefficients", filename_pattern=[
                        "{job_directory}",
                        "{parameter_name}",
                        "{item[id]}.coefficients",
                        ]),
                    ],
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
                parameters=[
                    JobParameter("features", filename_pattern=[
                        "{job_directory}",
                        "{parameter_name}",
                        "{item[id]}.features",
                        ])
                    ],
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


class CoefficientPlotJob(FileIOJob):
    def __init__(self, job_directory, read=False, write=True):
        super(CoefficientPlotJob, self).__init__(job_directory,
                parameters=[
                    JobIteratorParameter("coefficients",
                        each_parameter=JobCoefficientPlotParameter(None, [
                            "{iter_filename}",
                            "{iter_key}.png",
                            ]),
                        filename_pattern=[
                            "{job_directory}",
                            "coefficient_plot",
                            "{item[id]}",
                            ],
                        ),
                    ],
                read=read,
                write=write,
                )


class FeaturePlotJob(FileIOJob):
    def __init__(self, job_directory, feature_name, read=False, write=True):
        super(FeaturePlotJob, self).__init__(job_directory,
                parameters=[
                    JobFeaturePlotParameter("features",
                        feature_name=feature_name,
                        filename_pattern=[
                            "{job_directory}",
                            "feature_plot_{}".format(feature_name),
                            "{item[id]}",
                            ],
                        ),
                    ],
                read=read,
                write=write,
                )
