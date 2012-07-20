import numpy
from pyct import fdct2

from ..common.coefficients import (
        CurveletCoefficients,
        CurveletCoefficientScale,
        CurveletCoefficientAngle,
        )


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

    c = CurveletCoefficients()
    for scale, scale_data in enumerate(coefficients):
        if len(scale_data) > 1:
            s = CurveletCoefficientScale()
            c.scales.append(s)
            for angle, angle_data in enumerate(\
                    scale_data[:len(scale_data) / 2]):
                a = CurveletCoefficientAngle(numpy.fabs(angle_data))
                s.angles.append(a)
    return c
