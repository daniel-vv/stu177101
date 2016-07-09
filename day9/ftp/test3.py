#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import hashlib

def MD5(password):
    '''
    用md5校验密码的函数
    :param password: 接受用户传入的一个密码
    :return: 返回一个hash过后的密码
    '''
    result = hashlib.md5(bytes('fe!49sKQe3Xe8',encoding='utf-8'))  #添加填充字符,防止暴库
    result.update(bytes(password,encoding='utf-8'))

    return result.hexdigest()  #return加密后的密码

def md5sum(filename):
    '''
    文件完整性校验
    :param filename:  接受用户输入一个文件
    :return:          返回给用户一个值
    '''
    f = open(filename,'rb')
    content = f.read()
    f.close()

    m = hashlib.md5(content)
    file_md5 = m.hexdigest()

    return file_md5


name = 'kaike.mp4'

res = md5sum(name)
print(res)