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
            result.append(self._apply_single(image,
                    self.parameters.scales,
                    self.parameters.angles
                    ))
            if reporter:
                reporter.on_apply_transformation()

        if reporter:
            reporter.on_apply_transformation_stop()

        return result

    def _apply_single(self, image, scales, angles):
        transformation = fdct2(
                image.shape,
                scales,
                angles,
                True,
                norm=True,
                )
        cl = transformation.fwd(image)

        return DescriptorResult(
                features=None,
                coefficients=cl,
                parameters=self.parameters,
                )
