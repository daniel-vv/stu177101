#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import socketserver,socket,time
import configparser,subprocess
import os,sys,hashlib,json,re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from lib import log


class ProgressBar():
    '''
    进度条类
    '''
    def __init__(self, width=100):
        self.last_x = -1
        self.width = width

    def update(self, x):
        '''
        进度条方法
        :param x:
        :return:
        '''
        if self.last_x == int(x): return False
        self.last_x = int(x)
        pointer = int(self.width * (x / 100.0))
        sys.stdout.write( '\r%d%% [%s]' % (int(x), '#' * pointer + '.' * (self.width - pointer)))
        sys.stdout.flush()
        if x == 100: print()


def GetConfig(servertype,key):
    '''
    获取配置文件中的参数的函数
    :param servertype: 接受用户传入一个类型,有两个字段, client和server
    :param key: key是接受用户传入的要获取的key值,如ip
    :return:   如果获取成功将return 获取的结果
    '''
    config = configparser.ConfigParser()
    config.read(settings.CONFIG,encoding='utf-8')  #读取配置文件

    if config.has_section(servertype):
        return config.get(servertype,key)
    else:
        return False


def MD5(password):
    '''
    用md5校验密码的函数
    :param password: 接受用户传入的一个密码
    :return: 返回一个hash过后的密码
    '''
    result = hashlib.md5(bytes('fe!49sKQe3Xe8',encoding='utf-8'))  #添加填充字符,防止暴库
    result.update(bytes(password,encoding='utf-8'))

    return result.hexdigest()  #return加密后的密码


def md5sum(filename):
    '''
    文件完整性校验
    :param filename:  接受用户输入一个文件
    :return:          返回给用户一个值
    '''
    f = open(filename,'rb')
    content = f.read()
    f.close()

    m = hashlib.md5(content)
    file_md5 = m.hexdigest()

    return file_md5


