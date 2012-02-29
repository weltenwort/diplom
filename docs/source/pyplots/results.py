import json
import pickle

import matplotlib.pyplot as pyplot
import numpy
from pathlib import Path


def load_result(result_directory):
    mean_correlation = numpy.loadtxt(str(result_directory["correlation.mean"]))
    correlations = numpy.loadtxt(str(result_directory["correlations"]))
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
            )


def load_results(results_directory):
    return [load_result(d) for d in results_directory]


def format_label(result):
    return "{parameters[feature_extractor]}, {parameters[metric]}".format(
            parameters=result["parameters"],
            )


def plot_comparison():
    results = load_results(Path("../results").resolve())

    indices = numpy.arange(len(results))
    labels = [format_label(r) for r in results]
    mean_correlations = [r["mean_correlation"] for r in results]

    pyplot.ylabel("Mean Correlation to User Study")
    pyplot.xticks(indices + 0.4, labels, rotation=80)
    pyplot.bar(indices, mean_correlations)

    pyplot.tight_layout()
    pyplot.show()


def plot_comparison_detail():
    results = load_results(Path("../results").resolve())

    indices = numpy.arange(len(results))
    #labels = [format_label(r) for r in results]
    #correlations = [r["correlations"] for r in results]

    bar_plots = []
    for result in results:
        correlations = result["correlations"]
        bar_plots.append(pyplot.bar(indices, correlations))

    pyplot.ylabel("Correlations to User Study")
    #pyplot.xticks(indices + 0.4, labels, rotation=80)

    pyplot.tight_layout()
    pyplot.show()
