#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import sys
import os
import pickle
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf import setting
from lib import log


class Teacher:
    '''
    老湿的类
    '''
    def __init__(self,user):
        '''
        初始化老湿构造函数
        :param user: 姓名
        :param age:  年龄
        :param favor: 老湿别名  asset: 财富值,默认为0
        :return:
        '''
        teacherdb = pickle.load(open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'rb'))
        self.user = user
        self.age = teacherdb[user].get('age')
        self.asset = teacherdb[user].get('asset')
        self.course = teacherdb[user].get('course','无')
        self.favor = teacherdb[user].get('favor')


    def accident(self,value):
        '''
        教学事故方法
        :param value:
        :return:
        '''
        self.asset -= float(value)


    def show_course(self,user,flag):
        '''
        查看代课\资产方法
        :param user:
        :return:
        '''
        teacherdb = pickle.load(open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'rb'))
        #{"username":user, "age":age, "favor": favor, "asset":asset,"password":'123',"first_login":True}
        print('\033[34;1m %s 信息 \033[0m'.center(80,'@')%flag)
        title = '姓名     年龄       别号       资产      代课'
        Format = '{}     {}      {}      {}       {}'
        print(title)
        if user in teacherdb.keys():
            print(Format.format(self.user,self.age,self.favor,self.asset,self.course))
            print('@'*72)
            log.logger.info('%s 查看 %s 信息'%(user,flag))


    def login(self,user,password):
        '''
        老湿登录函数
        :param user:
        :param password:
        :return:
        '''
        if not os.path.exists(os.path.join(setting.TEACHER_DIR,'teacher.db')):
            teacherdb = {}
            print('\033[31;1m还没有任何老湿, 请联系管理员添加老湿!\033[0m')
        else:
            teacherdb = pickle.load(open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'rb'))
            if user in teacherdb.keys():
                if teacherdb[user].get('first_login'):
                    print('%s, 您是初次登录系统,请先修改您的密码!'%user)
                    inp_pass = input('请输入密码(至少6位): ').strip()
                    if len(inp_pass) >= 6:
                        inp_pass_verify = input('请重复输入一遍密码:').strip()
                        if inp_pass == inp_pass_verify:
                            teacherdb[user]['password'] = inp_pass
                            teacherdb[user]['first_login'] = False
                            pickle.dump(teacherdb,open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'wb'))
                            print('密码已更改,请妥善保管密码!')
                            log.logger.info('%s初次登录,密码已成功修改'%user)
                            return False
                        else:
                            print('\033[31;1m两次输入密码不一致!\033[0m')
                            return False
                    else:
                        print('\033[31;1m密码输入不规范,长度至少6位!\033[0m')
                        return False


                else:
                    for i in teacherdb.keys():
                        if user == teacherdb[i]['username'] and password == teacherdb[i]['password']:
                            print('\033[32;1m登录成功\033[0m')
                            log.logger.info('%s 登录成功'%user)
                            return True
            else:
                print('\033[31;1m用户名或者密码错误!\033[0m')
                log.logger.info('%s 登录失败,用户名或者密码错误 '%user)
                return False






