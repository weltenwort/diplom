# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 11:46:57 2012

@author: laeroth
"""
import os

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as pyplot
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
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


def show_insets(image, insets_coords, size=(6, 3)):
    fig = pyplot.figure(
            figsize=size,
            )

    line_colors = colors.LinearSegmentedColormap.from_list("line_colors", ["red", "blue"], len(insets_coords))

    gs = gridspec.GridSpec(len(insets_coords), 2)
    main_ax = fig.add_subplot(gs[:, 0])

    main_extent = (0, image.shape[1], image.shape[0], 0)
    main_ax_img = main_ax.imshow(image, interpolation="nearest", extent=main_extent, origin="upper")
    main_ax_img.set_cmap("binary_r")
    pyplot.setp(main_ax.get_yticklabels(), visible=False)
    pyplot.setp(main_ax.get_xticklabels(), visible=False)

    for inset_index, inset_coords in enumerate(insets_coords):
        inset_ax = fig.add_subplot(gs[inset_index, 1])
        inset_ax_img = inset_ax.imshow(image, interpolation="nearest", extent=main_extent, origin="upper")
        inset_ax_img.set_cmap("binary_r")
        inset_ax.set_ylim(inset_coords[0].stop, inset_coords[0].start)
        inset_ax.set_xlim(inset_coords[1].start, inset_coords[1].stop)
        pyplot.setp(inset_ax.get_yticklabels(), visible=False)
        pyplot.setp(inset_ax.get_xticklabels(), visible=False)
        mark_inset(main_ax, inset_ax, loc1=1, loc2=3, fc="none", ec=line_colors(inset_index))

    gs.tight_layout(fig)

    return fig


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


canny_img = read_canny(FILENAME, DATA)
curvelet_coefficients = curvelet_transform(canny_img, DATA)
curvelet_img = numpy.rot90(curvelet_coefficients["1,3"], 3)
means_img = extract_means(curvelet_img, DATA)

all_images = [
        {"filename": "signature_example_curvelet.pdf", "image": curvelet_img},
        {"filename": "signature_example_curvelet_means.pdf", "image": means_img},
        {
            "filename": "signature_example_curvelet_patches.pdf",
            "image": means_img,
            "factory_func": show_insets,
            "insets_coords": [(slice(0, 3), slice(0, 3)), (slice(1, 4), slice(0, 3)), (slice(2, 5), slice(0, 3))],
            },
        ]


def save_image(image, filename, factory_func=show_image, **kwargs):
    fig = factory_func(image, **kwargs)
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
    show_insets(means_img, [(slice(0, 3), slice(0, 3)), (slice(1, 4), slice(0, 3)), (slice(2, 5), slice(0, 3))])
