import matplotlib.pyplot as pyplot
import numpy
from pathlib import Path

from benchmark_loader import load_benchmarks


results = load_benchmarks(Path("../benchmark").resolve())

indices = numpy.arange(len(results))
labels = [r.get("label", "") for r in results]
mean_correlations = [r["mean_correlation"] for r in results]
colors = [r["plot_color"] for r in results]

pyplot.ylabel("Mean Correlation to User Study")
pyplot.xticks(indices + 0.4, labels, rotation=80)
pyplot.bar(indices, mean_correlations, color=colors)

pyplot.tight_layout()
pyplot.show()
