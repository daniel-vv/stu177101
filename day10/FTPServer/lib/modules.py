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
        welcome_msg = '''Connected to %s\n220 (DBQ FTPServer %s)'''%(socket.gethostname(),settings.VERSION)
        server_respone = {'message':welcome_msg,"hostname":socket.gethostname()}
        self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))
        self.login()
        self.task_run()


    def task_run(self):
        '''
        服务器运行方法
        :return:
        '''
        while True:
            client_respone = self.request.recv(1024)
            if len(client_respone) == 0:continue

            client_respone_str = json.loads(client_respone.decode())   #接受客户端发送的指令和代码

            if client_respone_str.get("status") == 220:   #如果发送220代码,要退出登录
                res = self.logout(self.user)  #退出登录
                if res:
                    server_respone = {"status":221,"message":"Goodbye!"}
                    self.request.sendall(bytes(json.dumps(server_respone),encoding='utf8'))   #成功退出,发送bye给客户端
                    return True
            else:
                # task_data = json.loads(client_respone.decode())
                task_action = client_respone_str.get('action')
                if hasattr(self,task_action):       #反射
                    func = getattr(self,task_action)
                    func(client_respone_str)
                    # print(task_action,task_data)
                else:
                    self.request.sendall(bytes('?Invalid command.-- %s'%client_respone.decode(),encoding='utf-8'))

    def put(self,*args,**kwargs):
        '''
        上传文件到FTP服务器
        :return:
        '''
        filename = args[0].get('filename')  #获取用户传过来的文件名
        filesize = args[0].get('file_size')     #获取文件大小

        filepath = settings.USER_STATUS[self.user].get('currdir')    #获取用户的当前路径

        userdb = json.load(open(settings.USERDB,'r'))          #加载用户配置文件
        quota =  settings.USER_STATUS[self.user].get('quota')   #加载用户限额
        recv_size = 0                #初始一个用户接受到的大小为0

        try:
            if filesize + userdb[self.user].get('used') >= quota:         #如果用户上传的文件加上现有使用空间大小大于用户配额的话
                server_respone = {"status":551,"message":"The use dirsk space quota overrun."}      #发送给用户551代码
                self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8')) #发送服务器响应
                raise Exception('overrun quota')           #超出磁盘配额,主动触发异常

            if os.path.exists(os.path.join(filepath,filename)):    #如果服务器上存在目标文件,先判断是否接受完成
                if os.stat(os.path.join(filepath,filename)).st_size == filesize:  #文件已经存在,并且接受完成
                    server_respone = {"status":200,"message":"Could not create file. remote file already exists."}   #告诉客户端文件已存在,并且接受完成, 发送200代码
                else:                   #如果大小不等, 发送给用户,询问是否断点续传
                    have_size = os.stat(os.path.join(filepath,filename)).st_size            #已接受的文件大小
                    server_respone = {"status":210,"have_size":have_size}    #发送给客户端未接受完成(210)和 已接受到的大小
                    self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8')) #发送服务器响应给客户端

                    client_respone_bytes = self.request.recv(1024)             #接受用户的回应
                    client_respone_str = json.loads(client_respone_bytes.decode() )

                    if client_respone_str.get('status') == 211:  #如果用户确认续传, 211
                        server_respone = {"status":212,"message":"Ok to send data."}      #回送给用户一个确认值(ok)
                        recv_size = have_size               #重置变量recv_size为已经接收到的大小
                        f = open(os.path.join(filepath,filename),'ab')   #打开文件以追加形式打开
                    elif client_respone_str.get('status') == 410:  #如果客户端拒绝续传 410, 主动触发异常,并退出
                        raise Exception('用户放弃操作')
            else:
                server_respone = {"status":150,"message":"Ok to send data."}
                f = open(os.path.join(filepath,filename),'wb')       #如果文件不存在,且配额满足需求,直接打开文件

            self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8')) #发送服务器响应

            while recv_size < filesize:
                data = self.request.recv(2048)
                f.write(data)
                recv_size += len(data)
            f.close()
            server_recv_success_bytes = self.request.recv(1024)    #接受用户传来的客户端文件校验值, 和发送文件文件代码
            server_recv_success_str = json.loads(server_recv_success_bytes.decode())

            md5_value = md5sum(os.path.join(filepath,filename))     #在服务器端也做校验

            if server_recv_success_str.get('md5sum') == md5_value and server_recv_success_str.get('status') == 225:      #比对成功
                server_recv_success_confir = {"status":226}     #226, 接受完成
                self.request.sendall(bytes(json.dumps(server_recv_success_confir),encoding='utf-8'))

                userdb[self.user]['used'] += recv_size      #将用户已经使用的空间容量+=接受到的文件大小
                json.dump(userdb,open(settings.USERDB,'w'))   #持久化到文件
                log.logger.info('226, %s upload %s success '%(self.user,filename))

            else:
                server_recv_success_confir = {"status":550,"message":"File to accept successful but failed an integrity check"}
                self.request.sendall(bytes(json.dumps(server_recv_success_confir),encoding='utf-8'))
                log.logger.info('%s upload %s failure, File to accept successful but failed an integrity check'%(self.user,filename))
        except Exception as e:
            return False

    def ls(self,*args,**kwargs):
        '''
        列出目录下的文件和文件夹
        :param args:
        :param kwargs:
        :return:
        '''
        flag = args[0].get('dirname')
        cmd = args[0].get('action')
        if not flag:  #如果用户没有输入列出的指定目录,
            # print('+'*30)
            Dirname = settings.USER_STATUS[self.user].get('currdir')  #Dirname 为当前目录
            abs_path = Dirname     #用户目录的绝对路径
        else:
            Dirname = flag      #如果用户输入了,那么拼接一下
            abs_path = os.path.join(settings.USER_STATUS[self.user].get('currdir'),Dirname)

        if abs_path.count('..'):
            if os.path.abspath(abs_path).startswith(settings.USER_STATUS[self.user].get('homedir')):
                if os.path.exists(abs_path):
                    command = subprocess.Popen('%s -lh %s'%(cmd,abs_path),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    command_out = command.stdout.read()  #获取标准输出
                    command_err = command.stderr.read()  #获取错误输出

                    if not command_err:
                        send_data = command_out
                    else:
                        send_data = command_err

                    server_respone = {"size":len(send_data),"status":150,"message":"Here comes the directory listing."}   #150 Here comes the directory listing.
                    self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))    #发送给用户

                    client_response_bytes = self.request.recv(1024)    #接受用户端发送的确认码, 150+1
                    client_response_str = json.loads(client_response_bytes.decode())

                    if client_response_str.get("status") == 151:    #获取用户准备接受标志位
                        self.request.sendall(send_data)              #发送命令执行结果给用户
                        server_send_success = {"status":226,"message":"226 Directory send OK."}     #发送完成确认给客户
                        self.request.sendall(bytes(json.dumps(server_send_success),encoding='utf-8'))
                else:
                    server_respone = {"status":250,"message":"Not Found files or directory!"}
                    self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))   #不存在
            else:
                data = {"status":403}
                self.request.sendall(bytes(json.dumps(data),encoding='utf-8'))   #访问拒绝!

        elif abs_path.startswith(settings.USER_STATUS[self.user].get('homedir')):
            if os.path.exists(abs_path):
                command = subprocess.Popen('%s -lh %s'%(cmd,abs_path),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                command_out = command.stdout.read()  #获取标准输出
                command_err = command.stderr.read()  #获取错误输出
                if command_out:
                    send_data = command_out
                else:
                    send_data = command_err

                server_respone = {"size":len(send_data),"status":150,"message":"Here comes the directory listing."}   #150 Here comes the directory listing.
                self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))    #发送给用户

                client_respone_bytes = self.request.recv(1024)
                client_response_str = json.loads(client_respone_bytes.decode())

                if client_response_str.get("status") == 151:    #获取用户准备接受标志位
                    self.request.sendall(send_data)              #发送命令执行结果给用户
                    server_send_success = {"status":226,"message":"226 Directory send OK."}     #发送完成确认给客户
                    self.request.sendall(bytes(json.dumps(server_send_success),encoding='utf-8'))
            else:
                server_respone = {"status":250,"message":"Not Found files or directory!"}
                self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))   #不存在
        else:
                data = {"status":403}
                self.request.sendall(bytes(json.dumps(data),encoding='utf-8'))   #访问拒绝!

    def delete(self,*args,**kwargs):
        '''
        删除目录下的文件和文件夹
        :param args:
        :param kwargs:
        :return:
        '''
        Dirname = args[0].get('dirname')  #取出文件名
        abs_path = os.path.join(settings.USER_STATUS[self.user].get('currdir'),Dirname)   #拼接一下

        userdb = json.load(open(settings.USERDB,'r'))   #加载用户配置文件
        filesize = 0           #取出要删除文件的大小, 初始化一个值,然后在下面根据判断来更改

        if abs_path.count('..') or abs_path.startswith(settings.USER_STATUS[self.user].get('homedir')):
            if os.path.abspath(abs_path).startswith(settings.USER_STATUS[self.user].get('homedir')):
                if os.path.isdir(abs_path):   #用户输入的是一个目录
                    filesize = os.stat(abs_path).st_size
                    try:
                        os.rmdir(abs_path)
                        server_respone = {"status":250,"message":"Delete operation successful."}
                        self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))
                        userdb[self.user]['used'] -= filesize       #减少大小
                        json.dump(userdb,open(settings.USERDB,'w'))  #持久化到文件
                        log.logger.info('250 %s del %s success, IP/Port: %s'%(self.user,Dirname,self.client_address))
                    except OSError:
                        server_respone = {"status":550,"message":"Directory not empty: '%s'"%Dirname}
                        self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))
                        return False
                elif os.path.isfile(abs_path):  #文件的操作
                    filesize = os.stat(abs_path).st_size
                    os.remove(abs_path)
                    server_respone = {"status":250,"message":"Delete operation successful."}
                    self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))
                    userdb[self.user]['used'] -= filesize
                    json.dump(userdb,open(settings.USERDB,'w'))
                    log.logger.info('250 %s del %s success, IP/Port: %s'%(self.user,Dirname,self.client_address))
                else:
                    data = {"status":404,"message":"Delete operation failed, Not found file or directory!"}
                    self.request.sendall(bytes(json.dumps(data),encoding='utf-8'))   #不存在
                    log.logger.info('404 %s del %s falure, not fount file, IP/Port: %s'%(self.user,Dirname,self.client_address))
            else:
                server_respone = {"status":403,"message":"Forbidden!"}
                self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))   #访问拒绝!
                log.logger.info('403 %s del %s operation not permitted! IP/Port: %s'%(self.user,Dirname,self.client_address))
        else:
            server_respone = {"status":403,"message":"Forbidden!"}
            self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))   #访问拒绝!
            log.logger.info('403 %s del %s operation not permiitted, IP/port: %s'%(self.user,Dirname,self.client_address))

    def mkdir(self,*args,**kwargs):
        '''
        创建文件夹
        :param args:
        :param kwargs:
        :return:
        '''
        Dirname = args[0].get('dirname')  #取出文件名
        abs_path = os.path.join(settings.USER_STATUS[self.user].get('currdir'),Dirname)   #拼接一下

        userdb = json.load(open(settings.USERDB,'r'))  #打开用户自己的配置文件

        if not abs_path.startswith(settings.USER_STATUS[self.user].get('homedir')):
            server_respone = {"status":403,"message":"Forbidden: Operation not permitted!"}
            self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))   #访问拒绝!
            log.logger.info('%s create %s operation not permitted, IP/Port: %s'%(self.user,Dirname,self.client_address))
        else:
            if os.path.abspath(abs_path).startswith(settings.USER_STATUS[self.user].get('homedir')):
                if not os.path.exists(abs_path):
                    os.makedirs(abs_path)
                    filesize = os.stat(abs_path).st_size
                    server_respone = {"status":257,"message":"'%s' created"%Dirname}
                    self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))

                    userdb[self.user]['used'] += filesize       #用户使用大小+=文件夹大小, PS: 文件夹也占用空间的
                    json.dump(userdb,open(settings.USERDB,'w'))

                    log.logger.info('%s create dir %s successfully, IP/Port: %s'%(self.user,Dirname,self.client_address))
                else:
                    server_respone = {"status":550,"message":"Create directory operation failed, Target forlder already exists."}
                    self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))   #不存在
                    log.logger.info('%s create dir %s failure, Target forlder already exists Tar, IP/Port: %s'%(self.user,Dirname,self.client_address))
            else:
                server_respone = {"status":403,"message":"Forbidden: Operation not permitted!"}
                self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))   #访问拒绝!
                log.logger.info('%s created %s failure, Operation not permiited!  IP/Port: %s'%(self.user,Dirname,self.client_address))

    def get(self,*args,**kwargs):
        '''
        下载文件到本地
        :return:
        '''
        abs_filepath = args[0].get('filename')  #获取用户要下载的文件名和绝对路径
        count_num = abs_filepath.count(os.sep)  #根据系统平台统计是否还有相对路径,并用os.sep替换
        if count_num == 0:      #如果用户输入的是一个
            filename = abs_filepath
            filepath = settings.USER_STATUS[self.user].get('currdir')   #当前工作路径
        else:
            par_path = abs_filepath.split(os.sep)[:-1]    #取出用户传入的目录的开头路径,取出来是个列表
            par_path_join = "%s"%os.sep.join(par_path)    #在拼接一下成字符串
            filename = abs_filepath.split(os.sep)[-1]     #取出文件名,需要发送给客户端
            filepath = os.path.join(settings.USER_STATUS[self.user].get('currdir'),par_path_join)
        try:
            if os.path.isfile(os.path.join(filepath,filename)):
                file_size = os.stat(os.path.join(filepath,filename)).st_size  #发送单位为字节

                server_respone = {"status":150,"filesize":file_size,"filename":filename,
                                  "message":"Opening BINARY mode data connection for %s (%s bytes)"%(filename,file_size)}
                self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))            #发送给用户一个找到文件的信息 包括: 文件大小和文件名给客户端

                response = self.request.recv(1024)
                client_respone = json.loads(response.decode())

                if client_respone.get('status') == 400:   #客户端文件已存在
                    return False
                elif client_respone['status'] == 401:  #用户放弃续传
                    return False
                elif client_respone['status'] == 210:         #断点续传
                    have_size = client_respone['have_size']   #获取已接受到的大小
                    send_size = have_size
                elif client_respone['status'] == 200:   #本地没有要下载的文件
                    send_size = 0

                print('Transfer: ',filename)
                f = open(os.path.join(filepath,filename),'rb')
                f.seek(send_size)   #改变文件指针从用户接受到的大小开始
                for line in f:      #循环
                    self.request.sendall(line)  #发送
                    send_size += len(line)

                print()
                f.close()
                #md5校验
                md5_value = md5sum(os.path.join(filepath,filename))    #服务器端计算出来一个md5值
                server_send_success = {"status":226,"md5sum":md5_value,"message":"Transfer complete."}   #发送给客户端响应代码和md5校验值
                self.request.sendall(bytes(json.dumps(server_send_success),encoding='utf-8'))

                client_recv_respone = self.request.recv(1024)     #收取用户接受的情况
                client_recv_respone_str = json.loads(client_recv_respone.decode())
                if client_recv_respone_str.get('status') == 227:
                    log.logger.info('226 %s download %s success'%(self.user,filename))        #记录日志
                else:
                    log.logger.info('550 %s download %s failure'%(self.user,filename))  #记录日志

            elif os.path.isdir(os.path.join(filepath,filename)):  #如果用户下载的是个目录的话
                server_respone = {"status":551,"filename":filename,"message":"Can not download directory"}
                self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))
            else:
                server_respone = {"status":404,"filename":filename,"message":"Not found remote file or directory!"}
                self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))
        except Exception as e:
            return False

    def login(self,*args,**kwargs):
        '''
        用户登录方法
        :param user: 接受用户输入账号
        :param pwd:  接受用户传入密码
        :return:     return 0: 表示认证成功, 1: 表示账户或者密码错误, 2, 表示用于已经登录,不能重复登录!
        '''
        flag = False
        while not flag:
            recv_user_info = self.request.recv(1024)    #接受用户传入的账号密码
            if len(recv_user_info) == 0:break           #如果为空,跳出循环
            user,pwd = recv_user_info.decode().split()  #取出用户名和密码


            userdb = json.load(open(settings.USERDB,'r'))
            if user in userdb.keys():
                if user == userdb[user].get('username') and MD5(pwd) == userdb[user].get('password'):
                    msg_data = {"status":230,"message":"230 Login successful.\nRemote system type is %s.\nUsing binary mode to transfer files."%sys.platform.upper()}
                    self.request.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))
                    if not os.path.isdir(os.path.join(settings.HOMEDIR,user)):
                        os.mkdir(os.path.join(settings.HOMEDIR,user))
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
                    self.user = user
                    log.logger.info('230 %s login FTP server successfully, IP/Port: %s'%(user,self.client_address))
                    flag = True   #登录成功后退出循环
                else:
                    msg_data = {"status":530,"message":"530 Login incorrect.\nftp: Login failed"}
                    self.request.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))
                    log.logger.info('530 %s log FTP server falure, username or passsword is incorrect'%user)
            else:
                msg_data = {"status":530,"message":"530 Login incorrect.\nftp: Login failed"}
                self.request.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))
                log.logger.info('530 %s log FTP server falure, username or passsword is incorrect'%user)

    def rename(self,*args,**kwargs):
        ''' 重命名文件/文件夹
        :param args:
        :param kwargs:
        :return:
        '''
        filename = args[0].get('filename')    #获取用户要下载的文件名和绝对路径
        newfilename = args[0].get('newname')  #获取更改后的名字
        abs_filepath = os.path.join(settings.USER_STATUS[self.user].get('currdir'),filename)
        newfile_abs_filepath = os.path.join(settings.USER_STATUS[self.user].get('currdir'),newfilename)
        count_num = abs_filepath.count(os.sep)  #根据系统平台统计是否还有相对路径,并用os.sep替换
        if os.path.exists(abs_filepath):
            if not os.path.exists(newfile_abs_filepath):  #确认更改后的文件不存在
                server_respone = {"status":350,"message":"Ready for RNTO."}
                self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))
                client_respone_bytes = self.request.recv(1024)
                client_respone_str = json.loads(client_respone_bytes.decode())
                if client_respone_str.get('status') == 351:
                    os.rename(abs_filepath,newfile_abs_filepath)
                    rename_res = {"status":250,"message":"Rename successful."}
                    self.request.sendall(bytes(json.dumps(rename_res),encoding='utf-8'))
                    log.logger.info('250 %s rename success, newname is %s'%(filename,newfilename))
            else:
                server_respone = {"status":401,"message":"Target file already exists."}
                self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))
                log.logger.info('401 %s rename failure, target file %s is already exists '%(filename,newfilename))
        else:  #源文件不在
            server_respone = {"status":404,"message":"Not Fount source file."}
            self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))
            log.logger.info('404 %s rename failure, Not found source file'%filename)

    def logout(self,user):
        '''
        注销用户方法
        :param user:
        :return:
        '''
        del settings.USER_STATUS[user]  #删除用户全局变量中的值
        log.logger.info('220 %s  logout FTP server'%user)
        return True

    def cd(self,*args,**kwargs):
        '''
        服务器目录切换方法
        :param args:
        :param kwargs:
        :return:
        '''
        flag = args[0].get('dirname')   #获取要改变的目录
        Dirname = flag if args[0].get('dirname') else settings.USER_STATUS[self.user].get('currdir')  #用户列出的目录的相对路径
        abs_path = os.path.join(settings.USER_STATUS[self.user].get('currdir'),Dirname)  #用户目录的绝对路径

        if abs_path.startswith(settings.USER_STATUS[self.user].get('homedir')):
            #如果切换的目录是以homedir开头,证明是用户家目录下的文件
            if os.path.isdir(abs_path):
                # os.chdir(abs_path)    #切换目录
                settings.USER_STATUS[self.user]['currdir'] = os.path.abspath(abs_path)   #改变当前目录变量
                msg_data = {"status":250,"message":"250  Directory successfully changed."}
                self.request.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))
            else:
                msg_data = {"status":550,"message":"550 Failed to change directory."}
                self.request.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))
        else:
            msg_data = {"status":403,"message":"403 Forbidden to change directory."}
            self.request.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))

    def pwd(self,*args,**kwargs):
        '''
        打印当前所在目录
        :param args:
        :param kwargs:
        :return:
        '''
        pwd = settings.USER_STATUS[self.user].get('currdir')
        self.request.sendall(bytes(pwd,encoding='utf-8'))

    def system(self,*args,**kwargs):
        '''
        列出当前系统平台
        :param args:
        :param kwargs:
        :return:
        '''
        Platfrom = sys.platform  #获取当前系统平台
        server_respone = {"status":215,"message":"Type: %s"%Platfrom.upper()}
        self.request.sendall(bytes(json.dumps(server_respone),encoding='utf-8'))

    def status(self,*args,**kwargs):
        '''
        显示现有用户相关信息
        :param args:
        :param kwargs:
        :return:
        '''
        userdb = json.load(open(settings.USERDB,'r'))  #打开用户自己的配置文件
        msg_data = '''
Connected and logged into:   %s
User Home: %s
User quota:   %s MB
Used size:  %.2f MB
Server version: %s
        '''%(self.user,
             settings.USER_STATUS[self.user].get('homedir'),
             settings.USER_STATUS[self.user].get('quota')/1024/1024,
             userdb[self.user].get('used')/1024/1024,
             settings.VERSION,)
        self.request.sendall(bytes(msg_data,encoding='utf-8'))
