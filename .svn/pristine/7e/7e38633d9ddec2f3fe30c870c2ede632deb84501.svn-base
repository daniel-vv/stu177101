#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

'''
Author: DBQ
Blog: http://www.cnblogs.com/dubq/articles/5543466.html
Github: https://github.com/daniel-vv/ops
'''

import time
import re
import os


USER_STATUS = {'user_status':False,'username':False,'user_type':False} #全局用户状态字典变量, user_status: 登录成功后会置为True
                                                                       # username:  登录成功后会将值置为用户名,便于在后面引用
                                                                       # user_type: 默认普通用户为False,管理员登录置为True
LOCK_FILE = 'locked.db'  #黑名单数据库文件
USERDB = 'passwd'        #用户数据库文件
USERDB_NEW = 'passwd.new' #用户临时文件
LOCK_FILE_NEW = 'locked.db.new'

def validate_email(email):
    '''
    检测用户输入邮箱地址合法性
    :param email: 接受用户传入的形式参数
    :return: 地址合法返回True,否则为False
    '''
    if len(email)>7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",email) != None:
            return True
    return False

def valid_phone(phone):
    '''
    合法性检测,主要检测用户输入电话号码是否合法
    :param phone: 接受形式参数
    :return: True合法,False不合法
    '''
    if len(phone) == 11:
        if re.match("[1]{1}[3,5,7,8,9]{1}[0-9]{9}",phone) != None:
            return True
    return False

def valid_str(string):
    '''
    合法性检测,主要检测用户用户名是否合法,必须是字母开头,并且大于两位的字符,不包含特殊字符
    :param phone: 接受形式参数
    :return: True合法,False不合法
    '''
    if len(string) != 0:
        if re.match("^[a-zA-Z][a-zA-Z0-9]{1,10}$",string) != None:
            return True
    return False

def check_user(func):
    '''
    检查用户是否登录装饰器,主要装饰修改密码,查询用户,删除用户,提示权限四个模块
    :param func:
    :return:
    '''
    def inner(*args,**kwgras):
        if  USER_STATUS['username']:
            result = func(*args,**kwgras)
            return result
        else:
            if input('\033[31;1m您还没有登录,瞎逛什么呢,登录再说!!按下任意键继续...\033[0m'):pass
    return inner


def login():
    '''
    用户登录函数,输入密码错误三次,并且是同一个用户的话,将锁定这个用户
    :return: True,表示认证成功, 还会返回用户名username
    '''
    Count = 0
    user_init = ''
    user_lock_count = 1
    flag = False
    while Count<3:
        username = input('请输入您的用户名:').strip()
        if username:
            password = input('请输入您的密码: ').strip()
            with open(LOCK_FILE,'r') as lockfile:
                for i in lockfile:
                    if username == i.strip():
                        print('\033[31;1m抱歉, [ {} ]用户已经被锁定, 请联系管理员解锁!\033[0m'.format(username))
                        return False

            if username == user_init:
                user_lock_count += 1
                # print(user_lock_count,username,user_init)
            else:
                user_init = username
                user_lock_count -= 1
                # print(user_lock_count,username,user_init)
            with open(USERDB,'r') as f:
                for i in f:
                    user,passwd,user_type = i.strip().split(':')[0],i.strip().split(':')[1],i.strip().split(':')[5]
                    if username == user and password == passwd:
                        print('\033[32;1m[ {} ] 欢迎登录用户管理系统\033[0m'.format(username))
                        flag = True
                        break
                else:
                    print('用户名或密码错误!')

            if flag:  #如何认证成功,更改默认全局变量里的用户属性信息,并返回True
                USER_STATUS['user_status'] = True
                USER_STATUS['username'] = username
                USER_STATUS['user_type'] = True if user_type == '0' else False  #为True表示用户是管理员身份,写到字典里待进一步判断
                return True
            if not flag:
                Count += 1
                continue
        else:
            continue
    else:
        # print(user_lock_count)
        # print(username,user_init)
        if user_lock_count == 2:  #如果用户计数器累加到2,锁定用户到黑名单文件
            with open(LOCK_FILE,'a+') as f:
                print('\033[31;1m十分抱歉的告诉您,输入次数超限,[ {} ]用户已经被锁定,请联系管理员解锁!'.format(username))
                f.write(username+'\n')
                time.sleep(1)


