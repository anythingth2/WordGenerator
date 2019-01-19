# -*- coding: utf8 -*-

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os


CHARACTERS_SET = 'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤลฦวศษสหฬอฮฯะัาำิีึืฺุูเโใไๅๆ็่้๊๋์ํ๎0123456789abcdefgijklmnopqrstuvwxyz'
# CHARACTERS_SET = ' ่'
FONT_FOLDER = 'font'
OUTPUT_FOLDER = 'characters'
fonts = [ImageFont.truetype(os.path.join(FONT_FOLDER, path), 64)
         for path in os.listdir(FONT_FOLDER)]

for char in CHARACTERS_SET:
    i = 0
    workspacePath = os.path.join(OUTPUT_FOLDER, char)
    if not os.path.exists(os.path.join(OUTPUT_FOLDER, char)):
        os.mkdir(workspacePath)
    for font in fonts:

        textWidth, textHeight = font.getsize(char)

        img = Image.new('L', (textWidth, textHeight), color=(255,))
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), char, fill=0, font=font)
        i += 1
        img.save(os.path.join(workspacePath, '{}.png'.format(i)))

        print(char, (textWidth, textHeight))
