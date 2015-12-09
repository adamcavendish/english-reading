#!/bin/bash

apt-get -y install tesseract-ocr redis-server libjpeg-dev libpng-dev
pip install rq bottle pytesseract requests Pillow