def registry_user():
    '''
    注册函数
    :return: 注册成功返回True和记录值, 失败返回False和记录值
    '''
    flag = False if not USER_STATUS['user_status'] else True
    Count = 0
    if flag and not USER_STATUS['user_type']: #如果是普通用户登录的状态下选择注册用户,
        user_input = input('\033[31;1m{} 您已经登录了,但是普通用户无法添加用户,你可以尝试退出账户,而后注册一个用户, 确定退出登录么? y/Y\033[0m'.format(USER_STATUS['username'])).strip()
        if user_input == 'y' or user_input == 'Y':
            flag = False
            USER_STATUS['user_status'] = False  #在字典里将标志位置为否表示退出用户登录
            USER_STATUS['username'] = False
            if input('\033[31;1m您已退出登录,按下任意键继续...\033[0m'):pass
        else:
            return False,None
    if flag and USER_STATUS['user_type']:  #如果用户已经登录,并且是管理员权限的话,直接添加用户
        flag = False
    while not flag:
        username = input('输入一个个性的名字吧:\033[31;1m(必填项)\033[0m  ').strip()
        if not valid_str(username):
            print('您输入的用户名不合法, 需要字母或者字母+数字组合,不能包含特殊字符,不能是数字开头,不能少于3个字符,谢谢.')
            continue
        else:
            Count += 1
        password = input('来一个牛逼一点的密码,前提是你能记得住哈:\033[31;1m(必填项)\033[0m  ').strip()
        password_verify = input('来吧,重复一遍你牛逼的密码:\033[31;1m(必填项)\033[0m  ').strip()
        if password != password_verify:
            print('\033[31;1m你输入的两次牛逼的密码不一致!\033[0m')
            continue
        else:
            Count += 1

        if not password or not password_verify:
            continue
        else:
            Count += 1
        homedir = input('输入你的用户家目录, 默认/home/username').strip()
        if not homedir:homedir = '/home/{}'.format(username)
        mailaddr = input('输入你的邮箱地址:\033[31;1m(必填项,格式:username@domain.com)\033[0m ').strip()
        if not validate_email(mailaddr):
            print('\033[31;1m邮箱输入不合法,我做了合法性检测,不要糊弄我!!!\033[0m')
            continue
        else:
            Count += 1
        user_shell = input('输入你的shell, 默认/bin/bash').strip()
        user_shell = user_shell if user_shell else '/bin/bash'
        user_status = 1
        user_phone = input('请输入电话号码,方便通知你有妹子找你.\033[31;1m(必填项)\033[0m ').strip()
        if not valid_phone(user_phone):  #调用电话号码合法性检测
            print('\033[31;1m输入的电话号码不合法,我做了合法性检测,不要糊弄我!!!\033[0m')
            continue
        else:
            Count += 1

        if Count >= 5:
            break

    record = '{}:{}:{}:{}:{}:{}:{}'.format(username,password,homedir,mailaddr,user_shell,user_status,user_phone)
    with open(USERDB,'r') as f:
        for i in f:
            if i.strip().split(':')[0] == username:
                if input('\033[31;1m用户名{}太受欢迎,已经被注册啦,再换一个吧,老兄! 按下任意键继续...\033[0m'.format(username)):pass
                return False,record
    return True,record


@check_user
def get_user(username):
    '''
    查询用户信息函数
    :param username: 接受用户参数
    :return: 暂时没用到
    '''

    if USER_STATUS['user_type']:
        user_input = input('\033[31;1m哇哇哇,管理员呐,请输入你的查询, 仅限于邮箱模糊查询,如(gmail.com)\033[0m   ').strip()
        with open('passwd','r') as f:
            flag = False
            for i in f:
                if user_input in i:
                    # print('True')
                    username,homedir = i.strip().split(':')[0],i.strip().split(':')[2]
                    emailaddr,user_shell,user_phone = i.strip().split(':')[3],i.strip().split(':')[4],i.strip().split(':')[6]
                    user_type = '管理员' if i.strip().split(':')[5] == '0' else '普通用户'
                    print('您模糊搜索到的包含{}的用户:'.center(50,'+').format(user_input))
                    print('''
                        用户名:      {}
                        家目录:      {}
                        邮箱地址:    {}
                        用户Shell:   {}
                        用户类型:    {}
                        联系电话:    {}
                    '''.format(username,homedir,emailaddr,user_shell,user_type,user_phone))
                    print('+'*63)
                    if input('\033[32;1m按下任意键继续...\033[0m'):pass
                    flag = True
            else:
                if not flag:
                    print('没有匹配到包含 %s 的用户信息'%user_input)


    else:
        # print(USER_STATUS['user_type'])
        print('\033[32;1m普通用户只能查看自己的信息啦,想看其他人,得提升权限,找管理员哈!\033[0m')
        with open(USERDB,'r') as f:
            for i in f:
                # print(i.strip().split(':')[0])
                user = i.strip().split(':')[0]
                homedir = i.strip().split(':')[2]
                email = i.strip().split(':')[3]
                userbash = i.strip().split(':')[4]
                phone = i.strip().split(':')[6]
                user_status = '管理员' if i.strip().split(':')[5] == '0' else '普通用户'
                if i.strip().split(':')[0] == username:
                   print('''
                      \033[32;1m[{}] 用户信息\033[0m
                   用户名:        {}
                   家目录:        {}
                   邮箱地址:      {}
                   用户shell:     {}
                   用户类型:      {}
                   联系电话:      {}
                   '''.format(user,user,homedir,email,userbash,user_status,phone))
                   if input('\033[32;1m按下任意键继续...\033[0m'):pass


