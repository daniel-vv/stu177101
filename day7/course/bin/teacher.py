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
import pickle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import modules
from lib import menu


def show_help():
    print(' 老湿平台帮助 '.center(80,'@'))
    print('''\033[35;1m
        1. 此程序为老湿平台登录程序,用户可通过此平台查看老湿的代课情况以及资产信息;
        2. 所有添加的老湿默认初始密码为123, 登录账号为老湿姓名;
        3. 第一次登录系统时候,要求重置密码,密码长度最少6位, 请用户妥善保管密码;\033[0m
    ''')
    print('@'*86)
    if input('按下回车键继续...'):pass


def main():
    while True:
        menu.show_teacher_info()
        inp = input('请输入一个选择序列!\n>>').strip()
        if inp == '1':   #登录
            user = input('请输入老湿名: ').strip()
            if user:
                password = input('请输入密码: ').strip()
                if password:
                    teacher = modules.Teacher(user)
                    result = teacher.login(user,password)
                    if result:
                        while True:
                            menu.show_teacher_menu(user)
                            inp_num = input('请输入一个选择序列!\n>>').strip()
                            if inp_num == '1':   #查看代课
                                teacher.show_course(user,'代课')
                            elif inp_num == '2': #查看资产
                                teacher.show_course(user,'资产')
                            elif inp_num == '3': #退出程序
                                break
                            else:
                                print('\033[31;1m错误的选择序列!\033[0m')
        elif inp == '2': #帮助
            show_help()
        elif inp == '3': #退出
            break
        else:
            print('\033[31;1m 非法操作序列!\033[0m')


if __name__ == '__main__':
    main()







