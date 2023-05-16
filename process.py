import os
import os.path as osp
import json
import numpy as np
import matplotlib.pyplot as plt


def process(img_dir='colours-img', json_file='rgb.json'):
    '''
    Extract from a set of images the corresponding colour of each image.
    This should be used on images of specifically colour objects.
    '''
    d = {}
    imgs = sorted(os.listdir(img_dir))
    for index, img in enumerate(imgs):
        I = plt.imread(osp.join(img_dir, img))
        if np.size(I, axis=-1) > 3:
            print(img)
            I = (255*(I[:,:,:3]*I[:,:,3:] + 1 - I[:,:,3:])).astype(int)
        LI = np.reshape(I, (-1, 3))
        LI = I > np.mean(LI, axis=0)
        LI = np.mean(LI, axis=-1) > 0.5
        if LI[0,0]:
            LI = np.logical_not(LI)
        colour = (
            np.mean(I[:,:,0][LI])/255,
            np.mean(I[:,:,1][LI])/255,
            np.mean(I[:,:,2][LI])/255,
        )
        img = osp.splitext(img)[0].strip()
        assert img.startswith('10')
        img = img[2:].replace('_pixelsquare', '')
        assert img.isdigit()
        img = int(img)
        d[img] = colour
        print(f'{index} of {len(imgs)}')
    with open(json_file, 'w') as j:
        json.dump(d, j, indent=2)


if __name__ == '__main__':
    process()
