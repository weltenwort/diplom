import numpy
from pyct import fdct2

from basedescriptor import BaseDescriptor, DescriptorResult


class MeanDescriptor(BaseDescriptor):
    name = "MeanDescriptor"

    def __init__(self, scales=4, angles=12, **kwargs):
        super(MeanDescriptor, self).__init__(**kwargs)
        self.parameters.scales = scales
        self.parameters.angles = angles

    def apply(self, images, reporter=None):
        if reporter:
            reporter.on_apply_transformation_start(max=len(images))

        result = []
        for image in images:
            result.append(self._apply_single(image, self.parameters))
            if reporter:
                reporter.on_apply_transformation()

        if reporter:
            reporter.on_apply_transformation_stop()

        return result

    def _apply_single(self, image, parameters):
        grid_size = 4
        angles = [1] + [self.parameters.angles] * (self.parameters.scales - 1)
        features = {}
        transformation = fdct2(
                image.shape,
                parameters.scales,
                parameters.angles,
                True,
                norm=True,
                )
        cl = transformation.fwd(image)

        for scale in range(parameters.scales):
            for angle in range(angles[scale]):
                grid_cells = [cell for row in\
                        numpy.array_split(cl(scale, angle), grid_size)\
                        for cell in\
                        numpy.array_split(row, grid_size, axis=1)]
                means = [numpy.mean(cell) for cell in grid_cells]
                std_devs = [numpy.std(cell) for cell in grid_cells]
                features[(scale, angle)] = {
                        "means": means,
                        "std_devs": std_devs,
                        }

        return DescriptorResult(
                features=features,
                coefficients=cl,
                parameters=parameters,
                )
