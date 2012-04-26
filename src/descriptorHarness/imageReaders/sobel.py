from scipy.misc import imread
from skimage.filter import sobel


def read_image(image_filename, parameters):
    image = imread(image_filename, flatten=True)
    image /= image.max()
    return sobel(image)
