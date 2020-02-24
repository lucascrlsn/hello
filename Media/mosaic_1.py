import itertools
import random
import sys
import time
import datetime
from colorama import Fore, Back, Style, init

import os
import glob

import numpy as np
from PIL import Image
from skimage import img_as_float
from skimage.measure import compare_mse
Image.MAX_IMAGE_PIXELS = None
init()

# https://github.com/dvdtho/python-photo-mosaic/blob/master/mosaic.py
my_folder = '/Users/LucasCarlson/Documents/Python/hello/Media/pictures'

files = [os.path.join(r,file) for r,d,f in os.walk("F:\\_python") for file in f]
# User Added
image_count = 631


def shuffle_first_items(lst, i):
    if not i:
        return lst
    first_few = lst[:i]
    remaining = lst[i:]
    random.shuffle(first_few)
    return first_few + remaining


def bound(low, high, value):
    return max(low, min(high, value))


class ProgressCounter:
    def __init__(self, total):
        self.total = total
        self.counter = 0

    def update(self):
        self.counter += 1
        sys.stdout.write("Progress: %s%% %s" % (100 * self.counter / self.total, "\r"))
        sys.stdout.flush()


def img_mse(im1, im2):
    """Calculates the root mean square error (RSME) between two images"""
    try:
        return compare_mse(img_as_float(im1), img_as_float(im2))
    except ValueError:
        print(f'RMS issue, Img1: {im1.size[0]} {im1.size[1]}, Img2: {im2.size[0]} {im2.size[1]}')
        raise KeyboardInterrupt


def resize_box_aspect_crop_to_extent(img, target_aspect, centerpoint=None):
    width = img.size[0]
    height = img.size[1]
    if not centerpoint:
        centerpoint = (int(width / 2), int(height / 2))

    requested_target_x = centerpoint[0]
    requested_target_y = centerpoint[1]
    aspect = width / float(height)
    if aspect > target_aspect:
        # Then crop the left and right edges:
        new_width = int(target_aspect * height)
        new_width_half = int(new_width / 2)
        target_x = bound(new_width_half, width - new_width_half, requested_target_x)
        left = target_x - new_width_half
        right = target_x + new_width_half
        resize = (left, 0, right, height)
    else:
        # ... crop the top and bottom:
        new_height = int(width / target_aspect)
        new_height_half = int(new_height / 2)
        target_y = bound(new_height_half, height - new_height_half, requested_target_y)
        top = target_y - new_height_half
        bottom = target_y + new_height_half
        resize = (0, top, width, bottom)
    return resize


def aspect_crop_to_extent(img, target_aspect, centerpoint=None):
    '''
    Crop an image to the desired perspective at the maximum size available.
    Centerpoint can be provided to focus the crop to one side or another -
    eg just cut the left side off if interested in the right side.
    target_aspect = width / float(height)
    centerpoint = (width, height)
    '''
    resize = resize_box_aspect_crop_to_extent(img, target_aspect, centerpoint)
    return img.crop(resize)


class Config:
    def __init__(self, tile_ratio=1920 / 800, tile_width=50, enlargement=8, color_mode='RGB'):
        self.tile_ratio = tile_ratio  # 2.4
        self.tile_width = tile_width  # height/width of mosaic tiles in pixels
        self.enlargement = enlargement  # mosaic image will be this many times wider and taller than original
        self.color_mode = color_mode  # mosaic image will be this many times wider and taller than original

    @property
    def tile_height(self):
        return int(self.tile_width / self.tile_ratio)

    @property
    def tile_size(self):
        return self.tile_width, self.tile_height  # PIL expects (width, height)


class TileBox:
    """
    Container to import, process, hold, and compare all of the tiles
    we have to make the mosaic with.
    """

    def __init__(self, tile_paths, config):
        self.config = config
        self.tiles = list()
        self.prepare_tiles_from_paths(tile_paths)

    def __process_tile(self, tile_path):
        with Image.open(tile_path) as i:
            img = i.copy()
        img = aspect_crop_to_extent(img, self.config.tile_ratio)
        large_tile_img = img.resize(self.config.tile_size, Image.ANTIALIAS).convert(self.config.color_mode)
        self.tiles.append(large_tile_img)
        return True

    def prepare_tiles_from_paths(self, tile_paths):
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        print(Fore.RED + f'{timestamp} | Reading tiles from provided list...' + Style.RESET_ALL)
        progress = ProgressCounter(len(tile_paths))
        for tile_path in tile_paths:
            progress.update()
            self.__process_tile(tile_path)
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        print(Fore.RED + f'{timestamp} | Processed tiles.' + Style.RESET_ALL)
        return True

    def best_tile_block_match(self, tile_block_original):
        match_results = [img_mse(t, tile_block_original) for t in self.tiles]
        best_fit_tile_index = np.argmin(match_results)
        return best_fit_tile_index

    def best_tile_from_block(self, tile_block_original, reuse=False):
        if not self.tiles:
            timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            print(Fore.RED + f'{timestamp} | Ran out of images' + Style.RESET_ALL)
            reuse = True
            raise KeyboardInterrupt

        # start_time = time.time()
        i = self.best_tile_block_match(tile_block_original)
        # print("BLOCK MATCH took --- %s seconds ---" % (time.time() - start_time))
        match = self.tiles[i].copy()
        if not reuse:
            del self.tiles[i]
        return match


