import numpy

import common


class TestBenchmark(common.BenchmarkBase):
    def get_distances_from_matrix(self, config, matrix, study):
        results = {}
        for image_set, distances in zip(sorted(config["images"],\
                key=lambda x: x["query_image"]), matrix):
            image_set_results = {}
            for image, distance in zip(sorted(\
                    study[image_set["query_image"]].keys()), distances):
                image_set_results[image] = distance
            results[image_set["query_image"]] = image_set_results
        return results

    @common.BenchmarkBase.subcommand(help="execute the benchmark")
    @common.BenchmarkBase.argument("-b", "--benchmark", action="store",\
                dest="benchmark", required=True)
    def execute(self, args, config, study):
        benchmark = numpy.loadtxt(args.benchmark)
        distances = self.get_distances_from_matrix(config, benchmark, study)
        correlations, mean_correlation = self.correlate_to_study(distances,\
                study)
        return correlations, mean_correlation

if __name__ == "__main__":
    TestBenchmark()()
