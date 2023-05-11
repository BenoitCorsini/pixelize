import os
import os.path as osp
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class Process(object):

    def __init__(self):
        pass

    def run(self, img_dir='colours-img', json_file='rgb.json'):
        for img in sorted(os.listdir(img_dir)):
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
                int(0.5 + np.mean(I[:,:,0][LI])),
                int(0.5 + np.mean(I[:,:,1][LI])),
                int(0.5 + np.mean(I[:,:,2][LI])),
            )


if __name__ == '__main__':
    Process().run()