class MyFtpServer(socketserver.BaseRequestHandler):
    '''
    FTPServer 类
    '''
    def handle(self):
        '''
        handle方法
        :return:
        '''
        self.request.sendall(bytes('欢迎来到DBQ的FTP程序',encoding='utf-8'))
        global USER_STATUS
        flag = False
        while not flag:
            recv_user_info = self.request.recv(1024)
            if len(recv_user_info) == 0:break
            user,pwd = recv_user_info.decode().split()
            result = self.login(user,pwd)
            if result == 0:
                self.request.send(bytes('success',encoding='utf-8'))
                if GetConfig(user,'quota'):
                    defa_quota = GetConfig(user,'quota')  #如果用户设置了单独的配额,使用用户配额, 并转换为字节
                    quota = float(defa_quota)*1024*1024
                else:
                    defa_quota = GetConfig('default','quota')   #如果没设置单独的使用默认的,即400M, 并转换为字节
                    quota = float(defa_quota)*1024*1024
                userdb = json.load(open(settings.USERDB,'r'))
                used = userdb[user].get('used')
                settings.USER_STATUS[user] = {'ip_port':self.client_address,
                                              'username':user,
                                              'homedir':os.path.join(settings.HOMEDIR,user),
                                              'currdir':os.path.join(settings.HOMEDIR,user),
                                              'quota':quota,
                                              'used':used}
                flag = True   #登录成功后退出循环
            elif result == 1:
                self.request.send(bytes('failure',encoding='utf-8'))
            elif result == 2:
                self.request.send(bytes('logined',encoding='utf-8'))
        self.user = user

        while True:
            data = self.request.recv(1024)
            if len(data) == 0:break
            if data.decode() == 'bye':

                res = self.logout(self.user)  #退出登录
                if res:
                    self.request.send(bytes('Goodbye!',encoding='utf8'))   #成功退出,发送bye给客户端
                    break
                else:
                    self.request.send(bytes('我也不知道除了啥问题,似乎没有成功退出',encoding='utf-8'))

            else:
                task_data = json.loads(data.decode())
                task_action = task_data.get('action')
                if hasattr(self,task_action):       #反射
                    func = getattr(self,task_action)
                    func(task_data)
                    # print(task_action,task_data)
                else:
                    print('不支持的操作!-- %s'%data.decode())
                    self.request.send(bytes('不支持的操作!-- %s'%data.decode(),encoding='utf-8'))

    def put(self,*args,**kwargs):
        '''
        上传文件到FTP服务器
        :return:
        '''
        print('-----put-----')
        abs_filepath = args[0].get('filename')  #获取用户传过来的文件名
        filesize = args[0].get('file_size') #获取文件大小
        # filepath = os.path.join(settings.BASEDIR,'db','home',settings.USER_STATUS[self.user].get('username'))
        filepath = settings.USER_STATUS[self.user].get('currdir')
        filename = abs_filepath.split('/')[-1]
        userdb = json.load(open(settings.USERDB,'r'))          #加载用户配置文件
        quota = settings.USER_STATUS[self.user].get('quota')   #加载用户限额
        recv_size = 0

        if filesize + userdb[self.user].get('used') >= quota:
            server_respone = {"status":"overrun"}
        if os.path.exists(os.path.join(filepath,filename)):
            if os.stat(os.path.join(filepath,filename)).st_size == filesize:  #文件已经存在,并且接受完成
                server_respone = {"status":"finish"}  #告诉客户端文件已存在,并且接受完成
            else:        #如果大小不等
                have_size = os.stat(os.path.join(filepath,filename)).st_size           #已接受的文件大小
                server_respone = {"status":"unfinish","have_size":have_size}
                self.request.send(bytes(json.dumps(server_respone),encoding='utf-8')) #发送服务器响应
                res = self.request.recv(1024)
                client_respone = json.loads(res.decode() )
                if client_respone['status'] == 200:
                    server_respone = {"status":201}
                    recv_size = have_size   #接受大小从已接受的大小开始计算
                    f = open(os.path.join(filepath,filename),'ab')   #打开文件以追加形式打开
                elif client_respone['status'] == 400:
                    return False   #用户放弃操作

        else:
            server_respone = {"status":"ok"}
            f = open(os.path.join(filepath,filename),'wb')       #如果文件不存在,且配额满足需求,直接打开文件

        self.request.send(bytes(json.dumps(server_respone),encoding='utf-8')) #发送服务器响应

        while recv_size < filesize:
            data = self.request.recv(4096)
            f.write(data)
            recv_size += len(data)
        f.close()

        res = self.request.recv(1024)
        md5_value = md5sum(os.path.join(filepath,filename))

        if str(res,encoding='utf-8') == md5_value:
            self.request.send(bytes('success',encoding='utf-8'))

            userdb[self.user]['used'] += recv_size
            # print('已经使用的空间: ',userdb[self.user].get('used'))
            json.dump(userdb,open(settings.USERDB,'w'))

        else:
            self.request.send(bytes('fail',encoding='utf-8'))
            log.logger.info('%s 成功文件 %s 失败, 完整性校验失败'%(self.user,filename))

    def ls(self,*args,**kwargs):
        '''
        列出目录下的文件和文件夹
        :param args:
        :param kwargs:
        :return:
        '''
        flag = args[0].get('dirname')
        if not flag:  #如果用户没有输入列出的指定目录,
            # print('+'*30)
            Dirname = settings.USER_STATUS[self.user].get('currdir')  #Dirname 为当前目录
            abs_path = Dirname     #用户目录的绝对路径
        else:
            # print('='*30)
            Dirname = flag      #如果用户输入了,那么拼接一下
            abs_path = os.path.join(settings.USER_STATUS[self.user].get('currdir'),Dirname)

        if abs_path.count('..'):
            if os.path.abspath(abs_path).startswith(settings.USER_STATUS[self.user].get('homedir')):
                if os.path.isdir(abs_path):
                    ls_data = os.listdir(abs_path)  #列出目录
                    data = {"size":len(ls_data),"status":"pass"}
                    self.request.send(bytes(json.dumps(data),encoding='utf-8'))    #发送一个读取文件长度给用户
                    client_res = self.request.recv(1024)
                    client_response = json.loads(client_res.decode())
                    if client_response.get('status') == 'ok':
                        for line in range(len(ls_data)):
                            self.request.send(bytes(ls_data[line],encoding='utf-8'))  #发送给用户
                            time.sleep(0.03)
                else:
                    data = {"status":"notfount"}
                    self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #不存在
            else:
                data = {"status":"forbidden"}
                self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #访问拒绝!
        elif abs_path.startswith(settings.USER_STATUS[self.user].get('homedir')):
            if os.path.isdir(abs_path):
                ls_data = os.listdir(abs_path)  #列出目录
                data = {"size":len(ls_data),"status":"pass"}
                self.request.send(bytes(json.dumps(data),encoding='utf-8'))    #发送一个读取文件长度给用户
                client_res = self.request.recv(1024)
                client_response = json.loads(client_res.decode())
                if client_response.get('status') == 'ok':
                    for line in range(len(ls_data)):
                        self.request.send(bytes(ls_data[line],encoding='utf-8'))  #发送给用户
                        time.sleep(0.03)
            else:
                data = {"status":"notfount"}
                self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #不存在
        # elif abs_path.startswith(settings.USER_STATUS[self.user].get('homedir')):
        #     if os.path.isdir(abs_path):
        #         ls_data = os.listdir(abs_path)  #列出目录
        #         # print(ls_data)
        #         data = {"size":len(ls_data),"status":"pass"}
        #         # print(data)
        #         self.request.send(bytes(json.dumps(data),encoding='utf-8'))    #发送一个读取文件长度给用户
        #         client_res = self.request.recv(1024)
        #         client_response = json.loads(client_res.decode())
        #         if client_response.get('status') == 'ok':
        #             for line in range(len(ls_data)):
        #                 self.request.send(bytes(ls_data[line],encoding='utf-8'))  #发送给用户
        #                 time.sleep(0.03)
        #     else:
        #         data = {"status":"notfount"}
        #         self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #不存在
        else:
            data = {"status":"forbidden"}
            self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #访问拒绝!


    def delete(self,*args,**kwargs):
        '''
        删除目录下的文件和文件夹
        :param args:
        :param kwargs:
        :return:
        '''
        Dirname = args[0].get('dirname')  #取出文件名
        abs_path = os.path.join(settings.USER_STATUS[self.user].get('currdir'),Dirname)   #拼接一下

        userdb = json.load(open(settings.USERDB,'r'))
        filesize = os.stat(abs_path).st_size

        if abs_path.count('..'):
            if os.path.abspath(abs_path).startswith(settings.USER_STATUS[self.user].get('homedir')):
                if os.path.isdir(abs_path):
                    os.rmdir(abs_path)
                    data = {"status":"ok"}
                    self.request.send(bytes(json.dumps(data),encoding='utf-8'))
                    userdb[self.user]['used'] -= filesize
                    json.dump(userdb,open(settings.USERDB,'w'))

                    log.logger.info('%s 删除文件 %s 成功, 登录地址: %s'%(self.user,Dirname,self.client_address))
                elif os.path.isfile(abs_path):
                    os.remove(abs_path)
                    data = {"status":"ok"}
                    self.request.send(bytes(json.dumps(data),encoding='utf-8'))
                    userdb[self.user]['used'] -= filesize
                    json.dump(userdb,open(settings.USERDB,'w'))
                    log.logger.info('%s 删除文件 %s 成功, 登录地址: %s'%(self.user,Dirname,self.client_address))
                else:
                    data = {"status":"notfount"}
                    self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #不存在
                    log.logger.info('%s 删除文件 %s 失败, 文件不存在, 登录地址: %s'%(self.user,Dirname,self.client_address))
            else:
                data = {"status":"forbidden"}
                self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #访问拒绝!
                log.logger.info('%s 删除文件 %s 遭拒绝, 原因是没有权限! 登录地址: %s'%(self.user,Dirname,self.client_address))
        #if os.path.abspath(Dirname).startswith(settings.USER_STATUS[self.user].get('homedir')):
        elif abs_path.startswith(settings.USER_STATUS[self.user].get('homedir')):
            if os.path.abspath(abs_path).startswith(settings.USER_STATUS[self.user].get('homedir')):
                if os.path.isdir(abs_path):
                    os.rmdir(abs_path)
                    data = {"status":"ok"}
                    self.request.send(bytes(json.dumps(data),encoding='utf-8'))

                    userdb[self.user]['used'] -= filesize
                    json.dump(userdb,open(settings.USERDB,'w'))

                    log.logger.info('%s 删除文件 %s 成功, 登录地址: %s'%(self.user,Dirname,self.client_address))
                elif os.path.isfile(abs_path):
                    os.remove(abs_path)
                    data = {"status":"ok"}
                    self.request.send(bytes(json.dumps(data),encoding='utf-8'))

                    userdb[self.user]['used'] -= filesize
                    json.dump(userdb,open(settings.USERDB,'w'))

                    log.logger.info('%s 删除文件 %s 成功, 登录地址: %s'%(self.user,Dirname,self.client_address))
                else:
                    data = {"status":"notfount"}
                    self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #不存在
                    log.logger.info('%s 删除文件 %s 失败, 文件不存在, 登录地址: %s'%(self.user,Dirname,self.client_address))
            else:
                data = {"status":"forbidden"}
                self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #访问拒绝!
                log.logger.info('%s 删除文件 %s 遭拒绝, 原因是没有权限! 登录地址: %s'%(self.user,Dirname,self.client_address))
        else:
            data = {"status":"forbidden"}
            self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #访问拒绝!
            log.logger.info('%s 删除文件 %s 遭拒绝, 原因是没有权限! 登录地址: %s'%(self.user,Dirname,self.client_address))

    def mkdir(self,*args,**kwargs):
        '''
        创建文件夹
        :param args:
        :param kwargs:
        :return:
        '''
        Dirname = args[0].get('dirname')  #取出文件名
        abs_path = os.path.join(settings.USER_STATUS[self.user].get('currdir'),Dirname)   #拼接一下

        userdb = json.load(open(settings.USERDB,'r'))

        if abs_path.count('..'):
            if os.path.abspath(abs_path).startswith(settings.USER_STATUS[self.user].get('homedir')):
                if not os.path.exists(abs_path):
                    os.makedirs(abs_path)
                    filesize = os.stat(abs_path).st_size
                    data = {"status":"ok"}
                    self.request.send(bytes(json.dumps(data),encoding='utf-8'))

                    userdb[self.user]['used'] += filesize
                    json.dump(userdb,open(settings.USERDB,'w'))

                    log.logger.info('%s 创建目录 %s 成功, 登录地址: %s'%(self.user,Dirname,self.client_address))
                else:
                    data = {"status":"exist"}
                    self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #不存在
                    log.logger.info('%s 创建目录 %s 失败, 文件已经存在, 登录地址: %s'%(self.user,Dirname,self.client_address))
            else:
                data = {"status":"forbidden"}
                self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #访问拒绝!
                log.logger.info('%s 创建目录 %s 遭拒绝, 原因是没有权限! 登录地址: %s'%(self.user,Dirname,self.client_address))
        #if os.path.abspath(Dirname).startswith(settings.USER_STATUS[self.user].get('homedir')):
        elif abs_path.startswith(settings.USER_STATUS[self.user].get('homedir')):
            if os.path.abspath(abs_path).startswith(settings.USER_STATUS[self.user].get('homedir')):
                if not os.path.exists(abs_path):
                    os.makedirs(abs_path)
                    filesize = os.stat(abs_path).st_size
                    data = {"status":"ok"}
                    self.request.send(bytes(json.dumps(data),encoding='utf-8'))

                    userdb[self.user]['used'] += filesize
                    json.dump(userdb,open(settings.USERDB,'w'))

                    log.logger.info('%s 创建目录 %s 成功, 登录地址: %s'%(self.user,Dirname,self.client_address))
                else:
                    data = {"status":"exist"}
                    self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #不存在
                    log.logger.info('%s 创建目录 %s 失败, 文件已经存在, 登录地址: %s'%(self.user,Dirname,self.client_address))
            else:
                data = {"status":"forbidden"}
                self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #访问拒绝!
                log.logger.info('%s 创建目录 %s 遭拒绝, 原因是没有权限! 登录地址: %s'%(self.user,Dirname,self.client_address))

        else:
            data = {"status":"forbidden"}
            self.request.send(bytes(json.dumps(data),encoding='utf-8'))   #访问拒绝!
            log.logger.info('%s 删除文件 %s 遭拒绝, 原因是没有权限! 登录地址: %s'%(self.user,Dirname,self.client_address))

    def get(self,*args,**kwargs):
        '''
        下载文件到本地
        :return:
        '''
        print('------Get------')
        abs_filepath = args[0].get('filename')  #获取用户要下载的文件名和绝对路径
        count_num = abs_filepath.count('/')
        # bar = ProgressBar()  #实例化进度条类

        if count_num == 0:
            filename = abs_filepath
            filepath = settings.USER_STATUS[self.user].get('currdir')   #当前工作路径
            if os.path.isfile(os.path.join(filepath,filename)):
                file_size = os.stat(os.path.join(filepath,filename)).st_size  #发送单位为字节

                self.request.send(bytes('ok',encoding='utf-8'))  #发送给用户一个找到文件的信息
                send_msg = {"filesize":file_size,"filename":filename}
                self.request.send(bytes(json.dumps(send_msg),encoding='utf-8'))   #发送文件大小和文件名给客户端

                response = self.request.recv(1024)
                client_respone = json.loads(response.decode())
                if client_respone['status'] == 200:   #本地没有要下载的文件
                    print('开始传送文件: ',filename)
                elif client_respone['status'] == 210:  #断点续传
                    have_size = client_respone['have_size']   #获取已接受到的大小
                    send_size = have_size

                elif client_respone['status'] == 400:  #客户端文件已存在
                    return False

                elif client_respone['status'] == 401:  #用户放弃续传
                    return False

                f = open(os.path.join(settings.USER_STATUS[self.user].get('currdir'),filename),'rb')
                f.seek(send_size)   #改变文件指针
                for line in f:
                    self.request.send(line)
                    send_size += len(line)
                    # bar.update(send_size*100/(file_size-1))  #进度条
                print()
                f.close()
                #md5校验
                md5_value = md5sum(os.path.join(settings.USER_STATUS[self.user].get('currdir'),filename))
                self.request.send(bytes(md5_value,encoding='utf-8'))

                res = self.request.recv(1024)
                if str(res,encoding='utf-8') == 'success':
                    log.logger.info('%s 成功下载了文件 %s'%(self.user,filename))
                else:
                    log.logger.info('%s 下载文件[ %s ] 出现错误'%(self.user,filename))

            elif os.path.isdir(os.path.join(filepath,filename)):
                self.request.send(bytes('不支持文件夹的下载,请输入一个文件名,或者相对路径的文件!',encoding='utf-8'))
            else:
                self.request.send(bytes('文件不存在!',encoding='utf-8'))
        else:
            filepath = abs_filepath.split('/')[0]  #取出用户传入的目录的开头路径
            filename = abs_filepath.split('/')[-1]
            par_path = os.path.join(settings.USER_STATUS[self.user].get('currdir'),abs_filepath)

            if os.path.isdir(par_path):    #如果是目录的话:
                self.request.send(bytes('不支持文件夹的下载,请输入一个文件名,或者相对路径的文件!',encoding='utf-8'))

            elif os.path.isfile(par_path):  # 如果是文件的话下载
                self.request.send(bytes('ok',encoding='utf-8'))  #发送给用户一个找到文件的信息
                file_size = os.stat(par_path).st_size  #获取文件大小
                send_msg = {"filesize":file_size,"filename":filename}   #文件大小以及文件名的字典
                self.request.send(bytes(json.dumps(send_msg),encoding='utf-8'))   #发送文件大小和文件名给客户端

                response = self.request.recv(1024)   #接受用户传送一个确认信息

                client_respone = json.loads(response.decode())
                send_size = 0

                if client_respone['status'] == 200:
                    print('开始传送文件: ')

                elif client_respone['status'] == 210:  #断点续传
                    have_size = client_respone['have_size']   #获取已接受到的大小
                    send_size = have_size

                elif client_respone['status'] == 400:  #客户端文件已存在
                    return False
                elif client_respone['status'] == 401:  #用户放弃续传
                    return False

                f = open(par_path,'rb')
                f.seek(send_size)
                for line in f:
                    self.request.send(line)
                    # bar.update(send_size*100/(file_size-1))  #进度条
                f.close()
                print()
                md5_value = md5sum(par_path)
                self.request.send(bytes(md5_value,encoding='utf-8'))

                res = self.request.recv(1024)
                if str(res,encoding='utf-8') == 'success':
                    log.logger.info('%s 成功下载了文件 %s'%(self.user,filename))
                else:
                    log.logger.info('%s 下载文件[ %s ] 出现错误'%(self.user,filename))
            else:
                #没有匹配文件,不存在的操作
                self.request.send(bytes('你输入的文件夹/文件不存在,或者没有权限操作!',encoding='utf-8'))

    def login(self,user,pwd):
        '''
        用户登录方法
        :param user: 接受用户输入账号
        :param pwd:  接受用户传入密码
        :return:     return 0: 表示认证成功, 1: 表示账户或者密码错误, 2, 表示用于已经登录,不能重复登录!
        '''
        userdb = json.load(open(settings.USERDB,'r'))
        if user in userdb.keys():
            if not settings.USER_STATUS.get(user):
                if user == userdb[user].get('username') and MD5(pwd) == userdb[user].get('password'):
                    log.logger.info('%s 登录FTP服务器成功, 登录IP/Port: %s'%(user,self.client_address))
                    return 0
                else:
                    log.logger.info('%s 尝试登录FTP服务器失败,用户名或者密码不匹配'%user)
                    return 1
            else:
                log.logger.info('%s 已经登录FTP, 拒绝重复登录'%user)
                return 2
        else:
            log.logger.info('%s 用户名不存在!'%user)
            return 1


    def logout(self,user):
        '''
        注销用户方法
        :param user:
        :return:
        '''
        del settings.USER_STATUS[user]  #删除用户全局变量中的值
        log.logger.info('[ %s ] 退出登录'%user)
        return True


    def cd(self,*args,**kwargs):
        '''
        服务器目录切换方法
        :param args:
        :param kwargs:
        :return:
        '''
        print('------cd------')
        flag = args[0].get('dirname')   #获取要改变的目录
        Dirname = flag if args[0].get('dirname') else settings.USER_STATUS[self.user].get('currdir')  #用户列出的目录的相对路径
        abs_path = os.path.join(settings.USER_STATUS[self.user].get('currdir'),Dirname)  #用户目录的绝对路径

        if abs_path.startswith(settings.USER_STATUS[self.user].get('homedir')):
            #如果切换的目录是以homedir开头,证明是用户家目录下的文件
            if os.path.isdir(abs_path):
                os.chdir(abs_path)
                settings.USER_STATUS[self.user]['currdir'] = os.path.abspath(abs_path)
                self.request.send(bytes('切换完成, 当前目录: %s'%Dirname,encoding='utf-8'))
            else:
                self.request.send(bytes('Sorry, 目录不存在!',encoding='utf-8'))
        else:
            self.request.send(bytes('Forbidden, 禁止切换到此目录!',encoding='utf-8'))

    def pwd(self,*args,**kwargs):
        '''
        打印当前所在目录
        :param args:
        :param kwargs:
        :return:
        '''
        pwd = settings.USER_STATUS[self.user].get('currdir')
        self.request.send(bytes(pwd,encoding='utf-8'))


