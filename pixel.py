import os
import os.path as osp
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from time import time
import sys
import shutil
from sklearn.cluster import KMeans

from __init__ import PixelInit


class Pixel(PixelInit):

    def __init__(self, draft, dpi, **kwargs):
        super().__init__(**kwargs)
        self.draft = draft
        self.dpi = dpi
        folder, file = osp.split(self.image)
        file = osp.splitext(file)[0]
        self.save_dir = osp.join(folder, f'output:{file}')
        if osp.exists(self.save_dir):
            shutil.rmtree(self.save_dir)
        os.makedirs(self.save_dir)
        self.run()

    def get_colour_options(self):
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
        colour, option = zip(*colour_options)
        colour = np.stack(colour, axis=-1)
        option = np.stack(option, axis=-1)
        print(f'Time to get colour options: {self.timer()}')
        return colour, option

    def pixel_im(self):
        print(f'0% of pixel image: {self.timer()}')
        colour, option = self.get_colour_options()
        self.pim = np.zeros((self.nx, self.ny, 3), dtype=float)
        self.nim = np.zeros((self.nx, self.ny), dtype=int)
        xsteps = int(self.nx/self.xps)
        ysteps = int(self.ny/self.yps)
        for i in range(xsteps):
            for j in range(ysteps):
                block = np.stack([self.rim[
                    i*self.xps:i*self.xps + self.xps,
                    j*self.yps:j*self.yps + self.yps,
                :]], axis=-1)
                D = block - colour
                mean = np.mean(np.abs(np.mean(np.mean(D, axis=0), axis=0)), axis=0)
                dist = np.mean(np.mean(np.mean(np.abs(D), axis=0), axis=0), axis=0)
                dist += mean > np.min(mean)
                index = np.argmin(dist)
                self.pim[
                    i*self.xps:i*self.xps + self.xps,
                    j*self.yps:j*self.yps + self.yps,
                    :] = colour[:,:,:,index]
                self.nim[
                    i*self.xps:i*self.xps + self.xps,
                    j*self.yps:j*self.yps + self.yps,
                    ] = option[:,:,index]
                perc = int(100*(1 + i*ysteps + j)/(xsteps*ysteps))
                sys.stdout.write('\033[F\033[K')
                print(f'{perc}% of pixel image: {self.timer()}')
        sys.stdout.write('\033[F\033[K')
        print(f'Time to pixelize image: {self.timer()}')

    def savepim(self):
        fig = plt.figure(figsize=(self.ny, self.nx), dpi=self.dpi)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        ax = fig.add_subplot()
        ax.axis('off')
        ax.set_xlim(xmin=0, xmax=self.ny)
        ax.set_ylim(ymin=0, ymax=self.nx)
        ax.imshow(self.pim, extent=(0, self.ny, 0, self.nx))
        fig.savefig(osp.join(self.save_dir, 'image.png'))
        plt.close()

    def savenim(self):
        if not osp.exists(osp.join(self.save_dir, 'nims')):
            os.makedirs(osp.join(self.save_dir, 'nims'))
        self.plates = {}
        for num in np.unique(self.nim):
            fig = plt.figure(figsize=(self.ny, self.nx), dpi=self.dpi)
            fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
            ax = fig.add_subplot()
            ax.axis('off')
            ax.set_xlim(xmin=0, xmax=self.ny)
            ax.set_ylim(ymin=0, ymax=self.nx)
            ax.imshow(self.nim != num, cmap='gray', extent=(0, self.ny, 0, self.nx))
            count = int(np.sum(self.nim == num))
            plates = int(np.ceil(count/(6*6*4 - 4)))
            self.plates[int(num)] = {
                'plates' : plates,
                'pixels' : count,
                'extras' : (6*6*4 - 4)*plates - count,
            }
            fig.savefig(osp.join(self.save_dir, 'nims', f'{num}:{count}({plates}).png'))
            plt.close()
        with open(osp.join(self.save_dir, 'plates.json'), 'w') as p:
            json.dump(self.plates, p, indent=2)

    def saveplates(self):
        print(f'0% of pixel plates: {self.timer()}')
        if not osp.exists(osp.join(self.save_dir, 'templates')):
            os.makedirs(osp.join(self.save_dir, 'templates'))
        figsize = (40, 50)
        xmax = 40
        ymax = 50
        plateshift = (4, 5)
        platewidth = 63*40/100
        plateheight = 63*50/100
        extent = (
            plateshift[0],
            plateshift[0] + platewidth,
            plateshift[1],
            plateshift[1] + plateheight,
        )
        for i in range(self.xdim):
            for j in range(self.ydim):
                nim_plate = self.nim[
                        i*self.pixelplate[0]:(i+1)*self.pixelplate[0],
                        j*self.pixelplate[1]:(j+1)*self.pixelplate[1],
                ]
                for num in np.unique(nim_plate):
                    fig = plt.figure(figsize=figsize, dpi=self.dpi)
                    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
                    ax = fig.add_subplot()
                    ax.axis('off')
                    ax.set_xlim(xmin=0, xmax=xmax)
                    ax.set_ylim(ymin=0, ymax=ymax)
                    im = nim_plate != num
                    if self.pixelplate[0] > self.pixelplate[1]:
                        im = im.T[::-1,:]
                    ax.imshow(im, cmap='gray', extent=extent)
                    for z in range(41):
                        ax.plot(
                            [plateshift[0] + z*platewidth/40, plateshift[0] + z*platewidth/40],
                            [plateshift[1], plateshift[1] + plateheight],
                            'gray',
                            lw=5
                        )
                    for z in range(51):
                        ax.plot(
                            [plateshift[0], plateshift[0] + platewidth],
                            [plateshift[1] + z*plateheight/50, plateshift[1] + z*plateheight/50],
                            'gray',
                            lw=5
                        )
                    fig.savefig(osp.join(self.save_dir, 'templates', f'{j+1}x{self.xdim-i}({num}).png'))
                    plt.close()
                perc = int(100*(1 + i*self.ydim + j)/(self.xdim*self.ydim))
                sys.stdout.write('\033[F\033[K')
                print(f'{perc}% of pixel plates: {self.timer()}')
        sys.stdout.write('\033[F\033[K')
        print(f'Time to get pixel plates: {self.timer()}')

    def run(self):
        self.pixel_im()
        self.savepim()
        if not self.draft:
            self.savenim()
            self.saveplates()
