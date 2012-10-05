import json
import pathlib
study = {}
sr = pathlib.Path("/media/data0/unsorted/sketches/png/")
for category_path in sr:
    if category_path.is_dir():
        category_images = list(category_path)
        study[str(category_images[0])] = [str(i) for i in category_images[1:]]
with open("/home/laeroth/Documents/inf/dipl/repo/src/benchmark/pr_study.json", "w") as fp:
    json.dump(study, fp, indent=4)
