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


class Pixel(object):

    def __init__(self,
                 image,
                 orientation='vertical',
                 halign='center',
                 valign='center',
                 dimension='1',
                 colours='all',
                 pixelsize='1',
                 dpi=1):
        self.start_time = time()
        self.__image__(image)
        self.__orientation__(orientation)
        self.__halign__(halign)
        self.__valign__(valign)
        self.__dimension__(dimension)
        self.reduce_im()
        self.__colours__(colours)
        self.__pixelsize__(pixelsize)
        self.dpi = dpi
        folder, file = osp.split(self.image)
        file = osp.splitext(file)[0]
        self.save_dir = osp.join(folder, f'output:{file}')
        if osp.exists(self.save_dir):
            shutil.rmtree(self.save_dir)
        os.makedirs(self.save_dir)
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

    def reduce_im(self):
        self.rim = np.zeros((self.nx, self.ny, 3))
        for i in range(self.nx):
            for j in range(self.ny):
                self.rim[i,j,:] = np.mean(np.mean(
                    self.im[
                        self.dx + self.mult*i:self.dx + self.mult + self.mult*i,
                        self.dy + self.mult*j:self.dy + self.mult + self.mult*j,
                    :],
                axis=0), axis=0)

    def top_colours(self, colours, rgb):
        keys = ''
        use_image = False
        if colours.endswith('image'):
            use_image = True
        value = int(colours.replace('top', '').replace('image', ''))
        K = []
        T = []
        X = []
        for key, colour in rgb.items():
            K.append(key)
            T.append(colour)
        K = np.array(K)
        T = np.stack(T)
        if use_image:
            X = np.reshape(self.rim, (-1, 3))
        else:
            X = T.copy()
        clusters = KMeans(n_clusters=value, n_init='auto').fit_predict(X)
        for v in range(value):
            C = np.mean(X[clusters==v,:], axis=0, keepdims=True)
            key = K[np.argmin(np.mean(np.abs(T - C), axis=-1))]
            keys += f'{key}-'
        return keys[:-1]

    def __colours__(self, colours, rgb_dict='rgb.json'):
        self.colours = colours
        with open(rgb_dict, 'r') as d:
            rgb = json.load(d)
        if self.colours == 'all':
            self.rgb = rgb.copy()
        else:
            if self.colours == 'primary':
                keys = 'blue-red-yellow'
            elif self.colours == 'basic':
                keys = 'white-tab:blue-tab:red-tab:green-tab:pink-tab:orange-tab:brown'
            elif self.colours == 'classic':
                keys = 'peachpuff-crimson-ivory-gold-royalblue-navy-forestgreen'
            elif self.colours.startswith('top'):
                keys = self.top_colours(self.colours, rgb)
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
        print(f'Time to pixelize image: {self.timer()}')

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
                    if self.orientation == 'horizontal':
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
        self.savenim()
        self.saveplates()
