from bunch import Bunch
import numpy

DESCRIPTOR_NAME = "mean"


def apply_descriptor(coefficients, parameters):
    parameters = Bunch.fromDict(parameters)
    grid_size = 4
    angles = [1] + [parameters.angles] * (parameters.scales - 1)
    features = dict(
            means={},
            std_devs={},
            )

    for scale in range(1, parameters.scales):
        for angle in range(angles[scale]):
            current_coeffs = coefficients["{},{}".format(scale, angle)]
            grid_cells = [cell for row in\
                    numpy.array_split(current_coeffs, grid_size)\
                    for cell in\
                    numpy.array_split(row, grid_size, axis=1)]
            means = numpy.array([numpy.mean(cell) for cell in grid_cells])
            std_devs = numpy.array([numpy.std(cell) for cell in grid_cells])
            #features.setdefault(scale, {})[angle] = {
                    #"means": means,
                    #"std_devs": std_devs,
                    #}
            group_name = "{},{}".format(scale, angle)
            features["means"][group_name] = means
            features["std_devs"][group_name] = std_devs

    return features


def get_feature_groups(features):
    return features["means"].keys()


def plot_feature_group(feature_group):
    pass
