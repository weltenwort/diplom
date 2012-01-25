from bunch import Bunch
import numpy

DESCRIPTOR_NAME = "mean"


def apply_descriptor(coefficients, parameters):
    parameters = Bunch.fromDict(parameters)
    grid_size = 4
    angles = [1] + [parameters.angles] * (parameters.scales - 1)
    features = {}

    for scale in range(parameters.scales):
        for angle in range(angles[scale]):
            current_coeffs = coefficients["{},{}".format(scale, angle)]
            grid_cells = [cell for row in\
                    numpy.array_split(current_coeffs, grid_size)\
                    for cell in\
                    numpy.array_split(row, grid_size, axis=1)]
            means = numpy.array([numpy.mean(cell) for cell in grid_cells])
            std_devs = numpy.array([numpy.std(cell) for cell in grid_cells])
            features.setdefault(scale, {})[angle] = {
                    "means": means,
                    "std_devs": std_devs,
                    }

    return features
