# -*- coding: utf8 -*-

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import json
import cv2
import glob


class Character:
    def __init__(self, image, tag):
        self.image = image
        self.tag = tag


class ImagePackage:
    SIZE = 32

    def __init__(self, image, annotation,preprocess=False):
        self.image = image
        self.annotation = annotation
        self.preprocess = preprocess
        self.characters = []
        self.createCharacter()

    def __preprocess(self, img):

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        originalImg = img.copy()

        img = cv2.medianBlur(img, 5)
        # _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 4)
        # cv2.imshow('thres', img)

        # _, contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # contours.sort(key=lambda cnt: cv2.contourArea(cnt, True), reverse=True)
        # cnt = sorted(contours, key=cv2.contourArea)[-1]
        # print(cnt)
        h, w = 0, 0
        y, x = img.shape
        for _x in range(img.shape[1]):
            for _y in range(img.shape[0]):
                if img[_y][_x] == 0:
                    if _x < x:
                        x = _x
                    if _y < y:
                        y = _y
                    if _x > w:
                        w = _x
                    if _y > h:
                        h = _y

        h = h - y
        w = w - x
        padding = 2
        if x - padding >= 0:
            x -= padding
        else:
            x = 0
        if y - padding >= 0:
            y -= padding
        else:
            y = 0
        if w + padding < img.shape[1]:
            w += padding
        else:
            w = img.shape[1]
        if h + padding < img.shape[0]:
            h += padding
        else:
            h = img.shape[0]
        img = originalImg[y:y + h, x:x + w]
        if w < h:
            factor = ImagePackage.SIZE / h
        else:
            factor = ImagePackage.SIZE / w
        # img = cv2.resize(img, None, fx=factor, fy=factor, )
        # h, w = img.shape
        # top, bottom, left, right = 0, 0, 0, 0
        # if w < h:
        #     left = (ImagePackage.SIZE - w) // 2
        #     right = left
        # else:
        #     top = (ImagePackage.SIZE - h) // 2
        #     bottom = top
        # if left + right + w < ImagePackage.SIZE:
        #     left += 1
        # if top + bottom + h < ImagePackage.SIZE:
        #     top += 1
        # img = cv2.copyMakeBorder(
        #     img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=255)

        return img

    def createCharacter(self, ):
        objs = self.annotation['objects']
        self.characters = []
        for obj in objs:
            p1, p2 = obj['points']['exterior']
            left, top = p1
            right, bottom = p2
            left, top, right, bottom = int(left), int(
                top), int(right), int(bottom)
            cropImage = self.image[top:bottom, left:right]
            if self.preprocess:
                cropImage = self.__preprocess(cropImage)
            tags = obj['tags']
            if len(tags) > 0:
                tag = tags[0]
            else:
                continue
            self.characters.append(Character(cropImage, tag))


class SuperviselyDecoder:
    IMAGE_FORMATS = ['bmp', 'jpg', 'jpeg', 'png']

    def __init__(self, datasetPaths):
        self.imagePackages = []
        for datasetPath in datasetPaths:
            self.__load(datasetPath)

    def __load(self,datasetPath):
        imgDatasetPath = datasetPath + '/img'
        anntationPath = datasetPath + '/ann'
        
        # self.imagePackages = []
        for annoPath in os.listdir(anntationPath):
            filename = '.'.join(annoPath.split('.')[:-1])
            imgPath = glob.glob(imgDatasetPath + '/' + filename + '*')[0]
            img = cv2.imread(imgPath)
            with open(anntationPath + '/' + annoPath, 'r', encoding='utf-8') as f:
                annotation = json.loads(f.read(), encoding='utf-8')
            print(annoPath.center(16, '-', ))
            self.imagePackages.append(ImagePackage(img, annotation))

    def decodeCharacterTo(self, outputPath):
        i = 0
        if not os.path.exists(outputPath):
            os.mkdir(outputPath)
        for imagePackage in self.imagePackages:
            for character in imagePackage.characters:
                if len(character.tag) == 1:
                    savedFolder = outputPath + '/' + character.tag
                    if not os.path.exists(savedFolder):
                        os.mkdir(savedFolder)
                    i += 1
                    Image.fromarray(character.image).save(
                        '{}/{}.png'.format(savedFolder, i))
    def decodeSentence(self):
        imgs = []
        tags = []
        for imagePackage in self.imagePackages:
            for character in imagePackage.characters:
                if len(character.tag) > 1: 
                    imgs.append(character.image)
                    tags.append(character.tag)
        return imgs, tags

decoder = SuperviselyDecoder(
   glob.glob('./datasets/*'))
decoder.decodeCharacterTo('./characters')
decoder.decodeSentence()