class Manager:
    '''
    管理员类
    '''
    def __init__(self,user):
        self.user = user
        # self.pwd = None

    def login(self,user,pwd):
        '''
        管理员登录函数
        :param user:
        :param pwd:
        :return:
        '''
        if not os.path.exists(os.path.join(setting.ADMIN_DIR,user)):
            print('用户名不存在!')
        else:
            userdb = pickle.load(open(os.path.join(setting.ADMIN_DIR,user),'rb'),encoding='utf-8')
            if user == userdb['username'] and pwd == userdb['password']:
                print('登录成功, 欢迎回来 [ %s ] '%user)
                log.logger.info('[ %s ]登录成功'%user)
                return True
            else:
                print('用户名/密码错误!')
                log.logger.info('[ %s ]尝试登录, 账号密码验证失败'%user)
                return False


    def del_teacher(self):
        '''
        删除老湿方法
        :return:
        '''
        if os.path.exists(os.path.join(setting.COURSE_DIR,'course.db')):
            coursedb = pickle.load(open(os.path.join(setting.COURSE_DIR,'course.db'),'rb'))
        else:
            print('\033[31;1m没有任何课程!\033[0m')
            return False
        self.show_teacher()
        inp = input('请输入你要删除的老湿姓名: ').strip()
        if os.path.exists(os.path.join(setting.TEACHER_DIR,'teacher.db')):
            teacherdb = pickle.load(open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'rb'))
        else:
            return False
        if inp in teacherdb.keys():
            #coursedb[inp_name] = {"course":inp_name, "payment":inp_favor, "teacher":inp_id}
            if teacherdb[inp].get('course'):
                for i in range(len(teacherdb[inp]['course'])):
                    coursedb[teacherdb[inp]['course'][i]]['teacher'] = False
            del teacherdb[inp]
            print('\033[31;1m%s老湿删除成功,操作员 %s\033[0m'%(inp,self.user))
            pickle.dump(teacherdb,open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'wb'))
            pickle.dump(coursedb,open(os.path.join(setting.COURSE_DIR,'course.db'),'wb'))
            log.logger.info('%s老湿删除成功,操作员 %s'%(inp,self.user))
        else:
            print('\033[31;1m%s 老湿不存在!\033[0m'%inp)


    def del_course(self):
        '''
        删除课程方法
        :return:
        '''
        if os.path.exists(os.path.join(setting.COURSE_DIR,'course.db')):
            coursedb = pickle.load(open(os.path.join(setting.COURSE_DIR,'course.db'),'rb'))
        else:
            print('\033[31;1m没有任何课程!\033[0m')
            return False
        self.show_course()
        inp = input('请输入你要删除的课程名称, 如 蛤蟆功 : ').strip()
        if os.path.exists(os.path.join(setting.TEACHER_DIR,'teacher.db')):
            teacherdb = pickle.load(open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'rb'))
        else:
            teacherdb = {}
        if inp in coursedb.keys():
            #coursedb[inp_name] = {"course":inp_name, "payment":inp_favor, "teacher":inp_id}
            for i in teacherdb.keys():
                if inp in teacherdb[i].get('course'):
                    teacherdb[i]['course'].remove(inp)
                    log.logger.info('%s 老湿关联的课程 %s 已被删除, 原因是课程被删除, 操作员 %s '%(i,inp,self.user))
                    pickle.dump(teacherdb,open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'wb'))
            del coursedb[inp]
            print('\033[31;1m%s课程删除成功,操作员 %s\033[0m'%(inp,self.user))
            pickle.dump(coursedb,open(os.path.join(setting.COURSE_DIR,'course.db'),'wb'))
            log.logger.info('%s课程删除成功,操作员 %s '%(inp,self.user))
        else:
            print('\033[31;1m%s 课程不存在!\033[0m'%inp)


    def registry(self,user,pwd):
        '''
        注册管理员函数
        :return:
        '''
        if os.path.exists(os.path.join(setting.ADMIN_DIR,user)):
            print('用户名 [ %s ] 已经存在!'%user)
            log.logger.info('%s 用户注册失败, 用户已存在!' %user)
            return False
        else:
            userdb = {'username':user,'password':pwd}
            userdb = pickle.dump(userdb,open(os.path.join(setting.ADMIN_DIR,user),'wb'))
            if os.path.exists(os.path.join(setting.ADMIN_DIR,user)):
                print('\033[31;1m注册成功!\033[0m')
                log.logger.info('%s 用户注册成功' %user)
                return True
            else:
                print('注册失败')
                log.logger.info('%s 用户注册失败' %user)
                return False


    def add_teacher(self,username):
        '''
        添加老湿
        :return:
        '''

        user = input('请输入代课老湿名字:').strip()
        if not user:
            print('老湿名字不允许为空!')
            user = input('请输入代课老湿名字:').strip()
        age = input('%s 老湿的年龄多大了?'%user).strip()
        if age.isdigit():
            favor = input('%s老湿的别名/尊称?'%user)
        else:
            print('\033[31;1m输入的年龄类型不对!\033[0m')
            favor = input('%s老湿的别名/尊称?'%user)
            age = input('%s 老湿的年龄多大了?'%user).strip()
        asset = 0
        if os.path.exists(os.path.join(setting.TEACHER_DIR,'teacher.db')):
            teacherdb = pickle.load(open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'rb'))
        else:
            teacherdb = {}
        if user in teacherdb.keys():
            print('\033[31;1m%s 老湿已经存在啦!\033[0m'%user)
        else:
            teacherdb[user] = {"username":user, "age":age, "favor": favor, "asset":asset,"password":'123',"first_login":True}
            pickle.dump(teacherdb,open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'wb'))
            log.logger.info('老湿[ %s ]被添加成功, 操作员[ %s ]'%(user,username))
            print('\033[32;1m老湿添加成功!\033[0m')


    def show_teacher(self):
        '''
        显示所有老湿信息
        :return:
        '''
        if not os.path.exists(os.path.join(setting.TEACHER_DIR,'teacher.db')):
            print('还没有添加任何老湿!')
        else:
            teacherdb = pickle.load(open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'rb'))
            print('\033[34;1m 老湿信息 \033[0m'.center(80,'@'))
            title = '序号     姓名     年龄      别号      资产     代课'
            Format = '{}     {}      {}      {}      {}       {}'

            print(title)
            for id,user in enumerate(teacherdb.keys()):
                username = teacherdb[user].get('username')
                age = teacherdb[user].get('age')
                favor = teacherdb[user].get('favor')
                asset = teacherdb[user].get('asset')
                course = teacherdb[user].get('course','无')
                print(Format.format(id,username,age,favor,asset,course))
            print('@'*72)


    def add_course(self,user):
        '''
        添加课程
        :return:
        '''
        teacherdb = pickle.load(open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'rb'))
        if os.path.exists(os.path.join(setting.COURSE_DIR,'course.db')):
            coursedb = pickle.load(open(os.path.join(setting.COURSE_DIR,'course.db'),'rb'))
        else:
            coursedb = {}
        inp_name = input('请输入课程名字: ').strip()
        if inp_name:
            inp_period = input('请输入总课时(必须是整数)').strip()
            if inp_period and inp_period.isdigit():
                inp_favor = input('请输入课程费: ').strip()
                if inp_favor and float(inp_favor) > 0:
                    inp_favor = float(inp_favor)
                    self.show_teacher()
                    inp_id = input('请输入代课老湿的姓名: ').strip()
                    if inp_name in coursedb.keys():
                        if not coursedb[inp_name].get('teacher'):
                            inp_num3 = input('%s课程已经存在,但是没有关联任何老湿,需要关联老湿 [ %s ]么? y/Y'%(inp_name,inp_id)).strip()
                            if inp_num3 == 'y' or inp_num3 == 'Y':
                                if inp_id and inp_id in teacherdb.keys():
                                    if teacherdb[inp_id].get('course',None):
                                        course_list = teacherdb[inp_id]['course']
                                    else:
                                        course_list = []
                                    if inp_id not in course_list:
                                        course_list.append(inp_name)
                                        teacherdb[inp_id]['course'] = course_list
                                        coursedb[inp_name]['teacher'] = inp_id
                                    else:
                                        print('课程已经存在老湿的所授课程内!')
                                        return False
                                else:
                                    print('老湿不存在或者序列不合法! ')
                                    return False
                            else:
                                print('放弃操作!')
                                log.logger.info('%s 课程已经存在,但是没有关联代课老湿, %s放弃关联操作!'%(inp_name,user))
                                return False
                        else:
                            print('\033[31;1m课程已经存在!\033[0m')
                            log.logger.info('操作失败,课程 %s 已存在, 操作员 %s'%(inp_name,user))
                            return False
                    else:
                        coursedb[inp_name] = {"course":inp_name, "payment":float(inp_favor), "teacher":inp_id,"period":int(inp_period)}
                        if inp_id and inp_id in teacherdb.keys():
                            if teacherdb[inp_id].get('course',None):
                                course_list = teacherdb[inp_id]['course']
                            else:
                                course_list = []
                            if inp_id not in course_list:
                                course_list.append(inp_name)
                                teacherdb[inp_id]['course'] = course_list
                            else:
                                print('课程已经存在老湿的所授课程内!')
                                return False
                        else:
                            print('老湿不存在或者序列不合法! ')
                            return False
                else:
                    print('\033[31;1m总课时类型不对\033[0m')
                    return False
                print('\033[31;1m课程 %s 添加成功, 老湿 %s, 操作员 %s\033[0m'%(inp_name,inp_id,user))
                log.logger.info('课程 %s 添加成功, 老湿 %s, 操作员 %s'%(inp_name,inp_id,user))
                pickle.dump(coursedb,open(os.path.join(setting.COURSE_DIR,'course.db'),'wb'))
                pickle.dump(teacherdb,open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'wb'))


    def show_course(self):
        '''
        查看课程方法
        :return:
        '''
        if os.path.exists(os.path.join(setting.COURSE_DIR,'course.db')):
            coursedb = pickle.load(open(os.path.join(setting.COURSE_DIR,'course.db'),'rb'))
        else:
            coursedb = {}

        if not coursedb:
            print('\033[31;1m还没有任何课程信息\033[0m')
            return False
        else:
            print('\033[34;1m 课程信息 \033[0m'.center(80,'@'))
            title = '序号         课名       课时费       代课老湿        所学人数'
            Format = '{}          {}        {}         {}             {}'
            print(title)
            for id,course in enumerate(coursedb.keys()):
                course = course
                payment = coursedb[course].get('payment')
                teacher = coursedb[course].get('teacher')
                students_num = coursedb[course].get('students_num','0')
                print(Format.format(id,course,payment,teacher,students_num))
            print('@'*72)