class SourceImage:
    """Processing original image - scaling and cropping as needed."""

    def __init__(self, image_path, config):
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        print(Fore.RED + f'{timestamp} | Processing main image...' + Style.RESET_ALL)
        self.image_path = image_path
        self.config = config

        with Image.open(self.image_path) as i:
            img = i.copy()
        w = img.size[0] * self.config.enlargement
        h = img.size[1] * self.config.enlargement
        large_img = img.resize((w, h), Image.ANTIALIAS)
        w_diff = (w % self.config.tile_width) / 2
        h_diff = (h % self.config.tile_height) / 2

        # if necessary, crop the image slightly so we use a
        # whole number of tiles horizontally and vertically
        if w_diff or h_diff:
            large_img = large_img.crop((w_diff, h_diff, w - w_diff, h - h_diff))

        self.image = large_img.convert(self.config.color_mode)
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        print(Fore.RED + f'{timestamp} | Main image processed.' + Style.RESET_ALL)


class MosaicImage:
    """Holder for the mosaic"""

    def __init__(self, original_img, target, config):
        self.config = config
        self.target = target
        # Lets just start with original image, scaled up, instead of a blank one
        self.image = original_img
        # self.image = Image.new(original_img.mode, original_img.size)
        self.x_tile_count = int(original_img.size[0] / self.config.tile_width)
        self.y_tile_count = int(original_img.size[1] / self.config.tile_height)
        self.total_tiles = self.x_tile_count * self.y_tile_count
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        print(Fore.RED + f'{timestamp} | Mosaic will be {self.x_tile_count:,} tiles wide and {self.y_tile_count:,} tiles high ({self.total_tiles:,} total).' + Style.RESET_ALL)

    def add_tile(self, tile, coords):
        """Adds the provided image onto the mosiac at the provided coords."""
        try:
            self.image.paste(tile, coords)
        except TypeError as e:
            print('Maybe the tiles are not the right size. ' + str(e))

    def save(self):
        self.image.save(self.target)


def coords_from_middle(x_count, y_count, y_bias=1, shuffle_first=0, ):
    '''
    Lets start in the middle where we have more images.
    And we dont get "lines" where the same-best images
    get used at the start.
    y_bias - if we are using non-square coords, we can
        influence the order to be closer to the real middle.
        If width is 2x height, y_bias should be 2.
    shuffle_first - We can suffle the first X coords
        so that we dont use all the same-best images
        in the same spot -  in the middle
    from movies.mosaic_mem import coords_from_middle
    x = 10
    y = 10
    coords_from_middle(x, y, y_bias=2, shuffle_first=0)
    '''
    x_mid = int(x_count / 2)
    y_mid = int(y_count / 2)
    coords = list(itertools.product(range(x_count), range(y_count)))
    coords.sort(key=lambda c: abs(c[0] - x_mid) * y_bias + abs(c[1] - y_mid))
    coords = shuffle_first_items(coords, shuffle_first)
    return coords


