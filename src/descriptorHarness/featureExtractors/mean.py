from bunch import Bunch
from matplotlib import pyplot
import numpy


def apply_descriptor(coefficients, parameters):
    parameters = Bunch.fromDict(parameters)
    grid_size = parameters.feature_parameters.grid_size
    #angles = [1] + [parameters.angles] * (parameters.scales - 1)
    features = dict(
            means={},
            std_devs={},
            )

    #for scale in range(1, len(parameters.size_info)):
        #for angle in range(parameters.size_info[scale]):
    for group_name, current_coeffs in coefficients.iteritems():
            #current_coeffs = coefficients["{},{}".format(scale, angle)]
        grid_cells = [cell for row in\
                numpy.array_split(current_coeffs, grid_size)\
                for cell in\
                numpy.array_split(row, grid_size, axis=1)]
        means = numpy.array([numpy.mean(cell) for cell in grid_cells])\
                .reshape((grid_size, grid_size))
        std_devs = numpy.array([numpy.std(cell) for cell in grid_cells])\
                .reshape((grid_size, grid_size))

        #group_name = "{},{}".format(scale, angle)
        features["means"][group_name] = means
        features["std_devs"][group_name] = std_devs

    return features


def get_feature_types(features):
    return features.keys()


def get_feature_groups(features):
    return features[get_feature_types(features)[0]].keys()


def plot_feature_group(features, feature_type, feature_group):
    value = features[feature_type][feature_group]

    figure = pyplot.figure()
    axes = figure.gca()
    mappable = axes.imshow(value, interpolation="none")
    figure.colorbar(mappable, ax=axes)

    return figure
