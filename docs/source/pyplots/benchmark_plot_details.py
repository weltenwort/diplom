import collections
import itertools

import matplotlib.pyplot as pyplot
import numpy
from pathlib import Path

from benchmark_loader import load_benchmarks, naturally_sorted



results = load_benchmarks(Path("../benchmark").resolve())

if len(results):
    sketch_filenames = list(reversed(naturally_sorted(list(set(itertools.chain.from_iterable(
        result["correlations"].keys() for result in results))))))
    indices = numpy.arange(len(sketch_filenames))

    bar_width = 0.8 / len(results)
    inches_per_sketch = 1
    padding = 0.2
    pyplot.gcf().set_size_inches((12, len(sketch_filenames) * inches_per_sketch), forward=True)

    #sketch_correlations = collections.defaultdict(dict)
    #for result_index, result in enumerate(results):
        #for sketch_index, sketch in enumerate(result["sketches"]):
            #sketch_correlations[sketch][result_index] =\
                    #result["correlations"][sketch_index]

    #sketches = naturally_sorted(sketch_correlations.keys())

    bar_plots = []
    for result_index, result in enumerate(results):
        #correlations = [sketch_correlations[s][result_index] for s in sketches]
        correlations = [result["correlations"][sketch_filename]\
                for sketch_filename in sketch_filenames]
        bar_plots.append(pyplot.barh(
            indices - bar_width * result_index,
            correlations,
            height=bar_width,
            #linewidth=0,
            color=result["plot_color"],
            label=result.get("label"),
            ))

    pyplot.ylim((indices.min() - 0.8 - padding, indices.max() + padding))
    pyplot.xlabel("Correlations to User Study")
    pyplot.ylabel("Query Sketches")
    pyplot.yticks(indices - 0.4, [Path(str(f)).parts[-1]\
            for f in sketch_filenames])
            #for f in sketch_filenames], rotation=80)

    pyplot.legend(loc="upper left", prop={"size": "small"})\
            .get_frame().set_alpha(0.5)
pyplot.grid(True)
pyplot.tight_layout()
pyplot.show()
