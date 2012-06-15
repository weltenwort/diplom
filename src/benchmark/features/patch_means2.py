import numpy


def iter_lin_slices(minimum, maximum, segments):
    """Returns evenly spaced slices.

    >>> list(iter_lin_slices(0,10,2))
    [slice(0, 5, 1), slice(5, 10, 1)]
    >>> list(iter_lin_slices(0,10,3))
    [slice(0, 3, 1), slice(3, 7, 1), slice(7, 10, 1)]
    """
    start_points = numpy.rint(numpy.linspace(minimum, maximum, segments + 1,\
            True))
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
    """
    grid_size = data["config"]["features"]["grid_size"]
    patch_size = data["config"]["features"]["patch_size"]

    mean_grid_stack = numpy.empty([grid_size, grid_size,\
            len(coefficients.keys())])
    for stack_index, group_name in enumerate(sorted(coefficients.keys())):
        current_coeffs = coefficients[group_name]
        x_slices = list(iter_lin_slices(0, current_coeffs.shape[1],\
                grid_size))
        y_slices = list(iter_lin_slices(0, current_coeffs.shape[0],\
                grid_size))
        grid_cells = [[current_coeffs[y, x] for x in x_slices]\
                for y in y_slices]
        means = numpy.array([[numpy.mean(grid_cells[y][x])\
                for x in range(grid_size)] for y in range(grid_size)])
        mean_grid_stack[:, :, stack_index] = means

    features = []
    for y in iter_overlap_slices(0, grid_size, patch_size):
        for x in iter_overlap_slices(0, grid_size, patch_size):
            feature = mean_grid_stack[y, x].reshape(-1)
            features.append(feature)
    return features
