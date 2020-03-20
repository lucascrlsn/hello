from PIL import Image, ImageFilter
from matplotlib import pyplot as plt

source_image = '.jpeg'
source_image_outline = '.jpeg'
mosaic = '.jpeg'
final_image_name = '.jpeg'


def find_edges():
    # Utilizes from PIL import Image, ImageFilter
    # https://stackoverflow.com/questions/9319767/image-outline-using-python-pil
    image = Image.open(source_image)
    image = image.filter(ImageFilter.FIND_EDGES)
    image.save(source_image_outline)


def find_canny_edges():
    # Canny Edge Detection: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_canny/py_canny.html
    # Requires import cv2 import numpy as np from matplotlib import pyplot as plt
    img = cv2.imread(source_image, 0)
    edges = cv2.Canny(img, 100, 200)
    plt.subplot(121), plt.imshow(img, cmap='gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(edges, cmap='gray')
    plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
    plt.show()


def changeImageSize(maxWidth, maxHeight, image):
    # https://pythontic.com/image-processing/pillow/blend
    # Function to change the image size
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def blend_images():
    # https://pythontic.com/image-processing/pillow/blend
    # Take two images for blending them together
    image1 = Image.open(mosaic)
    image2 = Image.open(source_image_outline)
    # Make the images of uniform size
    image3 = changeImageSize(800, 500, image1)
    image4 = changeImageSize(800, 500, image2)
    # Make sure images got an alpha channel
    image5 = image3.convert('RGBA')
    image6 = image4.convert('RGBA')
    # Display the images
    # image5.show()
    # image6.show()
    # alpha-blend the images with varying values of alpha
    alphaBlended2 = Image.blend(image5, image6, alpha=.4)
    alphaBlended3 = Image.blend(image5, image6, alpha=.7)
    alphaBlended4 = Image.blend(image5, image6, alpha=.8)
    alphaBlended5 = Image.blend(image5, image6, alpha=.9)
    # Display the alpha-blended images
    alphaBlended2.show()
    alphaBlended3.show()
    alphaBlended4.show()
    alphaBlended5.show()




# find_canny_edges()


blend_images()