def create_mosaic(
        source_path='/Users/LucasCarlson/Downloads/mosaic/source/source.jpg',
        target='/Users/LucasCarlson/Downloads/mosaic/output/done.jpg',
        tile_ratio=1920 / 800,
        tile_width=300,
        enlargement=4,
        reuse=False,
        color_mode='RGB',
        tile_paths=None,
        shuffle_first=100):
    """Forms an mosiac from an original image using the best
    tiles provided. This reads, processes, and keeps in memory
    a copy of the source image, and all the tiles while processing.
    Arguments:
    source_path -- filepath to the source image for the mosiac
    target -- filepath to save the mosiac
    tile_ratio -- height/width of mosaic tiles in pixels
    tile_width -- width of mosaic tiles in pixels
    enlargement -- mosaic image will be this many times wider and taller than the original
    reuse -- Should we reuse tiles in the mosaic, or just use each tile once?
    color_mode -- L for greyscale or RGB for color
    tile_paths -- List of filepaths to your tiles
    shuffle_first -- Mosiac will be filled out starting in the center for best effect. Also,
        we will shuffle the order of assessment so that all of our best images aren't
        necessarily in one spot.
    """
    if tile_paths is None:
        tile_paths = [
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0996.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0982.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0981.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0759.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0942.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1083.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1269.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1097.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1068.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1040.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1054.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1731.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1916.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1902.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1917.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2588.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0406.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1718.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2211.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2205.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1055.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1041.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1069.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0162.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0604.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1096.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1082.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2007.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1254.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1308.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2601.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2167.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1334.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0994.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1877.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0983.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0997.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1863.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0599.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1650.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1136.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0968.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0558.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1646.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2401.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2373.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1691.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1685.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0981.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0995.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1450.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0955.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0941.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1256.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1094.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2011.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0612.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1080.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0835.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1057.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0809.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1043.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1054.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1097.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0411.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1042.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1056.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1081.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1095.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0149.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2038.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0968.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1486.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1492.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0001.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1479.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1323.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0994.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0980.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0571.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0559.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1653.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2362.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0575.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2404.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1119.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1643.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0984.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0990.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1680.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1858.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1469.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0005.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0039.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0950.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1091.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1085.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1509.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1535.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1052.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1046.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1284.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0830.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1079.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2564.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1045.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2558.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1938.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1086.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0399.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1736.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0414.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1285.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1047.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1053.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0158.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1520.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1084.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1090.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0951.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0010.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0776.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1468.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0991.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1871.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0985.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1124.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1130.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0206.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2411.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2377.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2405.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2407.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1640.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0978.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0993.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0987.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1697.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2605.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0012.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0990.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1086.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1092.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1244.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1045.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1051.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0833.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1079.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0359.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2214.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1709.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0826.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1292.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1078.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1050.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1093.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0167.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1087.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2638.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1331.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0985.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2176.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0986.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0992.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0979.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1133.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1127.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0211.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0577.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2360.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2412.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0538.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2449.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1140.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1154.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0289.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2677.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2663.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0921.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0882.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0114.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0855.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1587.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1023.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1037.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1034.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2529.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2501.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1785.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1975.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2299.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0465.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2500.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0317.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1753.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1035.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1036.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1022.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0868.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0840.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0667.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1237.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0908.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2104.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0061.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1419.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1357.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0277.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1157.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0513.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1816.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1802.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1355.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1341.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0077.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1396.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0936.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1382.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0659.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1553.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1008.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1034.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1020.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1751.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1779.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2502.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0472.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2271.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0466.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1778.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1021.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1035.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1009.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2073.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0894.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0923.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1383.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2661.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1368.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0270.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1620.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1185.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0714.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0072.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1378.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0933.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1393.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1224.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0890.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1031.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1025.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2088.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0847.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1019.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0476.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2249.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1754.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0339.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0477.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0305.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1018.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0852.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1024.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1030.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0661.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0098.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1386.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1345.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1351.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2658.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1379.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1190.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1806.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0259.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1147.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0503.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2472.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0265.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0517.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0273.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1637.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2458.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1810.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1353.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0930.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1233.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0139.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1026.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0878.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1032.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1582.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0844.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0307.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1019.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1031.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1757.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0449.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1780.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1795.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0460.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0306.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2505.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0845.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0851.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1597.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1033.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1027.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0886.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1540.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1391.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0931.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1385.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2667.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2101.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0299.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1811.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2303.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0519.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2468.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1613.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2440.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0280.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1363.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2656.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2124.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2642.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0900.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0914.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1388.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1217.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0135.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0653.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1559.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0874.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0690.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1002.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2087.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1016.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2520.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1029.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1983.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1955.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2284.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2535.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0478.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1766.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1014.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1017.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1003.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2045.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1564.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0929.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2643.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2657.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0040.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2131.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1376.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1809.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0256.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0518.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1162.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0532.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0526.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0283.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2494.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0724.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2655.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2682.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1228.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1029.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1015.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0687.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1001.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1980.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0334.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0485.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2287.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2250.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1000.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1014.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2091.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1028.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0862.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0889.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1567.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0902.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0916.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2132.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2654.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2640.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1375.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0282.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2481.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0527.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1605.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2320.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1629.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0523.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1615.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0292.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2644.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0047.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2650.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1403.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0912.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0641.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1577.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1010.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1004.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0696.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0866.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1038.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1749.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0319.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1775.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0495.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1947.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1774.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0456.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1748.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2533.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0324.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1039.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1005.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1011.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1204.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0654.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2043.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0898.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1364.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1370.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0734.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2645.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0287.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0522.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2447.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0520.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2323.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0534.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0508.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1170.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0285.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2647.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1414.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1399.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0911.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2055.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1007.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0859.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1013.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1992.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2257.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0468.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0497.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1789.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0483.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1763.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1005.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1039.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0327.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0870.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1012.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1006.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1213.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0125.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0910.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1367.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2646.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1824.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1165.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0535.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1670.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0974.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1658.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0552.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0234.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1300.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2609.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0750.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0963.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0977.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1499.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1512.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1274.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0618.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1506.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0156.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0624.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0817.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1049.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1061.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1075.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0368.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1704.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0426.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2231.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0383.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2594.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1922.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2581.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1074.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1060.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0194.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1048.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0802.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0619.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0779.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1467.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2436.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0975.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2378.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1103.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0551.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0545.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0977.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0988.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0586.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1840.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2391.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2144.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2636.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0974.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0960.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2187.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1089.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1263.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1076.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0828.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1062.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0419.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1908.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2597.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0394.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1935.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2582.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1706.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1063.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1077.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0815.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0801.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2031.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1088.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0949.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0020.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2637.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1458.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0989.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0976.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0550.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1666.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0966.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0972.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2419.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1104.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2380.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1689.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1851.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0583.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0999.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2627.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1098.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1073.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1067.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0811.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2551.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2545.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0434.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1070.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1919.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2587.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2578.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1059.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0347.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1066.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1072.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0838.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1515.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1099.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1273.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0145.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0623.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0794.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1461.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0025.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0031.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0998.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1850.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1663.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1111.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0973.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0227.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0967.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0971.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0965.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2340.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0219.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1675.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0580.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0999.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0741.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1311.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1517.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1064.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1070.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0184.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1058.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0806.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1729.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1715.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2585.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2591.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1099.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1933.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0344.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2235.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0422.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0350.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1059.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1071.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0185.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_1065.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1258.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0634.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1489.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0797.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0783.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2619.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas1338.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas2382.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/rachelandlucas0542.jpg',
            '/Users/LucasCarlson/Documents/Python/hello/Media/IMG_0970.jpg']
    config = Config(
        tile_ratio=tile_ratio,  # height/width of mosaic tiles in pixels
        tile_width=tile_width,  # height/width of mosaic tiles in pixels
        enlargement=enlargement,  # the mosaic image will be this many times wider and taller than the original
        color_mode=color_mode,  # L for greyscale or RGB for color
    )
    # Pull in and Process Original Image
    timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    print(Fore.RED + f'{timestamp} | Setting Up Target image' + Style.RESET_ALL)
    source_image = SourceImage(source_path, config)

    # Setup Mosaic
    mosaic = MosaicImage(source_image.image, target, config)

    # Assest Tiles, and save if needed, returns directories where the small and large pictures are stored
    timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    print(Fore.RED + f'{timestamp} | Assessing Tiles' + Style.RESET_ALL)
    tile_box = TileBox(tile_paths, config)

    try:
        progress = ProgressCounter(mosaic.total_tiles)
        for x, y in coords_from_middle(mosaic.x_tile_count, mosaic.y_tile_count, y_bias=config.tile_ratio,
                                       shuffle_first=shuffle_first):
            progress.update()

            # Make a box for this sector
            box_crop = (
            x * config.tile_width, y * config.tile_height, (x + 1) * config.tile_width, (y + 1) * config.tile_height)

            # Get Original Image Data for this Sector
            comparison_block = source_image.image.crop(box_crop)

            # Get Best Image name that matches the Orig Sector image
            tile_match = tile_box.best_tile_from_block(comparison_block, reuse=reuse)

            # Add Best Match to Mosaic
            mosaic.add_tile(tile_match, box_crop)

            # Saving Every Sector
            mosaic.save()

    except KeyboardInterrupt:
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        print(Fore.RED + f'{timestamp} | Stopping, saving partial image...' + Style.RESET_ALL)
    finally:
        mosaic.save()
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        print(Fore.RED + f'{timestamp} | Mosaic successfully saved at {target}' + Style.RESET_ALL)


create_mosaic()