import json

from cliff.lister import Lister
from cliff.formatters.base import ListFormatter
import pathlib


TRANSLATIONS = {
        "metrics.l2_means": "$L_2$",
        "metrics.cosine_means": "COS",
        "metrics.histogram_intersection": "HI",
        "metrics.histogram_intersection_binary": "HIB",
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

        for result_filename in args.results:
            result_path = pathlib.Path(result_filename)
            with result_path.open() as fp:
                result_info = json.load(fp)
            config = result_info.get("config", {})

            correlations_keys = sorted(result_info["correlations"].keys())

            results.append([
                str(result_path.parts[-1]).replace("_", "\_"),
                result_info["mean_correlation"],
                self._format_description(result_info),
                config.get("curvelets", {}).get("scales", ""),
                config.get("curvelets", {}).get("angles", ""),
                config.get("features", {}).get("grid_size", ""),
                config.get("features", {}).get("patch_size", ""),
                config.get("readers", {}).get("canny_sigma", ""),
                TRANSLATIONS.get(config.get("metric", {}).get("metric", ""), ""),
                ] + [result_info["correlations"][p] for p in correlations_keys])

        return (
                ["ConfigFilename", "MeanCorrelation", "Description", "scales", "angles", "gridsize", "patchsize", "cannysigma", "metric"] + [str(pathlib.Path(str(p)).parts[-1]) for p in correlations_keys],
                sorted(results, key=lambda x: x[3:8]),
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
