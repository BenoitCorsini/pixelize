import argparse
from pixel import Pixel


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, default='image.jpg',
        help='The image to be pixelized.')
    parser.add_argument('--orientation', type=str, default='vertical',
        help='If the pixel plates should be placed: v, vertical, h, or horizontal.')
    parser.add_argument('--halign', type=str, default='center',
        help='''
        How the image should be aligned horizontally.
        Can be either 'left', 'right', 'center', 'centre', or a number between 0 and 1
        ''')
    parser.add_argument('--valign', type=str, default='center',
        help='''
        How the image should be aligned vertically.
        Can be either 'bottom', 'top', 'center', 'centre', or a number between 0 and 1
        ''')
    parser.add_argument('--dimension', type=str, default='1',
        help='''
        The number of horizontal and vertical plates.
        Either a single number or two numbers with an 'x' in-between.
        ''')
    parser.add_argument('--colours', type=str, default='basic',
        help='''
            the colours to be used for the pixelized image.
            Can be:
            - a list of colours separated by '-', for example 'blue-darkblue-cyan';
            - a list of plate numbers separated by '-', for example '100-220-333';
            - of the form 'topX' to pick the top X plate colours, for example 'top10';
            - of the form 'topXimage' to pick the top X colours of the image; or
            - one of the pre-implemented options ('primary' 'basic', 'classic', or 'all').
        ''')
    parser.add_argument('--pixelsize', type=str, default='1',
        help='''
        The number of squares of the pixel plate used to represent a single pixel.
        This parameter can be used to mix simple colours to create more complec ones.
        Either a single or two numbers with an 'x' in-between.
        ''')
    parser.add_argument('--draft', type=int, default=1,
        help='Whether using the draft mode, only testing the image output.')
    parser.add_argument('--dpi', type=int, default=20,
        help='The dpi for all images.')
    kwargs = vars(parser.parse_args())
    Pixel(**kwargs)
