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


def show_help():
    print(' 学生平台帮助 '.center(80,'@'))
    print('''\033[35;1m
        1. 此程序为学生平台登录程序,用户可通过此平台查看学生的选课信息,以及上了多少个课时;
        2. 用户可以选择课程, 一个用户可以选择多个课程;
        3. 上课时如果用户有多个在学课程,可以选择上哪一个;
        4. 如果没有用户名,可以通过注册选项注册一个,成为我们功夫学校的学员;
        5. 注册时需要输入学员的消费金额,上课会增加老湿资产,并减少学员可用资产.\033[0m
    ''')
    print('@'*86)
    if input('按下回车键继续...'):pass



def main():
    '''
    主函数
    :return: 
    '''
    while True:
        menu.show_student_info()
        inp = input('请选择一个操作序列>>').strip()
        student = modules.Students()
        if inp == '1':   #登录1

            user = input('请输入登录名:').strip()
            if user:
                passwd = input('请输入密码: ').strip()

                if passwd:
                    result = student.login(user,passwd)
                    if result:
                        while True:
                            menu.show_student_menu(user)
                            inp2 = input('请选择一个操作序列>>').strip()
                            if inp2 == '1':    #选课
                                student.show_course()
                                student.select_course()

                            elif inp2 == '2':  #查看选课信息
                                student.show_select_course()
                            elif inp2 == '3':  #上课
                                student.study()
                            elif inp2 == '4':  #查看上课记录
                                student.show_study_history()
                            elif inp2 == '5':  #退出
                                break
                            else:
                                print('\033[31;1m错误的选择序列!\033[0m')
        elif inp == '2': #注册
            student.registry()
        elif inp == '3': #帮助
            show_help()
        elif inp == '4': #退出
            print('bye!')
            break
        else:
            print('\033[31;1m 错误的操作序列!\033[0m')



if __name__ == '__main__':
    main()
