import numpy

from common.coefficients import CurveletCoefficients


def iter_lin_slices(minimum, maximum, segments):
    """Returns evenly spaced slices.

    >>> list(iter_lin_slices(0,10,2))
    [slice(0, 5, 1), slice(5, 10, 1)]
    >>> list(iter_lin_slices(0,10,3))
    [slice(0, 3, 1), slice(3, 7, 1), slice(7, 10, 1)]
    """
    start_points = numpy.rint(numpy.linspace(minimum, maximum, segments + 1, True))
    for start_point, stop_point in zip(start_points, start_points[1:]):
        yield slice(int(start_point), int(stop_point), 1)


def iter_overlap_slices(minimum, maximum, width):
    """Returns overlapping slices of the given width.

    >>> list(iter_overlap_slices(0, 5, 3))
    [slice(0, 3, 1), slice(1, 4, 1), slice(2, 5, 1)]
    >>> list(iter_overlap_slices(0, 5, 2))
    [slice(0, 2, 1), slice(1, 3, 1), slice(2, 4, 1), slice(3, 5, 1)]
    """
    for index in range(minimum, maximum - width + 1):
        yield slice(index, index + width, 1)


def create_dir_vectors(n):
    f = numpy.linspace(0.0, numpy.pi, n, True)
    return numpy.column_stack((numpy.cos(f), numpy.sin(f)))


def execute(coefficients, data):
    """ Extract feature patches from the coefficients.

    >>> import numpy
    >>> coefficients = {
    ...     "1,1": numpy.arange(0, 100).reshape(10, 10),
    ...     "1,2": numpy.arange(100, 200).reshape(10, 10),
    ...     }
    >>> data = {"config": {"features": {"grid_size": 6, "patch_size": 3}}}
    >>> r = execute(coefficients, data)
    >>> len(r)
    16
    >>> r[0].shape
    (18,)
    """
    if not isinstance(coefficients, CurveletCoefficients):
        coefficients = CurveletCoefficients.from_coeff_dict(coefficients)

    grid_size = data["config"]["features"]["grid_size"]
    patch_size = data["config"]["features"]["patch_size"]

    angles = list(coefficients.all_angles)
    mean_grid_stack = numpy.empty([grid_size, grid_size, len(angles)])
    for stack_index, angle in enumerate(angles):
        current_coeffs = angle.data
        for y_index, y_slice in enumerate(iter_lin_slices(0, current_coeffs.shape[0], grid_size)):
            for x_index, x_slice in enumerate(iter_lin_slices(0, current_coeffs.shape[1], grid_size)):
                mean_grid_stack[y_index, x_index, stack_index] = numpy.mean(current_coeffs[y_slice, x_slice])

    dom_grid_stack = numpy.empty([grid_size, grid_size, 2])
    maxima = numpy.argmax(mean_grid_stack, axis=2)

    dir_vectors = numpy.empty([len(angles), 2])
    for scale in coefficients.scales:
        dir_vectors[:len(scale.angles)] = create_dir_vectors(len(scale.angles))

    for y in range(grid_size):
        for x in range(grid_size):
            stack_index = maxima[y, x]
            dom_grid_stack[y, x] = dir_vectors[stack_index] * mean_grid_stack[y, x, stack_index]

    features = []
    for y in iter_overlap_slices(0, grid_size, patch_size):
        for x in iter_overlap_slices(0, grid_size, patch_size):
            feature = dom_grid_stack[y, x].reshape(-1)
            features.append(feature)
    return features


def get_angles(coefficients, sep=","):
    scale_angles = {}
    for group_name in coefficients.keys():
        scale, angle = [int(x) for x in group_name.split(sep)]
        scale_angles.setdefault(scale, {})[angle] = group_name
    return scale_angles
