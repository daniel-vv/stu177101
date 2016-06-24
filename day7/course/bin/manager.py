#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

'''
Author: DBQ(Du Baoqiang)
Blog: http://www.cnblogs.com/dubq/p/5601705.html
Github: https://github.com/daniel-vv/stu177101
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import modules
from lib import menu



def main():
    while True:
        menu.show_manager_info()
        inp = input('请选择一个操作序列>>').strip()
        if inp == '1':
            user = input('请输入您的管理员账户: ').strip()
            pwd = input('请输入您的管理员密码: ').strip()
            if user and pwd:
                manager = modules.Manager(user)
                result = manager.login(user,pwd)
                if result:
                    while True:
                        menu.show_manager_menu(user)
                        inp2 = input('请选择一个操作序列>>').strip()
                        if inp2 == '1':     #创建老师
                            manager.add_teacher(user)
                        elif inp2 == '2':   #创建课程
                            manager.add_course(user)
                        elif inp2 == '3':   #查看老师
                            manager.show_teacher()
                        elif inp2 == '4':   #查看课程
                            manager.show_course()
                        elif inp2 == '5':   #删除老师
                            manager.del_teacher()
                        elif inp2 == '6':   #删除课程
                            manager.del_course()
                        elif inp2 == '7':   #退出程序
                            break
                        else:
                            print('错误的操作序列!')
                else:
                    pass

        elif inp == '2': #注册
            user = input('请输入一个管理员账户名: ').strip()
            pwd = input('请输入管理员密码: ').strip()
            phone = input('请输入联系电话: ').strip()
            if pwd:
                pwd_verify = input('请再输入您的密码: ').strip()
                if pwd_verify == pwd:
                    if phone.isdigit():
                        manager = modules.Manager()
                        manager.registry(user,pwd)
                    else:
                        print('电话号码输入错误!')
                else:
                    print('两次输入密码不一致!')
        elif inp == '3' or inp == 'q' or inp == 'quit':
            print('bye')
            break


if __name__ == '__main__':
    main()