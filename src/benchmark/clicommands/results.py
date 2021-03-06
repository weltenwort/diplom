import json

from cliff.lister import Lister
from cliff.formatters.base import ListFormatter
from cliff.show import ShowOne
import numpy
import pathlib


TRANSLATIONS = {
        "metrics.l2_means": "$L_2$",
        "metrics.cosine_means": "COS",
        "metrics.l2": "$L_2$",
        "metrics.cosine": "COS",
        "metrics.emd": "EMD",
        "metrics.histogram_intersection": "HI",
        "metrics.histogram_intersection_binary": "HIB",
        "features.patch_means": "PMEAN",
        "features.patch_means2": "PMEAN2",
        "features.global_means": "MEAN",
        "readers.canny": "CANNY",
        "readers.sobel": "SOBEL",
        "readers.segment": "SEGMENT",
        "readers.luma": "LUMA",
        }


class CustomLister(Lister):
    @property
    def formatter_default(self):
        return "custom"

    def load_formatter_plugins(self):
        super(CustomLister, self).load_formatter_plugins()
        self.formatters["custom"] = CustomPgfFormatter()


class CollectResults(CustomLister):
    def get_parser(self, prog_name):
        parser = super(CollectResults, self).get_parser(prog_name)
        parser.add_argument("results", nargs="+")
        return parser

    def _format_description(self, result_info):
        description = []

        config = result_info["config"]

        if config.get("is_reference", False):
            description.append("SHOG")
        else:
            if "readers" in config and "canny_sigma" in config["readers"]:
                description.append("$\sigma = {}$".format(config["readers"]["canny_sigma"]))
            if "curvelets" in config:
                description.append("$N = ({}, {})$".format(config["curvelets"]["scales"], config["curvelets"]["angles"]))
            if "features" in config:
                if "grid_size" in config["features"] and "patch_size" in config["features"]:
                    description.append("$G = ({}, {})$".format(config["features"]["grid_size"], config["features"]["patch_size"]))
                elif "grid_size" in config["features"]:
                    description.append("$G={}$".format(config["features"]["grid_size"]))
            if "metric" in config:
                description.append(TRANSLATIONS.get(config["metric"]["metric"], ""))

        return ", ".join(description)

    def take_action(self, args):
        results = []
        columns = [
                "ConfigFilename",
                "MeanCorrelation",
                "StandardDeviation",
                "Description",
                "group",
                "features",
                "scales",
                "angles",
                "gridsize",
                "patchsize",
                "cannysigma",
                "queryreader",
                "imagereader",
                "metric",
                ]
        sort_keys = columns[4:]

        for result_filename in args.results:
            result_path = pathlib.Path(result_filename)
            with result_path.open() as fp:
                result_info = json.load(fp)
            config = result_info.get("config", {})

            correlations_keys = sorted(result_info["correlations"].keys())
            short_correlation_keys = [str(pathlib.Path(str(p)).parts[-1]) for p in correlations_keys]
            std_dev = numpy.std(result_info["correlations"].values())

            entry = {
                    "ConfigFilename": str(result_path.parts[-1]).replace("_", "\_"),
                    "MeanCorrelation": result_info["mean_correlation"],
                    "StandardDeviation": std_dev,
                    "Description": self._format_description(result_info),
                    "group": "{}+{}".format(
                        TRANSLATIONS.get(config["readers"]["image"], ""),
                        TRANSLATIONS.get(config["features"]["extractor"], ""),
                        ),
                    "scales": config.get("curvelets", {}).get("scales", ""),
                    "angles": config.get("curvelets", {}).get("angles", ""),
                    "features": TRANSLATIONS.get(config.get("features", {}).get("extractor", ""), ""),
                    "gridsize": config.get("features", {}).get("grid_size", ""),
                    "patchsize": config.get("features", {}).get("patch_size", ""),
                    "cannysigma": config.get("readers", {}).get("canny_sigma", ""),
                    "queryreader": TRANSLATIONS.get(config.get("readers", {}).get("query", ""), ""),
                    "imagereader": TRANSLATIONS.get(config.get("readers", {}).get("image", ""), ""),
                    "metric": TRANSLATIONS.get(config.get("metric", {}).get("metric", ""), ""),
                    }
            for s, k in zip(short_correlation_keys, correlations_keys):
                entry[s] = result_info["correlations"][k]

            results.append(entry)
            results.sort(key=lambda x: [x[k] for k in sort_keys])

        return (
                columns + short_correlation_keys,
                [[row[c] for c in columns + short_correlation_keys] for row in results]
                )


