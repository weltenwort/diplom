import datetime
import os

from matplotlib import pyplot
import termtool

from basedescriptor import BaseDescriptor
from reporter import ConsoleReporter, HtmlReporter


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
    @termtool.argument("--artifact-directory", default=None)
    @termtool.argument("descriptor")
    @termtool.argument("image")
    def apply(self, args):
        console_reporter = ConsoleReporter()
        html_reporter = HtmlReporter()

        if args.artifact_directory is None:
            args.artifact_directory = datetime.datetime.now().strftime(
                    os.path.basename(args.image) + "_%Y%m%d%H%M%S")

        with console_reporter.with_read_image(1) as progress:
            image = pyplot.imread(args.image)[:, :, args.channel]
            progress()

        descriptor_class = BaseDescriptor.get_descriptor(
                directory=args.descriptor_directory,
                descriptor_name=args.descriptor,
                )

        descriptor = descriptor_class()
        result = descriptor.apply([image, ], reporter=console_reporter)[0]
        result.create_artifact_images(args.artifact_directory,
                reporter=console_reporter)

        console_reporter.export_summary(result)
        html_reporter.export_summary(result, args.artifact_directory)

if __name__ == "__main__":
    Harness().run()