@check_user
def edit_password(username):
    '''
    修改密码函数
    :param username: 接受用户传入形式参数用户名
    :return: True: 更改密码成功   False: 更改失败!
    '''
    flag = False
    Count = 0
    if not USER_STATUS['user_type']:  #如果用户是普通用户身份,只能修改自己密码
        with open(USERDB,'r') as readonly_file ,open(USERDB_NEW,'w+') as write_file:
            for i in readonly_file: #遍历循环,并把每个值赋给变量,准备后面验证后拼接;
                # print(i.strip().split(':')[0])
                user,password = i.strip().split(':')[0],i.strip().split(':')[1],
                userdir,usermail = i.strip().split(':')[2],i.strip().split(':')[3],
                user_shell,user_type,user_phone = i.strip().split(':')[4],i.strip().split(':')[5],i.strip().split(':')[6]
                if username != user:
                    write_file.write(i.strip()+'\n')
                else:
                    password_new = input('请输入您的新密码: ').strip()
                    password_new_verify = input('请再次输入您的新密码: ').strip()
                    if password_new == password_new_verify:  #做一次密码校验,验证两次输入是否一致
                        write_file.write('{}:{}:{}:{}:{}:{}:{}\n'.format(user,password_new,userdir,usermail,user_shell,user_type,user_phone))
                        if input('\033[32;1m密码更改成功!任意键继续...\033[0m'):pass
                        flag = True
                    else:
                        if input('\033[31;1m两次输入的密码不一致!任意键继续...\033[0m'):pass
                        return False
                Count += 1
        if flag:
        # os.rename(USERDB_NEW,USERDB)   #如果更改成功,直接把老文件改名为源文件,实现改密码,并返回True
            with open(USERDB_NEW,'r') as f_new, open(USERDB,'w+') as f_old:
                for i in f_new:
                    i = i.strip()
                    f_old.write(i+'\n')
            return True

    else: #如果用户身份是管理员的话,将可以更改用户自身密码,还有其他普通用户的密码;
        user_input = input('\033[31;1m哇哇哇,管理员呐,您要改谁的密码? 1:当前用户  2.其他用户\033[0m   ').strip()
        if user_input == '1':
            with open(USERDB,'r') as readonly_file ,open(USERDB_NEW,'w+') as write_file:
                for i in readonly_file: #遍历循环,并把每个值赋给变量,准备后面验证后拼接;
                    user,password = i.strip().split(':')[0],i.strip().split(':')[1]
                    userdir,usermail = i.strip().split(':')[2],i.strip().split(':')[3],
                    user_shell,user_type,user_phone = i.strip().split(':')[4],i.strip().split(':')[5],i.strip().split(':')[6]
                    if username != user:
                        write_file.write(i.strip()+'\n')
                    else:
                        password_new = input('请输入您的新密码: ').strip()
                        password_new_verify = input('请再次输入您的新密码: ').strip()
                        if password_new == password_new_verify:  #做一次密码校验,验证两次输入是否一致
                            write_file.write('{}:{}:{}:{}:{}:{}:{}\n'.format(user,password_new,userdir,usermail,user_shell,user_type,user_phone))
                            if input('\033[32;1m密码更改成功!任意键继续...\033[0m'):pass
                            flag = True
                        else:
                            if input('\033[31;1m两次输入的密码不一致!任意键继续...\033[0m'):pass
                            return False

        if user_input == '2':
            user_input_name = input('\033[31;1m您要改谁的密码? 输入一个要更改密码的用户名: \033[0m   ').strip()
            # print(user_input_name)
            username = user_input_name  #将用户输入的用户名赋值给username变量
            with open(USERDB,'r') as readonly_file ,open(USERDB_NEW,'w+') as write_file:
                for i in readonly_file: #遍历循环,并把每个值赋给变量,准备后面验证后拼接;
                    user = i.strip().split(':')[0]
                    userdir,usermail = i.strip().split(':')[2],i.strip().split(':')[3]
                    user_shell,user_type,user_phone = i.strip().split(':')[4],i.strip().split(':')[5],i.strip().split(':')[6]
                    if username != user:
                        write_file.write(i.strip()+'\n')
                    else:
                        password_new = input('请输入您的新密码: ').strip()
                        password_new_verify = input('请再次输入您的新密码: ').strip()
                        if password_new == password_new_verify:  #做一次密码校验,验证两次输入是否一致
                            write_file.write('{}:{}:{}:{}:{}:{}:{}\n'.format(user,password_new,userdir,usermail,user_shell,user_type,user_phone))
                            if input('\033[32;1m密码更改成功!任意键继续...\033[0m'):pass
                            flag = True
                        else:
                            if input('\033[31;1m两次输入的密码不一致!任意键继续...\033[0m'):pass
                            return False

    if flag:
        # os.rename(USERDB_NEW,USERDB)   #如果更改成功,直接把老文件改名为源文件,实现改密码,并返回True
        with open(USERDB_NEW,'r') as f_new, open(USERDB,'w+') as f_old:
            for i in f_new:
                f_old.write(i.strip()+'\n')
        return True


