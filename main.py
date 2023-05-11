import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, default='image.jpg',
        help='The image to be pixelized.')
    parser.add_argument('--orientation', type=str, default='vertical',
        help='If the pixel plates should be placed: vertical or horizontal.')
    parser.add_argument('--align', type=str, default='center center',
        help='How the image should be aligned with the pixel plates.')
    parser.add_argument('--dimension', type=str, default='1',
        help='''
        The number of horizontal and vertical plates.
        Either a single number or two numbers with an 'x' in-between.
        ''')
    parser.add_argument('--colours', type=str, default='all',
        help='''
            the colours to be used for the pixelized image.
            Can be:
            - a list of colours separated by  '-', for example 'blue-darkblue-cyan';
            - a list of plate numbers separated by '-', for example '100-220-333'; or
            - one of the pre-implemented options ('primary', 'simple', 'classic', or 'all').
        ''')
    parser.add_argument('--pixelsize', type=str, default='1',
        help='''
        The number of squares of the pixel plate used to represent a single pixel.
        This parameter can be used to mix simple colours to create more complec ones.
        Either a single or two numbers with an 'x' in-between.
        ''')
    kwargs = vars(parser.parse_args())
