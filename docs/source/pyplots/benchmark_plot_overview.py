import matplotlib.pyplot as pyplot
import numpy
from pathlib import Path

from benchmark_loader import load_benchmarks


results = load_benchmarks(Path("../benchmark").resolve())

indices = numpy.arange(len(results))
labels = [r.get("label", "") for r in results]
mean_correlations = [r["mean_correlation"] for r in results]
colors = [r["plot_color"] for r in results]

pyplot.gcf().set_size_inches((12, 12), forward=True)

pyplot.ylabel("Mean Correlation to User Study")
pyplot.xticks(indices + 0.4, labels, rotation=90)
pyplot.bar(indices, mean_correlations, color=colors)

pyplot.tight_layout()
pyplot.show()
