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

    def __init__(self, image, annotation):
        self.image = image
        self.annotation = annotation
        self.characters = []
        self.createCharacter()

    def __preprocess(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(img, 5)
        # img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        _, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, 3)
        contours.sort(key=lambda cnt: cv2.contourArea(cnt, True), reverse=True)
        cnt = contours[0]
        x, y, w, h = cv2.boundingRect(cnt)
        # cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)
        img = img[y:y+h, x:x+w]

        if w < h:
            factor = ImagePackage.SIZE/h
        else:
            factor = ImagePackage.SIZE / w
        img = cv2.resize(img, None, fx=factor, fy=factor,)
        h, w = img.shape
        top, bottom, left, right = 0, 0, 0, 0
        if w < h:
            left = (ImagePackage.SIZE-w)//2
            right = left
        else:
            top = (ImagePackage.SIZE-h)//2
            bottom = top
        if left+right+w<ImagePackage.SIZE:
            left +=1
        if top+bottom+h<ImagePackage.SIZE:
            top +=1
        img = cv2.copyMakeBorder(
            img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=255)

        return img

    def createCharacter(self,):
        objs = self.annotation['objects']
        self.characters = []
        for obj in objs:
            p1, p2 = obj['points']['exterior']
            left, top = p1
            right, bottom = p2
            left, top, right, bottom = int(left), int(
                top), int(right), int(bottom)
            cropImage = self.image[top:bottom, left:right]
            cropImage = self.__preprocess(cropImage)
            tags = obj['tags']
            if len(tags) > 0:
                tag = tags[0]
            else:
                continue

            self.characters.append(Character(cropImage, tag))
            # cv2.imshow('f', cropImage)
            # cv2.waitKey()


class SuperviselyDecoder:
    IMAGE_FORMATS = ['bmp', 'jpg', 'jpeg', 'png']

    def __init__(self, datasetPath, annotationsPath):
        self.datasetPath = datasetPath
        self.annotationsPath = annotationsPath + '/ann'
        self.imagePackages = []
        self.__load()

    def __load(self):
        self.imagePackages = []
        for annoPath in os.listdir(self.annotationsPath):
            filename = annoPath.split('.')[0]
            imgPath = glob.glob(self.datasetPath + '/' + filename + '*')[0]
            img = cv2.imread(imgPath)
            with open(self.annotationsPath + '/'+annoPath, 'r', encoding='utf-8') as f:
                annotation = json.loads(f.read(), encoding='utf-8')
            print(annoPath.center(15, '-',))
            self.imagePackages.append(ImagePackage(img, annotation))

    def decodeTo(self, outputPath):
        i = 0
        if not os.path.exists(outputPath):
            os.mkdir(outputPath)

        for imagePackage in self.imagePackages:
            for character in imagePackage.characters:
                if len(character.tag) == 1:
                    savedFolder = outputPath + '/'+character.tag
                    if not os.path.exists(savedFolder):
                        os.mkdir(savedFolder)
                    i += 1
                    Image.fromarray(character.image).save(
                        '{}/{}.png'.format(savedFolder, i))


decoder = SuperviselyDecoder(
    './datasets/68PersonsBmp', './datasets/NSC__68PersonsBmp')
decoder.decodeTo('./characters')
