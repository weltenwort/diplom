from scipy.misc import imread


def read_image(image_filename, parameters):
    image = imread(image_filename, flatten=True)
    return image / image.max()
