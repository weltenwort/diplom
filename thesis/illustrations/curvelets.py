# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 11:46:57 2012

@author: laeroth
"""
import os

import matplotlib.pyplot as pyplot
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy

from readers.canny import execute as read_canny
from transforms.curvelet import execute as curvelet_transform
from features.patch_means import iter_lin_slices

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
        "features": {
            "grid_size": 8,
            "patch_size": 3,
        },
    },
}


def extract_means(coefficients, data):
    grid_size = data["config"]["features"]["grid_size"]

    x_slices = list(iter_lin_slices(0, coefficients.shape[1], grid_size))
    y_slices = list(iter_lin_slices(0, coefficients.shape[0], grid_size))
    grid_cells = [[coefficients[y, x] for x in x_slices] for y in y_slices]
    means = numpy.array([[numpy.mean(grid_cells[y][x]) for x in range(grid_size)] for y in range(grid_size)])

    return means

canny_img = read_canny(FILENAME, DATA)
curvelet_coefficients = curvelet_transform(canny_img, DATA)
curvelet_img = numpy.rot90(curvelet_coefficients["1,3"], 3)
means_img = extract_means(curvelet_img, DATA)

all_images = [
        {"filename": "signature_example_curvelet.pdf", "image": curvelet_img},
        {"filename": "signature_example_curvelet_means.pdf", "image": means_img},
        ]


def show_image(image, size=(4, 3), colorbar=True):
    fig = pyplot.figure(
            figsize=size,
            )
    ax = fig.add_subplot(111)
    aximg = ax.imshow(image, interpolation="nearest")
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
    show_image(curvelet_img)
    show_image(means_img)
    save_all(all_images, "/home/laeroth/Documents/inf/dipl/repo/thesis/illustrations/")
    save_all(all_images[-1:], "/home/laeroth/Documents/inf/dipl/repo/thesis/illustrations/")
