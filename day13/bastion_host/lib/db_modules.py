#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

from sqlalchemy import create_engine,and_,or_,func,Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,ForeignKey,UniqueConstraint,DateTime
from  sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.exc import OperationalError
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import settings
import time


#生成一个SqlORM 基类
Base = declarative_base()


# UserProfileToHostUser(user_profile_id=1,host_user_id=1,group_id=1,project_id=1)

class Project(Base):
    '''
    项目表
    '''
    __tablename__ = 'project'
    id = Column(Integer,autoincrement=True,primary_key=True)
    project_name = Column(String(64),unique=True,nullable=False)

    def __repr__(self):
        return "<Project(id='%s', project_name='%s')>"%(self.id,self.project_name)

class AuditLog(Base):
    '''
    审计表, 用户执行的操作记录会存放在此表中
    '''
    __tablename__ = 'audit_log'
    id = Column(Integer,autoincrement=True,primary_key=True)
    user_profile_id = Column(Integer,ForeignKey('user_profile.id'))
    host_user_id = Column(Integer,ForeignKey('host_user.id'))
    cmd = Column(String(255))
    date = Column(DateTime)

    user_profile = relationship('UserProfile',backref='auditlog')

    def __repr__(self):
        return "<AuditLog(id='%s',user_profile_id='%s',host_user_id='%s'," \
               "cmd='%s',date='%s')>"%(self.id,self.user_profile_id,
                                       self.host_user_id,self.cmd,
                                       self.date)


class Host(Base):
    '''
    主机表,存放堡垒机管理的主机的各种信息, 主机名\ip\端口等
    '''
    __tablename__ = 'host'
    id = Column(Integer,primary_key=True,autoincrement=True)
    hostname = Column(String(64),unique=True,nullable=False)
    ip_addr = Column(String(32),unique=True,nullable=False)
    port = Column(Integer,default=22)

    # 将主机与主机组、主机与主机用户之间进行多对多的关联, 仅为查询用
    users = relationship("UserProfile",secondary=lambda :UserProfileToHostUser.__table__,backref='host')
    groups = relationship("UserGroup",secondary=lambda :UserProfileToHostUser.__table__,backref='host')
    host_users = relationship("HostUser",secondary=lambda :UserProfileToHostUser.__table__,backref='host')
    project = relationship('Project',secondary=lambda :UserProfileToHostUser.__table__,backref='host')

    def __repr__(self):
        return  "<Host(id=%s,hostname=%s, ip_addr=%s, port=%s)>" %(self.id,
                                                    self.hostname,
                                                    self.ip_addr,
                                                    self.port)

class UserGroup(Base):
    '''
    堡垒机用户组表
    '''
    __tablename__ = 'user_group'
    id = Column(Integer,primary_key=True,autoincrement=True)
    group_name = Column(String(32),unique=True,nullable=False)

    def __repr__(self):
        return "<UserGroup(id='%s',group_name='%s')>" % (self.id, self.group_name)

class HostUser(Base):
    '''
    主机用户表,存放用户登录服务器的账户名\密码,以及认证类型
    '''
    __tablename__ = 'host_user'
    id = Column(Integer,primary_key=True,autoincrement=True)
    AuthTypes = [
        (u'ssh-passwd',u'SSH/Password'),
        (u'ssh-key',u'SSH/KEY'),
    ]
    auth_type = Column(String(64),nullable=False)
    username = Column(String(64),nullable=False)
    password = Column(String(255))

    host_id = Column(Integer,ForeignKey('host.id'))

    def __repr__(self):
        return "<HostUser(id='%s',auth_type='%s', username='%s', password='%s',hostid='%s')>" % (self.id,
                                                  self.auth_type,
                                                  self.username,
                                                  self.password,self.host_id)

    #__table_args__ = (UniqueConstraint('host_id','username',name='_host_username_uc'))

class UserProfile(Base):
    '''
    堡垒机用户表,存放堡垒机用户名\密码以及组信息
    '''
    __tablename__ = 'user_profile'
    id = Column(Integer,primary_key=True)
    username = Column(String(64),unique=True,nullable=False)
    password = Column(String(64),nullable=False)
    group_id = Column(Integer,ForeignKey('user_group.id'))



    def __repr__(self):
        return "<UserProfile(id='%s',username='%s', password='%s',group_id='%s')>" % (self.id,
                                                                                      self.username,
                                                                                      self.password,
                                                                                      self.group_id)


# 程序登陆用户和服务器账户，一个人可以有多个服务器账号，一个服务器账号可以给多个人用
class UserProfileToHostUser(Base):
    '''
    堡垒机用户对应主机表,存放对应关系
    '''
    __tablename__ = 'user_profile_to_host_user'
    id = Column(Integer,primary_key=True)
    #外键关联user_profile.id
    user_profile_id = Column(Integer,ForeignKey('user_profile.id'))
    #外键关联host_user表的id值
    host_user_id = Column(Integer,ForeignKey('host_user.id'))
    #外键关联group表的id值
    user_group_id = Column(Integer,ForeignKey('user_group.id'))
    #外键关联项目表的id值
    project_id = Column(Integer,ForeignKey('project.id'))
    #外键关联主机表的id键
    host_id = Column(Integer,ForeignKey('host.id'))

    def __repr__(self):
        return "<UserProfileToHostUser(id='%s',user_profile_id='%s'," \
               "user_group_id='%s',project_id='%s')>"%(self.id,self.user_profile_id,
                                                       self.host_user_id,self.user_group_id,)

