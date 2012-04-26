from scipy.misc import imread
from skimage.filter import canny


def read_image(image_filename, parameters):
    image = imread(image_filename, flatten=True)
    image /= image.max()
    return canny(image, sigma=3)
