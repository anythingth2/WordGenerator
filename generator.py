# -*- coding: utf8 -*-

import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
import random
from PIL import Image


class CharacterDataset:

    def __init__(self, label,  imgs):
        self.label = label
        self.imgs = imgs

    def loadFrom(path):
        if not os.path.isdir(path):
            raise Exception('wrong load path')

        label = os.path.basename(path)

        imgs = [np.asarray(Image.open(os.path.join(path, imgPath)))
                for imgPath in os.listdir(path)]
        return CharacterDataset(label, imgs)

    def getRandomImage(self):
        return self.imgs[random.randint(0, len(self.imgs)-1)]


class Word:

    def __init__(self):
        self.img = None

    def push(self, charDataset):
        charImg = charDataset.getRandomImage()
        if self.img is None:
            self.img = charImg
            return self.img

        self.img = np.concatenate((self.img, charImg), axis=1)
        return self.img


class Generator:
    def __init__(self, charaterDatasetPath):
        self.characterDatasetPath = charaterDatasetPath
        self.charDatasets = [CharacterDataset.loadFrom(os.path.join(
            self.characterDatasetPath, charPath)) for charPath in os.listdir(self.characterDatasetPath)]

    def __getDatasetByChar(self, char):
        for charDataset in self.charDatasets:
            if charDataset.label == char:
                return charDataset
        return None

    def generate(self, word):
        chars = list(word)
        word = Word()
        for char in chars:
            charDataset = self.__getDatasetByChar(char)
            word.push(charDataset)
            self.imshow(word.img)

    def imshow(self, img):
        cv2.imshow('generator', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


generator = Generator('characters')
generator.generate('กกกก')
