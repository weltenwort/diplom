import base64
import datetime
import glob
import itertools
#import logging
import multiprocessing
import os
import shutil

import numpy
import scipy.stats
import termtool

import jobs


class Harness(termtool.Termtool):
    def parallel_map(self, job, items):
        process_number = max(multiprocessing.cpu_count() - 1, 1)
        pool = multiprocessing.Pool(
                processes=process_number,
                maxtasksperchild=2,
                )
        result = pool.map(job, items)
        pool.close()
        pool.join()
        return result

    #@termtool.subcommand(help="transform a set of image using the curvelet \
            #transform")
    #@termtool.argument("--job-directory", default=None)
    #@termtool.argument("--angles", type=int, default=12)
    #@termtool.argument("--scales", type=int, default=4)
    #@termtool.argument("--grid-size", type=int, default=4)
    #@termtool.argument("image", nargs="+")
    #def transform(self, args):
        #if args.job_directory is None:
            #args.job_directory = datetime.datetime.now().strftime(
                    #"job_%Y%m%d%H%M%S%f")

        #parameter_job = jobs.ParameterPersistenceJob(
                #job_directory=args.job_directory,
                #)
        #parameter_job(dict(
            #parameters=dict(
                #angles=12,
                #scales=4,
            #)))

        #job = jobs.CompositeJob([
            #parameter_job,
            #jobs.ImageReaderJob(args.job_directory),
            #jobs.CurveletTransformationJob(),
            #jobs.CurveletPersistenceJob(args.job_directory),
            #])

        #for image_filename in args.image:
            #item = dict(
                    #id=base64.urlsafe_b64encode(image_filename),
                    #source_image_filename=image_filename,
                    #)
            #job(item)

    @termtool.subcommand(help="extract features from a set of images")
    @termtool.argument("--job-directory", default=None)
    @termtool.argument("--angles", type=int, default=12)
    @termtool.argument("--scales", type=int, default=4)
    @termtool.argument("--grid-size", type=int, default=4)
    @termtool.argument("extractor")
    @termtool.argument("image", nargs="+")
    def extract(self, args):
        if args.job_directory is None:
            args.job_directory = datetime.datetime.now().strftime(
                    "job_%Y%m%d%H%M%S%f")

        parameters = dict(
                angles=args.angles,
                scales=args.scales,
                feature_extractor=args.extractor,
                grid_size=args.grid_size,
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

        #pool = multiprocessing.Pool(
                #processes=max(multiprocessing.cpu_count() - 1, 1),
                #maxtasksperchild=1,
                #)
        #pool.map(job, items)
        self.parallel_map(job, items)

    @termtool.subcommand(help="visualize features from a set of images")
    @termtool.argument("--job-directory", default=None)
    @termtool.argument("--angles", type=int, default=12)
    @termtool.argument("--scales", type=int, default=4)
    @termtool.argument("--grid-size", type=int, default=4)
    @termtool.argument("extractor")
    @termtool.argument("image", nargs="+")
    def visualize(self, args):
        if args.job_directory is None:
            args.job_directory = datetime.datetime.now().strftime(
                    "job_%Y%m%d%H%M%S%f")

        parameters = dict(
                angles=args.angles,
                scales=args.scales,
                feature_extractor=args.extractor,
                grid_size=args.grid_size,
                )
        jobs.ParameterPersistenceJob(args.job_directory)(dict(
            parameters=parameters,
            ))

        job = jobs.CompositeJob([
            jobs.ParameterPersistenceJob(args.job_directory, write=False),
            jobs.ImageReaderJob(args.job_directory),
            jobs.CurveletTransformationJob(),
            jobs.CoefficientPlotJob(args.job_directory),
            jobs.FeatureExtractionJob(),
            jobs.FeaturePlotJob(args.job_directory),
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
        self.parallel_map(job, items)
        #map(job, items)

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
            source_image_filename=base64.urlsafe_b64decode(item_id),
            )) for item_id in feature_ids]

        comparison_job = jobs.FeatureComparisonJob()

        distance_items = [comparison_job(dict(
            metric=args.metric,
            query_features=query_features,
            comparison_features=feature_item,
            )) for feature_item in feature_items]

        ranking_job = jobs.CompositeJob([
            jobs.ParameterPersistenceJob(args.features_directory, write=False),
            jobs.DistanceSortingJob(),
            jobs.RankVisualizationJob(args.features_directory),
            ])

        ranking_job(dict(
            items=distance_items,
            query_item=query_features,
            descending=True,
            ))

    @termtool.subcommand(help="Creates the files neccessary to run a \
            benchmark with the given parameters")
    @termtool.argument("--job-directory", default=None)
    @termtool.argument("--study-directory", default="./study")
    @termtool.argument("--angles", type=int, default=12)
    @termtool.argument("--scales", type=int, default=4)
    @termtool.argument("--grid-size", type=int, default=4)
    @termtool.argument("extractor")
    @termtool.argument("metric")
    @termtool.argument("sketches_file")
    @termtool.argument("images_file")
    @termtool.argument("sketches_directory")
    @termtool.argument("images_directory")
    def benchmark(self, args):
        if args.job_directory is None:
            args.job_directory = datetime.datetime.now().strftime(
                    "job_%Y%m%d%H%M%S%f")
        args.study_directory = os.path.abspath(os.path.join(\
                os.path.dirname(__file__), args.study_directory))
        result_filename = os.path.join(args.job_directory, "result.scores")
        correlations_filename = os.path.join(args.job_directory,\
                "correlations")
        mean_correlation_filename = os.path.join(args.job_directory,\
                "correlation.mean")

        if os.path.isfile(result_filename):
            scores = numpy.loadtxt(result_filename)
        else:
            shutil.copy(args.sketches_file, args.job_directory)
            queries = []
            with open(args.sketches_file, "r") as f_sketches,\
                    open(args.images_file, "r") as f_images:
                for sketch_filename_rel, image_filename_line in itertools.izip(
                        f_sketches, f_images):
                    sketch_filename = os.path.join(args.sketches_directory,\
                            sketch_filename_rel.strip())
                    image_filenames = [os.path.join(args.images_directory,\
                            image_filename.strip()) for image_filename\
                            in image_filename_line.split("\t")]
                    queries.append(dict(
                        sketch_filename=sketch_filename,
                        image_filenames=image_filenames,
                        ))

            parameters = dict(
                    angles=args.angles,
                    scales=args.scales,
                    feature_extractor=args.extractor,
                    grid_size=args.grid_size,
                    )
            jobs.ParameterPersistenceJob(args.job_directory)(dict(
                parameters=parameters,
                ))

            scores = []
            for query in queries:
                scores.append(self._benchmark_one(args,\
                        query["sketch_filename"], query["image_filenames"]))
            scores = numpy.array(scores)
            numpy.savetxt(result_filename, scores, "%1i", "\t")

        correlations = self._correlate_to_study(scores,\
                args.study_directory)
        mean_correlation = numpy.mean(correlations)
        numpy.savetxt(correlations_filename, correlations)
        numpy.savetxt(mean_correlation_filename, [mean_correlation, ])
        print mean_correlation

    def _benchmark_one(self, args, sketch_filename, image_filenames):
        job = jobs.CompositeJob([
            jobs.ParameterPersistenceJob(args.job_directory, write=False),
            jobs.ImageReaderJob(args.job_directory),
            jobs.CurveletTransformationJob(),
            jobs.FeatureExtractionJob(),
            ])

        items = [dict(
            id=base64.urlsafe_b64encode(image_filename),
            source_image_filename=image_filename,
            ) for image_filename in image_filenames + [sketch_filename, ]]
        image_features = self.parallel_map(job, items)
        sketch_features = image_features.pop()

        comparison_job = jobs.FeatureComparisonJob()

        distance_items = [comparison_job(dict(
            metric=args.metric,
            query_features=sketch_features,
            comparison_features=feature_item,
            )) for feature_item in image_features]

        return [item["distance"] for item in distance_items]

    def _correlate_to_study(self, scores, study_directory):
        study_pattern = os.path.join(study_directory, "*.study")
        studies = []
        for study_filename in glob.glob(study_pattern):
            study = numpy.loadtxt(study_filename)
            studies.append(study[:study.shape[0] / 2])
        studies = numpy.dstack(studies)

        benchmark = numpy.mean(studies, axis=2)
        #rho, _ = scipy.stats.spearmanr(benchmark.T, scores.T)
        rho = numpy.array([scipy.stats.kendalltau(x, y)[0] for x, y\
                in zip(benchmark.tolist(), scores.tolist())])
        return rho


if __name__ == "__main__":
    Harness().run()
