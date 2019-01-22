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
    def __init__(self, image, annotation):
        self.image = image
        self.annotation = annotation
        self.characters = []
        self.createCharacter()

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
            
            tags = obj['tags']
            if len(tags)>0:
                tag = tags[0]
            else:
                continue
            
            self.characters.append(Character(cropImage, tag))


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
            print(annoPath.center(15,'-',))
            self.imagePackages.append(ImagePackage(img, annotation))


decoder = SuperviselyDecoder(
    './datasets/68PersonsBmp', './datasets/NSC__68PersonsBmp')
print(decoder.imagePackages[0].characters[0])