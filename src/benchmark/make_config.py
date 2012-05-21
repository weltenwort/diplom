import argparse
import copy
import json

import pathlib


CONFIG_TEMPLATE = {
        "curvelets": {
            "scales": 4,
            "angles": 12,
            },
        "images": [],
        }


def sketch_num(path):
    return int(path.parts[-1].rsplit(".", 1)[0])


def run(args):
    results = copy.deepcopy(CONFIG_TEMPLATE)
    sketch_directory = pathlib.Path(args.sketch_directory)
    for index, sketch_path in enumerate(sorted(sketch_directory.glob("*.png"), key=sketch_num)):
        sketch_number = sketch_num(sketch_path)
        results["images"].append({
            "key": "set{}".format(sketch_number),
            "query_image": str(sketch_path),
            "source_images": [
                str(sketch_directory.parent().join("images", str(sketch_number), "*.jpg")),
                ]
            })
    print json.dumps(results, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sketch-directory", dest="sketch_directory",\
            required=True)
    run(parser.parse_args())
