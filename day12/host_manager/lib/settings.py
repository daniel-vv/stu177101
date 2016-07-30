#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import os,sys
import configparser
from sqlalchemy import create_engine

def GetConfig(servertype,key):
    '''
    获取配置文件中的参数的函数
    :param servertype: 接受用户传入一个类型,有两个字段, client和server
    :param key: key是接受用户传入的要获取的key值,如ip
    :return:   如果获取成功将return 获取的结果
    '''
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE,encoding='utf-8')  #读取配置文件

    if config.has_section(servertype):
        return config.get(servertype,key)
    else:
        return False

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASEDIR,'conf','host_manager.conf')
DATABASE_IP = GetConfig('database','host')
DATABASE_PORT = GetConfig('database','port')
DATABASE_USER = GetConfig('database','user')
DATABASE_PASS = GetConfig('database','password')
DATABASE_TYPE = GetConfig('database','database_type')
DATABASE_CONN_TYPE = GetConfig('database','connection_type')
DATABASE_DB_NAME = GetConfig('database','dbname')


engine = create_engine('%s+%s://%s:%s@%s:%s/%s'%(DATABASE_TYPE,
                                                 DATABASE_CONN_TYPE,
                                                 DATABASE_USER,
                                                 DATABASE_PASS,
                                                 DATABASE_IP,
                                                 DATABASE_PORT,
                                                 DATABASE_DB_NAME,),
                       max_overflow=5)




