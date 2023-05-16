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
        self.image = image

        assert orientation in ['vertical', 'horizontal']
        self.orientation = orientation
        if self.orientation == 'vertical':
            self.pixelplate = (40, 50)
        else:
            self.pixelplate = (50, 40)

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

        assert dimension.count('*') <= 1
        self.dimension = dimension
        if '*' not in self.dimension:
            self.xdim = int(self.dimension)
            self.ydim = int(self.dimension)
        else:
            self.xdim, self.ydim = self.dimension.split('*')
            self.xdim = int(self.xdim)
            self.ydim = int(self.ydim)

        self.colours = colours
        self.__colours__()

        assert pixelsize.count('*') <= 1
        self.pixelsize = pixelsize
        if '*' not in self.pixelsize:
            self.xps = int(self.pixelsize)
            self.yps = int(self.pixelsize)
        else:
            self.xps, self.yps = self.pixelsize.split('*')
            self.xps = int(self.xps)
            self.yps = int(self.yps)

    def __colours__(self):
        pass

    def run(self):
        pass

