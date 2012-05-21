from scipy.misc import imread
from skimage.filter import canny


def execute(image_filename, data):
    image = imread(image_filename, flatten=True)
    image /= image.max()
    return canny(image, sigma=3)