@check_user
def update_user():
    '''
    提升用户权限函数,主要用户将普通管理员提升为管理员权限
    :return:
    '''
    username_list = [] #定义一个空列表,用户把所有的用户名抓到里面来,来判断提升用户权限的用户名是否存在
    flag = False
    if USER_STATUS['user_type']:
        username = input('\033[32;1m管理员,你要提升谁的权限为管理员? 来吧, 告诉我他/她的名字: \033[0m').strip()
        with open(USERDB,'r') as f:  #遍历文件,把所有用户名追加到列表中
            for i in f:
                user = i.strip().split(':')[0]
                username_list.append(user)
        if username not in username_list:  #如果用户名不存在的话,提示用户用户名不存在
            print('\033[31;1m滚粗,用户名根本不存在,逗谁呢!\033[0m')
            return False
        else:
            with open(USERDB,'r') as readfile,open(USERDB_NEW,'w+') as writefile:
                for line in readfile:
                    user_name,password,homedir = line.strip().split(':')[0],line.strip().split(':')[1],line.strip().split(':')[2]
                    emailaddr,user_shell,user_phone = line.strip().split(':')[3],line.strip().split(':')[4],line.strip().split(':')[6]
                    if username != user_name:
                        writefile.write(line.strip()+'\n')
                    else:
                        user_type = '0' if username == user_name else '1'
                        record = '{}:{}:{}:{}:{}:{}:{}\n'.format(user_name,password,homedir,emailaddr,user_shell,user_type,user_phone)
                        writefile.write(record)
                        print('\033[31;1m%s用户已经被你提升为管理员,哈!\033[0m'%username)
                        flag = True
    if flag:
        os.rename(USERDB_NEW,USERDB)
        time.sleep(1)
        return True


@check_user
def unlock_user():
    '''
    解锁用户函数,主要是管理员使用
    :return: 成功返回True,否则为False
    '''
    user_list = []
    flag = False
    if USER_STATUS['user_type']:  #如果用户是管理员可以执行这个
        user_input_name = input('请输入要解锁的用户名:').strip()
        if user_input_name:
            with open(LOCK_FILE,'r') as f,open(LOCK_FILE_NEW,'w+') as f1:
                for i in f:
                    if user_input_name == i.strip():
                        flag = True
                        continue
                    else:
                        f1.write(i)

        else:
            return False
    else:
        if input('\033[32;1m只有管理员可以解锁用户,普通用户不可进行此操作!\033[0m'):pass
        return False
    if flag:
        print('解锁成功!')
        os.rename(LOCK_FILE_NEW,LOCK_FILE)
        return True
    if not flag:
        print('\033[31;1m用户名[ %s ]不在黑名单列表中!\033[0m'%user_input_name)
        return False

