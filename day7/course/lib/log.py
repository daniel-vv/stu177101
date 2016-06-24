#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf import setting


logger = logging.getLogger('COURSE')

logger.setLevel(logging.INFO)

fh = logging.FileHandler(os.path.join(setting.LOG_DIR,'access.log'))
fh.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh.setFormatter(formatter)

logger.addHandler(fh)


# def atm_log(atm_user,struct_time,level_log,messages):
#     '''
#     会员消费写日志函数
#     :param atm_user:  接受用户传入atm账号
#     :param struct_time: 接受传入struct time时间
#     :param loglevel:  接受用户传入级别
#     :param messages:  接受用户传入日志记录
#     :return:
#     '''
#     if not os.path.exists(os.path.join(setting.DBDIR,'atm',atm_user,'record')):
#         os.makedirs(os.path.join(setting.DBDIR,'atm',atm_user,'record'))
#
#     logger = logging.Logger('ATM')
#     logger.setLevel(logging.INFO)
#     bill_date = shop_mall.curr_datetime()
#     fh = logging.FileHandler(os.path.join(setting.DBDIR,'atm',atm_user,'record',bill_date))
#
#     atm_fmt = logging.Formatter('%(asctime)s - %(message)s')
#     fh.setFormatter(atm_fmt)
#     logger.addHandler(fh)
#     if level_log == 'info':
#         logger.info(messages)
#     elif level_log == 'warn':
#         logger.warning(messages)
#     elif level_log == 'error':
#         logging.error(messages)
#     elif level_log == 'critical':
#         logging.critical(messages)
#     else:
#         return False
#     return True

