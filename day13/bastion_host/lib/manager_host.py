#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import paramiko
import threading
import sys,re
import os, time
import socket
import getpass
from paramiko.py3compat import u
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import settings
from lib import db_modules



class Operate_manager:
    '''
    堡垒机类
    '''
    def __init__(self):
        '''
        构造函数
        :return:
        '''
        self.obj = db_modules.operate_db()
        self.main()

    def manager(self,dst_ip,dst_port,dst_username,dst_password,dst_auth_type):
        '''
        远程管理主机方法
        :param dst_ip: ip
        :param dst_port: ssh端口
        :param dst_username: 用户名
        :param dst_password: 密码
        :param dst_auth_type: 认证类型
        :return:
        '''
        # windows does not have termios...
        transport = paramiko.Transport((dst_ip,dst_port))
        transport.start_client()
        transport.auth_password(dst_username,dst_password)
        #打开一个通道
        chan = transport.open_session()
        #获取一个终端
        chan.get_pty()
        #激活器
        chan.invoke_shell()
        try:
            import termios
            import tty
            has_termios = True
        except ImportError:
            has_termios = False

        def interactive_shell(chan):
            if has_termios:  #如果标志为真,执行*inux方法
                posix_shell(chan)
            else:            #否则, 执行windows_shell方法
                windows_shell(chan)

        def posix_shell(chan):
            import select
            #获取原 tty属性
            oldtty = termios.tcgetattr(sys.stdin)
            try:
                # 为tty设置新属性
                # 默认当前tty设备属性：
                #   输入一行回车，执行
                #   CTRL+C 进程退出，遇到特殊字符，特殊处理。

                # 这是为原始模式，不认识所有特殊符号
                # 放置特殊字符应用在当前终端，如此设置，将所有的用户输入均发送到远程服务器
                tty.setraw(sys.stdin.fileno())
                tty.setcbreak(sys.stdin.fileno())
                chan.settimeout(0.0)
                f = open('handle.log','a+')
                tab_flag = False
                temp_list = []    #临时列表
                while True:
                    #监视 用户输入 和远程服务器返回的数据 socket
                    #阻塞, 直到句柄可读
                    r, w, e = select.select([chan, sys.stdin], [], [])
                    if chan in r:
                        try:
                            x = chan.recv(2048)
                            if len(x) == 0:
                                sys.stdout.write('\r\n*** EOF ***\r\n')
                                cmd = 'logout'
                                user_obj = self.obj.get_userid_from_username(self.user)  #获取用户ID
                                userid = user_obj.first().id   #用户ID
                                self.obj.add_audit_log(userid, self.dst_userid, cmd, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
                                break
                            if tab_flag:    #如果标志位为真, 表示用户输入的是tab键
                                if x.startswith('\r\n'):  #判断,如果用户服务器返回的是以用户\r\n开头的不做任何操作
                                    pass
                                else:     #否则的话, 写日志
                                    temp_list.append(x)
                                tab_flag = False   #继续把标志位置为False
                            sys.stdout.write(x.decode())
                            sys.stdout.flush()
                        except socket.timeout:
                            pass

                    if sys.stdin in r:
                        x = sys.stdin.read(1)   #输入一个字符, 读取一个,发送一个,添加对tab补全的支持
                        if len(x) == 0:
                            break
                        if x == '\t':  #如果输入是tab键, 置标志位为真
                            tab_flag = True
                        else:          #否则,写审计日志
                            temp_list.append(x)
                        if x == '\r':
                            cmd = ''.join(temp_list)
                            cmd = re.sub('\a|\r|\b|\t', '', cmd)
                            user_obj = self.obj.get_userid_from_username(self.user)  #获取用户ID
                            userid = user_obj.first().id   #用户ID
                            self.obj.add_audit_log(userid, self.dst_userid, cmd, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
                            temp_list.clear()   #清空临时列表
                        chan.sendall(bytes(x,encoding='utf-8'))
            #重新设置终端属性
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)

        def windows_shell(chan):
            import threading

            sys.stdout.write("Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n")

            def writeall(sock):
                while True:
                    data = sock.recv(256)
                    if not data:
                        sys.stdout.write('\r\n*** EOF ***\r\n\r\n')
                        sys.stdout.flush()
                        break
                    sys.stdout.write(data)
                    sys.stdout.flush()

            writer = threading.Thread(target=writeall, args=(chan,))
            writer.start()

            try:
                while True:
                    d = sys.stdin.read(1)
                    if not d:
                        break
                    chan.send(d)
            except EOFError:
                # user hit ^Z or F6
                pass

        interactive_shell(chan)
        chan.close()
        transport.close()


    def login(self):
        '''
        登录堡垒机方法
        :return:
        '''
        while True:
            user = input('Username: ').strip()
            if user:
                passwd = getpass.getpass('Password: ').strip()
                try:
                    res = self.obj.get_user_from_username(user)
                    username = res.first().username
                    pwd = res.first().password
                    # print(username, pwd)
                except TypeError:
                    print('账户名或者密码错误!')
                    continue
                if user == username and passwd == pwd:
                    print('\033[32;1m登录成功\033[0m')
                    self.user = user
                    return True
                else:
                    print('账户名或者密码错误!')
                    continue
            else:
                continue

    def main(self):
        '''
        主方法
        :return:
        '''
        res = self.login()
        if res:
            while True:
                print('\033[32;1m 请选择菜单 \033[0m'.center(60,'#'))
                rep = input('   1. 管理用户所属的所有主机\n   2. 管理组内的所有主机\n   3. 查看操作记录\n   4. 退出程序\n>>> ').strip()
                if rep == '1':
                    self.hostlist = self.obj.get_host_from_username(self.user)
                    welcome_msg = '当前用户[ \033[32;1m%s\033[0m ]所属主机列表'.center(50)%self.user
                elif rep == '2':
                    self.group = self.obj.get_group_from_username(self.user) #返回的是一个对象
                    self.hostlist = self.obj.get_host_from_groupname(self.group.first().group_name)
                    welcome_msg = '当前组[ \033[32;1m%s\033[0m ]所属主机列表'.center(50)%self.group.first().group_name
                elif rep == '3':
                    log_obj = self.obj.get_audit_log_from_username(self.user)
                    if len(log_obj.all()) == 0:
                        if input('\033[31;1m您还没有任何操作记录! 按下回车键继续...\033[0m'):pass
                    else:
                        print('序 号    用户     主机用户      命 令        时 间')
                        num = 1
                        for item in log_obj.all():
                            host_user_obj = self.obj.get_hostuser_from_userid(item.host_user_id)
                            hostuser = host_user_obj.first().username
                            print(num,'\t',self.user,'\t', hostuser,'\t', item.cmd,'\t', item.date)
                            num += 1
                    continue
                elif rep == '4':
                    print('Goodbye!')
                    exit(0)
                else:
                    print('\033[31;1m错误的选择!\033[0m')
                    continue

                print(welcome_msg)
                print('-'*50)
                print('序列      主机名           IP        SSH端口     项目')
                for i,v in enumerate(self.hostlist.all()):
                    res = self.obj.get_project_from_hostname(v.hostname)
                    project = res.first().project_name
                    print(i,'\t',v.hostname,'\t',v.ip_addr,'\t',v.port,'\t',project)
                print('-'*50)
                inp = input('请选择你要远程管理的主机序列, b/B(返回上一层): ').strip()
                try:
                    if inp == 'b' or inp == 'B' or inp == 'back':
                        continue
                    elif int(inp) <= len(self.hostlist.all()):
                        dst_ip = self.hostlist.all()[int(inp)].ip_addr
                        dst_hostname = self.hostlist.all()[int(inp)].hostname
                        dst_port = self.hostlist.all()[int(inp)].port
                        ret = self.obj.get_user_from_hostname(dst_hostname)
                        dst_username, dst_password, dst_auth_type= ret.first().username, ret.first().password,ret.first().auth_type

                        self.dst_username = dst_username  #登录用户名, 写日志用
                        self.dst_userid = ret.first().id  #登录用户id, 写日志用
                        self.manager(dst_ip,dst_port,dst_username,dst_password,dst_auth_type)  #调用manager方法
                    else:
                        raise ValueError('输入操作序列不合法')
                except ValueError:
                    print('输入操作序列不合法')
                    continue
