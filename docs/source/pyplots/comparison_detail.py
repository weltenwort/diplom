import collections
#import sys

import matplotlib.pyplot as pyplot
import numpy
from pathlib import Path

from loader import format_label, load_results, naturally_sorted

results = load_results(Path("../results").resolve())

bar_width = 0.8 / len(results)
indices = numpy.arange(len(results[0]["correlations"]))

sketch_correlations = collections.defaultdict(dict)
for result_index, result in enumerate(results):
    for sketch_index, sketch in enumerate(result["sketches"]):
        sketch_correlations[sketch][result_index] =\
                result["correlations"][sketch_index]

sketches = naturally_sorted(sketch_correlations.keys())

bar_plots = []
for result_index, result in enumerate(results):
    correlations = [sketch_correlations[s][result_index] for s in sketches]
    bar_plots.append(pyplot.bar(
        indices + bar_width * result_index,
        correlations,
        width=bar_width,
        color=result["plot_color"],
        label=format_label(result),
        ))

pyplot.ylabel("Correlations to User Study")
pyplot.xlabel("Query Sketches")
pyplot.xticks(indices + 0.4, sketches, rotation=80)

pyplot.legend(loc="lower right", prop={"size": "small"})\
        .get_frame().set_alpha(0.5)
pyplot.grid(True)
pyplot.tight_layout()
pyplot.show()