@check_user
def del_user():
    '''
    删除用户函数
    :return: 用户删除成功返回True, 失败为False
    '''
    flag = False
    username_list = [] #定义一个空列表,用户把所有的用户名抓到里面来,来判断提用户是否存在
    if not USER_STATUS['user_type']:
        if input('\033[31;1m[ %s ],你不是管理员啦,谁也无法删除!\033[0m'%USER_STATUS['username']):pass
    else:
        user_input_name = input('\033[31;1m管理员[ %s ]先生/女士, 你要删谁? 给我个名字:  \033[0m'%USER_STATUS['username']).strip()
        if user_input_name:
            with open(USERDB,'r') as f_list:  #遍历文件,把所有用户名追加到列表中
                for i in f_list:
                    user = i.strip().split(':')[0]
                    username_list.append(user)
            if user_input_name in username_list:
                with open(USERDB,'r') as f,open(USERDB_NEW,'w+') as f1:
                    for line in f:
                        user_name,password,homedir = line.strip().split(':')[0],line.strip().split(':')[1],line.strip().split(':')[2]
                        emailaddr,user_shell,user_phone = line.strip().split(':')[3],line.strip().split(':')[4],line.strip().split(':')[6]
                        if user_input_name == user_name:
                            continue
                        else:
                            f1.write(line)
                            flag = True
            else:
                print('\033[31;1m抱歉, 你输入的用户名[ %s ]不存在!\033[0m '%user_input_name)
                return False
    if flag:
        os.rename(USERDB_NEW,USERDB)
        time.sleep(1)
        if input('\033[32;1m[ %s ]已经被删除!\033[0m '%user_input_name):pass
        return True


def print_fun():
    if USER_STATUS['username']:
        print('\033[32;1m欢迎 [%s] 来到用户管理系统\033[0m'.center(90,'#')%USER_STATUS['username'])
        print('''
            1. 登录系统
            2. 添加用户
            3. 修改密码
            4. 查询用户
            5. 删除用户
            6. 提升权限
            7. 解锁用户
            8. 退出账户
        ''')
        print('#'*90)
    else:
        print('欢迎来到用户管理系统'.center(82,'#'))
        print('''
            1. 登录系统
            2. 注册用户
            3. 修改密码
            4. 查询用户
            5. 删除用户
            6. 提升权限
            7. 解锁用户
            8. 退出程序
        ''')
        print('#'*90)


def main():
    '''
    主函数,调用各个菜单函数
    :return: 暂时没用到
    '''
    while True:
        print_fun()
        user_input_num = input('请选择序列').strip()
        if user_input_num == '1':
            if not USER_STATUS['user_status']:  #先判断用户没有登录才调用实例
                result = login()
                if not result:   #如果result返回为False,表示认证失败,退出循环
                    break
            else: #为True的话,证明用户已经登录,不允许重复登录
                if input('\033[31;1m%s 你已经登录了,重复登录你想干什么???\033[0m'%USER_STATUS['username']):pass
        elif user_input_num == '2':  #如果输入2,用户进入改密码程序
            result,record = registry_user()  #实例化函数
            registry_flag = False #添加标志位
            if result:   #registry_user返回两个函数,如果result为真, 继续下面操作
                username = record.split(':')[0]  #切割下,把用户名切割成一个变量
                with open(USERDB,'a+') as f:     #打开文件以追加模式,把用户注册的信息写入到数据文件中
                    f.write('\n' + record)
                    if input('\033[31;1m[ %s ]注册成功,按下任意键继续...\033[0m'%username):pass
        elif user_input_num == '3':
            edit_password(USER_STATUS['username'])
        elif user_input_num == '4':
            get_user(USER_STATUS['username'])
        elif user_input_num == '5':
            del_user()
        elif user_input_num == '6':
            result = update_user()
        elif user_input_num == '7':
            unlock_user()
        elif user_input_num == '8':
            if USER_STATUS['user_status']:
                user_input_retry = input('\033[31;1m确定退出登录账户? y/Y').strip()
                if user_input_retry == 'y' or user_input_retry == 'Y':
                    print('[ %s ]你已经退出程序'%USER_STATUS['username'])
                    USER_STATUS['user_status'] = False
                    USER_STATUS['username'] = False
                    USER_STATUS['user_type'] = False
            else:
                print('bye!')
                break
        else:
            print('\033[31;1m不合法的序列!\033[0m')

if __name__ == '__main__':
    main()


