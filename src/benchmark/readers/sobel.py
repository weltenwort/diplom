from scipy.misc import imread
from skimage.filter import sobel


def execute(image_filename, data):
    image = imread(image_filename, flatten=True)
    image /= image.max()
    return sobel(image)
