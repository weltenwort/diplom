#from pprint import pprint

import datetime
import os

import baker
from matplotlib import pyplot
from mpl_toolkits.axes_grid1 import ImageGrid
from pyct import fdct2

@baker.command
def create(filename, channel=0, scales=3, angles=12, output_dir=None, output_pattern="{prefix}_{scale}_{angle}.png"):
    if not output_dir:
        output_dir = datetime.datetime.now().strftime(filename + "_%Y%m%d%H%M%S")

    if os.path.exists(output_dir):
        print("Error: Output directory '{}' already exists.".format(output_dir))
        return

    print("Reading channel {} of file '{}'...".format(channel, filename))
    image = pyplot.imread(filename)[:, :, channel]

    print("Applying curvelet transform on {} scales and {} angles...".format(scales, angles))
    transformation = fdct2(image.shape, scales, angles, True, norm=True)
    cl = transformation.fwd(image)

    file_path, file_tail = os.path.split(filename)
    file_prefix, file_ext = os.path.splitext(file_tail)

    angles = [1, ] + [angles] * (scales - 1)

    print("Writing output to directory '{}'...".format(output_dir))
    os.mkdir(output_dir)
    for scale in range(scales):
        for angle in range(angles[scale]):
            fig = pyplot.figure()
            axes = fig.gca()
            cl_image = cl(scale, angle)

            mappable = axes.imshow(cl_image)
            fig.colorbar(mappable, ax=axes)
            fig.savefig(os.path.join(output_dir, output_pattern.format(
                prefix = file_prefix,
                scale  = scale,
                angle  = angle,
                )),
                format = "png",
                )

def show_fdct(filename, channel=0, scales=4, angles=16):
    image = pyplot.imread(filename)[:, :, channel]
    transformation = fdct2(image.shape, scales, angles, True, norm=True)

    cl = transformation.fwd(image)

    #fig, axs = pyplot.subplots(angles, scales + 1)
    pyplot.spectral()
    fig = pyplot.figure(1)

    # display original image
    #img_orig = axs[0, 0].imshow(image)
    img_orig = pyplot.imshow(image)
    pyplot.colorbar(orientation="horizontal")
    #pyplot.colorbar(img_orig, ax=axs[0, 0], orientation="horizontal")

    #imgs = []
    angles = [1, ] + [angles] * (scales - 1)
    for scale in range(scales):
        fig = pyplot.figure(scale + 100)
        grid = ImageGrid(fig, 111, (1, angles[scale]))
        for angle in range(angles[scale]):
            print("displaying",scale,angle)
            cl_img = cl(scale, angle)
            print(cl_img.shape)
            grid[angle].imshow(cl_img)
            #img = axs[0, scale + 1].imshow(cl_img)
        #pyplot.colorbar(img, ax=axs[0, scale + 1], orientation="horizontal")
        #imgs.append(img)

    pyplot.show()

baker.run()
