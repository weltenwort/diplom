import json

from cliff.lister import Lister
from cliff.formatters.base import ListFormatter
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


class CollectResults(Lister):
    @property
    def formatter_default(self):
        return "custom"

    def get_parser(self, prog_name):
        parser = super(CollectResults, self).get_parser(prog_name)
        parser.add_argument("results", nargs="+")
        return parser

    def load_formatter_plugins(self):
        super(CollectResults, self).load_formatter_plugins()
        self.formatters["custom"] = CustomPgfFormatter()

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


class CustomPgfFormatter(ListFormatter):
    def add_argument_group(self, parser):
        pass

    def _quote(self, data):
        return "{" + str(data) + "}"

    def emit_list(self, column_names, data, stdout, parsed_args):
        stdout.write(" ".join([self._quote(column_name) for column_name in column_names]) + "\n")
        for row in data:
            stdout.write(" ".join([self._quote(cell) for cell in row]) + "\n")
