import numpy
from pyct import fdct2


def execute(image, data):
    transformation = fdct2(
            image.shape,
            data["config"]["curvelets"]["scales"],
            data["config"]["curvelets"]["angles"],
            False,
            norm=False,
            vec=False,
            )

    coefficients = transformation.fwd(image)
    coefficient_map = {}

    scale = data["config"]["curvelets"]["use_scale"]
    scale_data = coefficients[scale]
    for angle, angle_data in enumerate(scale_data[:len(scale_data) / 2]):
        angle_data = numpy.fabs(angle_data)
        coefficient_map["{},{}".format(scale, angle)] = angle_data

    return coefficient_map
