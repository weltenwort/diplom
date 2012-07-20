import numpy
import scipy.ndimage


class CurveletCoefficients(object):
    """Stores scale data of a curvelet transformation.

    >>> a1_1 = CurveletCoefficientAngle(0, [[1.0, 3.0], [3.0, 5.0], [5.0, 7.0]])
    >>> a1_2 = CurveletCoefficientAngle(1, [[2.0, 3.0, 4.0], [6.0, 7.0, 8.0]])
    >>> a2_1 = CurveletCoefficientAngle(0, [[0.0, 2.0], [2.0, 4.0], [4.0, 6.0]])
    >>> a2_2 = CurveletCoefficientAngle(1, [[1.0, 2.0, 3.0], [5.0, 6.0, 7.0]])
    >>> s1 = CurveletCoefficientScale(0, [a1_1, a1_2])
    >>> s2 = CurveletCoefficientScale(1, [a2_1, a2_2])
    >>> c = CurveletCoefficients([s1, s2])
    >>> c.max_shape.tolist()
    [3, 3]
    >>> c.as_stack().tolist()
    [[[1.0, 2.0, 0.0, 1.0], [2.0, 3.0, 1.0, 2.0], [3.0, 4.0, 2.0, 3.0]], [[3.0, 4.0, 2.0, 3.0], [4.0, 5.0, 3.0, 4.0], [5.0, 6.0, 4.0, 5.0]], [[5.0, 6.0, 4.0, 5.0], [6.0, 7.0, 5.0, 6.0], [7.0, 8.0, 6.0, 7.0]]]
    >>> c.as_stack((4, 4)).shape
    (4, 4, 4)

    """
    def __init__(self, scales=None):
        self.scales = scales if scales is not None else []

    @property
    def all_angles(self):
        for scale in self.scales:
            for angle in scale.angles:
                yield angle

    @property
    def max_shape(self):
        return numpy.amax([s.max_shape for s in self.scales], axis=0)

    def as_stack(self, new_shape=None):
        if new_shape is None:
            new_shape = self.max_shape
        stack = numpy.dstack([angle.get_scaled_data(new_shape) for angle in self.all_angles])
        return stack

    @classmethod
    def from_coeff_dict(cls, coeff_dict):
        """Creates an instance from a coefficient dictionary.

        >>> c = CurveletCoefficients.from_coeff_dict({
        ...     "1,0": numpy.asarray([[1.0, 2.0], [3.0, 4.0]]),
        ...     "1,1": numpy.asarray([[2.0, 3.0], [4.0, 5.0]]),
        ...     "2,0": numpy.asarray([[3.0, 4.0], [5.0, 6.0]]),
        ...     })
        >>> len(c.scales)
        2
        >>> c.scales[0].index
        0
        >>> len(c.scales[0].angles)
        2
        >>> len(c.scales[1].angles)
        1
        >>> c.scales[0].angles[1].index
        1
        >>> c.scales[0].angles[1].scale is c.scales[0]
        True
        """
        scale_angles = {}
        for group_name in coeff_dict.keys():
            scale, angle = [int(x) for x in group_name.split(",")]
            scale_angles.setdefault(scale, {})[angle] = group_name

        c = cls()
        for scale_index, (scale, angles) in enumerate(sorted(scale_angles.items(), key=lambda x: x[0])):
            s = CurveletCoefficientScale(scale_index)
            c.scales.append(s)

            for angle_index, (angle, group_name) in enumerate(sorted(angles.items(), key=lambda x: x[0])):
                s.angles.append(CurveletCoefficientAngle(angle_index, coeff_dict[group_name], s))
        return c


class CurveletCoefficientScale(object):
    """Stores all angles for a specific coefficient scale.

    >>> a1 = CurveletCoefficientAngle(0, [[1.0, 3.0], [3.0, 5.0], [5.0, 7.0]])
    >>> a2 = CurveletCoefficientAngle(1, [[2.0, 3.0, 4.0], [6.0, 7.0, 8.0]])
    >>> s = CurveletCoefficientScale(0, [a1, a2])
    >>> s.max_shape.tolist()
    [3, 3]
    >>> s.as_stack().shape
    (3, 3, 2)
    """
    def __init__(self, index=None, angles=None):
        self.angles = angles if angles is not None else []
        self.index = index

    @property
    def max_shape(self):
        return numpy.amax([a.data.shape for a in self.angles], axis=0)

    def as_stack(self, new_shape=None):
        if new_shape is None:
            new_shape = self.max_shape
        stack = numpy.dstack([angle.get_scaled_data(new_shape) for angle in self.angles])
        return stack


class CurveletCoefficientAngle(object):
    """Stores coefficient data of a specific curvelet angle.

    >>> a = CurveletCoefficientAngle(0, [[1.0, 2.0], [3.0, 4.0]])
    >>> a.get_scaled_data(a.data.shape).tolist()
    [[1.0, 2.0], [3.0, 4.0]]
    >>> a.get_scaled_data((3,3)).tolist()
    [[1.0, 1.5, 2.0], [2.0, 2.5, 3.0], [3.0, 3.5, 4.0]]
    """
    def __init__(self, index=None, data=None, scale=None):
        self.data = numpy.asarray(data) if data is not None else data
        self.index = index
        self.scale = scale

    def get_scaled_data(self, new_shape):
        zoom = (float(new_shape[0]) / self.data.shape[0], float(new_shape[1]) / self.data.shape[1])
        return scipy.ndimage.zoom(self.data, zoom, order=1)
