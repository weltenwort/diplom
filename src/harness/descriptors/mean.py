from pyct import fdct2

from basedescriptor import BaseDescriptor, DescriptorResult


class MeanDescriptor(BaseDescriptor):
    name = "MeanDescriptor"

    def __init__(self, scales=4, angles=12, **kwargs):
        super(MeanDescriptor, self).__init__(**kwargs)
        self.parameters.scales = scales
        self.parameters.angles = angles

    def apply(self, image):
        transformation = fdct2(
                image.shape,
                self.parameters.scales,
                self.parameters.angles,
                True,
                norm=True,
                )
        cl = transformation.fwd(image)

        return DescriptorResult(
                features=None,
                coefficients=cl
                )
