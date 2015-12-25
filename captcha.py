#!/usr/bin/env python
# -*- coding: utf_8 -*-

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

im = Image.open('vcode.bmp')
# im = im.filter(ImageFilter.MedianFilter())
enhancer = ImageEnhance.Contrast(im)
im = enhancer.enhance(2)
im = im.convert('1')
im = im.resize(tuple(map(lambda i: i*3, im.size)), Image.ANTIALIAS)
im.save('test.tif')
vcode = pytesseract.image_to_string(im, config="-psm 6")
print vcode
