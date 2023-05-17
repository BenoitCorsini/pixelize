import os
import os.path as osp
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb


class Pixel(object):

    def __init__(self,
                 image,
                 orientation='vertical',
                 align='center center',
                 dimension='1',
                 colours='all',
                 pixelsize='1'):
        self.__image__(image)
        self.__orientation__(orientation)
        self.__align__(align)
        self.__dimension__(dimension)
        self.__colours__(colours)
        self.__pixelsize__(pixelsize)
        
        self.run()

    def __image__(self, image):
        assert osp.exists(image)
        self.image = image
        self.im = plt.imread(self.image)
        if np.size(self.im, axis=-1) > 3:
            self.im = self.im[:,:,:3]*self.im[:,:,3:]
        if np.max(self.im) > 1:
            self.im = self.im/255
        self.imx = np.size(self.im, axis=0)
        self.imy = np.size(self.im, axis=1)

    def __orientation__(self, orientation):
        assert orientation in ['vertical', 'horizontal']
        self.orientation = orientation
        if self.orientation == 'vertical':
            self.pixelplate = (40, 50)
        else:
            self.pixelplate = (50, 40)

    def __align__(self, align):
        assert align.count('*') == 1
        self.align = align
        self.xalign, self.yalign = self.align.split('*')
        if self.xalign == 'left':
            self.xalign = 0.
        elif self.xalign == 'right':
            self.xalign = 1.
        elif self.xalign == 'center':
            self.xalign = 0.5
        elif self.xalign == 'centre':
            self.xalign = 0.5
        else:
            self.xalign = float(self.xalign)
        if self.yalign == 'bottom':
            self.yalign = 0.
        elif self.yalign == 'top':
            self.yalign = 1.
        elif self.yalign == 'center':
            self.yalign = 0.5
        elif self.yalign == 'centre':
            self.yalign = 0.5
        else:
            self.yalign = float(self.yalign)

    def __dimension__(self, dimension):
        assert dimension.count('*') <= 1
        self.dimension = dimension
        if '*' not in self.dimension:
            self.xdim = int(self.dimension)
            self.ydim = int(self.dimension)
        else:
            self.xdim, self.ydim = self.dimension.split('*')
            self.xdim = int(self.xdim)
            self.ydim = int(self.ydim)

        self.nx = self.pixelplate[0]*self.xdim
        self.ny = self.pixelplate[1]*self.ydim
        self.mult = min(
            int(self.imx/self.nx),
            int(self.imx/self.nx),
        )
        assert self.mult > 0
        self.dx = self.imx - self.mult*self.nx
        self.dx = int(0.5 + self.xalign*self.dx)
        self.dy = self.imy - self.mult*self.ny
        self.dy = int(0.5 + self.yalign*self.dy)

    def __colours__(self, colours, rgb_dict='rgb.json'):
        self.colours = colours
        with open(rgb_dict, 'r') as d:
            rgb = json.load(d)
        if self.colours == 'all':
            self.rgb = rgb.copy()
        else:
            if self.colours == 'primary':
                keys = 'blue-red-yellow'
            elif self.colours == 'simple':
                keys = 'b-g-r-c-m-y-k-w'
            elif self.colours == 'classic':
                keys = 'tab:blue'
                keys += '-tab:orange'
                keys += '-tab:green'
                keys += '-tab:red'
                keys += '-tab:purple'
                keys += '-tab:brown'
                keys += '-tab:pink'
                keys += '-tab:gray'
                keys += '-tab:olive'
                keys += '-tab:cyan'
                keys += '-white'
                keys += '-black'
            else:
                keys = self.colours

            rgb_keys = []
            for key in keys.split('-'):
                rgb_keys.append(self.key_to_rgb_key(key, rgb))
            self.rgb = {key : rgb[key] for key in sorted(rgb_keys)}

    def __pixelsize__(self, pixelsize):
        assert pixelsize.count('*') <= 1
        self.pixelsize = pixelsize
        if '*' not in self.pixelsize:
            self.xps = int(self.pixelsize)
            self.yps = int(self.pixelsize)
        else:
            self.xps, self.yps = self.pixelsize.split('*')
            self.xps = int(self.xps)
            self.yps = int(self.yps)

        assert (self.nx % self.xps) == 0
        assert (self.ny % self.yps) == 0

    @staticmethod
    def key_to_rgb_key(key, rgb):
        if key.isdigit():
            assert key in rgb
            return key
        else:
            key_colour = np.array(to_rgb(key))
            best_key = '000'
            best_dist = 1
            for rgb_key, rgb_colour in rgb.items():
                dist = np.mean((key_colour - np.array(rgb_colour))**2)
                if dist < best_dist:
                    best_key = rgb_key
                    best_dist = dist
            return best_key

    def reduce_im(self):
        print(self.im.shape)
        print(self.nx, self.ny)

    def run(self):
        self.reduce_im()
