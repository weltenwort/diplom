import matplotlib.pyplot as pyplot
import numpy
from pathlib import Path

from loader import load_results, format_label


results = load_results(Path("../results").resolve())

indices = numpy.arange(len(results))
labels = [format_label(r) for r in results]
mean_correlations = [r["mean_correlation"] for r in results]
colors = [r["plot_color"] for r in results]

pyplot.ylabel("Mean Correlation to User Study")
pyplot.xticks(indices + 0.4, labels, rotation=80)
pyplot.bar(indices, mean_correlations, color=colors)

pyplot.tight_layout()
pyplot.show()