class operate_db:
    '''
    数据库操作类
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
        初始化堡垒机数据库,创建所有表结构，并添加原始数据
        :param db_class:
        :return:
        '''
        self.init_db_meta()

        # # #添加项目表初始数据, 项目名称, 默认提供两个
        self.session.add_all([
            Project(project_name='Cloud'),
            Project(project_name='BigData')
        ])

        #添加用户组初始化数据, 提供两个组,用于关联用户分组的主机
        self.session.add_all([
            UserGroup(id=1,group_name='OPS'),
            UserGroup(id=2,group_name='DEV')
        ])
        # #添加主机表数据
        self.session.add_all([
            Host(hostname='Server1',ip_addr='192.168.1.105',port=22,),
            Host(hostname='Server2',ip_addr='192.168.1.106',port=22,),
            Host(hostname='Server3',ip_addr='10.211.55.4',port=22,),
            Host(hostname='Server4',ip_addr='192.168.2.201',port=22,),
        ])
        #在提交一次
        self.session.commit()


        # #添加Users表数据,三个用户, tom, jerry, sam, 主要用户登录堡垒机程序
        self.session.add_all([
            UserProfile(username='tom',password='123456',group_id=1),
            UserProfile(username='jerry',password='123456',group_id=2),
            UserProfile(username='sam',password='123456',group_id=2)
        ])

        #添加主机的ssh账号密码, 默认提供一个用户, test/123456
        self.session.add_all([
            HostUser(id=1,auth_type='ssh/Password',username='test',password='123456',host_id=1),
            HostUser(id=2,auth_type='ssh/Password',username='test',password='123456',host_id=2),
            HostUser(id=3,auth_type='ssh/Password',username='root',password='123456',host_id=3)
        ])
        #提交一次
        self.session.commit()

        #添加用户对应主机对应关系数据
        self.session.add_all([
            UserProfileToHostUser(user_profile_id=1,host_user_id=1,user_group_id=1,project_id=1,host_id=1),
            UserProfileToHostUser(user_profile_id=2,host_user_id=2,user_group_id=2,project_id=2,host_id=2),
            UserProfileToHostUser(user_profile_id=1,host_user_id=1,user_group_id=1,project_id=1,host_id=3),
            UserProfileToHostUser(user_profile_id=2,host_user_id=2,user_group_id=2,project_id=2,host_id=4)
        ])
        #提交内容
        self.session.commit()


    def get_all_host(self):
        '''
        获取所有主机列表方法,返回一个对象
        :return:
        '''
        hosts = self.session.query(Host)
        return hosts

    def get_all_group(self):
        '''
        获取所有组
        :return: 组
        '''
        groups = self.session.query(UserGroup)
        return groups

    def get_group_from_username(self,username):
        '''
        根据用户名返回用户所属组
        :param username: 用户名
        :return:
        '''
        group = self.session.query(UserGroup).join(UserProfile).filter(UserProfile.username==username)
        return group

    def get_host_from_hostname(self,hostname):
        '''
        通过用户提供一个主机名,返回主机所有信息
        :param hostname: 主机名
        :return: 主机的对象
        '''
        host = self.session.query(Host).filter(Host.hostname == hostname)
        return host

    def get_host_from_groupname(self,groupname):
        '''
        通过用户提供一个组名,获取和组名相关的主机
        :param groupname: 组名
        :return: 返回主机对象
        '''
        #多表联合查询
        host = self.session.query(Host).join(Host.groups).filter(UserGroup.group_name == groupname)
        return host

    def get_host_from_username(self,username):
        '''
        通过用户名获取相关联的主机信息
        :param username: 用户名
        :return: 返回主机列表对象
        '''
        host = self.session.query(Host).join(Host.users).filter(UserProfile.username == username)
        return host

    def get_hostuser_from_userid(self,userid):
        '''
        通过用户id查询用户名
        :param userid: id
        :return: 返回一个对象
        '''
        hostuser = self.session.query(HostUser).filter(HostUser.id == userid)
        return hostuser


    def get_user_from_username(self,username):
        '''
        通过用户提供用户名获取该用户的全部信息
        :param username:
        :return:
        '''
        user = self.session.query(UserProfile).filter(UserProfile.username==username)
        return user

    def get_user_from_hostname(self,hostname):
        '''
        通过用户提供的主机名获取关联的用户信息
        :param hostname: 主机名
        :return: 用户对象
        '''
        #Inner join查询,连接host_user表
        user = self.session.query(HostUser).join(Host.host_users).filter(Host.hostname == hostname)
        return  user

    # def get_hostuser_id_from_hostuser(self,hostuser):
    #     '''
    #     通过主机名
    #     :param hostuser:
    #     :return:
    #     '''
    #     hostuser_id = self.session.query(HostUser).join(Host).filter(HostUser.username==hostuser)
    #     return hostuser_id

    def get_userid_from_username(self,username):
        '''
        通过用户名获取用户id
        :param username:
        :return:
        '''
        userid = self.session.query(UserProfile).filter(UserProfile.username==username)
        return userid

    def get_project_from_hostname(self,hostname):
        '''
        通过用户提供的主机名查询主机所属哪个项目
        :param hostname: 主机名
        :return: 项目对象
        '''
        project = self.session.query(Project).join(Host.project).filter(Host.hostname == hostname)
        return project

    def add_audit_log(self,user_id,host_id,command,Date):
        '''
        添加日志审计
        :param user_id: 用户id
        :param host_id: 主机id
        :param command: 命令
        :param Date:    日期
        :return:
        '''
        self.session.add_all([
            AuditLog(user_profile_id=user_id,host_user_id=host_id,cmd=command,date=Date)
        ])
        self.session.commit()

    def get_audit_log_from_username(self,username):
        '''
        通过用户名查找主机操作记录
        :param username:
        :return:
        '''
        logs = self.session.query(AuditLog).join(AuditLog.user_profile).filter(UserProfile.username==username)
        return logs