class Students(Manager):
    '''
    学生类
    '''

    def __init__(self):
        pass

    def select_course(self):
        '''
        选课方法
        :return:
        '''
        user = setting.USER_STATUS.get('student')
        coursedb = pickle.load(open(os.path.join(setting.COURSE_DIR,'course.db'),'rb'))
        #coursedb[inp_name] = {"course":inp_name, "payment":inp_favor, "teacher":inp_id}
        studentdb = pickle.load(open(os.path.join(setting.STUDENT_DIR,user),'rb'))
        # print(studentdb)
        inp = input('\033[31;1m请输入你感兴趣的课程名:\033[0m').strip()
        if inp in coursedb.keys():
            inp1 = input('你选择了课程 %s 课时费:%.2f 授课老师: %s, 确定吗? y/Y'%(inp,coursedb[inp]['payment'],coursedb[inp]['teacher'])).strip()
            if inp1 == 'y' or inp1 == 'Y':
                if inp not in studentdb['course'].keys():
                    studentdb['course'][inp] = {'payment':coursedb[inp]['payment'],
                                                'teacher':coursedb[inp]['teacher'],
                                                "period":coursedb[inp]['period'],
                                                "end_period":0,
                                                "balance_period":coursedb[inp]['period']
                                                }
                    students_num = coursedb[inp].get('students_num',0)
                    students_num += 1
                    coursedb[inp]['students_num'] = students_num
                    studentid = studentdb['studentid']
                    pickle.dump(coursedb,open(os.path.join(setting.COURSE_DIR,'course.db'),'wb'))
                    pickle.dump(studentdb,open(os.path.join(setting.STUDENT_DIR,user),'wb'))
                    log.logger.info('学生 %s(学号:%s)成功选课 %s'%(user,studentid,inp))
                    print('\033[32;1m选课成功!\033[0m')
                else:
                    print('\033[31;1m选择的课程已经在已选课程中了,不能重复选课!\033[0m')
                    if input('按下回车键继续...'):pass
            else:
                print('\033[31;1m放弃操作\033[0m')


    def show_select_course(self):
        '''
        查看所选课程列表
        :return:
        '''
        user = setting.USER_STATUS.get('student')
        studentdb = pickle.load(open(os.path.join(setting.STUDENT_DIR,user),'rb'))
        # print(studentdb)
        if studentdb.get('course'):
            print('\033[34;1m 选课信息 \033[0m'.center(80,'@'))
            title = '序号      课程          课时费       老湿       课程课时     已上课时     剩余课时'
            Format = '{}       {}       {}        {}         {}         {}          {}'
            print(title)
            for id,course in enumerate(studentdb['course'].keys()):
                payment = studentdb['course'][course].get('payment')
                teacher = studentdb['course'][course].get('teacher')
                period = studentdb['course'][course].get('period')
                end_period = studentdb['course'][course].get('end_period')
                balance_period = studentdb['course'][course].get('balance_period')
                print(Format.format(id,course,payment,teacher,period,end_period,balance_period))
            print('@'*72)
            if input('\033[34;1m按下回车键继续...\033[0m'):pass
        else:
            print('\033[31;1m您还没有选择任何课程,请先选课后在查看!\033[0m')


    def study(self):
        '''
        上课方法
        :param user:
        :return:
        '''
        user = setting.USER_STATUS.get('student')
        studentdb = pickle.load(open(os.path.join(setting.STUDENT_DIR,user),'rb'))
        teacherdb = pickle.load(open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'rb'))
        #teacherdb={"username":user, "age":age, "favor": favor, "asset":asset,"password":'123',"first_login":True}
        if studentdb.get('course'):
            self.show_select_course()
            inp = input('请输入要上课的课程名, 如(蛤蟆功)\n>>').strip()
            if inp in studentdb['course'].keys():
                if studentdb['course'][inp].get('end_period') < studentdb['course'][inp].get('period'):
                    inp1 = input('\033[31;1m课程: %s, 老湿: %s, 课时费: %.2f, 确定上课么? y/Y\033[0m'%(inp,
                                                                          studentdb['course'][inp].get('teacher'),
                                                                          studentdb['course'][inp].get('payment'))).strip()
                    if inp1 == 'y' or inp1 == 'Y':
                        if studentdb.get('balance',0) < studentdb['course'][inp].get('payment'):  #金额不足的时候,提示充值
                            inp2 = input('\033[31;1m您账户的可用余额不足,无法进行此次上课,账户可用余额为:[ %.2f ]是否充值? y/Y\n>>\033[0m' \
                                         %studentdb.get('balance',0)).strip()
                            if inp2 == 'y' or inp2 == 'Y':
                                inp_money = input('请输入此次要充值的金额(元):').strip()
                                if inp_money and float(inp_money) > 1:
                                    balance = studentdb.get('balance',0)
                                    assets = studentdb.get('assets',0)
                                    balance += float(inp_money)
                                    assets += float(inp_money)
                                    studentdb['balance'],studentdb['assets'] = balance,assets
                                    pickle.dump(studentdb,open(os.path.join(setting.STUDENT_DIR,user),'wb'))
                                    time.sleep(2)
                                    print('\033[31;1m充值成功, 此次充值 %.2f元, 充值后的余额为: %.2f 元\033[0m'%(float(inp_money),
                                                                                                studentdb['balance']
                                                                                                ))
                                    log.logger.info('%s(学号:%s) 充值成功, 充值金额: %.2f'%(user,
                                                                                        studentdb['studentid'],
                                                                                        float(inp_money)
                                                                                            ))
                                    return True
                                else:
                                    print('\033[31;1m充值金额不合法!\033[0m')
                                    return False
                            else:
                                print('\033[31;1m放弃充值,没有完成上课!\033[0m')
                                log.logger.info('%s(学号:%s) 放弃充值,没有完成上课!'%(user,studentdb['studentid']))
                                return False
                        else:
                            if os.path.exists(os.path.join(setting.COURSE_DIR,'course.db')):
                                coursedb = pickle.load(open(os.path.join(setting.COURSE_DIR,'course.db'),'rb'))
                                course_detail = '\033[31;1m%s是一个很牛逼的武功,花这么点钱就学这么牛逼的武功,值吧, 秘籍拿去, 不谢! ^_^  请精心修炼...\033[0m'%inp
                                if coursedb[inp].get('course_detail'):
                                    print(coursedb[inp].get('course_detail'))
                                else:
                                    print(course_detail)
                                teacher = studentdb['course'][inp].get('teacher')
                                payment = studentdb['course'][inp].get('payment')
                                teacherdb[teacher]['asset'] += float(payment)             #老湿资产增加
                                studentdb['balance'] -= float(payment)                    #学生剩余资产减少
                                studentdb['course'][inp]['balance_period'] -= 1           #学生剩余课时-1
                                studentdb['course'][inp]['end_period'] += 1               #学生已学课时+1

                                #添加上课记录
                                if studentdb.get('study_record'):
                                    record_list = studentdb['study_record']
                                else:
                                    record_list = []
                                Datetime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
                                record_list.append([inp,teacher,1,float(payment),Datetime])
                                studentdb['study_record'] = record_list


                                log.logger.info('%s(学号:%s) 学习了武功 %s, 资产减少: %.2f 老湿 %s, 资产成功增加 %.2f'%(user,
                                                                                          studentdb['studentid'],inp,
                                                                                          float(payment),
                                                                                          teacher,float(payment)))

                                #持久化到文件:
                                pickle.dump(studentdb,open(os.path.join(setting.STUDENT_DIR,user),'wb'))
                                pickle.dump(teacherdb,open(os.path.join(setting.TEACHER_DIR,'teacher.db'),'wb'))
                                time.sleep(5)
                                if input('\033[32;1m1课时学习完成, 按下回车键继续!\033[0m'):pass
                            else:
                                print('\033[31;1m没有任何课程!\033[0m')
                                return False
                    else:
                        print('\033[31;1m放弃操作!\033[0m')
                else:
                    print('\033[31;1m 课程%s课时已学满,你已经出师啦,可以出去找人PK了,如果想回学招数,快回家看视频啦~!\033[0m')
                    log.logger.info('%s(学号:%s) 武功 %s 已经学完了,无法再学一遍!'%(user,studentdb['studentid'],inp))
                    return False
            else:
                print('\033[31;1m你输入的课程名[ %s ]不存在或者你没有选修!\033[0m'%inp)
        else:
            print('\033[31;1m你还没有选择任何课程,请先选课后再上课!\033[0m')
            return False


    def login(self,user,password):
        '''
        学生登录函数
        :param user:
        :param password:
        :return:
        '''
        if not os.path.exists(os.path.join(setting.STUDENT_DIR,user)):
            studentdb = {}
            print('\033[31;1m 用户不存在!\033[0m')
            return False
        else:
            studentdb = pickle.load(open(os.path.join(setting.STUDENT_DIR,user),'rb'))
            if user == studentdb['username'] and password == studentdb['password']:
                print('\033[32;1m登录成功\033[0m')
                setting.USER_STATUS['student'] = user
                log.logger.info('%s 成功登录学生平台'%user)
                return True
            else:
                print('\033[31;1m用户名或者密码错误!\033[0m')
                log.logger.info('%s 登录学生平台失败,用户名或者密码错误!'%user)
                return False


    def registry(self):
        '''
        学生注册函数
        :return:
        '''
        user = input('请输入学生姓名!').strip()
        if user:
            password = input('请输入登录密码(长度不低于6位):').strip()
            if len(password) < 6:
                print('\033[31;1m密码长度不符合要求!\033[0m')
                return False
            else:
                password_verify = input('请再次输入登录密码: ').strip()
                if password != password_verify:
                    print('\033[31;1m两次输入密码不一致!\033[0m')
                    return False
                qqnum = input('请输入您的QQ号').strip()
                if qqnum.isdigit() and len(qqnum) >= 5:
                    studentid = 'stu%s'%qqnum[-1-3:]  #学号
                    assets = input('请输入你想学就绝世武功准备花销的费用?(元)').strip()
                    if assets and float(assets) > 300:
                        assets = float(assets)
                    else:
                        print('\033[31;1m费用类型错误或者费用太少, 不够300元!\033[0m')
                        return False
                else:
                    print('\033[31;1m学号输入不正确,请输入5位以上的QQ号!\033[0m')
                    return False
        if os.path.exists(os.path.join(setting.STUDENT_DIR,user)):
            print('\033[31;1m 用户已经存在!\033[0m')
            log.logger.info('%s 注册失败,用户名已存在!'%user)
            return False
        else:
            studentdb = {}
            studentdb['username'] = user
            studentdb['password'] = password
            studentdb['course'] = {}
            studentdb['studentid'] = studentid
            studentdb['assets'] = assets
            studentdb['balance'] = assets
            pickle.dump(studentdb,open(os.path.join(setting.STUDENT_DIR,user),'wb'))
            print('\033[32;1m注册成功\033[0m')
            log.logger.info('%s 成功注册学生平台'%user)
            return True

    def show_study_history(self):
        '''
        查看用户上课记录以及资产信息
        :return:
        '''
        user = setting.USER_STATUS.get('student')
        studentdb = pickle.load(open(os.path.join(setting.STUDENT_DIR,user),'rb'))
        #[课程名, 授课老师, 学时, 课时费,上课时间]
        if not studentdb.get('study_record'):
            print('\033[31;1m您还没有任何上课记录\033')
            return False
        else:
            print('\033[34;1m 您的上课记录 \033[0m'.center(80,'@'))
            title = '序号      课程名      老湿       学时       课时费     上课时间'
            Format = '{}       {}       {}        {}         {}         {}'
            print(title)
            for i in range(len(studentdb['study_record'])):
                print(Format.format(
                    i,studentdb['study_record'][i][0],
                    studentdb['study_record'][i][1],
                    studentdb['study_record'][i][2],
                    studentdb['study_record'][i][3],
                    studentdb['study_record'][i][4]
                ))
            print('@'*74)
            print('\033[31;1m用户名:[ %s ], 学号: [ %s ], 共消费: [ %.2f ], 可用余额: [ %.2f ]\033[0m'%(user,
                                                                             studentdb['studentid'],
                                                                            studentdb['assets']-studentdb['balance'],
                                                                            studentdb['balance']))

            if input('按下回车键继续...'):pass


