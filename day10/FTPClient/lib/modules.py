#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import os,json,socket,sys
import configparser,hashlib
import getpass,subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import settings

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
        self.client.connect(ip_port)            #连接服务器
        server_respone_bytes = self.client.recv(2048)    #接受服务器欢迎消息
        server_respone_str = json.loads(server_respone_bytes.decode())
        self.server_hostname = server_respone_str.get('hostname')   #获取服务器主机名
        print(server_respone_str.get('message'))  #打印欢迎信息


    def put(self,*args,**kwargs):
        '''put      send one file.  Usage: put /path/to/filename'''
        task_type = args[0][0]     #操作类型
        abs_filepath = args[0][1]  #获取文件路径

        if abs_filepath.count(os.sep):
            filename = abs_filepath.split(os.sep)[-1]
        else:
            filename = abs_filepath
        send_size = 0    #初始化一个接收到的大小为0, 下面的判断来更改值
        if os.path.isfile(abs_filepath):   #要发送的本地文件如果存在,并且是文件的话
            file_size = os.stat(abs_filepath).st_size   #获取大小

            msg_data = {"action":task_type,"filename":filename, "file_size":file_size}
            self.client.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))   #发送给服务器端

            server_confirmation_msg = self.client.recv(1024)    #接受服务器的确认信息
            if len(server_confirmation_msg) == 0:return False   #如果为空,直接退出

            confirm_data = json.loads(str(server_confirmation_msg,encoding='utf-8'))  #接受服务器确认信息
            if confirm_data['status'] == 150:  # 150 代码, 重头开始开始发送文件
                send_size = 0    #指针为0
            elif confirm_data['status'] == 200:   #远端已经存在文件
                print('%s %s'%(confirm_data.get('status'),confirm_data.get('message')))
                return True
            elif confirm_data['status'] == 210:          #续传模式, 210
                have_size = confirm_data['have_size']    #获取到服务器已经接受到的大小
                inp = input('\033[31;1mTarget file already exists, and there is no transmission is complete, whether the resume? y/Y\033[0m').strip()
                #询问用户是否续传
                if inp == 'y' or inp == 'Y':
                    client_respone = {"status":211}   #如果用户输入的y 则发送一个211给服务器
                    self.client.sendall(bytes(json.dumps(client_respone),encoding='utf-8'))

                    server_respone_bytes = self.client.recv(1024)
                    server_respone_str = json.loads(server_respone_bytes.decode())
                    if server_respone_str.get('status') == 212:   #如果服务器确认信息的话,212
                        send_size = have_size
                        #将文件指针指向对方已接收到的大小
                else:
                    client_respone = {"status":410}
                    print('\033[31;1m%s User abort the operation\033[0m'%client_respone.get('status'))
                    self.client.sendall(bytes(json.dumps(client_respone),encoding='utf-8'))
                    return False

            elif confirm_data.get('status') == 551:   #如果服务器发送过来为'551' 为超出磁盘配额
                print('\033[31;1m%s %s\033[0m'%(confirm_data.get('status'),confirm_data.get('message')))
                return False
        elif os.path.isfile(abs_filepath):
            print('%s ot a plain file.'%filename)
        else:
            print('\033[31;1mNot fount files!\033[0m'%abs_filepath)
            return False
        print('local: %s  remote: %s'%(filename,filename))
        f = open(abs_filepath,'rb')
        f.seek(send_size)      #充值指针
        bar = ProgressBar()
        for line in f:
            self.client.sendall(line)
            send_size += len(line)
            bar.update(send_size*100/(file_size-1))  #进度条
        f.close()
        print('  %d KiB' %(send_size/1024))


        print('\033[32;1m Progress integrity verification, please wait...\033[0m')

        md5_value = md5sum(abs_filepath)
        client_send_success = {"status":225,"md5sum":md5_value}                       #发送完成代码225
        self.client.sendall(bytes(json.dumps(client_send_success),encoding='utf-8'))  #发送给服务器

        server_respone_vertify_bytes = self.client.recv(1024)
        server_respone_vertify_str = json.loads(server_respone_vertify_bytes.decode())
        if server_respone_vertify_str.get('status') == 226:  #比对成功
            print('%s integrity verification, upload file %s success. ' %(server_respone_vertify_str.get('status'),abs_filepath))
        else:
            print('\033[31;1m%s %s\033[0m'%(server_respone_vertify_str.get('status'),server_respone_vertify_str.get('message')))


    def ls(self,*args,**kwargs):
        '''ls   list contents of remote path.   Usage: ls [dirname] '''
        if type(args[0]) is str:   #如果用户输入的只是一个ls
            task_type = args[0][0] #获取命令
            Dirname = args[0][1]   #获取用户输入的文件夹/文件名字
            msg_data = {"action":args[0],"dirname":False}
        else:
            msg_data = {"action":args[0][0],"dirname":args[0][1]}

        self.client.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))

        server_respone_bytes = self.client.recv(1024)       #接受服务器端发送的代码
        server_respone_str = json.loads(str(server_respone_bytes,encoding='utf-8') )   #加载服务器发送给用户的列目录信息
        size = server_respone_str.get('size')     #取出文件个数
        if server_respone_str.get('status') == 150:
            client_response = {"status":151}
            self.client.sendall(bytes(json.dumps(client_response),encoding='utf-8'))
            print('%s %s'%(server_respone_str.get('status'),server_respone_str.get('message')))
            recv_size = 0
            while recv_size < size:   #循环接受文件
                recv_data = self.client.recv(1024)
                recv_size += len(recv_data)
                print(recv_data.decode())
            client_recv_success = self.client.recv(1024)
            client_recv_success_str = json.loads(client_recv_success.decode())
            if client_recv_success_str.get('status') == 226:
                print(client_recv_success_str.get('message'))

    def lpwd(self,*args,**kwargs):
        '''lpwd       	print local working directory.    '''
        print('Local directory: %s '% os.getcwd())

    def ldir(self,*args,**kwargs):
        '''ldir     列出本地目录下的文件和文件夹, 用法:  ldir [dirname]'''
        if type(args[0]) is str:
            # res = os.listdir(os.getcwd())
            res = subprocess.Popen('ls -l',shell=True,stdout=subprocess.PIPE)
            res_out = res.stdout.read()
            if res_out:
                print(res_out.decode())
            else:
                print('\033[31;1mNot found directory!\033[0m'%Dirname)

        else:
            Dirname = args[0][1]
            # if os.path.exists(Dirname):
            #     res = os.listdir(Dirname)
            #     for i in res:
            #         print(i)
            res = subprocess.Popen('ls -l %s'%args[0][1],shell=True,stdout=subprocess.PIPE)
            res_out = res.stdout.read()
            if res_out:
                print(res_out.decode())
            else:
                print('\033[31;1mNot found directory!\033[0m'%Dirname)

    def lcd(self,*args,**kwargs):
        '''lcd        	change local working directory.   Usage:  lcd directory-name'''
        if type(args[0]) is not str:
            Dirname = args[0][1]    #用户输入的路径
            if os.path.isdir(Dirname):
                os.chdir(Dirname)
                print('Local directory now:',Dirname)

    def system(self,*args,**kwargs):
        '''system     	show remote system type.   '''
        msg_data = {"action":args[0]}
        self.client.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))
        server_respone_bytes = self.client.recv(1024)
        server_respone_str = json.loads(server_respone_bytes.decode())

        print('%s %s' %(server_respone_str.get('status'),server_respone_str.get('message')))

    def cd(self,*args,**kwargs):
        '''cd         	change remote working directory.  Usage:  cd dirname'''
        task_type = args[0][0]
        abs_filepath = args[0][1]
        msg_data = {"action":task_type,"dirname":abs_filepath}
        self.client.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))
        server_respone_bytes = self.client.recv(1024)
        server_respone_str = json.loads(server_respone_bytes.decode())
        if server_respone_str.get('status') == 250:
            print(server_respone_str.get('message'))
        elif server_respone_str.get('status') == 550:
            print(server_respone_str.get('message'))
        else:
            print('\033[31;1m%s\033[0m'%server_respone_str.get('message'))

    def pwd(self,*args,**kwargs):
        '''pwd        	print working directory on remote machine.  Usage:  pwd '''
        task_type = args[0]
        msg_data = {"action":task_type}
        self.client.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))  #发送给服务器
        res = self.client.recv(1024)
        print('Remote directory: %s'%str(res,encoding='utf-8'))

    def delete(self,*args,**kwargs):
        '''delete     	delete remote file.   Usage:  delete remote-file'''
        if type(args[0]) is str:
            Dirname = input('(remote-file) ').strip()   #提示用户输入
            if Dirname:
                task_type = args[0]
                Dirname = Dirname
            else:
                print('usage: delete remote-file')
                return False
        else:
            task_type = args[0][0]
            Dirname = args[0][1]

        msg_data = {"action":task_type,"dirname":Dirname}
        self.client.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))  #发送要删除的文件和目录

        server_respone_bytes = self.client.recv(1024)
        server_respone_str = json.loads(server_respone_bytes.decode())
        if server_respone_str.get('status') == 250:   #如果权限通过,接受并打印列出的文件/文件夹
            print('%s %s'%(server_respone_str.get('status'),server_respone_str.get('message')))
        else:
            print('\033[31;1m%s %s\033[0m'%(server_respone_str.get('status'),server_respone_str.get('message')))

    def mkdir(self,*args,**kwargs):
        '''mkdir      	make directory on the remote machine.   Usage:  mkdir directory-name'''
        if type(args[0]) is str:
            Dirname = input('(directory-name) ').strip()
            if Dirname:
                Dirname = Dirname
                task_type = args[0]
            else:
                print('usage: mkdir directory-name')
                return False
        else:
            task_type = args[0][0]
            Dirname = args[0][1]

        msg_data = {"action":task_type,"dirname":Dirname}
        self.client.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))  #发送要删除的文件和目录

        server_respone_bytes = self.client.recv(1024)
        server_respone_str = json.loads(server_respone_bytes.decode())
        if server_respone_str.get('status') == 257:   #如果权限通过,接受并打印列出的文件/文件夹
            print('%s %s'%(server_respone_str.get('status'),server_respone_str.get('message')))
        else:
            print('\033[31;1m%s %s\033[0m'%(server_respone_str.get('status'),server_respone_str.get('message')))

    def help(self,*args,**kwargs):
        '''help       	print local help information'''
        if type(args[0]) is str:
            print('''
Commands may be abbreviated.  Commands are:

get     put     ls      lpwd    lcd     ldir    bye     quit    cd     pwd    delete    mkdir    system   status    rename      !
            ''')
        else:
            cmd = args[0][1]
            if cmd == '!':
                res = getattr(self,'run_local_command')
                print(res.__doc__)
            elif hasattr(self,cmd):
                res = getattr(self,cmd)
                print(res.__doc__)

    def status(self,*args,**kwargs):
        '''status     	show current status '''
        msg_data = {"action":args[0]}
        self.client.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))
        recv_data = self.client.recv(8192)
        print('%s' %recv_data.decode())
        print('Client Version: %s'%settings.VERSION)

    def get(self,*args,**kwargs):
        '''get        	receive file.  Usage: get remote-filename'''
        task_type = args[0][0]
        abs_filepath = args[0][1]
        msg_data = {"action":task_type,"filename":abs_filepath}   #用户要下载的文件

        self.client.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))   #发送要下载信息给服务器

        server_respone_bytes = self.client.recv(1024)
        server_respone_str = json.loads(server_respone_bytes.decode())
        if server_respone_str.get('status') == 150:   #收到服务器找到目录中的文件信息
            filesize = server_respone_str.get('filesize')
            filename = server_respone_str.get('filename')
            message = server_respone_str.get('message')

            if os.path.exists(os.path.join(os.getcwd(),filename)):    #如果文件已存在
                have_size = os.stat(os.path.join(os.getcwd(),filename)).st_size   #获取已经接受到的文件大小
                if have_size == filesize:   #如果本地大小和服务器大小一致, 则发送给服务器一个通知,并告知客户无需下载
                    print('\033[31;1mFile already exists (%s)!\033[0m'%filename)
                    client_respone = {"status":400}  #发送确认给服务器, 客户端这边已经存在文件了,无需再往下进行了
                    self.client.sendall(bytes(json.dumps(client_respone),encoding='utf-8'))
                    return False
                else:   #如果大小不一致, 进入续传对话框
                    inp = input('File already exists, and there is no reception complete, whether to continue? y/Y').strip()
                    if inp == 'Y' or inp == 'y':
                        client_respone = {"status":210,"have_size":have_size}     #发送给服务器,客户端这边要断点续传
                        f = open(os.path.join(os.getcwd(),filename),'ab')    #断点续传, 以追加的模式打开文件
                    else:
                        print('\033[31;1mUser abort the operation!\033[0m')
                        client_respone = {"status":401}
                        self.client.sendall(bytes(json.dumps(client_respone),encoding='utf-8'))
                        return False
            else:
                client_respone = {"status":200}
                have_size = 0
                f = open(os.path.join(os.getcwd(),filename),'wb')

            self.client.sendall(bytes(json.dumps(client_respone),encoding='utf-8'))   #发送响应给服务器

            print('local: %s remote: %s'%(filename,filename))  #打印本地和远程文件名
            print(message)             #服务器传送的消息
            recv_size = have_size      #从上次下载的地方开始显示百分比
            bar = ProgressBar()        #实例化进度条类
            while recv_size < filesize:
                data = self.client.recv(2048)
                f.write(data)
                recv_size += len(data)

                bar.update(recv_size*100/(filesize-1))  #进度条
            f.close()
            print('%.2f KiB'%(filesize/1024))

            client_recv_success_bytes = self.client.recv(1024)    #接受服务器传输完成后的信息
            client_recv_success_str = json.loads(client_recv_success_bytes.decode())

            print('%s %s'%(client_recv_success_str.get('status'),client_recv_success_str.get('message')))
            print('\033[32;1mProgress the integrity check, please wait ...\033[0m')
            server_file_md5_value = client_recv_success_str.get('md5sum')   #服务器发送的MD5值
            md5_value = md5sum(os.path.join(os.getcwd(),filename))                                    #本地也计算出MD5值
            if md5_value ==server_file_md5_value:
                client_recv_respone = {"status":227}
                self.client.sendall(bytes(json.dumps(client_recv_respone),encoding='utf-8'))
                print('Wow, checksum is complate, the file %s is downloaded successfully!'%filename)
            else:
                print('\033[31;1mThe check fails, try the download again\033[0m')
        else:
            filename = server_respone_str.get('filename')
            message = server_respone_str.get('message')
            print('%s %s'%(server_respone_str.get('status'),message))

    def run_local_command(self,*args,**kwargs):
        '''!          	escape to the shell'''
        command = subprocess.Popen(args[0],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        command_out = command.stdout.read()
        command_err = command.stderr.read()
        try:
            if command_out:
                print(str(command_out,encoding='utf-8'))
            elif command_err:
                print(str(command_err,encoding='utf-8'))
        except Exception:
            print('\033[31;1m?Invalid command!\033[0m')

    def rename(self,*args,**kwargs):
        ''' rename     	rename file.    Usage: rename oldname newname'''
        if type(args[0]) is list and len(args[0]) == 3:
            msg_data = {"action":args[0][0],"filename":args[0][1],"newname":args[0][2]}
        elif type(args[0]) is str:
            msg_data = {"action":args[0],"filename":False,"newname":False}
        else:
            msg_data = {"action":"rename","filename":False,"newname":False}
        self.client.sendall(bytes(json.dumps(msg_data),encoding='utf-8'))
        server_respone_bytes = self.client.recv(1024)
        server_respone_str = json.loads(server_respone_bytes.decode())
        if server_respone_str.get('status') == 350:
            print('%s %s'%(server_respone_str.get('status'),server_respone_str.get('message')))
            client_respone = {"status":351}
            self.client.sendall(bytes(json.dumps(client_respone),encoding='utf-8'))
            rename_res_bytes = self.client.recv(1024)
            rename_res_str = json.loads(rename_res_bytes.decode())
            if rename_res_str.get('status') == 250:
                print('%s %s'%(rename_res_str.get('status'),rename_res_str.get('message')))
        else:  #接受服务器传来的其他消息
            print('\033[31;1m%s %s\033[0m'%(server_respone_str.get('status'),server_respone_str.get('message')))

    def login(self):
        '''
        客户端登录服务器方法
        :return:
        '''
        flag = False
        while not flag:
            username = input('Name (%s:%s):'%(getpass.getuser(),self.server_hostname)).strip()
            if username:
                print('331 Please specify the password.')  #用户名不为空,开始验证密码, 代码331
                password = input('Password:').strip()
                if password:
                    self.client.sendall(bytes('%s %s'%(username,password),encoding='utf-8'))  #发送账号和密码到服务器认证
                    server_respone_bytes = self.client.recv(1024)                               #接受用户返回的认证结果
                    server_respone_str = json.loads(server_respone_bytes.decode())
                    if server_respone_str.get('status') == 230:   #认证成功代码 230
                        print('\033[32;1m%s\033[0m'%server_respone_str.get('message'))
                        self.user = username
                        flag = True
                    elif server_respone_str.get('status') == 530:
                        print(server_respone_str.get('message'))

    def client_run(self):
        '''
        客户端主运行方法
        :return:
        '''

        self.login()   #提示用户登录
        while True:
            cmd = input('ftp>  ').strip()
            if cmd == 'bye' or cmd == 'quit' or cmd == 'QUIT':
                client_respone = {"status":220}
                self.client.sendall(bytes(json.dumps(client_respone),encoding='utf-8'))   #发送220 给服务器
                server_respone_bytes = self.client.recv(1024)
                server_respone_str = json.loads(server_respone_bytes.decode())

                if server_respone_str.get('status') == 221:    #221 退出登录代码
                    print('%s %s'%(server_respone_str.get('status'),server_respone_str.get('message')))
                    return True
            elif len(cmd) == 0:
                continue
            elif cmd.startswith('!'):
                command = cmd.split('!',1)[1]   #调用本地命令, 用!切割,且只切割一次
                self.run_local_command(command)
            else:
                cmd_list = cmd.split()
                task_action = cmd_list[0]

                if len(cmd_list) >= 2:
                    if hasattr(self,task_action):
                        func = getattr(self,task_action)
                        func(cmd_list)
                        continue
                    else:
                        print('\033[31;1m?Invalid command!\033[0m')
                        continue
                elif hasattr(self,task_action):
                    func = getattr(self,task_action)
                    func(task_action)
                    continue
                else:
                    print('\033[31;1m?Invalid command.!\033[0m')
                    continue

