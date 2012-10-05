import json
import pathlib

query_images = []
source_images = []
sr = pathlib.Path("/media/data0/unsorted/sketches/png/")
category_paths = [p for p in sr if p.is_dir()][:50]
for category_path in category_paths:
    category_images = list(category_path)
    category_name = str(category_path.parts[-1])
    query_images.append(dict(
        query_image=str(category_images[0]),
        key=category_name,
        ))
    source_images += [str(i) for i in category_images[1:]]
print json.dumps(dict(
    images=query_images,
    source_images=source_images,
    ), indent=4)
