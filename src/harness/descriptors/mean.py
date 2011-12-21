from pyct import fdct2

from basedescriptor import BaseDescriptor, DescriptorResult


class MeanDescriptor(BaseDescriptor):
    name = "MeanDescriptor"

    def __init__(self, scales=4, angles=12, **kwargs):
        super(MeanDescriptor, self).__init__(**kwargs)
        self.parameters.scales = scales
        self.parameters.angles = angles

    def apply(self, image, reporter=None):
        if reporter:
            reporter.on_apply_transformation_start(max=1)

        transformation = fdct2(
                image.shape,
                self.parameters.scales,
                self.parameters.angles,
                True,
                norm=True,
                )
        cl = transformation.fwd(image)
        if reporter:
            reporter.on_apply_transformation()
            reporter.on_apply_transformation_stop()

        return DescriptorResult(
                features=None,
                coefficients=cl,
                parameters=self.parameters,
                )
