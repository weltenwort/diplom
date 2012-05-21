import pprint

import numpy

import common


class TestBenchmark(common.BenchmarkBase):
    def get_argv_parser(self):
        parser = super(TestBenchmark, self).get_argv_parser()
        parser.add_argument("-b", "--benchmark", action="store",\
                dest="benchmark", required=True)
        return parser

    def get_distances_from_matrix(self, config, matrix):
        results = {}
        for image_set, distances in zip(sorted(config["images"], key=lambda x: x["query_image"]), matrix):
            image_set_results = {}
            for image, distance in zip(sorted(self.study[image_set["query_image"]].keys()), distances):
                image_set_results[image] = distance
            results[image_set["query_image"]] = image_set_results
        return results

    def execute(self, config, args):
        benchmark = numpy.loadtxt(args.benchmark)
        distances = self.get_distances_from_matrix(config, benchmark)
        correlations, mean_correlation = self.correlate_to_study(distances, data={})
        #pprint.pprint(correlations)
        #print mean_correlation
        return correlations, mean_correlation

if __name__ == "__main__":
    TestBenchmark()()
