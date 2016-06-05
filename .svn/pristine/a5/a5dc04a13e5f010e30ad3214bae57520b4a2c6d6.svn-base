#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

# import re
#
# def valid_str(string):
#     '''
#     合法性检测,主要检测用户输入电话号码是否合法
#     :param phone: 接受形式参数
#     :return: True合法,False不合法
#     '''
#     if len(string) > 2:
#         if re.match("^[a-zA-Z].[0-9a-zA-Z]$",string) != None:
#             return True
#     return False
#
# name = 'AB*'
# result = valid_str(name)
# if result:
#     print('合法')
# else:
#     print('不对啦!')

# userdb = ['sam@gmail.com','tom@gmail.com','jerry@dbq168.com','eric@hotmail.com',]
#
# user_input = input('输入你要模糊查询的邮箱地址: 如gmail.com').strip()

# if user_input in userdb:
#     print('True')
# else:
#     print('False')
# with open('passwd','r') as f:
#     flag = False
#     for i in f:
#         if user_input in i:
#             # print('True')
#             username,homedir = i.strip().split(':')[0],i.strip().split(':')[2]
#             emailaddr,user_shell,user_phone = i.strip().split(':')[3],i.strip().split(':')[4],i.strip().split(':')[6]
#             user_type = '管理员' if i.strip().split(':')[5] == '0' else '普通用户'
#             print('您模糊搜索到的包含{}的用户:'.center(50,'#').format(user_input))
#             print('''
#                 用户名:      {}
#                 家目录:      {}
#                 邮箱地址:    {}
#                 用户Shell:   {}
#                 用户类型:    {}
#                 联系电话:    {}
#             '''.format(username,homedir,emailaddr,user_shell,user_type,user_phone))
#             if input('按下任意键继续显示...'):pass
#             flag = True
#     else:
#         if not flag:
#             print('没有匹配到包含 %s 的用户信息'%user_input)
#     # else:
#     #     print(i)

USER_STATUS = {'user_status':True,'username':'dbq','user_type':True}

USER_STATUS['user_status'],USER_STATUS['username'],USER_STATUS['user_type'] = False

print(USER_STATUS)