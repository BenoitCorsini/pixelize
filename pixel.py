import os
import os.path as osp
import json
import numpy as np
import matplotlib.pyplot as plt
import sys
import shutil

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

    def set_image(self, im, figsize=None, extent=None, cmap=None):
        if figsize is None:
            figsize = self.pixelplate[::-1]
        if extent is None:
            extent = (0, figsize[0], 0, figsize[1])
        fig = plt.figure(figsize=figsize, dpi=self.dpi)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        ax = fig.add_subplot()
        ax.axis('off')
        ax.set_xlim(xmin=0, xmax=figsize[0])
        ax.set_ylim(ymin=0, ymax=figsize[1])
        ax.imshow(im, extent=extent, cmap=cmap)
        return fig, ax

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
        colour, option = self.get_colour_options()
        print(f'0% of pixel image: {self.timer()}')
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
        fig, ax = self.set_image(self.pim)
        fig.savefig(osp.join(self.save_dir, 'image.png'))
        plt.close()
        print(f'Time to pixelize image: {self.timer()}')

    def number_im(self):
        if not osp.exists(osp.join(self.save_dir, 'nims')):
            os.makedirs(osp.join(self.save_dir, 'nims'))
        self.plates = {}
        for num in np.unique(self.nim):
            count = int(np.sum(self.nim == num))
            plates = int(np.ceil(count/(6*6*4 - 4)))
            self.plates[int(num)] = {
                'plates' : plates,
                'pixels' : count,
                'extras' : (6*6*4 - 4)*plates - count,
            }
            fig, ax = self.set_image(self.nim != num, cmap='gray')
            fig.savefig(osp.join(self.save_dir, 'nims', f'{num}:{count}({plates}).png'))
            plt.close()
        with open(osp.join(self.save_dir, 'plates.json'), 'w') as p:
            json.dump(self.plates, p, indent=2)

    @staticmethod
    def draw_grid(ax, figsize, plateshift, platewidth, plateheight, colour='gray', lw=5):
        for x in range(1 + figsize[0]):
            ax.plot(
                [plateshift[0] + x*platewidth/figsize[0]]*2,
                [plateshift[1], plateshift[1] + plateheight],
                colour,
                lw=lw,
            )
        for y in range(1 + figsize[1]):
            ax.plot(
                [plateshift[0], plateshift[0] + platewidth],
                [plateshift[1] + y*plateheight/figsize[1]]*2,
                colour,
                lw=lw,
            )

    @staticmethod
    def draw_info(ax, info, x=2, y=2, fontsize=127, colour='gray'):
        ax.text(
            x=x,
            y=y,
            s=info,
            fontsize=fontsize,
            color=colour,
        )

    def plates_im(self, platewidth=63*40/100, plateheight=63*50/100):
        print(f'0% of pixel plates: {self.timer()}')
        if not osp.exists(osp.join(self.save_dir, 'plates')):
            os.makedirs(osp.join(self.save_dir, 'plates'))
        figsize = (40, 50)
        plateshift = (
            (figsize[0] - platewidth)/2,
            (figsize[1] - plateheight)/2,
        )
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
                    im = nim_plate != num
                    if self.pixelplate[0] < self.pixelplate[1]:
                        im = im.T[::-1,:]
                    fig, ax = self.set_image(im, figsize=figsize, cmap='gray', extent=extent)
                    plate_info = f'plate {j+1}x{self.xdim-i} (colour {num})'
                    self.draw_grid(ax, figsize, plateshift, platewidth, plateheight)
                    self.draw_info(ax, plate_info)
                    fig.savefig(osp.join(self.save_dir, 'plates', plate_info + '.png'))
                    plt.close()
                perc = int(100*(1 + i*self.ydim + j)/(self.xdim*self.ydim))
                sys.stdout.write('\033[F\033[K')
                print(f'{perc}% of pixel plates: {self.timer()}')
        sys.stdout.write('\033[F\033[K')
        print(f'Time to get pixel plates: {self.timer()}')

    def run(self):
        self.pixel_im()
        if not self.draft:
            self.number_im()
            self.plates_im()