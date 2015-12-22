#!/usr/bin/env python
# -*- coding: utf_8 -*-

import requests
import time
import random
import math
import cStringIO
import pytesseract
import logging
from PIL import Image, ImageEnhance, ImageFilter

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(name)-10s %(levelname)-7s %(message)s',
    datefmt='%m-%d-%H:%M', filename='web.log', filemode='w')

def GoForEnglishReadingInQueue(student_id, student_passwd, count, Going):
    logger = logging.getLogger(student_id)
    ret = GoForEnglishReading(student_id, student_passwd, count, logger)
    return ret

def getIndex():
    index_url = 'http://202.120.126.58/index.asp'
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'Accept-Language: en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2,ja;q=0.2',
    }
    index = requests.get(index_url, headers=headers)
    cookiedict = dict(index.cookies)
    return cookiedict

def tryCaptcha(student_id, cookiedict):
    captcha_url = 'http://202.120.126.58/VerifyCode.asp'
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'image/webp,image/*,*/*;q=0.8',
        'Accept-Language': 'Accept-Language: en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2,ja;q=0.2',
        'Cache-Control': 'no-cache',
    }
    captcha = requests.get(captcha_url, headers=headers, cookies=cookiedict)

    im = Image.open(cStringIO.StringIO(captcha.content))
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(2)
    im = im.convert('1')
    im = im.resize(tuple(map(lambda i: i*3, im.size)), Image.ANTIALIAS)
    im.save('captcha/' + student_id + '.tif')
    vcode = pytesseract.image_to_string(im, config="-psm 6")
    return vcode

def tryLogin(student_id, student_passwd, vcode, cookiedict, logger):
    login_url = 'http://202.120.126.58/index.asp?step=login'
    data = {
        'txtID': student_id,
        'txtPWD': student_passwd,
        'vrfCode': str(vcode),
        'rbtType': '%D1%A7%C9%FA',
        'submit': '%B5%C7%C2%BC',
        'submit.x': math.floor(1 + random.random() * 20),
        'submit.y': math.floor(1 + random.random() * 20),
    }
    login = requests.post(login_url, data = data, cookies=cookiedict)

    if login.content.count('frmLogin.txtID.focus();') > 1:
        # Login info error
        logger.error('ID or password incorrect: ({},{})'.format(student_id, student_passwd))
        return 'ERR_LOGIN_INFO'
    elif login.content.count('frmLogin.vrfCode.focus();') > 1:
        # Captcha Error
        logger.error('captcha failed: {}'.format(vcode))
        return 'ERR_CAPTCHA_FAILED'
    else:
        return 'SUCCESS'

def trySendTimePackets(student_id, cookiedict, count, logger):
    english_url = 'http://202.120.126.58/timeTotal.asp'
    articles = [564,489,490,491,492,504,505,506,507,508,
                522,523,524,525,526,537,538,539,540,541]
    data = {
        'ExecID': str(articles[int(math.floor(random.random() * 10))]),
        'StudentID': student_id,
    }
    logger.info('{} start!'.format(student_id))
    for i in range(0,count):
        english = requests.post(english_url, data = data, cookies=cookiedict)
        if english.content != '<?xml version="1.0" encoding="utf-8" ?><TimeTotal><Result>0</Result></TimeTotal>':
            loggger.error("GoForEnglishReading {} error: {}".format(i, english.content))
    logger.info('{} finish!'.format(student_id))

# @return values: ['ERR_LOGIN_INFO', 'ERR_CAPTCHA_FAILED', 'SUCCESS']
def GoForEnglishReading(student_id, student_passwd, count, logger):
    retry_times = 10

    cookiedict = getIndex()
    logger.info('cookie: {}'.format(cookiedict))
    while retry_times > 0:
        vcode = tryCaptcha(student_id, cookiedict)
        logger.info('vcode: {}'.format(vcode))

        login_result = tryLogin(student_id, student_passwd, vcode, cookiedict, logger)
        if login_result == 'SUCCESS':
            break
        elif login_result == 'ERR_LOGIN_INFO':
            return 'ERR_LOGIN_INFO'
        retry_times = retry_times - 1

    if retry_times == 0:
        return 'ERR_CAPTCHA_FAILED'

    trySendTimePackets(student_id, cookiedict, count, logger)
    return 'SUCCESS'