class Client:
    '''
    客户端使用的类
    '''
    def __init__(self):
        '''
        构造函数,初始化客户端程序
        :return:
        '''
        ip_port = tuple((GetConfig('client','ip'),int(GetConfig('client','port'))))  #获取配置文件中IP和端口
        self.client = socket.socket()
        self.client.connect(ip_port)          #连接服务器
        welcome_msg = self.client.recv(1024)  #欢迎消息
        print('\033[32;1m%s\033[0m'%welcome_msg.decode())

    def Send(self,msg):
        self.client.send(bytes(msg,encoding='utf-8'))

    def Recv(self):
        result = self.client.recv(1024)
        return result

    def put(self,*args,**kwargs):
        '''put      客户端上传方法.  用法: put /path/to/filename'''
        task_type = args[0][0]
        abs_filepath = args[0][1]
        # print(task_type,abs_filepath)
        if os.path.isfile(abs_filepath):
            file_size = os.stat(abs_filepath).st_size
            filename = abs_filepath
            # print('Size: %s, Filename: %s'%(file_size,filename))
            msg_data = {"action":task_type,"filename":filename,"file_size":file_size}
            self.Send(json.dumps(msg_data))
            server_confirmation_msg = self.client.recv(1024)
            # print(server_confirmation_msg)
            confirm_data = json.loads(str(server_confirmation_msg,encoding='utf-8'))  #接受服务器确认信息
            if confirm_data['status'] == 'ok':  #而后开始发送文件
                print('开始上传文件: ',filename)
                f = open(abs_filepath,'rb')
                send_size = 0
                bar = ProgressBar()
                for line in f:
                    self.client.send(line)
                    send_size += len(line)
                    bar.update(send_size*100/(file_size-1))  #进度条
                f.close()
                print()
                print('\033[32;1m文件上传完成, 正在进行完整性校验...\033[0m')

                md5_value = md5sum(abs_filepath)

                self.client.send(bytes(md5_value,encoding='utf-8'))
                server_respone = self.client.recv(1024)

                if str(server_respone,encoding='utf-8') == 'success':
                    print('完整性校验成功, 您已成功上传文件 %s ' %abs_filepath)
                else:
                    print('\033[31;1m文件发送失败,出现未知错误,请重新发送或者联系管理员!\033[0m')
            elif confirm_data['status'] == 'finish':
                print('\033[31;1m目标文件已经存在!\033[0m')
            elif confirm_data['status'] == 'unfinish':   #如果文件存在
                have_size = confirm_data['have_size']
                inp = input('目标文件已存在, 并且未发送完成,是否续传? y/Y').strip()
                if inp == 'y' or inp == 'Y':
                    client_respone = {"status":200}
                    self.client.send(bytes(json.dumps(client_respone),encoding='utf-8'))
                    res = self.client.recv(1024)
                    server_respone = json.loads(res.decode())
                    if server_respone['status'] == 201:
                        print('\033[31;1m正在断点续传文件...\033[0m')
                        f = open(abs_filepath,'rb')
                        f.seek(have_size)   #将文件指针指向对方已接收到的大小
                        send_size = have_size
                        bar = ProgressBar()
                        for line in f:
                            self.client.send(line)
                            send_size += len(line)
                            bar.update(send_size*100/(file_size-1))  #进度条
                        f.close()
                        print()
                        print('\033[32;1m文件续传完成, 正在进行完整性校验...\033[0m')

                        md5_value = md5sum(abs_filepath)

                        self.client.send(bytes(md5_value,encoding='utf-8'))
                        server_respone = self.client.recv(1024)

                        if str(server_respone,encoding='utf-8') == 'success':
                            print('完整性校验成功, 您已成功上传文件 %s ' %abs_filepath)
                        else:
                            print('\033[31;1m文件发送失败,出现未知错误,请重新发送或者联系管理员!\033[0m')

                else:
                    print('\033[31;1m用户放弃续传!\033[0m')
                    client_respone = {"status":400}
                    self.client.send(bytes(json.dumps(client_respone),encoding='utf-8'))

            elif confirm_data['status'] == 'overrun':
                print('\033[31;1m超出用户磁盘限额,请联系管理员调整配额!\033[0m')
                return False

        else:
            print('\033[31;1m文件[ %s ]不存在!\033[0m'%abs_filepath)
            return False

    def ls(self,*args,**kwargs):
        '''ls   列出服务器上指定位置下的所有文件/文件夹.   用法: ls [dirname] '''
        if type(args[0]) is str:
            # print('===================')
            msg_data = {"action":args[0],"dirname":False}
            self.client.send(bytes(json.dumps(msg_data),encoding='utf-8'))
            data = self.client.recv(1024)
            data_dict = json.loads(str(data,encoding='utf-8') )   #加载服务器发送给用户的列目录信息
            # print(str(data.decode()))
            recv_len = data_dict.get('size')     #取出文件个数
            client_response = {"status":"ok"}
            self.client.send(bytes(json.dumps(client_response),encoding='utf-8'))
            recv_size = 0
            if recv_len > 0:
                while recv_size < recv_len:   #循环接受文件
                    recv_data = self.Recv()
                    recv_size += 1
                    print(recv_data.decode())
        else:
            task_type = args[0][0]
            Dirname = args[0][1]
            print(task_type,Dirname)
            msg_data = {"action":task_type,"dirname":Dirname}
            self.client.send(bytes(json.dumps(msg_data),encoding='utf-8'))
            # recv_len = self.Recv()
            data = self.Recv()
            data_dict = json.loads(data.decode())
            if data_dict.get('status') == 'pass':   #如果权限通过,接受并打印列出的文件/文件夹
                recv_len = data_dict.get('size')
                client_response = {"status":"ok"}
                self.client.send(bytes(json.dumps(client_response),encoding='utf-8'))
                recv_size = 0
                while recv_size < recv_len:
                    recv_data = self.Recv()
                    recv_size += 1
                    print(recv_data.decode())
            elif data_dict.get('status') == 'notfount':
                print('\033[31;1mNotFount: 文件/文件夹不存在!\033[0m')
            else:
                print('\033[31;1mForbidden: 没有操作权限!\033[0m')

    def lpwd(self,*args,**kwargs):
        '''lpwd     列出客户端在本地当前的目录.   用法: lpwd '''
        print('当前所在本地目录: ',os.getcwd())

    def ldir(self,*args,**kwargs):
        '''ldir     列出本地目录下的文件和文件夹, 用法:  ldir [dirname]'''
        if type(args[0]) is str:
            res = os.listdir(os.getcwd())
            for i in res:
                print(i)
        else:
            Dirname = args[0][1]
            if os.path.exists(Dirname):
                res = os.listdir(Dirname)
                for i in res:
                    print(i)
            else:
                print('\033[31;1m输入的目录不存在!\033[0m'%Dirname)

    def lcd(self,*args,**kwargs):
        '''lcd    改变本地路径命令, 用法:  lcd /tmp'''
        if type(args[0]) is not str:
            Dirname = args[0][1]    #用户输入的路径
            if os.path.isdir(Dirname):
                os.chdir(Dirname)
                print('切换目录成功,当前所在目录:',Dirname)

    def cd(self,*args,**kwargs):
        '''cd   切换服务器上的目录.  用法:  cd dirname'''
        task_type = args[0][0]
        abs_filepath = args[0][1]
        msg_data = {"action":task_type,"dirname":abs_filepath}
        self.client.send(bytes(json.dumps(msg_data),encoding='utf-8'))
        res = self.client.recv(1024)
        if str(res,encoding='utf-8').startswith('For'):
            print('\033[31;1m%s\033[0m'%(str(res,encoding='utf-8')))
        elif str(res,encoding='utf-8').startswith('Sor'):
            print('\033[31;1m%s\033[0m'%(str(res,encoding='utf-8')))
        else:
            print(str(res,encoding='utf-8'))

    def pwd(self,*args,**kwargs):
        '''pwd   返回当前所在服务器的目录.  用法:  pwd '''
        task_type = args[0]
        msg_data = {"action":task_type}
        self.client.send(bytes(json.dumps(msg_data),encoding='utf-8'))  #发送给服务器
        res = self.client.recv(1024)
        print('当前路径: %s'%str(res,encoding='utf-8'))

    def delete(self,*args,**kwargs):
        '''delete   删除服务器上目录/文件,   用法:  delete /path/to/filename'''
        if type(args[0]) is str:
            print('===================')
            print('\033[31;1m命令不完整, 缺少参数!\033[0m')
            return False
        else:
            print('#####################')
            task_type = args[0][0]
            Dirname = args[0][1]
            print(task_type,Dirname)
            msg_data = {"action":task_type,"dirname":Dirname}
            self.client.send(bytes(json.dumps(msg_data),encoding='utf-8'))  #发送要删除的文件和目录

            data = self.Recv()
            data_dict = json.loads(data.decode())
            if data_dict.get('status') == 'ok':   #如果权限通过,接受并打印列出的文件/文件夹
                print('成功删除文件/文件夹: %s'%Dirname)
            elif data_dict.get('status') == 'notfount':
                print('\033[31;1mNotFount: 文件/文件夹不存在!\033[0m')
            else:
                print('\033[31;1mForbidden: 没有操作权限!\033[0m')

    def mkdir(self,*args,**kwargs):
        '''mkdir   创建服务器上目录,   用法:  mkdir dirname'''
        if type(args[0]) is str:
            print('\033[31;1m命令不完整, 缺少参数!\033[0m')
            return False
        else:
            task_type = args[0][0]
            Dirname = args[0][1]
            print(task_type,Dirname)
            msg_data = {"action":task_type,"dirname":Dirname}
            self.client.send(bytes(json.dumps(msg_data),encoding='utf-8'))  #发送要删除的文件和目录

            data = self.Recv()
            data_dict = json.loads(data.decode())
            if data_dict.get('status') == 'ok':   #如果权限通过,接受并打印列出的文件/文件夹
                print('成功创建目录: %s'%Dirname)
            elif data_dict.get('status') == 'exist':
                print('\033[31;1m 抱歉, 文件/文件夹已经存在!\033[0m')
            else:
                print('\033[31;1mForbidden: 没有操作权限!\033[0m')

    def help(self,*args,**kwargs):
        '''help   获取帮助信息,  用法: help [command]'''
        if type(args[0]) is str:
            print('''
get     put     ls      lpwd    lcd     ldir    bye     quit    cd     pwd    delete    mkdir
            ''')
        else:
            cmd = args[0][1]
            if hasattr(self,cmd):
                res = getattr(self,cmd)
                print(res.__doc__)

    def get(self,*args,**kwargs):
        '''从服务器下载文件 get /path/to/filename'''
        task_type = args[0][0]
        abs_filepath = args[0][1]
        msg_data = {"action":task_type,"filename":abs_filepath}

        self.client.send(bytes(json.dumps(msg_data),encoding='utf-8'))   #发送要下载信息给服务器

        recv_data = self.client.recv(1024)
        if str(recv_data,encoding='utf-8') == 'ok':   #收到服务器找到目录中的文件信息
            recv_file_info = self.client.recv(1024)
            file_info = json.loads(recv_file_info.decode() )
            filesize = file_info.get('filesize')
            filename = file_info.get('filename')

        if os.path.exists(filename):    #如果文件已存在
            have_size = os.stat(filename).st_size
            if have_size == filesize:
                print('\033[31;1m本地已存在%s文件!\033[0m'%filename)
                client_respone = {"status":400}  #发送确认给服务器, 客户端这边已经存在文件了,无需再往下进行了
                self.client.send(bytes(json.dumps(client_respone),encoding='utf-8'))
                return False
                #self.client.send(bytes(json.dumps(client_respone),encoding='utf-8'))
            else:
                inp = input('本地已存在文件, 但未完全接受, 是否续传? y/Y').strip()
                if inp == 'Y' or inp == 'y':
                    client_respone = {"status":210,"have_size":have_size}
                       #发送给服务器,客户端这边要断点续传
                else:
                    print('\033[31;1m用户放弃断点续传\033[0m')
                    client_respone = {"status":401}
                    self.client.send(bytes(json.dumps(client_respone),encoding='utf-8'))
                    return False

            self.client.send(bytes(json.dumps(client_respone),encoding='utf-8'))

            f = open(filename,'ab')    #以追加的模式打开文件
            print('开始续传文件: %s'%filename)
            recv_size = have_size
            bar = ProgressBar()
            while recv_size < filesize:
                data = self.client.recv(2048)
                f.write(data)
                recv_size += len(data)

                bar.update(recv_size*100/(filesize-1))  #进度条
            f.close()
            print()
            print('\033[32;1m文件续传完成,正在进行完整性校验, 请稍后...\033[0m')
            res = self.client.recv(1024)
            md5_value = md5sum(filename)
            if str(res,encoding='utf-8') == md5_value:
                self.client.send(bytes('success',encoding='utf-8'))
                print('校验完成, 您成功下载文件 [ %s ]!'%filename)
            else:
                print('\033[31;1m文件下载出现未知错误, 请重试...\033[0m')

        else:   #如果本地不存在文件, 直接发送200代码,告诉服务器开始传输数据
            client_respone = {"status":200}
            self.client.send(bytes(json.dumps(client_respone),encoding='utf-8')) #发送确认给服务器,客户端准备好接受了
            f = open(filename,'wb')
            print('开始下载文件: %s'%filename)
            print(filename,filesize)
            recv_size = 0
            bar = ProgressBar()
            while recv_size < filesize:
                data = self.client.recv(2048)
                f.write(data)
                recv_size += len(data)

                bar.update(recv_size*100/(filesize-1))  #进度条
            f.close()
            print()
            print('\033[32;1m文件下载完成,正在进行完整性校验, 请稍后...\033[0m')
            res = self.client.recv(1024)
            md5_value = md5sum(filename)

            if str(res,encoding='utf-8') == md5_value:
                self.client.send(bytes('success',encoding='utf-8'))
                print('校验完成, 您成功下载文件 [ %s ]!'%filename)
            else:
                print('\033[31;1m文件下载出现未知错误, 请重试...\033[0m')
        #
        # else:
        #     print('\033[31;1m%s\033[0m'%str(recv_data,encoding='utf-8'))

    def login(self):
        '''
        客户端登录服务器
        :return:
        '''
        flag = False
        while not flag:
            username = input('请输入你的账号:').strip()
            if username:
                password = input('请输入你的密码:').strip()
                if password:
                    self.Send('%s %s'%(username,password))  #发送账号和密码到服务器认证
                    result = self.Recv()                    #接受用户返回的认证结果
                    if str(result,encoding='utf-8') == 'success':
                        print('\033[32;1m登录成功 [ %s ]\033[0m'%username)
                        self.user = username
                        flag = True
                    elif str(result,encoding='utf-8') == 'logined':
                        print('\033[31;1m[ %s ]已经登录了,不能重复登录!\033[0m'%username)
                    else:
                        print('\033[31;1m登录失败, 账户名或者密码错误!\033[0m')

    def client_run(self):
        '''
        客户端主运行方法
        :return:
        '''
        self.login()
        while True:
            cmd = input('ftp> ').strip()
            if cmd == 'bye' or cmd == 'quit' or cmd == 'QUIT':
                self.Send('bye')  #发送bye给服务器
                data = self.Recv()
                if str(data,encoding='utf-8') == 'Goodbye!':
                    print(str(data,encoding='utf-8'))
                    break
                else:
                    print(str(data,encoding='utf-8'))
            elif len(cmd) == 0:
                continue
            else:
                cmd_list = cmd.split()
                task_action = cmd_list[0]

                if len(cmd_list) == 2:
                    if hasattr(self,task_action):
                        func = getattr(self,task_action)
                        func(cmd_list)
                        continue
                    else:
                        print('\033[31;1m不支持的操作!\033[0m')
                        continue
                elif hasattr(self,task_action):
                    func = getattr(self,task_action)
                    func(task_action)
                    continue
                else:
                    print('\033[31;1m不支持的操作!\033[0m')
                    continue



