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
        
        # imgs = [np.ones((30,30),dtype='uint8')*255
        #         for imgPath in os.listdir(path)]
        # border = 1
        # imgs = [cv2.copyMakeBorder(
        #     img, border, border, border, border, cv2.BORDER_CONSTANT)for img in imgs]
        return CharacterDataset(label, imgs)

    def getRandomImage(self):
        return self.imgs[random.randint(0, len(self.imgs)-1)]


class Word:

    UPPER_CHARACTERS = 'ิีึื็่้๊๋์ํ๎ั'
    LOWER_CHARACTERS = 'ฺุู'

    def __init__(self, randomOffset=False):
        self.img = None
        self.grid = None
        self.randomOffset = randomOffset

    def push(self, charDataset):
        
        charImg = charDataset.getRandomImage()

        if self.grid is None:
            self.grid = np.array(
                [[None, None, charDataset, None]], 'object').reshape([-1, 1])
            return

        if charDataset.label in Word.UPPER_CHARACTERS:
            self.__concateUpper(charDataset)
        elif charDataset.label in Word.LOWER_CHARACTERS:
            self.__concateLower(charDataset)
        else:
            self.__concateNormal(charDataset)

    def __concateNormal(self, charDataset):
        pad = np.array([None for i in range(
            self.grid.shape[0])]).reshape([-1, 1])
        pad[2] = charDataset
        self.grid = np.concatenate((self.grid, pad), axis=1)

    def __concateUpper(self, charDataset):
        column = self.grid[:, -1]
        if column[1] is None:
            self.grid[1, -1] = charDataset
        elif column[0] is None:
            self.grid[0, -1] = charDataset
        else:
            raise Exception('wrong word')

    def __concateLower(self, charDataset):
        column = self.grid[:, -1]
        if column[3] is None:
            self.grid[3, -1] = charDataset
        else:
            raise Exception('wrong word')

    def render(self):
        SIZE = 32
        MAX_OFFSET = 8
        if self.randomOffset:
            img = np.ones(np.array(self.grid.shape) *
                          (SIZE+MAX_OFFSET), dtype='uint8')*255
        else:
            img = np.ones(np.array(self.grid.shape)*SIZE, dtype='uint8')*255

        for i, row in enumerate(self.grid):
            for j, charDataset in enumerate(row):
                if charDataset is not None:

                    if self.randomOffset:
                        offset = random.randint(0, MAX_OFFSET)-MAX_OFFSET//2
                        if j == 0:
                            x = 0
                        else:
                            x = j*(SIZE+MAX_OFFSET) - offset
                        y = i*(SIZE+MAX_OFFSET)
                        w = SIZE
                        h = SIZE
                        
                        img[y:y+h, x:x +w] = charDataset.getRandomImage()
                    else:
                        img[i*SIZE:i*SIZE+SIZE, j*SIZE:j*SIZE +
                            SIZE] = charDataset.getRandomImage()

                    # print(charDataset.label, end='\t')
                else:
                    # print('None', end='\t')
                    pass
        #     print()
        # print('\n')
        return img


class Generator:
    def __init__(self, charaterDatasetPath,randomOffset=False):
        self.characterDatasetPath = charaterDatasetPath
        self.randomOffset = randomOffset
        self.charDatasets = [CharacterDataset.loadFrom(os.path.join(
            self.characterDatasetPath, charPath)) for charPath in os.listdir(self.characterDatasetPath)]

    def __getDatasetByChar(self, char):
        for charDataset in self.charDatasets:
            if charDataset.label == char:
                return charDataset
        return None

    def generate(self, word):
        chars = list(word)
        word = Word(randomOffset=self.randomOffset)
        for char in chars:
            charDataset = self.__getDatasetByChar(char)
            word.push(charDataset)

        return word.render()

    def generateAndSave(self, path, words):
        if not os.path.exists(path):
            os.mkdir(path)
        i = 0
        for word in words:
            i += 1
            img = self.generate(word)
            cv2.imwrite(os.path.join(path, '{}.png'.format(i)), img)

    def imshow(self, img):
        cv2.imshow('generator', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


generator = Generator('characters',randomOffset=False)
# generator.imshow(generator.generate(
#     'ฉัตรชัย'))
generator.generateAndSave(
    'output', ['การรู้จำลายมือเขียนไทย', 'ราคา', 'คอม', 'กระดาษ'])
