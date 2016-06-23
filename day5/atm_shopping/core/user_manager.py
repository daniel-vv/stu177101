#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import os,hashlib
import sys,json
import re,time,datetime


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf import setting
from core import log



SHOP_USERDB = os.path.join(setting.DBDIR,'shop_user.db')  #购物商城相关变量和序列化反序列化变量,命名规则同下面ATM
SHOP_USERDB_NEW = os.path.join(setting.DBDIR,'shop_user.db.new')
SHOP_ADMINDB = os.path.join(setting.DBDIR,'shop_admin.db')
SHOP_LOCK = os.path.join(setting.DBDIR,'shop_lock.db')
SHOP_LOCK_FILE_NEW = os.path.join(setting.DBDIR,'shop_lock.db.new')

ATM_USERDB = os.path.join(setting.DBDIR,'atm_user.db')  #ATM普通用户数据库文件
ATM_LOCK = os.path.join(setting.DBDIR,'atm_lock.db')  #ATM用户锁文件,锁定用户存在在此,一个用户一行
ATM_LOCK_NEW = os.path.join(setting.DBDIR,'atm_lock.db.new')  #临时文件
ATM_USER_INFO = json.load(open(ATM_USERDB,'r'))     #加载到内存
ATM_USER_STATUS = {'status':False, 'username':False}   #ATM普通用户登录状态变量
ATM_ADMIN_DB = os.path.join(setting.DBDIR,'atm','admin','admin_db.json')  #ATM管理员信息加载到内存
ATM_ADMIN_STATUS = {'status':False, 'username':False}   #ATM管理员状态信息


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


def md5(password):
    '''
    用md5校验密码的函数
    :param password: 接受用户传入的一个密码
    :return: 返回一个hash过后的密码
    '''
    result = hashlib.md5(bytes('sldfzx4411',encoding='utf-8'))  #添加填充字符
    result.update(bytes(password,encoding='utf-8'))

    return result.hexdigest()


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


def check_lock(type,username):
    '''
    检查用户是否锁定函数
    :param type: 如果用户传入type是shop,则判断商城锁,如果是atm,则判断atm锁
    :param username: 接受用户传入用户名的形参
    :return: 成功True,否则False
    '''
    if type == 'shop':
        with open(SHOP_LOCK,'r') as f:
            for i in f:
                if username == i.strip():
                    print('\033[31;1m [ %s ] 由于错误次数过多,已经被锁定,请联系管理员解锁!'%username)
                    #log.logger_shop.info('[ %s ] 由于错误次数过多,已经被锁定!'%username)
                    return False
            return True
    elif type == 'atm':
        with open(ATM_LOCK,'r') as f:
            for i in f:
                if username == i.strip():
                    print('\033[31;1m [ %s ] 由于错误次数过多,已经被锁定,请联系管理员解锁!'%username)
                    #log.logger_atm.info('[ %s ] 由于错误次数过多,已经被锁定!'%username)
                    return False
            return True
    else:
        return False


def deny_user(type,username):
    '''
    锁定用户函数,接受用户传入两个形参
    :param type: type值为shop表示锁定的是商城的用户,atm是其他地方的
    :param username: 接受用户传入形参用户名
    :return: 成功为True,否则为False
    '''
    if type == 'shop':
        with open(SHOP_LOCK,'a') as f:
            print('\033[31;1m抱歉,用户[ %s ]密码错误次数太多,已被程序锁定,请联系管理员解锁,谢谢!'%username)
            f.write(username+'\n')
            log.logger_shop.info('%s密码错误次数太多,被锁定'%username)
            return True

    elif type == 'atm':
        with open(ATM_LOCK,'a') as f:
            print('\033[31;1m抱歉,用户[ %s ]密码错误次数太多,已被程序锁定,请联系管理员解锁,谢谢!'%username)
            log.logger_atm.info('%s 密码错误次数太多,被锁定'%username)
            f.write(username+'\n')
            return True
    else:
        return False


def show_menu():
    '''
    登录注册菜单
    :return: True登录成功, False,登录失败
    '''
    inp = input('1. 注册用户;  2. 登录\n >>').strip()
    if inp.isdigit() and inp == '1':
        return inp
    elif inp.isdigit() and inp == '2':
        return inp
    else:
        return False


