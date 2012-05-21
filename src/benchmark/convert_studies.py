import itertools
import json
import os
import sys

import numpy
import pathlib


def run(root_directory):
    root_directory = pathlib.Path(root_directory)
    sketch_order_filename = root_directory.join("sketches.order")
    image_order_filename = root_directory.join("images.order")
    study_directory = root_directory.join("study")
    sketch_directory = root_directory.join("sketches")
    image_directory = root_directory.join("images")

    image_sets = []
    with sketch_order_filename.open("r") as f_sketches,\
            image_order_filename.open("r") as f_images:
        for sketch_filename_rel, image_filename_line in itertools.izip(
                f_sketches, f_images):
            sketch_filename = str(sketch_directory.join(str(sketch_filename_rel.strip())))
            image_filenames = [
                    str(image_directory.join(str(ifn.strip())))\
                    for ifn in image_filename_line.split("\t")]
            image_sets.append(dict(
                sketch_filename=sketch_filename,
                image_filenames=image_filenames,
                ))

    studies = []
    for study_filename in study_directory.glob("*.study"):
        study = numpy.loadtxt(str(study_filename))
        studies.append(study[:study.shape[0] / 2])
    studies = numpy.dstack(studies)
    benchmark = numpy.mean(studies, axis=2)

    assert len(image_sets) == len(benchmark)

    results = {}
    for image_set, benchmark_scores in zip(image_sets, benchmark):
        results[image_set["sketch_filename"]] = \
                {f: s for f, s in zip(image_set["image_filenames"], benchmark_scores)}

    print json.dumps(results, indent=True)

if __name__ == "__main__":
    run(sys.argv[1])
