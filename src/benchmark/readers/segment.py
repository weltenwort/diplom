from scipy.misc import imread


def execute(image_filename, data):
    image = imread(image_filename, flatten=True)
    return image / image.max()
