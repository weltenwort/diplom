import base64
import datetime
import os

from bunch import Bunch
from matplotlib import pyplot
import stream
import termtool

from basedescriptor import BaseDescriptor, DescriptorEnvironment
from reporter import ConsoleReporter, HtmlReporter, ProgressReporter
from utils import ImageLoader, ParameterWrapper, load_image
import jobs


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
    #@termtool.argument("--channel", type=int, default=0)
    @termtool.argument("--artifact-directory", default=None)
    @termtool.argument("descriptor")
    @termtool.argument("image")
    def applyone(self, args):
        console_reporter = ConsoleReporter()
        html_reporter = HtmlReporter()

        if args.artifact_directory is None:
            args.artifact_directory = datetime.datetime.now().strftime(
                    os.path.basename(args.image) + "_%Y%m%d%H%M%S")

        with console_reporter.with_read_image(1) as progress:
            image = pyplot.imread(args.image, flatten=True)
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

    @termtool.subcommand(help="apply a descriptor to a set of images")
    @termtool.argument("--cache-directory", default="./cache")
    @termtool.argument("--artifact-directory", default=None)
    @termtool.argument("descriptor")
    @termtool.argument("image", nargs="+")
    def apply(self, args):
        reporter = ProgressReporter()
        descriptorEnv = DescriptorEnvironment(
                directory=args.descriptor_directory,
                )

        if args.artifact_directory is None:
            args.artifact_directory = datetime.datetime.now().strftime(
                    "artifacts_%Y%m%d%H%M%S")

        results = args.image\
                >> load_image()\
                >> reporter.iterate_step("Loaded Image", "{image_filename}")\
                >> descriptorEnv.apply_descriptor(args.descriptor)\
                >> reporter.iterate_step("Applied Descriptor", "{descriptor_name} on {image_filename}")

        for result in results:
            print "RESULT: ", result

    @termtool.subcommand(help="transform a set of image using the curvelet \
            transform")
    @termtool.argument("--job-directory", default=None)
    @termtool.argument("--angles", type=int, default=12)
    @termtool.argument("--scales", type=int, default=4)
    @termtool.argument("image", nargs="+")
    def transform(self, args):
        if args.job_directory is None:
            args.job_directory = datetime.datetime.now().strftime(
                    "job_%Y%m%d%H%M%S%f")

        parameter_job = jobs.ParameterPersistenceJob(
                job_directory=args.job_directory,
                )
        parameter_job(dict(
            parameters=dict(
                angles=12,
                scales=4,
            )))

        job = jobs.CompositeJob([
            parameter_job,
            jobs.ImageReaderJob(args.job_directory),
            jobs.CurveletTransformationJob(),
            jobs.CurveletPersistenceJob(args.job_directory),
            ])

        for image_filename in args.image:
            item = dict(
                    id=base64.urlsafe_b64encode(image_filename),
                    source_image_filename=image_filename,
                    )
            result = job(item)
            #print result


if __name__ == "__main__":
    Harness().run()
