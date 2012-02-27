import pickle

import matplotlib.pyplot as pyplot
import numpy
from pathlib import Path


def load_result(result_directory):
    mean_correlation = numpy.loadtxt(str(result_directory["correlation.mean"]))
    with result_directory["parameters.pickle"].open() as f:
        parameters = pickle.load(f)
    return dict(
            mean_correlation=mean_correlation,
            parameters=parameters,
            )


def load_results(results_directory):
    return [load_result(d) for d in results_directory]


def plot_comparison():
    results = load_results(Path("../results").resolve())

    indices = numpy.arange(len(results))
    labels = [r["parameters"]["feature_extractor"] for r in results]
    mean_correlations = [r["mean_correlation"] for r in results]

    pyplot.ylabel("Mean Correlation to User Study")
    pyplot.xticks(indices + 0.4, labels, rotation=45)
    pyplot.bar(indices, mean_correlations)

    pyplot.tight_layout()
    pyplot.show()
