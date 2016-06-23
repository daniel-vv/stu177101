#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import os,sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# # from core import shop_mall

#获取到程序根目录
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#使用os.path.join来拼接,找到各个子目录,赋值给变量,便于模块间调用
DBDIR = os.path.join(BASEDIR,'db')
COREDIR = os.path.join(BASEDIR,'core')
LOGSDIR = os.path.join(BASEDIR,'logs')
BINDIR = os.path.join(BASEDIR,'bin')


#Log setting
# if shop_mall.ATM_USER_STATUS['username']:
ATM_LOG = os.path.join(BASEDIR,'logs','atm.log')
SHOP_LOG = os.path.join(BASEDIR,'logs','shop.log')






