import cv2
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import matplotlib.pyplot as plt
import os
import random
import json
import ndjson
from multiprocessing import Pool
from tqdm import tqdm
from imgaug import augmenters as iaa

with open('yaitron.ndjson', 'r') as f:
    yaitron = ndjson.load(f)
    words = []
    for data in yaitron:
        if data['lang'] == 'th':
            word = data['headword']
            word = word.replace('แ', 'เเ')
            words.append(word)

fontsFolder = 'font'
fontPaths = [os.path.join(fontsFolder, path)
             for path in os.listdir(fontsFolder)]

# fontPaths.remove('font/.DS_Store')
fonts = [ImageFont.truetype(fontPath, 32) for fontPath in fontPaths]
fonts.extend([ImageFont.truetype(fontPath, 30) for fontPath in fontPaths])
fonts.extend([ImageFont.truetype(fontPath, 35) for fontPath in fontPaths])
fonts.extend([ImageFont.truetype(fontPath, 40) for fontPath in fontPaths])

BG_COLOR = 209
BG_SIGMA = 5
MONOCHROME = 1


def generateWord(length=0, ignoreChar=None):
    if ignoreChar == None:
        def getRandomWord():
            return words[random.randint(0, len(words) - 1)]
    else:
        def isHasIgnoreChar(word):
            for char in word:
                if ignoreChar.find(char) != -1:
                    return True
            return False
        def getRandomWord():
            
            word = words[random.randint(0, len(words) - 1)]
            while isHasIgnoreChar(word):
                word = words[random.randint(0, len(words) - 1)]
            return word
        
    word = getRandomWord()
    while len(word) < length:
        word += getRandomWord()
    return word


def blankImage(img_w):
    img = np.ones((64, img_w, 3), np.uint8) * 255
    if random.random() > 0.5:
        img = iaa.Pepper(0.005).augment_image(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return img


def blank_image(width=512, height=64, background=BG_COLOR):
    img = np.full((height, width, MONOCHROME), background, np.uint8)
    return img


def add_noise(img, sigma=BG_SIGMA):
    width, height, ch = img.shape
    n = noise(width, height, sigma=sigma)
    img = img + n
    return img.clip(0, 255)


def noise(width, height, ratio=1, sigma=BG_SIGMA):
    mean = 0
    assert width % ratio == 0, "Can't scale image with of size {} and ratio {}".format(
        width, ratio)
    assert height % ratio == 0, "Can't scale image with of size {} and ratio {}".format(
        height, ratio)

    h = int(height / ratio)
    w = int(width / ratio)

    result = np.random.normal(mean, sigma, (w, h, MONOCHROME))
    if ratio > 1:
        result = cv2.resize(result, dsize=(width, height),
                            interpolation=cv2.INTER_LINEAR)
    return result.reshape((width, height, MONOCHROME))


def texture(image, sigma=BG_SIGMA, turbulence=2):
    result = image.astype(float)
    cols, rows, ch = image.shape
    ratio = cols
    while not ratio == 1:
        result += noise(cols, rows, ratio, sigma=sigma)
        ratio = (ratio // turbulence) or 1
    cut = np.clip(result, 0, 255)
    return cut.astype(np.uint8)


def generateImage(word, img_w, img_h):
    if random.random() > 0.5:
        img = blank_image(img_w, img_h)
        img = texture(img, random.randint(3, 9))
    else:
        img = blank_image(img_w, img_h, 255)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if len(word) != 0:
        font = fonts[random.randint(0, len(fonts) - 1)]
        font_width, _ = font.getsize(word)
        pos = (random.randint(0, 150), random.randint(8, 16))
        if pos[0] + font_width > img_w:
            return generateImage(word, img_w, img_h)
        imgPil = Image.fromarray(img)
        draw = ImageDraw.Draw(imgPil)
        draw.text(pos, word, font=font, fill=(0, 0, 0, 0))

        img = np.array(imgPil)

    if random.random() > 0.5:
        img = iaa.GaussianBlur((0, 0.5)).augment_image(img)

    if random.random() > 0.5:
        img = iaa.Pepper(0.005).augment_image(img)

    if random.random() > 0.5:
        img = iaa.Affine(rotate=(-2, 2), cval=(BG_COLOR, 255)
                         ).augment_image(img)

    if random.random() > 0.5:
        img = iaa.PiecewiseAffine(scale=(0.005, 0.01), cval=(
            BG_COLOR, 255)).augment_image(img)

    if random.random() > 0.5:
        img = iaa.Invert(1).augment_image(img)

    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    return img
