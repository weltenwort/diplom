import base64
import pickle
import os

from bunch import Bunch
import numpy
from pyct import fdct2
from scipy.misc import imread


def ensure_list(data):
    if isinstance(data, str):
        return [data, ]
    else:
        return list(data)


def format_path(path, *args, **kwargs):
    path = ensure_list(path)
    return os.path.join(*[c.format(*args, **kwargs) for c in path])


class Job(object):
    def __init__(self, job_directory, inputs=None, outputs=None):
        self.job_directory = job_directory
        self.inputs = inputs if inputs is not None else {}
        self.outputs = outputs if outputs is not None else {}

    def read_input_item(self, input_name, item_id):
        return self.inputs[input_name](self.job_directory, item_id)

    def write_output_item(self, output_name, item_id, result):
        self.outputs[output_name](self.job_directory, item_id, result)

    def __call__(self, item_id):
        inputs = {input_name: self.read_input_item(input_name, item_id)\
                        for input_name in self.inputs}
        result = self.execute(inputs)

        for output_name in self.outputs:
            self.write_output_item(output_name, item_id, result)

    def execute(self, inputs):
        raise NotImplementedError()


class StaticInput(object):
    def __init__(self, static_data):
        self.static_data = static_data

    def __call__(self, base_directory, item_id):
        return self.static_data


class FileInputReader(object):
    def __init__(self,\
            filename_pattern=["{base_directory}", "{item_id}"]):
        self.filename_pattern = filename_pattern

    def load(self, fp):
        return fp.read()

    def __call__(self, base_directory, item_id):
        filename = format_path(self.filename_pattern,
                base_directory=base_directory,
                item_id=item_id,
                safe_item_id=base64.urlsafe_b64encode(item_id),
                )

        with open(filename, "r") as f:
            return self.load(f)


class FileOutputWriter(object):
    def __init__(self, result_attr,\
            filename_pattern=["{base_directory}", "{item_id}"]):
        self.result_attr = result_attr
        self.filename_pattern = filename_pattern

    def dump(self, data, f):
        f.write(str(data))

    def __call__(self, base_directory, item_id, result):
        filename = format_path(self.filename_pattern,
                base_directory=base_directory,
                item_id=item_id,
                safe_item_id=base64.urlsafe_b64encode(item_id),
                )
        dirname = os.path.dirname(filename)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        print(filename)
        with open(filename, "w") as f:
            self.dump(getattr(result, self.result_attr), f)


class PickleInputReader(FileInputReader):
    def __init__(self,\
            filename_pattern=["{base_directory}", "{item_id}.pickle"]):
        super(PickleInputReader, self).__init__(filename_pattern)

    def load(self, fp):
        return pickle.load(fp)


class PickleOutputWriter(FileOutputWriter):
    def __init__(self, result_attr,\
            filename_pattern=["{base_directory}", "{item_id}.pickle"]):
        super(PickleOutputWriter, self).__init__(result_attr, filename_pattern)

    def dump(self, data, f):
        pickle.dump(data, f)


class NumpyOutputWriter(FileOutputWriter):
    def __init__(self, result_attr,\
            filename_pattern=["{base_directory}", "{item_id}.npy"]):
        super(NumpyOutputWriter, self).__init__(result_attr, filename_pattern)

    def dump(self, data, f):
        numpy.save(f, data)


class NumpyListOutputWriter(FileOutputWriter):
    def __init__(self, result_attr,\
            filename_pattern=["{base_directory}", "{item_id}.npz"]):
        super(NumpyListOutputWriter, self).__init__(result_attr,\
                filename_pattern)

    def dump(self, data, f):
        numpy.savez(f, **data)


class ImageInputReader(object):
    def __init__(self, filename_pattern="{item_id}"):
        self.filename_pattern = filename_pattern

    def __call__(self, base_directory, item_id):
        filename = format_path(self.filename_pattern,
                base_directory=base_directory,
                item_id=item_id,
                safe_item_id=base64.urlsafe_b64encode(item_id),
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
                        "{item_id}.pickle",
                        ])
                    )
                )

    def execute(self, inputs):
        return Bunch.fromDict(inputs)


class CurveletTransformationJob(Job):
    def __init__(self, job_directory):
        super(CurveletTransformationJob, self).__init__(job_directory,
                inputs=dict(
                    image=ImageInputReader(),
                    parameters=PickleInputReader([
                        "{base_directory}",
                        "parameters.pickle",
                        ])
                    ),
                outputs=dict(
                    coefficients=NumpyListOutputWriter("coefficients", [
                        "{base_directory}",
                        "coefficients",
                        "{safe_item_id}.npz",
                        ])
                    ),
                )

    def execute(self, inputs):
        inputs = Bunch.fromDict(inputs)

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

        return Bunch(
                coefficients=coefficient_map
                )
