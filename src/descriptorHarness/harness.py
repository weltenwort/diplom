import base64
import datetime
import multiprocessing

import termtool

import jobs


class Harness(termtool.Termtool):
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
            job(item)

    @termtool.subcommand(help="extract features from a set of images")
    @termtool.argument("--job-directory", default=None)
    @termtool.argument("--angles", type=int, default=12)
    @termtool.argument("--scales", type=int, default=4)
    @termtool.argument("extractor")
    @termtool.argument("image", nargs="+")
    def extract(self, args):
        if args.job_directory is None:
            args.job_directory = datetime.datetime.now().strftime(
                    "job_%Y%m%d%H%M%S%f")

        parameters = dict(
                angles=12,
                scales=4,
                feature_extractor=args.extractor,
                )
        jobs.ParameterPersistenceJob(args.job_directory)(dict(
            parameters=parameters,
            ))

        job = jobs.CompositeJob([
            jobs.ParameterPersistenceJob(args.job_directory, write=False),
            jobs.ImageReaderJob(args.job_directory),
            jobs.CurveletTransformationJob(),
            jobs.FeatureExtractionJob(),
            jobs.FeaturePersistenceJob(args.job_directory),
            ])

        items = []
        for image_filename in args.image:
            item = dict(
                    id=base64.urlsafe_b64encode(image_filename),
                    source_image_filename=image_filename,
                    parameters=parameters,
                    )
            items.append(item)

        pool = multiprocessing.Pool()
        pool.map(job, items)
        #map(job, items)

    @termtool.subcommand(help="visualize features from a set of images")
    @termtool.argument("--job-directory", default=None)
    @termtool.argument("--angles", type=int, default=12)
    @termtool.argument("--scales", type=int, default=4)
    @termtool.argument("extractor")
    @termtool.argument("image", nargs="+")
    def visualize(self, args):
        if args.job_directory is None:
            args.job_directory = datetime.datetime.now().strftime(
                    "job_%Y%m%d%H%M%S%f")

        parameters = dict(
                angles=12,
                scales=4,
                feature_extractor=args.extractor,
                )
        jobs.ParameterPersistenceJob(args.job_directory)(dict(
            parameters=parameters,
            ))

        job = jobs.CompositeJob([
            jobs.ParameterPersistenceJob(args.job_directory, write=False),
            jobs.ImageReaderJob(args.job_directory),
            jobs.CurveletTransformationJob(),
            #jobs.CoefficientPlotJob(args.job_directory),
            jobs.FeatureExtractionJob(),
            jobs.FeaturePlotJob(args.job_directory, "means"),
            ])

        items = []
        for image_filename in args.image:
            item = dict(
                    id=base64.urlsafe_b64encode(image_filename),
                    source_image_filename=image_filename,
                    parameters=parameters,
                    )
            items.append(item)

        #pool = multiprocessing.Pool()
        #pool.map(job, items)
        map(job, items)

    @termtool.subcommand(help="perform a similarity query on an image and the\
            results of a previous feature extraction")
    @termtool.argument("metric")
    @termtool.argument("features_directory")
    @termtool.argument("image")
    def query(self, args):
        query_features = jobs.CompositeJob([
            jobs.ParameterPersistenceJob(args.features_directory, write=False),
            jobs.ImageReaderJob("."),
            jobs.CurveletTransformationJob(),
            jobs.FeatureExtractionJob(),
            ])(dict(
                id=base64.urlsafe_b64encode(args.image),
                source_image_filename=args.image,
                ))

        feature_ids = jobs.FeaturePersistenceJob(args.features_directory)\
                .list_ids()

        feature_retrieval_job = jobs.CompositeJob([
            jobs.FeaturePersistenceJob(args.features_directory, write=False),
            ])

        feature_items = [feature_retrieval_job(dict(
            id=item_id,
            )) for item_id in feature_ids]

        comparison_job = jobs.FeatureComparisonJob()

        distances = [comparison_job(dict(
            metric=args.metric,
            query_features=query_features,
            comparison_features=feature_item,
            ))["distance"] for feature_item in feature_items]
        print(distances)

if __name__ == "__main__":
    Harness().run()
