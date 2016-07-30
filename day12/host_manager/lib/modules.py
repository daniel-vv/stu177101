#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import sys, os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,ForeignKey,UniqueConstraint,Index
from sqlalchemy.orm import sessionmaker,relationships
import paramiko
from sqlalchemy.exc import OperationalError

import pymysql
from lib import settings



Base = declarative_base()


class User_group(Base):
    __tablename__ = 'user_group'
    gid = Column(Integer,primary_key=True,autoincrement=True)
    groupname = Column(String(16),nullable=False,unique=True)

class Project(Base):
    __tablename__ = 'project'
    pid = Column(Integer,primary_key=True,autoincrement=True)
    p_name = Column(String(16),nullable=False,unique=True)

class Users(Base):
    '''
    用户表,主要存储堡垒机用户名密码以及对应的组信息
    '''
    __tablename__ = 'users'
    uid = Column(Integer,primary_key=True,autoincrement=True)   #uid
    username = Column(String(32),nullable=False,unique=True)    #用户名,值需要唯一
    password = Column(String(32),nullable=False)                #密码
    gid = Column(Integer,ForeignKey('user_group.gid'),nullable=False)  #对应组, 关联外键 用户组表的gid

class Host(Base):
    '''
    主机表
    '''
    __tablename__ = 'host'
    id = Column(Integer, primary_key=True, autoincrement=True) #Id
    host_ip = Column(String(32),nullable=False,unique=True)    #主机IP
    port = Column(Integer,nullable=False)                      #ssh端口
    hostname = Column(String(32),unique=True,nullable=False)   #主机名
    uid = Column(Integer,ForeignKey('user_to_host.uid'),nullable=False)  #外键,关联主机用户名密码表
    pid = Column(Integer,ForeignKey('project.pid'),nullable=False)       #外键,关联项目表
    gid = Column(Integer,ForeignKey('user_group.gid'),nullable=False)    #外键, 关联用户组表

class User_to_host(Base):
    '''
    服务器远程ssh连接的用户名和密码表
    '''
    __tablename__ = 'user_to_host'
    uid = Column(Integer,primary_key=True,autoincrement=True)   #uid, host表外键uid关联到此键
    username = Column(String(32),nullable=False)                #ssh用户名
    password = Column(String(32),nullable=False)                #ssh密码

class operate_db:
    '''
    管理数据库类
    '''
    def __init__(self):
        '''
        构造方法
        :return:
        '''
        try:
            self.Session = sessionmaker(bind=settings.engine)
            self.session = self.Session()
        except OperationalError:
            print('连接数据库超时!')


    def init_db_meta(self):
        '''
        初始化数据库方法
        :return:
        '''
        try:
            Base.metadata.create_all(settings.engine)
        except Exception:
            pass

    def del_db_meta(self):
        '''
        删除表方法
        :return:
        '''
        Base.metadata.drop_all(settings.engine)

    def init_db(self):
        '''
        初始化堡垒机数据库
        :param db_class:
        :return:
        '''
        self.init_db_meta()
        #添加Users表数据,三个用户, tom, jerry, sam, 主要用户登录堡垒机程序
        self.session.add_all([
            Users(username='tom',password='123456',gid=1),
            Users(username='jerry',password='123456',gid=1),
            Users(username='sam',password='123456',gid=2),]
        )
        #添加项目表初始数据, 项目名称, 默认提供两个
        self.session.add_all([
            Project(p_name='cloud'),
            Project(p_name='bigdata')
        ])

        #添加用户组初始化数据, 提供两个组,用于关联用户分组的主机
        self.session.add_all([
            User_group(groupname='ops'),
            User_group(groupname='dev')
        ])
        #添加主机的ssh账号密码, 默认提供一个用户, test/123456
        self.session.add_all([
            User_to_host(username='test',password='123456'),
        ])

        #添加主机表数据
        self.session.add_all([
            Host(host_ip='192.168.1.105',port=22,hostname='server1',uid=1,pid=1,gid=1),
            Host(host_ip='192.168.1.106',port=22,hostname='server2',uid=1,pid=1,gid=1),
            Host(host_ip='192.168.2.200',port=22,hostname='server3',uid=1,pid=2,gid=2),
            Host(host_ip='192.168.2.201',port=22,hostname='server4',uid=1,pid=2,gid=2),
        ])


        self.session.commit()


