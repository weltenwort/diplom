# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 11:46:57 2012

@author: laeroth
"""
import os

import matplotlib.pyplot as pyplot
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.misc import imread

from readers.luma import execute as read_luma
from readers.canny import execute as read_canny
from readers.sobel import execute as read_sobel

FILENAME = "/home/laeroth/Downloads/benchmark/images/2/376090783.jpg"
DATA = {
    "config": {
        "readers": {
            "canny_sigma": 1.5,
        },
        "curvelets": {
            "angles": 12,
            "scales": 4,
        },
    },
}

color_img = imread(FILENAME)
luma_img = read_luma(FILENAME, DATA)
canny_img = read_canny(FILENAME, DATA)
sobel_img = read_sobel(FILENAME, DATA)

all_images = [
        {"filename": "input_example_color.pdf", "image": color_img, "colorbar": False},
        {"filename": "input_example_luma.pdf", "image": luma_img},
        {"filename": "input_example_sobel.pdf", "image": sobel_img},
        {"filename": "input_example_canny.pdf", "image": canny_img},
        ]


def show_image(image, size=(4, 3), colorbar=True):
    fig = pyplot.figure(
            figsize=size,
            )
    ax = fig.add_subplot(111)
    aximg = ax.imshow(image)  # , interpolation="nearest")
    aximg.set_cmap("binary_r")
    if colorbar:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size=0.1, pad=0.05)
        fig.colorbar(aximg, cax=cax)
    pyplot.tight_layout()
    return fig


def save_image(image, filename, **kwargs):
    fig = show_image(image, **kwargs)
    pyplot.savefig(filename)
    pyplot.close(fig)


def save_all(images, directory):
    for image_params in images:
        params = {}
        params.update(image_params)
        params["filename"] = os.path.join(directory, params["filename"])

        save_image(**params)


def examples():
    save_all(all_images, "/home/laeroth/Documents/inf/dipl/repo/thesis/illustrations/")
