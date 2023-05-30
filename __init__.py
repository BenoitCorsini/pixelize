import os.path as osp
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from time import time
from sklearn.cluster import KMeans


class PixelInit(object):

    def __init__(self, image, orientation, halign, valign, dimension, colours, pixelsize):
        self.start_time = time()
        self.__image__(image)
        self.__orientation__(orientation)
        self.__halign__(halign)
        self.__valign__(valign)
        self.__dimension__(dimension)
        self.__reducer__()
        self.__colours__(colours)
        self.__pixelsize__(pixelsize)
        print(f'Time to setup: {self.timer()}')
        
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
        assert orientation in ['default', 'v', 'vertical', 'h', 'horizontal']
        self.orientation = orientation
        if self.orientation in ['v', 'vertical']:
            self.pixelplate = (50, 40)
        elif self.orientation in ['h', 'horizontal']:
            self.pixelplate = (40, 50)
        else:
            if self.imx >= self.imy:
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

    def __reducer__(self):
        mult = min(
            int(self.imx/self.nx),
            int(self.imy/self.ny),
        )
        assert mult > 0
        dx = self.imx - mult*self.nx
        dx = int(0.5 + self.xalign*dx)
        dy = self.imy - mult*self.ny
        dy = int(0.5 + self.yalign*dy)
        self.rim = np.zeros((self.nx, self.ny, 3))
        for i in range(self.nx):
            for j in range(self.ny):
                self.rim[i,j,:] = np.mean(np.mean(
                    self.im[
                        dx + mult*i:dx + mult + mult*i,
                        dy + mult*j:dy + mult + mult*j,
                    :],
                axis=0), axis=0)

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
                keys = self.__top_colours__(self.colours, rgb)
            else:
                keys = self.colours

            rgb_keys = []
            for key in keys.split('-'):
                rgb_keys.append(self.key_to_rgb_key(key, rgb))
            self.rgb = {key : rgb[key] for key in sorted(rgb_keys)}

    def __top_colours__(self, colours, rgb, n_init=100, max_iter=1000, tol=1e-5, random_state=27):
        assert colours.startswith('top')
        keys = ''
        use_image = colours.endswith('image')
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
        clusters = KMeans(
            n_clusters=value,
            n_init=n_init,
            max_iter=max_iter,
            tol=tol,
            random_state=random_state,
        ).fit_predict(X)
        for v in range(value):
            C = np.mean(X[clusters==v,:], axis=0, keepdims=True)
            key = K[np.argmin(np.mean(np.abs(T - C), axis=-1))]
            keys += f'{key}-'
        return keys[:-1]

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