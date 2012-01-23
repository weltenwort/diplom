import base64
import logging
import os
import pickle

from bunch import Bunch
import numpy
from pyct import fdct2
from scipy.misc import imread, imsave


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
            logging.debug("Executing job {} with item {}...".format(job, item))
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

    def execute(self, item):
        for parameter_name in self.parameters:
            if parameter_name in item:
                if self.write:
                    #logging.debug("Writing parameter '{}': {}".format(parameter_name, item[parameter_name]))
                    self.write_parameter(parameter_name, item,\
                            item[parameter_name])
            else:
                if self.read:
                    #logging.debug("Reading parameter '{}'...".format(parameter_name))
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
            os.makedirs(dirname)

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


class StaticInput(object):
    def __init__(self, static_data):
        self.static_data = static_data

    def __call__(self, base_directory, item):
        return self.static_data


class FileInputReader(object):
    def __init__(self,\
            filename_pattern=["{base_directory}", "{item.input_filename}"]):
        self.filename_pattern = filename_pattern

    def load(self, fp):
        return fp.read()

    def __call__(self, base_directory, item):
        filename = format_path(self.filename_pattern,
                base_directory=base_directory,
                item=item,
                )

        with open(filename, "r") as f:
            return self.load(f)


class FileOutputWriter(object):
    def __init__(self, result_attr,\
            filename_pattern=["{base_directory}", "{item.output_filename}"]):
        self.result_attr = result_attr
        self.filename_pattern = filename_pattern

    def dump(self, data, f):
        f.write(str(data))

    def __call__(self, base_directory, item, result):
        filename = format_path(self.filename_pattern,
                base_directory=base_directory,
                item=item,
                )
        dirname = os.path.dirname(filename)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        print(filename)
        with open(filename, "w") as f:
            self.dump(getattr(result, self.result_attr), f)


class PickleInputReader(FileInputReader):
    def __init__(self,\
            filename_pattern=["{base_directory}",
                "{item.input_filename}.pickle"]):
        super(PickleInputReader, self).__init__(filename_pattern)

    def load(self, fp):
        return pickle.load(fp)


class PickleOutputWriter(FileOutputWriter):
    def __init__(self, result_attr,\
            filename_pattern=["{base_directory}",
                "{item.output_filename}.pickle"]):
        super(PickleOutputWriter, self).__init__(result_attr, filename_pattern)

    def dump(self, data, f):
        pickle.dump(data, f)


class NumpyOutputWriter(FileOutputWriter):
    def __init__(self, result_attr,\
            filename_pattern=["{base_directory}",
                "{item.output_filename}.npy"]):
        super(NumpyOutputWriter, self).__init__(result_attr, filename_pattern)

    def dump(self, data, f):
        numpy.save(f, data)


class NumpyListOutputWriter(FileOutputWriter):
    def __init__(self, result_attr,\
            filename_pattern=["{base_directory}",
                "{item.output_filename}.npz"]):
        super(NumpyListOutputWriter, self).__init__(result_attr,\
                filename_pattern)

    def dump(self, data, f):
        numpy.savez(f, **data)


class ImageInputReader(object):
    def __init__(self, filename_pattern="{item.input_filename}"):
        self.filename_pattern = filename_pattern

    def __call__(self, base_directory, item):
        filename = format_path(self.filename_pattern,
                base_directory=base_directory,
                item=item,
                safe_item=base64.urlsafe_b64encode(item),
                )

        return imread(filename, flatten=True)


class ParameterWriterJob(Job):
    def __init__(self, job_directory, parameters):
        super(ParameterWriterJob, self).__init__(job_directory,
                inputs=dict(
                    parameters=StaticInput(parameters),
                    ),
                outputs=dict(
                    parameters=PickleOutputWriter("parameters", [
                        "{base_directory}",
                        "{item.output_filename}.pickle",
                        ])
                    )
                )

    def execute(self, inputs):
        return Bunch.fromDict(inputs)


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
    def __init__(self, job_directory):
        super(ParameterPersistenceJob, self).__init__(job_directory,
                parameters=dict(
                    parameters=JobParameter(filename_pattern=[
                        "{job_directory}",
                        "parameters.pickle",
                        ]),
                    ),
                )


class CurveletPersistenceJob(FileIOJob):
    def __init__(self, job_directory):
        super(CurveletPersistenceJob, self).__init__(job_directory,
                parameters=dict(
                    coefficients=JobNpzParameter(filename_pattern=[
                        "{job_directory}",
                        "{parameter_name}",
                        "{item[id]}.coefficients",
                        ]),
                    ),
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
