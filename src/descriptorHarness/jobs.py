import base64
import pickle
import os

from bunch import Bunch
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


class PickleInputReader(object):
    def __init__(self,\
            filename_pattern=["{base_directory}", "{item_id}.pickle"]):
        self.filename_pattern = filename_pattern

    def __call__(self, base_directory, item_id):
        filename = format_path(self.filename_pattern,
                base_directory=base_directory,
                item_id=item_id,
                safe_item_id=base64.urlsafe_b64encode(item_id),
                )

        with open(filename, "r") as f:
            return pickle.load(f)


class PickleOutputWriter(object):
    def __init__(self, result_attr,\
            filename_pattern=["{base_directory}", "{item_id}.pickle"]):
        self.result_attr = result_attr
        self.filename_pattern = filename_pattern

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
            pickle.dump(getattr(result, self.result_attr), f)


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
                    coefficients=PickleOutputWriter("coefficients", [
                        "{base_directory}",
                        "coefficients",
                        "{safe_item_id}.pickle",
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

        return Bunch(
                coefficients=transformation.fwd(inputs.image)
                )
