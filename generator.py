# -*- coding: utf8 -*-

import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
import random
from PIL import Image
import dataset_generator


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
        imgs = list(map(lambda img:cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)!=2 else img, imgs))


        # imgs = [np.ones((30,30),dtype='uint8')*255
        #         for imgPath in os.listdir(path)]
        # border = 1
        # imgs = [cv2.copyMakeBorder(
        #     img, border, border, border, border, cv2.BORDER_CONSTANT)for img in imgs]
        return CharacterDataset(label, imgs)

    def getRandomImage(self):
        return self.imgs[random.randint(0, len(self.imgs)-1)]
    
    def getMaxShape(self):
        widths = list(map(lambda img:img.shape[1],self.imgs))
        heights = list(map(lambda img:img.shape[0],self.imgs))
        return max(heights),max(widths)
    def getMeanShape(self):
        widths = list(map(lambda img:img.shape[1],self.imgs))
        heights = list(map(lambda img:img.shape[0],self.imgs))
        return sum(heights)//len(heights), sum(widths)//len(widths)
class Word:

    UPPER_CHARACTERS = 'ิีึื็่้๊๋์ํ๎ั'
    LOWER_CHARACTERS = 'ฺุู'

    def __init__(self, randomOffset=False,maxHeight=None,maxWidth=None):
        self.img = None
        self.grid = None
        self.randomOffset = randomOffset
        self.maxHeight = maxHeight
        self.maxWidth = maxWidth
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
                        img[y:y+h, x:x + w] = charDataset.getRandomImage()
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

    def printGrid(self):
        for row in self.grid:
            for charDataset in row:
                if charDataset is not None:
                    print(charDataset.label, end='\t')
                else:
                    print('None', end='\t')
            print()

    def renderDynamic(self):
        def pasteImage(img, pos, thumpnail):
            thumpnail = thumpnail.copy()
            h, w = thumpnail.shape
            x, y = pos
            try:
                img[y:y+h, x:x+w] = thumpnail
            except ValueError:
                print('error paste image',x,y,w,h,img.shape)
                exit()
        def calculateMaxHeight(columnImg):
            heights = []
            for img in columnImg:
                if img is not None:
                    heights.append(img.shape[0])
            return sum(heights)


        # if self.maxWidth == None or self.maxHeight == None:
        #     SIZE = 125
        #     img = np.ones(np.array(self.grid.shape) * SIZE, dtype='uint8')*255
        # else:
        #     img = np.ones(np.array(self.grid.shape) * (self.maxHeight,self.maxWidth) , dtype='uint8')*255
        
        imgGrid = self.grid.copy()
        for i,row in enumerate(imgGrid):
            for j,cell in enumerate(row):
                if cell !=None:
                    imgGrid[i,j] = imgGrid[i,j].getRandomImage()
        
        # columnHeights = list(map(calculateMaxHeight,imgGrid.T))
        # columnHeights.sort(reverse=True)
        columnHeights = list(imgGrid.T)
        columnHeights.sort(key=calculateMaxHeight,reverse=True)
        columnMaxHeight  = list(map(lambda img: img.shape[0] if img is not None else 0,columnHeights[0]))
        maxHeight = sum(columnMaxHeight)+100
        maxWidth = self.grid.shape[1]*100
        img = img = np.ones((maxHeight,maxWidth) , dtype='uint8')*255
        startY = sum(columnMaxHeight[:2]) + 100
        cursorX = 0
        cursorY = startY
        for index in range(self.grid.shape[1]):
            cursorY = startY
            upper1, upper2, consonant, lower = self.grid[:, index]

            consonantImg = consonant.getRandomImage()
            cursorY -= consonantImg.shape[0]
            pasteImage(img, (cursorX, cursorY), consonantImg)
            if upper2 != None:
                upper2Img = upper2.getRandomImage()
                cursorY -= upper2Img.shape[0]
                offsetX = (consonantImg.shape[1]-upper2Img.shape[1])//2
                if cursorX+offsetX not in range(img.shape[1]):
                    offsetX = 0
                pasteImage(
                    img, (cursorX + offsetX, cursorY), upper2Img)
            if upper1 != None:
                upper1Img = upper1.getRandomImage()
                cursorY -= upper1Img.shape[0]
                offsetX = (consonantImg.shape[1]-upper1Img.shape[1])//2
                if cursorX+offsetX not in range(img.shape[1]):
                    offsetX = 0
                pasteImage(
                    img, (cursorX +offsetX , cursorY), upper1Img)

            if lower != None:
                lowerImg = lower.getRandomImage()
                offsetX = (consonantImg.shape[1]-lowerImg.shape[1])//2
                if cursorX+offsetX not in range(img.shape[1]):
                    offsetX = 0
                pasteImage(
                    img, (cursorX+offsetX, cursorY+consonantImg.shape[0]), lowerImg)
            cursorX += consonantImg.shape[1]

        return img


class Generator:
    def __init__(self, charaterDatasetPath, randomOffset=False):
        self.characterDatasetPath = charaterDatasetPath
        self.randomOffset = randomOffset
        self.charDatasets = [CharacterDataset.loadFrom(os.path.join(
            self.characterDatasetPath, charPath)) for charPath in os.listdir(self.characterDatasetPath)]
        self.maxShape = self.__getMaxShapeCharacterDatasets()
    def __getDatasetByChar(self, char):
        for charDataset in self.charDatasets:
            if charDataset.label == char:
                return charDataset
        return None

    def __getMaxShapeCharacterDatasets(self):
        shapes = list(map(lambda characterDataset: characterDataset.getMaxShape(),self.charDatasets))
        maxWidth = max(list(map(lambda shape:shape[0],shapes)))
        maxHeight = max(list(map(lambda shape:shape[1],shapes)))
        return maxHeight,maxWidth
    
    def __getMeanShapeCharacterDatasets(self):
        shapes = list(map(lambda characterDataset: characterDataset.getMeanShape(),self.charDatasets))
        meanWidth = max(list(map(lambda shape:shape[0],shapes)))
        meanHeight = max(list(map(lambda shape:shape[1],shapes)))
        return np.array([meanHeight, meanHeight])
    
    def generate(self, word):
        chars = list(word)
        maxShape = self.__getMaxShapeCharacterDatasets()
        meanShape =( self.__getMeanShapeCharacterDatasets()*1).astype('int')

        word = Word(randomOffset=self.randomOffset,maxHeight=meanShape[0],maxWidth=meanShape[1])
        for char in chars:
            try:
                charDataset = self.__getDatasetByChar(char)
                word.push(charDataset)
            except:
                print(char, end='')
        return word.renderDynamic()

    def generateAndSave(self, path, words):
        if not os.path.exists(path):
            os.mkdir(path)
        i = 0
        for word in words:
            i += 1
            try:
                img = self.generate(word)
            except:
                print('error generate image')
            cv2.imwrite(os.path.join(path, '{}.png'.format(word)), img)

    def imshow(self, img):
        cv2.imshow('generator', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


ignoreChar ='.ๅำ'
generator = Generator('characters', randomOffset=False)
# generator.imshow(generator.generate(
#     'ฉัตรชัย'))
# generator.generateAndSave('test_output', ['ฉั้ตูรชั๋ย'])
generator.generateAndSave(
    'output', [dataset_generator.generateWord(i,ignoreChar) for i in range(10, 100)])