def registry_user():
    '''
    注册用户函数,主要是商城用户注册
    :return: 注册成功返回True和记录值, 失败返回False和记录值
    '''
    # flag = False if not USER_STATUS['user_status'] else True
    flag = False
    Count = 0
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
            password = md5(password)
            Count += 1

        if not password or not password_verify:
            continue
        else:
            Count += 1
        mailaddr = input('输入你的邮箱地址:\033[31;1m(必填项,格式:username@domain.com)\033[0m ').strip()
        if not validate_email(mailaddr):
            print('\033[31;1m邮箱输入不合法,我做了合法性检测,不要糊弄我!!!\033[0m')
            continue
        else:
            Count += 1

        user_phone = input('请输入电话号码,方便通知你有妹子找你.\033[31;1m(必填项)\033[0m ').strip()
        if not valid_phone(user_phone):  #调用电话号码合法性检测
            print('\033[31;1m输入的电话号码不合法,我做了合法性检测,不要糊弄我!!!\033[0m')
            continue
        else:
            Count += 1

        if Count >= 5:
            break

    record = '{}:{}:{}:{}'.format(username,password,mailaddr,user_phone)
    with open(SHOP_USERDB,'r') as f:
        for i in f:
            if i.strip().split(':')[0] == username:
                if input('\033[31;1m用户名{}太受欢迎,已经被注册啦,再换一个吧,老兄! 按下任意键继续...\033[0m'.format(username)):pass
                return False

    with open(SHOP_USERDB,'a') as f:
        f.write('\n'+record)
        print('\033[32;1m注册成功!\033[0m')
        log.logger_shop.info('%s注册成功' %username)
    return True


def shop_login():
    '''
    购物商城普通用户登录模块
    :return: 登录成功return True,否则return False
    '''
    flag = False
    Count = 0
    Lock_count = 1
    user_init = ''
    while Count < 3:
        inp = show_menu()
        if inp == '2':
            user = input('请输入用户名:').strip()
            pwd = input('请输入密码:').strip()
            if check_lock('shop',user):
                if user == user_init:
                    Lock_count += 1
                else:
                    user_init = user
                    Lock_count -= 1
                with open(SHOP_USERDB,'r') as f:
                    for i in f:
                        username,password = i.strip().split(':')[0],i.strip().split(':')[1]
                        if user == username and md5(pwd) == password:
                            print('登录成功')
                            log.logger_shop.info('%s登录成功'%user)
                            flag = True
                        if flag:break
                    else:
                        print('账户名或密码错误!')
                        log.logger_shop.info('%s 登录失败, 账号密码错误!'%user)
                        Count += 1
            else:
                return False
        if inp == '1':
            registry_user()
        if flag:
            return user
    else:
        if Lock_count == 2:
            deny_user('shop',user)



def atm_login():
    '''
    ATM机登录函数
    :return: 登录成功返回用户名\额度\可用额度
    '''
    flag = False
    Count = 0
    Lock_count = 1
    user_init = ''
    curr_date = datetime.date.isoformat(datetime.datetime.now())  #获取现有时间,看用户是否过期
    while Count < 3:
        user = input('请输入您的信用卡账号:').strip()
        pwd = input('请输入您的信用卡密码:').strip()
        if check_lock('atm',user):  #检查用户是否在黑名单里
            if user == user_init:
                Lock_count += 1
            else:
                user_init = user
                Lock_count -= 1
            if user in ATM_USER_INFO.keys():
                if user == ATM_USER_INFO[user]['username'] and md5(pwd) == ATM_USER_INFO[user]['password']:
                    limit = ATM_USER_INFO[user].get('limit')
                    avililable = ATM_USER_INFO[user].get('available')
                    expire_date = ATM_USER_INFO[user].get('expire_date')
                    print('\033[32;1m[ %s ] 成功登录ATM系统\033[0m'%user)
                    if not  ATM_USER_INFO[user].get('freeze'):
                        ATM_USER_STATUS['status'] = True
                        ATM_USER_STATUS['username'] = user
                    else:
                        if input('\033[31;1m抱歉, 用户[ %s ]已被冻结, 请联系ATM管理员解冻,谢谢合作!\033[0m'%user):pass
                        return False
                    if expire_date <= curr_date:
                        print('\033[31;1m[ %s ]账户已过期\033[0m'%user)
                        return False
                    flag = True
                    log.logger_atm.info('%s 成功登录ATM系统'%user)
                else:
                    print('账户名或密码错误!')
                    Count += 1
            else:
                 print('账户名或密码错误!')
                 Count += 1
        else:
            return False
        if flag:
            return user,limit,avililable
    else:
        if Lock_count == 2:
            deny_user('atm',user)



