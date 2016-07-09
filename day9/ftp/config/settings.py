#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import os,sys


BASEDIR = os.path.dirname(os.path.dirname(__file__))
CONFIG = os.path.join(BASEDIR,'config','server.conf')  #配置文件
LOGDIR = os.path.join(BASEDIR,'logs','access.log')    #日志文件
USERDB = os.path.join(BASEDIR,'db','userdb.json')     #用户DB文件
HOMEDIR = os.path.join(BASEDIR,'db','home')
#定义全局变量
USER_STATUS={}

