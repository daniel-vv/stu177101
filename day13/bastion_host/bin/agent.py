#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)
import paramiko
import sys,os
import socket,getpass

from paramiko.py3compat import u

#windows 没有termios

try:
    import termios
    import tty
    has_termios = True
except ImportError:
    has_termios = False

def interactive_shell(channel):
    if has_termios:
        posix_shell(channel)  #如果标志为真,执行*inux方法
    else:
        windows_shell(channel) #否则, 执行windows_shell方法

def posix_shell(channel):
    import select
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        channel.settimeout(0.0)
        log = open('handle.log','a+',encoding='utf-8')
        flag = False
        temp_list = []
        while True :
            r,w,e = select.select([channel,sys.stdin],[],[])
            if channel in r:
                try:
                    x = u(channel.recv(2048))
                    if len(x) == 0:
                        sys.stdout.write('\r\n***EOF***\r\n')
                        break
                    if flag:
                        if x.startswith('\r\n'):
                            pass
                        else:
                            temp_list.append(x)
                        flag = False
                    sys.stdout.write(x)
                    sys.stdout.flush()

                except socket.timeout:
                    pass
            if sys.stdin in r:
                x = sys.stdin.read(1)
                import json

                if len(x) == 0:
                    break

                if x == '\t':
                    flag = True
                else:
                    temp_list.append(x)

                if x == '\r':
                    log.write(''.join((temp_list)))
                    log.flush()
                    temp_list.clear()

                channel.sendall(bytes(x,encoding='utf-8'))
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


def windows_shell(channel):
    import threading

    sys.stdout.write('Line-buffered terminal emulation. Please F6 or ^Z to send EOF.\r\n\r\n')

    def writeall(sock):
        while True:
            data = sock.recv(2048)
            if not data:
                sys.stdout.write('\r\n***EOF***\r\n\r\n')
                sys.stdout.flush()
                break
            sys.stdout.write(data)
            sys.stdout.flush()

    writer = threading.Thread(target=writeall, args=(channel,))
    writer.start()

    try:
        while True:
            d = sys.stdin.read(1)
            if not d:
                break
            channel.sendall(bytes(d,encoding='utf-8'))

    except EOFError:
        pass

def run():
    default_username = getpass.getuser()  #获取当前用户
    username = input('Usersname[%s]:'%default_username).strip()   #提示用户输入用户名

    if len(username) == 0:   #如果用户输入为空, 则用户名为默认当前系统用户名
        username = default_username

    hostname = input('Hostname: ').strip()   #提示输入主机名
    if len(hostname) == 0:            #如果为空,错误退出程序
        print('*** Hostname required.')
        sys.exit(1)

    port = input('Port: [22] ').strip()   #提示输入端口
    if len(port) == 0:            #如果为空, 端口为默认的22
        port = 22

    transport = paramiko.Transport((hostname,port))
    transport.start_client()

    default_auth = "p"
    auth = input('Auth by (p)assword or (r)sa key [%s]' %default_auth).strip()  #让用户选择是密码认证还是证书认证

    if len(auth) == 0:
        auth = default_auth

    if auth == 'r':
        default_path = os.path.join(os.environ['HOME'],'.ssh','id_rsa')  #拼接用户家目录/.ssh/id_rsa
        path = input('RSA key [%s]: '%default_path).strip()
        if len(path) == 0:
            path = default_path
        try:
            key = paramiko.RSAKey.from_private_key_file(path)  #加载用户key
        except paramiko.PasswordRequiredException:
            password = getpass.getpass('RSA key password: ')
            key = paramiko.RSAKey.from_private_key_file(path,password)
        transport.auth_publickey(username,key)

    elif auth == 'p':
        password = getpass.getpass('Password for %s@%s '%(username, hostname))
        try:
            transport.auth_password(username,password)
        except paramiko.ssh_exception.AuthenticationException:
            print('\033[31;1mAuthentication failed.\033[0m')
            exit(1)


    #打开一个通道
    channel = transport.open_session()
    #获取终端
    channel.get_pty()
    #激活器
    channel.invoke_shell()

    interactive_shell(channel)

    channel.close()
    transport.close()

if __name__ == '__main__':
    run()


