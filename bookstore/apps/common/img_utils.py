#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

import random, StringIO, os, uuid
import logging

from django.conf import settings

from PIL import Image, ImageDraw, ImageFont, ImageFile

from common import utils, file_utils

logger = logging.getLogger("mysite")

'''
In this module, we mainly define the functions about image processing 
'''

IMG_QUALITY = 100
# exception code for image processing
EXCEPT_NULL_FILE = -1
EXCEPT_OVER_CAPACITY = 0
EXCEPT_UNSUPPORTED_FORMAT = 1

def open(path, fileName):
    """Opens and identifies the given image file. This is a lazy operation
        return an Image object
    """
    full = os.path.join(path, fileName)
    if not file_utils.isFileExist(full):
        raise Exception("path %s not exist" % full)
    
    return Image.open(full)

def _save(img, path, filename, format="JPEG", _quality=IMG_QUALITY, create_dir=True):
    '''save Image object to file system, according to the value of create_dir
    to create a new dir , or not
    
    params:
        create_dir:  if True, when then filepath not exists, create new one
            or not create.
    '''
    
    if not file_utils.isFileExist(path):
        if create_dir:
            os.makedirs(path)
            logger.info("path [%s] not exist, new one created" % path)
        else:
            logger.error("save file failed, path [%s] not exist" % path)
            return False    
    try:
        img.save(os.path.join(path, filename), format, quality=_quality)
        logger.debug("File with name %s saved" % filename)
        return True
    except:
        utils.traceBack()
        return False    


def _thumb(img, size):
    """按指定尺寸对img对象进行缩放(不进行保存操作). 缩放成功,return True, or return False.
        缩放将改变图片的宽高尺寸及图片存储容量
    
    params:
        img: PIL Image object
        size: 文件缩放高宽值,tuple type
    """
    try:
        img.thumbnail(size, Image.ANTIALIAS)
        return True
    except:
        logger.error("%s" % utils.traceBack())
        return False

def scale(img, size, path, quality):
    """按指定尺寸缩放图片,生成新图并保存. 缩放成功,返回新生成文件名,否则返回None
    call thumb()
    
    params:
        img: PIL Image object
        size: 文件缩放高宽值,tuple type
        path: 存储图片文件的目录(不包括最终文件名),绝对路径
        quality: 缩放后生成图片的分辨率, 将决定图片的存储容量, 100同原图容量, -->0依次减小 
    """
    
    filename = utils.genUuid()
    if _thumb(img, size) and _save(img, path, filename, _quality=quality):
        return filename

    return None

def scalePic(img, path, prefix, filename, size, quality):
    '''切剪图片: _thumb()缩放将改变原图,所以考虑在拷贝上进行
    
    params:
        path: 缩放后图片文件存放目录
        prefix: 文件名前缀, 如activity, profile等 
        filename: 文件uuid名
        size: 文件缩放尺寸
        quality: 分辨率
    '''
    
    try:
        _img = img.copy()
        _thumb(_img, size)
        _save(_img, os.path.join(path, prefix), filename, _quality=quality)
        return "%s/%s" % (prefix, filename)
    except:
        utils.traceBack()
        return None

def cut(img, xy, size, path, quality):
    '''剪切图片, 剪切后进行缩放,并保存为新的图片文件.
    
    params:
        img: Image object
        xy:  剪切坐标tuple,各坐标点为整数, 形如 (x1, y1, x2, y2)
        size: 缩放尺寸tuple, like (width, height)
        path: 剪切后图片存放目录,新图文件名将由uuid生成
        quality: 剪切后生成图片的分辨率, 将决定图片的存储容量, 100同原图容量, -->0依次减小
        
    return: 
        剪切成功, 返回由uuid生成的新文件名,否则返回none
    '''
    try:
        _img = img.copy()
        _img.crop(xy)
        return scale(_img, size, path, quality)
    except:
        logger.error("%s" % utils.traceBack())
        utils.traceBack()
        return None
    
def upload(file, size, path, quality):
    '''上传图片.
    the file data passed is an UploadedFile object, which is from 
    request.FILES, such as file=request.FILES["theFile"]. Each entry in this 
    dictionary is an UploadedFile object.
    
    params:
        file:      get from request.FILES["paramName"]
        size:      scaling (width, height)
        path:      the file path to saving
        quality:   上传后生成图片的分辨率, 将决定图片的存储容量, 100同原图容量, -->0依次减小
    
    return values:
        上传成功, 返回由uuid生成的新文件名,否则返回none
    '''

    parser, img = None, None
    try:
        parser = ImageFile.Parser()
        for chunk in file.chunks():
            parser.feed(chunk)
    except Exception, e:
        raise e    
    finally:
        img = parser.close()
        
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
               
               
    return scale(img.copy(), size, path, quality)    


#验证码参数设置
""" 
background #随机背景
line_color #随机干扰线条
img_width #画布宽度
img_height #画布高度
font_color #验证码字体颜色
font_size #验证码字体尺寸
font #验证码字体
"""
background = (random.randrange(150,200),random.randrange(150,200),random.randrange(150,200))
line_color = (random.randrange(100,101),random.randrange(100,101),random.randrange(100,200))
img_width = 80
img_height = 30
font_color =['black','darkblue','darkred']
font_size = 18
font_path = "static/xizhi/font/arial.ttf"
font = ImageFont.truetype(font_path, font_size)
CHAR_RANGE = '0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'

def drawSecureImg(code):
    """根据传入的code字符串,绘制验证码图片"""
    
    #新建画布
    im = Image.new('RGB', (img_width, img_height), background)
    ImageDraw.Draw(im)
    
    #新建画笔
    draw = ImageDraw.Draw(im)
    
    #画干扰线
    for i in range(random.randrange(3, 5)):
        xy = (random.randrange(0,img_width),random.randrange(0,img_height),
                random.randrange(0,img_width),random.randrange(0,img_height))
        draw.line(xy, fill=line_color, width=1)
        
    #绘制验证码文字
    x = 2
    for i in code:
        y = random.randrange(0,10)
        draw.text((x,y), i, font = font, fill = random.choice(font_color))
        x += 14
    del x
    del draw
    
    #写入缓存
    buf = StringIO.StringIO()
    im.save(buf,'gif')
    return buf

def generateCode():
    return random.sample(CHAR_RANGE, 5)

