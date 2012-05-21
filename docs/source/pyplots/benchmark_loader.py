import json
import re

import numpy
import pathlib
import matplotlib.pyplot as pyplot


def load_benchmark(benchmark_file):
    with pathlib.Path(benchmark_file).open("r") as fp:
        data = json.load(fp)
    data["sphinx_benchmark_path"] = str(benchmark_file)
    data["label"] = benchmark_file.parts[-1].split(".")[0]
    return data


def load_benchmarks(benchmarks_directory):
    benchmarks_directory = pathlib.Path(benchmarks_directory)
    benchmarks = sorted([load_benchmark(f) for f\
            in benchmarks_directory.glob("*.json")],\
            key=lambda x: x.get("label", ""))

    color_map = [pyplot.cm.hsv(x) for x in\
            numpy.linspace(0, 1, len(benchmarks) + 1)]
    for benchmark, color in zip(benchmarks, color_map):
        benchmark["plot_color"] = color
    return benchmarks


def naturally_sorted(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)
