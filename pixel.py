import os
import os.path as osp
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from time import time
import sys


class Pixel(object):

    def __init__(self,
                 image,
                 orientation='vertical',
                 halign='center',
                 valign='center',
                 dimension='1',
                 colours='all',
                 pixelsize='1'):
        self.start_time = time()
        self.__image__(image)
        self.__orientation__(orientation)
        self.__halign__(halign)
        self.__valign__(valign)
        self.__dimension__(dimension)
        self.__colours__(colours)
        self.__pixelsize__(pixelsize)
        print(f'Time to setup: {self.timer()}')
        
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
            self.pixelplate = (50, 40)
        else:
            self.pixelplate = (40, 50)

    def __halign__(self, halign):
        self.halign = halign
        if self.halign == 'left':
            self.yalign = 0.
        elif self.halign == 'right':
            self.yalign = 1.
        elif self.halign == 'center':
            self.yalign = 0.5
        elif self.halign == 'centre':
            self.yalign = 0.5
        else:
            self.yalign = float(self.halign)

    def __valign__(self, valign):
        self.valign = valign
        if self.valign == 'bottom':
            self.xalign = 0.
        elif self.valign == 'top':
            self.xalign = 1.
        elif self.valign == 'center':
            self.xalign = 0.5
        elif self.valign == 'centre':
            self.xalign = 0.5
        else:
            self.xalign = float(self.valign)
        self.xalign = 1 - self.xalign

    def __dimension__(self, dimension):
        assert dimension.count('x') <= 1
        self.dimension = dimension
        if 'x' not in self.dimension:
            self.ydim = int(self.dimension)
            self.xdim = int(self.dimension)
        else:
            self.ydim, self.xdim = self.dimension.split('x')
            self.ydim = int(self.ydim)
            self.xdim = int(self.xdim)

        self.nx = self.pixelplate[0]*self.xdim
        self.ny = self.pixelplate[1]*self.ydim
        self.mult = min(
            int(self.imx/self.nx),
            int(self.imy/self.ny),
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
        assert pixelsize.count('x') <= 1
        self.pixelsize = pixelsize
        if 'x' not in self.pixelsize:
            self.xps = int(self.pixelsize)
            self.yps = int(self.pixelsize)
        else:
            self.yps, self.xps = self.pixelsize.split('x')
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

    @staticmethod
    def time_to_string(t):
        hours = int(t/3600)
        minutes = int((t - 3600*hours)/60)
        seconds = int(t - 3600*hours - 60*minutes)
        if hours:
            s = f'{hours}h{minutes}m{seconds}s'
        elif minutes:
            s = f'{minutes}m{seconds}s'
        else:
            s = f'{seconds}s'
        return s

    def timer(self):
        return self.time_to_string(time() - self.start_time)

    def reduce_im(self):
        print(f'0% of reduced image: {self.timer()}')
        self.rim = np.zeros((self.nx, self.ny, 3))
        for i in range(self.nx):
            for j in range(self.ny):
                self.rim[i,j,:] = np.mean(np.mean(
                    self.im[
                        self.dx + self.mult*i:self.dx + self.mult + self.mult*i,
                        self.dy + self.mult*j:self.dy + self.mult + self.mult*j,
                    :],
                axis=0), axis=0)
                perc = int(100*(1 + i*self.ny + j)/(self.nx*self.ny))
                sys.stdout.write('\033[F\033[K')
                print(f'{perc}% of reduced image: {self.timer()}')
        sys.stdout.write('\033[F\033[K')
        print(f'Time to reduce image: {self.timer()}')

    def saverim(self):
        fig = plt.figure(figsize=(self.ny, self.nx), dpi=1)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        ax = fig.add_subplot()
        ax.axis('off')
        ax.set_xlim(xmin=0, xmax=self.ny)
        ax.set_ylim(ymin=0, ymax=self.nx)
        ax.imshow(self.rim, extent=(0, self.ny, 0, self.nx))
        fig.savefig('rim.png')

    def pixel_im(self):
        colour_options = self.get_colour_options()
        print(f'0% of pixel image: {self.timer()}')
        self.pim = np.zeros((self.nx, self.ny, 3), dtype=float)
        self.nim = np.zeros((self.nx, self.ny), dtype=int)
        xsteps = int(self.nx/self.xps)
        ysteps = int(self.ny/self.yps)
        for i in range(xsteps):
            for j in range(ysteps):
                block = self.rim[
                    i*self.xps:i*self.xps + self.xps,
                    j*self.yps:j*self.yps + self.yps,
                :]
                best_mean = 1
                best_dist = 1
                for colour, option in colour_options:
                    D = block - colour
                    mean = np.mean(np.abs(np.mean(np.mean(D, axis=0), axis=0)))
                    if mean <= best_mean + 1e-10:
                        best_mean = mean
                        dist = np.mean(np.abs(D))
                        if dist < best_dist:
                            best_dist = dist
                            self.pim[
                                i*self.xps:i*self.xps + self.xps,
                                j*self.yps:j*self.yps + self.yps,
                            :] = colour
                            self.nim[
                                i*self.xps:i*self.xps + self.xps,
                                j*self.yps:j*self.yps + self.yps,
                            ] = option
                perc = int(100*(1 + i*ysteps + j)/(xsteps*ysteps))
                sys.stdout.write('\033[F\033[K')
                print(f'{perc}% of pixel image: {self.timer()}')
        sys.stdout.write('\033[F\033[K')
        print(f'Time to pixel image: {self.timer()}')

    def get_colour_options(self):
        assert len(self.rgb)**(self.xps*self.yps) < 1e5
        colour_options = [(
            np.zeros((self.xps, self.yps, 3), dtype=float),
            np.zeros((self.xps, self.yps), dtype=int),
        )]
        for i in range(self.xps):
            for j in range(self.yps):
                pre_options = colour_options.copy()
                colour_options = []
                for colour, option in pre_options:
                    for number, rgb in self.rgb.items():
                        colour[i,j,:] = rgb
                        option[i,j] = number
                        colour_options.append((
                            colour.copy(),
                            option.copy(),
                        ))
        print(f'Time to get colour options: {self.timer()}')
        return colour_options

    def savepim(self):
        fig = plt.figure(figsize=(self.ny, self.nx), dpi=1)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        ax = fig.add_subplot()
        ax.axis('off')
        ax.set_xlim(xmin=0, xmax=self.ny)
        ax.set_ylim(ymin=0, ymax=self.nx)
        ax.imshow(self.pim, extent=(0, self.ny, 0, self.nx))
        fig.savefig('pim.png')

    def run(self):
        self.reduce_im()
        self.saverim()
        self.pixel_im()
        self.savepim()
