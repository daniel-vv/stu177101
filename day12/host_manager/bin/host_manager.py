#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import sys,os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import modules

if __name__ == '__main__':
    while True:
        inp = input('请输入一个选择序列:\n  1: 初始化数据库(\033[31;1m初次运行程序执行\033[0m)\n\
  2. 进入主机管理\n  3. 退出程序\n>>>').strip()
        if inp == '1':
            obj = modules.operate_db()
            obj.init_db()
        elif inp == '2':
            obj = modules.Operate_manager()
            obj.main()
        elif inp == '4':
            print('Goodbye!')
            break
        else:
            print('\033[31;1m非法的操作序列\033[0m')
            continue


