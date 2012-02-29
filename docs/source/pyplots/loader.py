import json
import pickle
import re

import numpy


def load_result(result_directory):
    mean_correlation = numpy.loadtxt(str(result_directory["correlation.mean"]))
    correlations = numpy.loadtxt(str(result_directory["correlations"]))
    with result_directory["sketches.order"].open() as f:
        sketches = [line.strip() for line in f.readlines()]
    if result_directory["parameters.pickle"].exists():
        with result_directory["parameters.pickle"].open() as f:
            parameters = pickle.load(f)
    elif result_directory["parameters.json"].exists():
        with result_directory["parameters.json"].open() as f:
            parameters = json.load(f)

    return dict(
            mean_correlation=mean_correlation,
            correlations=correlations,
            parameters=parameters,
            sketches=sketches,
            )


def load_results(results_directory):
    return [load_result(d) for d in results_directory]


def format_label(result):
    return "{parameters[feature_extractor]}, {parameters[metric]}".format(
            parameters=result["parameters"],
            )


def naturally_sorted(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)
