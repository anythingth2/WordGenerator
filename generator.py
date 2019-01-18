import cv2
import numpy as np
import os
import matplotlib.pyplot as plt


class CharacterDataset:
    def __init__(self, label, imgs):
        self.label = label
        self.imgs = imgs

    def loadFrom(path):
        if not os.path.isdir(path):
            raise Exception('wrong load path')

        label = os.path.basename(path)
        imgs = [cv2.imread(os.path.join(path, imgPath))
                for imgPath in os.listdir(path)]
        return CharacterDataset(label, imgs)


class Generator:
    def __init__(self):
        self.charDatasets = []


generator = Generator()
charDataset = CharacterDataset.loadFrom('characters/a')

