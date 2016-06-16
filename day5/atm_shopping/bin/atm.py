#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

'''
Author: DBQ(Du Baoqiang)
Blog: http://www.cnblogs.com/dubq/p/5563802.html
Github: https://github.com/daniel-vv/stu177101
'''

import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import atm_interface

if __name__ == '__main__':
    atm_interface.run()

