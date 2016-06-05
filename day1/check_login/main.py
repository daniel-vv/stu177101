#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: DBQ(Du Baoqiang)
Blog: http://www.cnblogs.com/dubq/articles/5474785.html
Github: https://github.com/daniel-vv/ops
'''

import sys
import getp

def Locked(username):
    '''定义一个锁定函数,以备下面调用,主要思路是以只读方式打开锁文件locked.db,而后遍历对比用户输入的用户名是否是锁定文件中的用户'''
    f = open('./locked.db','r')
    for line in f:
        if username == line.strip():        #这里必须使用strip()来把空白脱掉,否则对比会有问题
            print('\033[1;31m抱歉,用户 %s 已经被锁定 '% username)    #如果在黑名单内给用户打印一个信息
            sys.exit(0)
    f.close()

def Deny_user(username):
    '''定义一个写入用户信息到黑名单的函数,在后面的时候调用直接将锁定用户信息写入到锁文件中去'''
    f = open('./locked.db','a')
    print('\033[1;31m抱歉,用户 %s 输入次数太多, 已被锁定,请联系管理员解锁!' %username)
    f.write('%s\n' %username)
    f.close()


Flag = False   #定义一个标志位,用于在循环中跳出循环用
Count = 0 #定义一个初始值,用于进入变量
User_init = ''   #定义一个用户初始值,用户判定用户每次输入是否是统一用户输入
Locked_count = 1  #定义一个用户锁计数器,用于判定用户每次输入是否是同一个用户,是同一个用户+1,不是-1, 值为2的时候就锁定用户;

if __name__ == '__main__':
    while Count < 3:
        User_name = input('请输入用户名:').strip()     #接受用户输入的账号信息,并赋值给一个变量
        if User_name:        #判断用户输入不为空的时候才进入下面验证用户阶段;
            User_pass = getpass.getpass('请输入密码:').strip()       #判断用户不在黑名单后再让用户输入密码
            if User_name == User_init:     #如果用户初始变量等于用户输入信息的话,那就将用户锁定计数器+1
                Locked_count += 1
            else:    # 如果初始用户名不等于用户输入的用户名,则把值用户输入赋给初始变量User_init
                User_init = User_name
                Locked_count -= 1

            Locked(User_name)                            #用上面定义的函数,把用户输入的用户信息传进去
            with open('./passwd.db','r') as user_info:    #打开文件,以只读的方式
                for line in user_info.readlines():     #遍历文件
                    user,password = line.split()  #把从用户账号密码文件中读取出来的用户名密码分别赋值给两个变量,在下面比较
                    if User_name == str(user) and User_pass == (password): #比对用户输入用户名和密码是否和文件里记录的一致?
                       print('-'*30)
                       print('哇,认证成功,欢迎来到这里~ ,%s' %User_name)   #如果一致打印登录信息
                       print('-'*30)
                       Flag = True                #标志位置为True,用于在下面跳出while整个循环
                       break            #break跳出当前循环层
                else:   #else放在这里是要遍历整个文件后才执行下面的内容,在这里卡了有一会
                    print('用户名或密码错误,请重新输入!')
            if Flag:     #如果标志位为True,证明上面已经认证成功,直接跳出循环体
                break
            if not Flag:  #如果标志位还是Flag,证明上面匹配用户名密码没有成功,故将循环计数器+1,并continue跳出本次循环,继续下一次循环;
                Count += 1
                continue

    else:               #循环正常执行完成后,继续下面的操作,也就是锁定用户,但是需要判定用户锁定计数器的值是否是2,如果是证明是一个用户
        if Locked_count == 2:
            Deny_user(User_name)


