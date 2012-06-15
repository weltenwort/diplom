from scipy.misc import imread
from skimage.filter import canny


def execute(image_filename, data):
    sigma = data["config"]["readers"]["canny_sigma"]
    image = imread(image_filename, flatten=True)
    image /= image.max()
    return canny(image, sigma=sigma)
