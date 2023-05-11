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
            fig = plt.figure(figsize=(10, 10), dpi=100)
            fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
            ax = fig.add_subplot()
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_axis_off()

            I = plt.imread(osp.join(img_dir, img))
            if np.size(I, axis=-1) > 3:
                print(img)
                I = (255*(I[:,:,:3]*I[:,:,3:] + 1 - I[:,:,3:])).astype(int)
            ax.imshow(I, extent=(0, 1, 0, 1))

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
            ax.add_patch(patches.Rectangle(
                xy=(0.5, 0),
                width=0.5,
                height=1,
                color=colour,
            ))

            fig.savefig(img)


if __name__ == '__main__':
    Process().run()