def unlock_user():
    '''
    解锁用户函数,主要是管理员使用
    :return: 成功返回True,否则为False
    '''
    user_list = []
    flag = False
    user_input_name = input('请输入要解锁的用户名:').strip()
    if user_input_name:
        with open(SHOP_LOCK,'r') as f,open(SHOP_LOCK_FILE_NEW,'w+') as f1:
            for i in f:
                if user_input_name == i.strip():
                    flag = True
                    continue
                else:
                    f1.write(i)
    else:
        return False
    if flag:
        print('\033[31;1m解锁成功!\033[0m')
        os.rename(SHOP_LOCK_FILE_NEW,SHOP_LOCK)
        log.logger_shop.info('管理员成功解锁用户 %s '%user_input_name)
        return True
    if not flag:
        print('\033[31;1m用户名[ %s ]不在黑名单列表中!\033[0m'%user_input_name)
        return False


def del_user(user):
    '''
    删除用户函数,主要
    :return: 用户删除成功返回True, 失败为False
    '''
    flag = False
    username_list = [] #定义一个空列表,用户把所有的用户名抓到里面来,来判断提用户是否存在
    user_input_name = input('\033[31;1m管理员[ %s ]先生/女士, 你要删谁? 给我个名字:  \033[0m'%user).strip()
    if user_input_name:
        with open(SHOP_USERDB,'r') as f2:  #遍历文件,把所有用户名追加到列表中
            for i in f2:
                user = i.strip().split(':')[0]
                username_list.append(user)
        if user_input_name in username_list:
            with open(SHOP_USERDB,'r') as f,open(SHOP_USERDB_NEW,'w+') as f1:
                for line in f:
                    user_name,password = line.strip().split(':')[0],line.strip().split(':')[1]
                    emailaddr,user_phone = line.strip().split(':')[2],line.strip().split(':')[3]
                    if user_input_name == user_name:
                        continue
                    else:
                        f1.write(line)
                        flag = True
        else:
            print('\033[31;1m抱歉, 你输入的用户名[ %s ]不存在!\033[0m '%user_input_name)
            return False
    if flag:
        os.rename(SHOP_USERDB_NEW,SHOP_USERDB)
        time.sleep(1)
        if input('\033[32;1m[ %s ]已经被删除!\033[0m '%user_input_name):pass
        log.logger_shop.info('%s 用户已经被管理员删除'%user_input_name)
        return True


def shop_admin_login():
    '''
    用户管理后台登录,主要是商城后台模块
    :return: 登录成功return成功的用户名,否则False
    '''
    flag = False
    Count = 0
    Lock_count = 1
    user_init = ''
    while Count < 3:
        user = input('请输入管理员账号:').strip()
        pwd = input('请输入管理员密码:').strip()
        if check_lock('shop',user):
            if user == user_init:
                Lock_count += 1
            else:
                user_init = user
                Lock_count -= 1
            with open(SHOP_ADMINDB,'r') as f:
                for i in f:
                    username,password = i.strip().split(':')[0],i.strip().split(':')[1]
                    if user == username and md5(pwd) == password:
                        print('登录成功')
                        log.logger_shop.info('管理员 %s 成功登录管理后台'%user)
                        flag = True
                    if flag:break
                else:
                    print('账户名或密码错误!')
                    log.logger_shop.info('%s 登录失败, 账号密码错误!'%user)
                    Count += 1
        else:
            return False
        if flag:
            return user
    else:
        if Lock_count == 2:
            deny_user('shop',user)



def atm_admin_login():
    '''
    ATM管理员登录函数
    :return:
    '''
    flag = False
    Count = 0
    Lock_count = 1
    user_init = ''
    admin_dict = json.load(open(ATM_ADMIN_DB,'r'))
    while Count < 3:
        user = input('请输入ATM管理员账号:').strip()
        pwd = input('请输入ATM管理员密码:').strip()
        if check_lock('shop',user):
            if user == user_init:
                Lock_count += 1
            else:
                user_init = user
                Lock_count -= 1
            if user == admin_dict.get('username') and md5(pwd) == admin_dict.get('password'):
                print('登录成功')
                log.logger_atm.info('管理员 %s 成功ATM登录管理后台'%user)
                ATM_ADMIN_STATUS['status']=True
                ATM_ADMIN_STATUS['username']=user
                return user
            else:
                print('账户名或密码错误!')
                log.logger_shop.info('%s 登录失败, 账号密码错误!'%user)
                Count += 1
    else:
        if Lock_count == 2:
            deny_user('atm',user)
        return False

