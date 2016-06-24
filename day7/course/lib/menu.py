#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)


def show_manager_info():
    '''
    管理后台欢迎菜单
    :return:
    '''
    print('欢迎来到管理平台,请选择操作菜单'.center(50))
    print('#'*60)
    print('''
                1. 管理员登录
                2. 注册管理员
                3. 退出程序
    ''')
    print('#'*60)

def show_manager_menu(user):
    '''
    商城后台管理菜单
    :param user:
    :return:
    '''
    print('\033[32;1m[ {} ], 欢迎来到管理后台,请选择操作菜单\033[0m'.center(50).format(user))
    print('\033[32;1m#\033[0m'*60)
    print('''\033[32;1m
                1. 创建老湿
                2. 创建课程
                3. 查看老湿
                4. 查看课程
                5. 删除老湿
                6. 删除课程
                7. 退出程序
    \033[0m''')
    print('\033[32;1m#\033[0m'*60)

def show_teacher_info():
    '''
    老师欢迎菜单
    :return:
    '''
    print('欢迎来到老湿管理平台,请选择操作菜单'.center(50))
    print('#'*60)
    print('''
                    1. 老师登录
                    2. 获取帮助
                    3. 退出程序
    ''')
    print('#'*60)

def show_teacher_menu(user):
    '''
    商城后台管理菜单
    :param user:
    :return:
    '''
    print('\033[32;1m[ {} ], 欢迎来到教师平台,请选择操作菜单\033[0m'.center(50).format(user))
    print('\033[32;1m#\033[0m'*60)
    print('''\033[32;1m
                    1. 查看代课
                    2. 查看资产
                    3. 退出程序
    \033[0m''')
    print('\033[32;1m#\033[0m'*60)


def show_student_info():
    '''
    学生欢迎菜单
    :return:
    '''
    print('欢迎来到学生平台,请选择操作菜单'.center(50))
    print('#'*60)
    print('''
                1. 学生登录
                2. 注册账户
                3. 获取帮助
                4. 退出程序
    ''')
    print('#'*60)

def show_student_menu(user):
    '''
    商城后台管理菜单
    :param user:
    :return:
    '''
    print('\033[32;1m[ {} ], 欢迎来到学生平台,请选择操作菜单\033[0m'.center(50).format(user))
    print('\033[32;1m#\033[0m'*60)
    print('''\033[32;1m
                    1. 选课
                    2. 查看选课信息
                    3. 上课
                    4. 查看上课记录
                    5. 退出程序
    \033[0m''')
    print('\033[32;1m#\033[0m'*60)

