#import datetime

from matplotlib import pyplot
import termtool

from basedescriptor import BaseDescriptor


@termtool.argument("--descriptor-directory",
        default="./descriptors",
        help="the directory in which to look for descriptors",
        )
class Harness(termtool.Termtool):

    @termtool.subcommand(help="list the known descriptors")
    def list(self, args):
        for descriptor in BaseDescriptor.get_descriptors(\
                args.descriptor_directory):
            print(descriptor.name)

    @termtool.subcommand(help="apply a descriptor to an image")
    @termtool.argument("--channel", type=int, default=0)
    @termtool.argument("descriptor")
    @termtool.argument("image")
    def apply(self, args):
        image = pyplot.imread(args.image)[:, :, args.channel]

        descriptor_class = BaseDescriptor.get_descriptor(
                directory=args.descriptor_directory,
                descriptor_name=args.descriptor,
                )
        descriptor = descriptor_class()
        descriptor.apply(image)


if __name__ == "__main__":
    Harness().run()
