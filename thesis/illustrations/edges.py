# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 11:46:57 2012

@author: laeroth
"""

import matplotlib.pyplot as pyplot
from mpl_toolkits.axes_grid1 import make_axes_locatable

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

luma_img = read_luma(FILENAME, DATA)
canny_img = read_canny(FILENAME, DATA)
sobel_img = read_sobel(FILENAME, DATA)


def show_image(image):
    fig = pyplot.figure()
    ax = fig.add_subplot(111)
    aximg = ax.imshow(image, interpolation="nearest")
    aximg.set_cmap("binary_r")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size=0.1, pad=0.05)
    fig.colorbar(aximg, cax=cax)
    pyplot.tight_layout()
