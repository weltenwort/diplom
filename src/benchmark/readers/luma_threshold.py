from scipy.misc import imread


def execute(image_filename, data):
    image = imread(image_filename, flatten=True)
    image = image / image.max()
    image[image >= data["config"]["readers"]["threshold"]] = 1.0
    image[image < data["config"]["readers"]["threshold"]] = 0.0
    return image
