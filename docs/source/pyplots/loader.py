import json
import pickle
import re

from matplotlib import pyplot
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
            path=result_directory,
            label=result_directory.parts[-1],
            mean_correlation=mean_correlation,
            correlations=correlations,
            parameters=parameters,
            sketches=sketches,
            )


def load_results(results_directory):
    results = [load_result(d) for d in results_directory]

    color_map = [pyplot.cm.hsv(x) for x in\
            numpy.linspace(0, 1, len(results) + 1)]
    for result, color in zip(results, color_map):
        result["plot_color"] = color

    return results


def format_label(result):
    return result["label"]
    #return "{parameters[feature_extractor]}, {parameters[metric]}".format(
            #parameters=result["parameters"],
            #)


def naturally_sorted(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)
