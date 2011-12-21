import contextlib
import sys

#import blinker
from progressbar import ProgressBar, Bar, Percentage


class ReporterProgressBar(ProgressBar):
    def __init__(self, label):
        widgets = [
                "{}: ".format(label).ljust(30),
                Bar(marker="-", left="[", right="]"),
                Percentage(),
                ]
        super(ReporterProgressBar, self).__init__(widgets=widgets)

    def start(self, maxval=None):
        if maxval is not None:
            self.maxval = maxval

        super(ReporterProgressBar, self).start()

    def increment(self, num=1):
        super(ReporterProgressBar, self).update(self.currval + num)


class ResultReporter(object):
    def __init__(self, interactive=False, output=None):
        self.is_interactive = interactive
        self.output = output if output is not None else sys.stdout

    def on_read_image_start(self, max):
        pass

    def on_read_image(self):
        pass

    def on_read_image_stop(self):
        pass

    @contextlib.contextmanager
    def with_read_image(self, max):
        self.on_read_image_start(max)
        yield self.on_read_image
        self.on_read_image_stop()

    def on_apply_transformation_start(self, max):
        pass

    def on_apply_transformation(self):
        pass

    def on_apply_transformation_stop(self):
        pass

    @contextlib.contextmanager
    def with_apply_transformation(self, max):
        self.on_apply_transformation_start(max)
        yield self.on_apply_transformation
        self.on_apply_transformation_stop()

    def on_create_image_artifacts_start(self, max):
        pass

    def on_create_image_artifacts(self):
        pass

    def on_create_image_artifacts_stop(self):
        pass

    @contextlib.contextmanager
    def with_create_image_artifacts(self, max):
        self.on_create_image_artifacts_start(max)
        yield self.on_create_image_artifacts
        self.on_create_image_artifacts_stop()


class ConsoleReporter(ResultReporter):
    def __init__(self, **kwargs):
        super(ConsoleReporter, self).__init__(**kwargs)
        self.pbar_read_image = ReporterProgressBar("Reading Images")
        self.pbar_apply_transformation = ReporterProgressBar(
                "Applying Transformations")
        self.pbar_create_image_artifacts = ReporterProgressBar(
                "Creating Image Artifacts")

    def info(self, msg):
        print(msg)

    def on_read_image_start(self, max):
        self.pbar_read_image.start(max)

    def on_read_image(self):
        self.pbar_read_image.increment()

    def on_read_image_stop(self):
        self.pbar_read_image.finish()

    def on_apply_transformation_start(self, max):
        self.pbar_apply_transformation.start(max)

    def on_apply_transformation(self):
        self.pbar_apply_transformation.increment()

    def on_apply_transformation_stop(self):
        self.pbar_apply_transformation.finish()

    def on_create_image_artifacts_start(self, max):
        self.pbar_create_image_artifacts.start(max)

    def on_create_image_artifacts(self):
        self.pbar_create_image_artifacts.increment()

    def on_create_image_artifacts_stop(self):
        self.pbar_create_image_artifacts.finish()
