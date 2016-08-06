#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import sys,os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import manager_host,db_modules

if __name__ == '__main__':
    while True:
        print('#'*50,'\n','\033[32;1m欢迎来到DBQ的跳板机V1.0.0版本\033[0m'.center(40),'\n','#'*49)
        inp = input('  1: 初始化数据库(\033[31;1m初次运行程序执行\033[0m)\n\
  2. 进入主机管理\n  3. 删除数据库(\033[31;1m测试程序,请勿频繁进行删除/初始化库操作!\033[0m)\n  4. 退出程序\n请输入一个选择序列\n>>>').strip()
        if inp == '1':
            obj = db_modules.operate_db()
            obj.init_db()
            print('\033[31;1m数据库初始化完成...\033[0m')
        elif inp == '2':
            obj = manager_host.Operate_manager()
            obj.main()
        elif inp == '3':
            obj = db_modules.operate_db()
            obj.del_db_meta()
            print('\033[31;1m数据库表数据已成功删除...\033[0m')
        elif inp == '4':
            print('Goodbye!')
            break
        else:
            print('\033[31;1m非法的操作序列\033[0m')
            continue

