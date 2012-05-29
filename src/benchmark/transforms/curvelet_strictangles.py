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

    for scale, scale_data in enumerate(coefficients):
        if len(scale_data) > 1:
            angles = [int(x) for x in numpy.linspace(0, len(scale_data) / 2,\
                    data["config"]["curvelets"]["angles"], False)]
            #for angle, angle_data in enumerate(\
                    #scale_data[:len(scale_data) / 2]):
            for angle, angle_index in enumerate(angles):
                angle_data = numpy.fabs(scale_data[angle_index])
                #angle_data = numpy.fabs(angle_data)[angles]
                coefficient_map["{},{}".format(scale, angle)] = angle_data
    return coefficient_map
