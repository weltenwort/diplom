import json
import pathlib
study = {
        "category_map": {},
        "category_size": {}
        }
sr = pathlib.Path("/media/data0/unsorted/sketches/png/")
for category_path in sr:
    if category_path.is_dir():
        category_name = str(category_path.parts[-1])
        category_images = list(category_path)
        #study[str(category_images[0])] = [str(i) for i in category_images[1:]]
        for category_image in category_images:
            study["category_map"][str(category_image)] = category_name
        study["category_size"][category_name] = len(category_images)
print json.dumps(study)
#with open("/home/laeroth/Documents/inf/dipl/repo/src/benchmark/pr_study.json", "w") as fp:
    #json.dump(study, fp, indent=4)