class Operate_manager:
    '''
    堡垒机类
    '''
    def __init__(self):
        '''
        构造函数
        :return:
        '''
        self.Session = sessionmaker(bind=settings.engine)
        self.session = self.Session()
        self.main()

    def close(self):
        '''
        关闭连接方法
        :return:
        '''
        self.ssh.close()

    def manager(self,host,port,user,passwd):
        '''
        管理主机方法
        :param host: 连接的ssh主机IP或者主机名(可解析)
        :param port: 主机ssh端口
        :param user: 用户名
        :param passwd: 密码
        :return:
        '''
        #创建ssh对象
        self.ssh = paramiko.SSHClient()

        #允许连接不在Know_hosts文件中的主机
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        #连接服务器
        self.ssh.connect(hostname=host,port=port,username=user,password=passwd)

        while True:
            inp_comm = input('请输入远程执行命令, q/Q(退出操作)').strip()
            if inp_comm == 'q' or inp_comm == 'Q':
                self.close()
                return False
            elif inp_comm:
                stdin,stdout,stderr = self.ssh.exec_command(inp_comm)
                res = stdout.read()
                res_err = stderr.read()
                if res:
                    print(res.decode())
                else:
                    print(res_err.decode())
            else:
                continue


    def login(self):
        '''
        登录堡垒机方法
        :return:
        '''
        while True:
            user = input('Username: ').strip()
            if user:
                passwd = input('Password: ').strip()
                try:
                    username = self.session.query(Users.username).filter_by(username=user).first()[0]
                    pwd = self.session.query(Users.password).filter_by(username=user).first()[0]
                    self.session.commit()
                except TypeError:
                    print('账户名或者密码错误!')
                    continue
                if user == username and passwd == pwd:
                    print('登录成功')
                    self.user = user
                    self.gid = self.session.query(Users.gid).filter_by(username=user).first()[0]

                    #获取到的是一个列表中包含元组的值,元组中是 主机ip, 主机名, 端口, userid(ssh主机用户id)
                    self.hostlist = self.session.query(Host.host_ip,Host.hostname,Host.port,Host.uid).filter_by(gid=self.gid).all()
                    self.group = self.session.query(User_group.groupname).filter_by(gid=self.gid).first()[0]
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
        print('欢迎使用DBQ的堡垒机(V1.0.0)')
        res = self.login()
        if res:
            while True:
                print(' 用户信息 '.center(30,'#'))
                print('堡垒机用户: %s,   所属组: %s \n您可操作的服务器列表:'%(self.user,self.group))
                print('序列   主机IP        主机名')
                for i in enumerate(self.hostlist):

                    print(i[0],i[1])
                inp = input('请选择你要远程管理的主机序列, q/Q(退出程序): ').strip()
                try:
                    if inp == 'q' or inp == 'Q' or inp == 'quit':
                        print('Goodbye!')
                        exit(0)
                    elif int(inp) <= len(self.hostlist):

                        user_info = self.session.query(User_to_host.username,User_to_host.password).filter_by(
                            uid=self.hostlist[int(inp)][3]).all()
                        user,pwd = user_info[0][0],user_info[0][1]  #ssh连接用户名密码
                        host_ip,port = self.hostlist[int(inp)][0],self.hostlist[int(inp)][2]     #主机IP和端口
                        self.manager(host_ip,port,user,pwd)
                    else:
                        raise ValueError('输入操作序列不合法')
                except ValueError:
                    print('输入操作序列不合法')
                    continue

