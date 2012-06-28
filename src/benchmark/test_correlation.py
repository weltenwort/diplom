import subprocess

import numpy
import pathlib

import common


class TestBenchmark(common.BenchmarkBase):
    def get_distances_from_matrix(self, config, matrix, study):
        results = {}
        for image_set, distances in zip(sorted(config["images"], key=lambda x: x["query_image"]), matrix):
            image_set_results = {}
            for image, distance in zip(sorted(study[image_set["query_image"]].keys()), distances):
                image_set_results[image] = distance
            results[image_set["query_image"]] = image_set_results
        return results

    @common.BenchmarkBase.subcommand(help="execute the benchmark")
    @common.BenchmarkBase.argument("-b", "--benchmark", action="store", dest="benchmark", required=True)
    def execute(self, args, config, study):
        benchmark = numpy.loadtxt(args.benchmark)
        distances = self.get_distances_from_matrix(config, benchmark, study)
        correlations, mean_correlation = self.correlate_to_study(distances, study)
        return correlations, mean_correlation

    @common.BenchmarkBase.subcommand(help="convert imdb results to benchmark results")
    def convert(self, args, config, study):
        distances = common.RDict()
        for image_set in self.logger.loop(
                config["images"],
                entry_message="Processing {count} image sets",
                item_prefix="image set"):
            self.logger.log("Processing query image '{}'...".format(image_set["query_image"]))

            source_image_filenames = dict((str(pathlib.Path(str(f)).parts[-2:]), str(f)) for f in common.glob_list(image_set["source_images"]))
            query_image_filename = image_set["query_image"]
            commandline = config["search"]["commandline"].format(query_image=query_image_filename)
            search_output = subprocess.check_output(commandline, shell=True)

            for index, line in enumerate(search_output.splitlines()):
                parts = line.split()
                if len(parts) == 3:
                    number, similarity, filename = parts
                    if filename in source_image_filenames:
                        distances[query_image_filename][source_image_filenames[filename]] = index

        correlations, mean_correlation = self.correlate_to_study(distances, study)
        return (correlations, mean_correlation)

if __name__ == "__main__":
    TestBenchmark()()