class CollectResultMeans(CustomLister):
    def get_parser(self, prog_name):
        parser = super(CustomLister, self).get_parser(prog_name)
        parser.add_argument("results", nargs="+")
        return parser

    def take_action(self, args):
        #results = []

        correlations = {}
        for result_filename in args.results:
            result_path = pathlib.Path(result_filename)
            with result_path.open() as fp:
                result_info = json.load(fp)

            for key, value in result_info["correlations"].iteritems():
                correlations.setdefault(key, []).append(value)

        #for key, values in sorted(correlations.items(), key=lambda x: x[0]):
            #results
        keys = sorted(correlations.keys())
        short_keys = [str(pathlib.Path(str(p)).parts[-1]) for p in keys]
        means = numpy.mean([correlations[k] for k in keys], axis=1)
        stddevs = numpy.std([correlations[k] for k in keys], axis=1)

        return (
                ("key", "mean", "stddev"),
                zip(short_keys, means, stddevs),
                )


class PlotPrResults(CustomLister):
    def get_parser(self, prog_name):
        parser = super(PlotPrResults, self).get_parser(prog_name)
        parser.add_argument("result")
        return parser

    def take_action(self, args):
        with pathlib.Path(args.result).open() as fp:
            result_info = json.load(fp)
        precisions = result_info["precisions"]
        image_sets = [(x["key"], x["query_image"]) for x in result_info["config"]["images"]]

        recall_precisions = numpy.zeros((max([len(x) for x in precisions.values()]), 2, len(precisions)))
        for query_index, (query_key, query_image) in enumerate(image_sets):
            recall_precision = precisions[query_image]
            recall_precisions[:, :, query_index] = recall_precision
        #for query_index, recall_precision in enumerate(precisions.values()):
            #print(numpy.asarray(recall_precision))
        means = numpy.mean(recall_precisions, axis=2)
        stds = numpy.std(recall_precisions, axis=2)

        return (
                ["recall", "precision", "stddev", "min", "max"] + [x for x, _ in image_sets],
                [[mr, mp, sp, numpy.min(p), numpy.max(p)] + p.tolist() for (mr, mp), (_, sp), p in zip(means.tolist(), stds.tolist(), [recall_precisions[i, 1, :] for i in range(recall_precisions.shape[0])])]
                )


class ShowPrResults(ShowOne):
    def get_parser(self, prog_name):
        parser = super(ShowPrResults, self).get_parser(prog_name)
        parser.add_argument("result")
        return parser

    def take_action(self, args):
        with pathlib.Path(args.result).open() as fp:
            result_info = json.load(fp)
        precisions = result_info["precisions"]
        image_sets = sorted([(x["key"], x["query_image"]) for x in result_info["config"]["images"]], key=lambda x: x[0])

        avg_precisions = []
        for query_index, (query_key, query_image) in enumerate(image_sets):
            recall_precision = precisions[query_image]
            recall_diffs = numpy.ediff1d([0, ] + [r for r, p in recall_precision])
            avg_precision = numpy.average([p for r, p in recall_precision], weights=recall_diffs)
            avg_precisions.append(avg_precision)

        mean_avg_precision = numpy.mean(avg_precisions)

        return (
                ("Mean Average Precision", ),
                (mean_avg_precision, ),
                )


class PlotApResults(CustomLister):
    def get_parser(self, prog_name):
        parser = super(PlotApResults, self).get_parser(prog_name)
        parser.add_argument("result")
        return parser

    def take_action(self, args):
        with pathlib.Path(args.result).open() as fp:
            result_info = json.load(fp)
        precisions = result_info["precisions"]
        image_sets = sorted([(x["key"], x["query_image"]) for x in result_info["config"]["images"]], key=lambda x: x[0])

        results = []
        for query_index, (query_key, query_image) in enumerate(image_sets):
            recall_precision = precisions[query_image]
            recall_diffs = numpy.ediff1d([0, ] + [r for r, p in recall_precision])
            avg_precision = numpy.average([p for r, p in recall_precision], weights=recall_diffs)
            results.append((query_key, avg_precision))

        #recall_precisions = numpy.zeros((max([len(x) for x in precisions.values()]), 2, len(precisions)))
        #for query_index, (query_key, query_image) in enumerate(image_sets):
            #recall_precision = precisions[query_image]
            #recall_precisions[:, :, query_index] = recall_precision
        #for query_index, recall_precision in enumerate(precisions.values()):
            #print(numpy.asarray(recall_precision))
        #means = numpy.mean(recall_precisions, axis=2)
        #stds = numpy.std(recall_precisions, axis=2)

        return (
                ["query", "average"],
                results,
                )


class CustomPgfFormatter(ListFormatter):
    def add_argument_group(self, parser):
        pass

    def _quote(self, data):
        return "{" + str(data) + "}"

    def emit_list(self, column_names, data, stdout, parsed_args):
        stdout.write(" ".join([self._quote(column_name) for column_name in column_names]) + "\n")
        for row in data:
            stdout.write(" ".join([self._quote(cell) for cell in row]) + "\n")
