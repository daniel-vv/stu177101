#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)


import os,sys,logging,time
# import shop_mall
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import shop_mall
from conf import setting



#创建两个程序的logger
logger_atm = logging.getLogger('ATM')
logger_shop = logging.getLogger('SHOP')

logger_atm.setLevel(logging.INFO)
logger_shop.setLevel(logging.INFO)

atm_fh = logging.FileHandler(setting.ATM_LOG)
shop_fh = logging.FileHandler(setting.SHOP_LOG)
shop_fh.setLevel(logging.INFO)

#创建格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# formatter_atm = logging.Formatter('%(asctime)s - %(message)s')

#添加到handler
atm_fh.setFormatter(formatter)
shop_fh.setFormatter(formatter)

#添加handler到Logger中
logger_atm.addHandler(atm_fh)
logger_shop.addHandler(shop_fh)

def atm_log(atm_user,struct_time,level_log,messages):
    '''
    atm 会员消费写日志函数
    :param atm_user:  接受用户传入atm账号
    :param struct_time: 接受传入struct time时间
    :param loglevel:  接受用户传入级别
    :param messages:  接受用户传入日志记录
    :return:
    '''
    atm_user = str(atm_user)
    if struct_time.tm_mday < 23:
        filename = "%s_%s_%d" %(struct_time.tm_year,struct_time.tm_mon,22)
    else:
        filename = "%s_%s_%d" %(struct_time.tm_year,struct_time.tm_mon+1,22)
    if not os.path.exists(os.path.join(setting.DBDIR,'atm',atm_user,'record')):
        os.makedirs(os.path.join(setting.DBDIR,'atm',atm_user,'record'))

    logger = logging.Logger('ATM')
    logger.setLevel(logging.INFO)
    bill_date = shop_mall.curr_datetime()
    fh = logging.FileHandler(os.path.join(setting.DBDIR,'atm',atm_user,'record',bill_date))

    atm_fmt = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(atm_fmt)
    logger.addHandler(fh)
    if level_log == 'info':
        logger.info(messages)
    elif level_log == 'warn':
        logger.warning(messages)
    elif level_log == 'error':
        logging.error(messages)
    elif level_log == 'critical':
        logging.critical(messages)
    else:
        return False
    return True

