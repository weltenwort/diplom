#from pprint import pprint

from matplotlib import pyplot
from mpl_toolkits.axes_grid1 import ImageGrid
from pyct import fdct2


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

show_fdct("square.png", scales=3, angles=8)
