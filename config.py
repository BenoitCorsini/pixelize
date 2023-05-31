RGB_MAX_INT = 255
RGB_DIM = 3

RGB_DICT = 'rgb.json'
PIXELPLATE_SIZE = (50, 40)
PIXELS_PER_SQUARE = 6*6*4 - 4 # = 140
PLATE_RATIO = 63/100

KMEANS_PARAMS = {
    'n_init' : 100,
    'max_iter'  : 1000,
    'tol'  : 1e-5,
    'random_state' : 27,
}
GRID_PARAMS = {
    'color' : 'gray',
    'lw' : 5,
}
PLATE_INFO_PARAMS = {
    'x' : 1,
    'y' : 1,
    'fontsize' : 127,
    'color' : 'gray',
}
NIM_THRESHOLD = 0.2
NIM_RATIO = 0.8

OUTPUT_FOLDER = 'output:'
IMAGE_FILE = 'image.png'
PLATES_INFO = 'plates.json'
IMAGES_PER_NUMBER_FOLDER = 'nims'
PLATES_FOLDER = 'plates'