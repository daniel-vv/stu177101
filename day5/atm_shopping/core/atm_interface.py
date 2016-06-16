#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import os,sys,time,json,pickle,datetime  #导入各种模块
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import user_manager
from core import shop_mall
from core import menu
from core import log
from conf import setting




def show_help():
    '''
    ATM机帮助函数
    :return:
    '''
    print(' HELP '.center(100,'@'))
    print('''\033[35;1m
        1. 用户额度： 默认用户额度50000
        2. 提现：	提现手续费5%, 提现金额为可用额度的 50%
        3. 账单：	每月22号为用户账单日，次月10号为还款日，过期未还，按欠款总额 万分之5来每日计息
        4. 多账户：	支持多账户登录
        5. 转账：	支持账户间转账， 账户间转账手续费为5%(同提现手续费)
        6. 流水：	记录每月日常消费流水
        7. 还款:		用户还款日之前(每月10晚24:00之前)必须全额还清上期账单，否则会按账单全额的总额万分之五来每日计息。
        8. 日志: 	ATM记录操作日志
        9. 管理接口:	包括添加账户、用户额度调整，冻结账户等。。。
    \033[0m''')


def show_user(user,args):
    '''
    查看用户字典函数
    :param user: 接受用户传入形参ATM用户卡号
    :param args: 接受用户传入要查询的值
    :return: 返回给用户查询的值
    '''
    result = user_manager.ATM_USER_INFO[user][args]
    return result


def draw_cash():
    '''
    提现函数
    :return:
    '''
    user = user_manager.ATM_USER_STATUS['username']
    username = user_manager.ATM_USER_INFO[user]['user']
    avalilable = show_user(user,'available')
    cash_limit = avalilable/2
    # print(cash_limit)
    # print(avalilable)
    # print(type(avalilable))
    verify = input('\033[31;1m尊敬的用户[ %s ],取现手续费为提取现金金额的5%%, 确认? (y/Y)\033[0m'%username).strip()
    if verify == 'y' or verify == 'Y':
        inp = input('您的账户最高可取现[ %.2f ]元, 请输入你要提取的现金金额:  '%int(cash_limit)).strip()
        if inp and inp.isdigit():
            if float(inp) <= avalilable/2 and int(inp) > 0:
                inp = float(inp)
                cost = inp * 0.05
                avalilable = avalilable - inp - cost   #减金额和手续费
                log.atm_log(user,time.localtime(),'info','信用卡账户: [%s]  提现: [%.2f] 元  手续费[ %.2f ] 元'%(user,inp,cost))
                user_manager.ATM_USER_INFO[user]['available'] = avalilable

                curr_time = shop_mall.curr_datetime()  #取出账单日期
                if user_manager.ATM_USER_INFO[user]['record'].get(curr_time,None):
                    if user_manager.ATM_USER_INFO[user]['record'].get(curr_time,None).get('total_debt') and \
                                    user_manager.ATM_USER_INFO[user]['record'].get(curr_time,None).get('total_debt') >= 0:
                        user_manager.ATM_USER_INFO[user]['record'][curr_time]['total_debt'] += (inp + cost) #账单欠款金额增加
                    else:
                        user_manager.ATM_USER_INFO[user]['record'].setdefault(curr_time,{'total_debt': inp+cost})
                else:
                    user_manager.ATM_USER_INFO[user]['record'].setdefault(curr_time,{'total_debt': inp+cost})

                json.dump(user_manager.ATM_USER_INFO,open(user_manager.ATM_USERDB,'w'))  #持久化

                print('正在出抄票,请不要离开...')
                time.sleep(2)
                if input('\033[31;1m 成功提现: [%.2f] 元  手续费[ %.2f ] 元\033[0m'%(inp,cost)):pass
            else:
                print('\033[31;1m账户可用额度不够或者输入金额不合法!\033[0m')

                return False
        else:
            print('输入的金额不合法!')
            return False


def show_bill(user):
    '''
    账户查询账单函数
    :return:
    '''
    struct_time = time.localtime()  #struct_time时间
    curr_date = datetime.date.isoformat(datetime.datetime.now())  #现有日期 年-月-日格式
    available = show_user(user,'available')  #可用额度
    limit = show_user(user,'limit')          #额度
    username = show_user(user,'user')        #账户名
    debt = float(available) - float(limit)                 #欠款金额
    cost = 0
    repayment_num = 0

    curr_time = shop_mall.curr_datetime()    #取出账单日期

    for value in user_manager.ATM_USER_INFO[user]['record'].keys():
        bill_date = value
        if struct_time.tm_mday >= 23:  #取出账单金额, 如果日期日期是22号以后,列出当月账单
            curr_time = '%d-%d-%d'%(struct_time.tm_year,struct_time.tm_mon,22)
            if user_manager.ATM_USER_INFO[user]['record'].get(value):
                curr_bill = user_manager.ATM_USER_INFO[user]['record'].get(value).get('total_debt')
            else:
                curr_bill = '当月账单还未生成'
                bill_date = '账单日每月22日'
            if user_manager.ATM_USER_INFO[user]['record'][value].get('repayment'):
                repayment_num = user_manager.ATM_USER_INFO[user]['record'][value].get('repayment')
            else:
                repayment_num = 0

            if user_manager.ATM_USER_INFO[user]['record'][value]:
                repayment_num = user_manager.ATM_USER_INFO[user]['record'][value].get('repayment')
            else:
                repayment_num = 0

        elif '%d-%d-%d'%(struct_time.tm_year,struct_time.tm_mon-1,22) in \
                user_manager.ATM_USER_INFO[user]['record'].keys():      #如果有上月账单显示
            curr_date = '%d-%d-%d'%(struct_time.tm_year,struct_time.tm_mon-1,22)
            curr_bill = user_manager.ATM_USER_INFO[user]['record'].get(curr_date).get('total_debt')
            if user_manager.ATM_USER_INFO[user]['record'][curr_date].get('repayment'):
                repayment_num = user_manager.ATM_USER_INFO[user]['record'][curr_date].get('repayment')
            else:
                repayment_num = 0

            if user_manager.ATM_USER_INFO[user]['record'][curr_date].get('repayment'):
                repayment_num = user_manager.ATM_USER_INFO[user]['record'][curr_date].get('repayment')
            else:
                repayment_num = 0

        elif user_manager.ATM_USER_INFO[user]['available'] < float(user_manager.ATM_USER_INFO[user]['limit']) and \
                value != '%d-%d-%d'%(struct_time.tm_year,struct_time.tm_mon,22):
            curr_bill = user_manager.ATM_USER_INFO[user]['record'].get(value).get('total_debt')
            repayment_num = user_manager.ATM_USER_INFO[user]['record'][value].get('repayment',0)
            bill_date = value
        else:
            curr_bill = '当月账单还未生成'



        struct_bill_date = time.strptime(bill_date,'%Y-%m-%d')
        repayment_date = '%d-%d-%d'%(struct_bill_date.tm_year,struct_bill_date.tm_mon+1,10)  #还款日

        #计算延期手续费
        date1 = time.strftime('%j',time.strptime(repayment_date,'%Y-%m-%d'))  #还款日


        date2 = time.strftime('%j',struct_time)  #当前时间

        diff_days = int(date2) - int(date1)  #差

        cost = curr_bill * 0.0005 * int(diff_days) if int(diff_days) > 0 else 0


        if curr_bill == '当月账单还未生成':
            print('''\033[34;1m
                        个人信用卡账单:
{}
                    账    号:      [{}]
                    账 户 名:      [{}]

                    人民币账单:      [{}]
{}
                \033[0m'''.format('#'*60,user,username,curr_bill,'#'*60))
            if input('按下回车键,继续...'):pass
        elif repayment_num and repayment_num >= curr_bill + cost:
            print('''\033[34;1m
                        个人信用卡账单:
{}
                    账    号:      [{}]
                    账 户 名:       [{}]

                    人民币账单:      [{}]
                    已还金额:        [{}]
                    账单日期:        [{}]
                    到期还款日:      [{}]
                    延期手续费:      [{}]

                    已还清当期账单全部金额!
{}
                \033[0m'''.format('#'*60,user,username,curr_bill,repayment_num,bill_date,repayment_date,cost,'#'*60))
            if input('按下回车键,继续...'):pass
        else:
            print('''\033[34;1m
                        个人信用卡账单:
{}
                    账    号:      [{}]
                    账 户 名:       [{}]

                    人民币账单:      [{}]
                    已还金额:        [{}]
                    账单日期:        [{}]
                    到期还款日:      [{}]
                    延期手续费:      [{}]
{}
                \033[0m'''.format('#'*60,user,username,curr_bill,repayment_num,bill_date,repayment_date,cost,'#'*60))
            if input('按下回车键,继续...'):pass

    if not user_manager.ATM_USER_INFO[user]['record']:
        print('\033[31;1m您还未有任何消费!\033[0m')
        return False

    # if cost:
    #     return cost
    # else:
    #     cost = 0
    return cost


def show_bill_bak(user):
    '''
    账户查询账单函数备份用
    :return:
    '''
    struct_time = time.localtime()  #struct_time时间
    curr_date = datetime.date.isoformat(datetime.datetime.now())  #现有日期 年-月-日格式
    available = show_user(user,'available')  #可用额度
    limit = show_user(user,'limit')          #额度
    username = show_user(user,'user')        #账户名
    debt = available - limit                 #欠款金额
    # cost = '无'
    curr_time = shop_mall.curr_datetime()    #取出账单日期

    if struct_time.tm_mday >= 23:  #取出账单金额, 如果日期日期是22号以后,列出当月账单
        curr_time = '%d-%d-%d'%(struct_time.tm_year,struct_time.tm_mon,22)
        if user_manager.ATM_USER_INFO[user]['record'].get(curr_time):
            curr_bill = user_manager.ATM_USER_INFO[user]['record'].get(curr_time).get('total_debt')
        bill_date = curr_time
        if user_manager.ATM_USER_INFO[user]['record'][curr_time].get('repayment'):
            repayment_num = user_manager.ATM_USER_INFO[user_manager]['record'][curr_time].get('repayment')
        else:
            repayment_num = 0
    elif user_manager.ATM_USER_INFO[user]['record'].get('%d-%d-%d'%(struct_time.tm_year,struct_time.tm_mon-1,22)):  #22号之前读取上一个月账单
        curr_bill = user_manager.ATM_USER_INFO[user]['record'].get('%d-%d-%d'%(struct_time.tm_year \
                                                                            ,struct_time.tm_mon-1,22)).get('total_debt')
        bill_date = '%d-%d-%d'%(struct_time.tm_year,struct_time.tm_mon-1,22)
        if user_manager.ATM_USER_INFO[user]['record'].get(curr_time,None):
            repayment_num = user_manager.ATM_USER_INFO[user_manager]['record'][curr_time].get('repayment',None)
        else:
            repayment_num = 0
    else:
        curr_bill = '账单还未生成'
        bill_date = '账单日每月22日'
        if user_manager.ATM_USER_INFO[user]['record'][curr_time].get('repayment'):
            repayment_num = user_manager.ATM_USER_INFO[user]['record'][curr_time].get('repayment')
        else:
            repayment_num = 0

    struct_bill_date = time.strptime(bill_date,'%Y-%m-%d')
    repayment_date = '%d-%d-%d'%(struct_bill_date.tm_year,struct_bill_date.tm_mon+1,10)  #还款日

    #计算延期手续费
    date1 = time.strftime('%j',time.strptime(repayment_date,'%Y-%m-%d'))  #还款日


    date2 = time.strftime('%j',struct_time)  #当前时间

    diff_days = int(date2) - int(date1)  #差

    cost = curr_bill * 0.0005 * int(diff_days) if int(diff_days) > 0 else '无'


    if curr_bill == '账单还未生成':
        print('''\033[34;1m
                    个人信用卡账单:
{}
                账    号:      [{}]
                账 户 名:      [{}]

                人民币账单:      [{}]
{}
            \033[0m'''.format('#'*60,user,username,curr_bill,'#'*60))
        if input('按下回车键,继续...'):pass
    else:
        print('''\033[34;1m
                    个人信用卡账单:
{}
                账    号:      [{}]
                账 户 名:       [{}]

                人民币账单:      [{}]
                已还金额:        [{}]
                账单日期:        [{}]
                到期还款日:      [{}]
                延期手续费:      [{}]
{}
            \033[0m'''.format('#'*60,user,username,curr_bill,repayment_num,bill_date,repayment_date,cost,'#'*60))
        if input('按下回车键,继续...'):pass


def transfer():
    '''
    账户间转账函数
    :return: 失败的话 return False
    '''
    user = user_manager.ATM_USER_STATUS['username']   #先获取用户当前登录账户
    username = user_manager.ATM_USER_INFO[user]['user']
    avalilable = show_user(user,'available')  #可用额度
    cash_limit = avalilable/2   #可转账金额最大限度
    verify = input('\033[31;1m尊敬的用户[ %s ],转账手续费为当前转账金额的5%%, 确认否? (y/Y)\033[0m'%username).strip()
    if verify == 'y' or verify == 'Y':
        inp_user = input('请输入对方账户:').strip()
        inp_user_verify = input('请再次输入对方账号').strip()
        if inp_user != inp_user_verify:
            print('\033[31;1m两次输入号码不一致')
            return False
        else:
            inp = input('您的账户最高可转账[ %d ]元, 请输入你要向对方转账的金额:  '%int(cash_limit)).strip()
            if inp_user not in user_manager.ATM_USER_INFO.keys():
                print('\033[31;1m对方账户不存在!\033[0m')
                return False
            else:
                transfer_username = show_user(inp_user,'user')
                if inp_user == user_manager.ATM_USER_STATUS['username']:
                    print('\033[31;1m不允许给自己转账!!!\033[0m')
                else:
                    if inp and inp.isdigit():
                        inp = float(inp)
                        transfer_verify = input("""

                            对方银行账号:     [ %s ]
                            对方账户名称:     [ %s ]
                            对方转账金额:     [ %.2f ]
                            手续费:          [ %.2f ]

                           \033[31;1m 是否确定?  y/N \n>>\033[0m """%(inp_user,transfer_username,inp,inp*0.05)).strip()
                        if transfer_verify == 'y' or transfer_verify == 'Y':
                            if float(inp) <= avalilable/2 and int(inp) > 0:
                                cost = inp * 0.05
                                avalilable = avalilable - inp - cost  #减自己账户信息
                                log.atm_log(user,time.localtime(),'info','信用卡账户: [%s]  转账: [%.2f] 元  手续费[ %.2f ] 元'%(user,inp,cost))
                                user_manager.ATM_USER_INFO[user]['available'] = avalilable

                                curr_time = shop_mall.curr_datetime()  #取出账单日期
                                if user_manager.ATM_USER_INFO[user]['record'].get(curr_time,None):
                                    if user_manager.ATM_USER_INFO[user]['record'].get(curr_time).get('total_debt') and \
                                                    user_manager.ATM_USER_INFO[user]['record'].get(curr_time).get('total_debt') >= 0:
                                        user_manager.ATM_USER_INFO[user]['record'][curr_time]['total_debt'] += (inp + cost) #账单欠款金额增加
                                    else:
                                        user_manager.ATM_USER_INFO[user]['record'].setdefault(curr_time,{'total_debt': inp+cost})
                                else:
                                    user_manager.ATM_USER_INFO[user]['record'].setdefault(curr_time,{'total_debt': inp+cost})


                                transfer_user = user_manager.ATM_USER_INFO[inp_user]  #对方账户加金额
                                transfer_avalilable = show_user(inp_user,'available')   #对方可用额度

                                transfer_avalilable += inp   #加金额
                                user_manager.ATM_USER_INFO[inp_user]['available'] = transfer_avalilable

                                log.atm_log(inp_user,time.localtime(),'info','信用卡账户: [%s]  收到转账: [%.2f] 元  手续费[ %.2f ] 元'%(inp_user,inp,0))
                                json.dump(user_manager.ATM_USER_INFO,open(user_manager.ATM_USERDB,'w'))  #持久化到文件

                                print('正在转账,请不要离开操作台...')
                                time.sleep(2)
                                if input('\033[31;1m 成功转账: [%.2f] 元  手续费[ %.2f ] 元\033[0m'%(inp,cost)):pass
                            else:
                                print('\033[31;1m账户可用额度不够!\033[0m')

                                return False
                    else:
                        print('\033[31;1m输入的金额不合法!\033[0m')
                        return False


def repayment(user):
    '''
    用户还款函数
    :return:
    '''
    cost = show_bill(user)
    if cost:
        cost = float(cost)
    else:
        cost = 0
    bill_month = input('请输入你要还款的账单日期, 如: 2016-5-22\n>>').strip()
    if bill_month and user_manager.ATM_USER_INFO[user]['record'].get(bill_month):
        bill = user_manager.ATM_USER_INFO[user]['record'].get(bill_month).get('total_debt',0)
        repayment_money = user_manager.ATM_USER_INFO[user]['record'].get(bill_month).get('repayment',0)
        if repayment_money >= bill + cost:  #如果已还金额大于用户账单金额,则不让其还款
            if input('\033[31;1m账单总额: [ %.2f ], 已还金额: [%.2f] 已还清当期[ %s ]账单!\033[0m'%(bill,repayment_money,bill_month)):pass
            return False
        else:
            inp_money = input('[ %s ] 账单总额: [ %.2f ], 已还金额: [%.2f], 还差 [ %.2f ]可以还清当期账单\n请输入你要还款的金额 >>'%(bill_month,bill,repayment_money,bill+cost-repayment_money)).strip()
            if inp_money and inp_money >= '0':
                inp_money = float(inp_money)
                if repayment_money + inp_money >= bill + cost:

                    repayment = user_manager.ATM_USER_INFO[user]['record'][bill_month].get('repayment',0) #+= inp_money    #还款金额赋值为还款后的金额
                    repayment += inp_money
                    user_manager.ATM_USER_INFO[user]['record'][bill_month]['repayment'] = repayment

                    del user_manager.ATM_USER_INFO[user]['record'][bill_month]  #还清账单之后,删除月份账单,这块在字典里真的很难判断多个账单,本想实现类似于招行信用卡那种,还完账单 \
                                                                                #之后显示账单已还清,但是还能查看上期账单多少. 所以没办法,删除了这个功能,还完款之后直接删掉账单

                    user_manager.ATM_USER_INFO[user]['available'] += inp_money



                    json.dump(user_manager.ATM_USER_INFO,open(user_manager.ATM_USERDB,'w'))
                    log.atm_log(user,time.localtime(),'info','信用卡账户: [%s]  还款: [%.2f] 元  逾期手续费[ %.2f ] 元, 账单金额: [ %.2f ], [ %s ]账单已还清'%(user,inp_money,cost,bill,bill_month))

                    print('正在还款,请稍等...')
                    time.sleep(2)
                    print('\033[31;1m 已成功还清[ %s ]账单\033[0m' %bill_month)

                else:
                    # repayment_money +=
                    if user_manager.ATM_USER_INFO[user]['record'][bill_month].get('repayment'):
                        user_manager.ATM_USER_INFO[user]['record'][bill_month]['repayment'] += inp_money  #还款金额赋值为还款后的金额
                    else:
                        user_manager.ATM_USER_INFO[user]['record'][bill_month]['repayment'] = inp_money
                    user_manager.ATM_USER_INFO[user]['available'] += inp_money  #增加可用额度
                    print('正在还款,请稍等...')
                    time.sleep(2)
                    print('\033[31;1m账单未还清,逾期会有手续费! 已还金额 [ %.2f ], 账单金额: [ %.2f ] \033[0m'%(inp_money,bill))
                    json.dump(user_manager.ATM_USER_INFO,open(user_manager.ATM_USERDB,'w'))  #持久化到文件
                    log.atm_log(user,time.localtime(),'info','信用卡账户: [%s]  还款: [%.2f] 元  逾期手续费[ %.2f ] 元'%(user,inp_money,cost))

    else:
        print('\033[31;1m您输入的账单不存在!')


def show_debt(user):
    '''
    查询欠款函数
    :return:
    '''
    available = show_user(user,'available')
    limit = show_user(user,'limit')
    username = show_user(user,'user')  #账户名
    registry_date = show_user(user,'registry_date')
    expire_date = show_user(user,'expire_date')
    debt = float(available) - float(limit)
    if debt > 0:
        debt = -debt
        # debt = float(debt)
    elif float(debt) == 0:
        debt = 0
    else:
        debt = abs(debt)

    #freeze = '可用' if not user_manager.ATM_USER_INFO[user].get('freeze',False) else '已冻结'

    print('''\033[34;1m
                您的账户欠款信息:
{}
            账    号:     [{}]
            姓    名:     [{}]
            当前欠款:      [{:.2f}]
{}
        \033[0m'''.format('#'*60,user,username,debt,'#'*60))
    if input('按下回车键,继续...'):pass


def show_user_detail(user):
    '''
    查询ATM账户信息函数
    :return:
    '''
    available = show_user(user,'available')
    limit = show_user(user,'limit')
    username = show_user(user,'user')  #账户名
    registry_date = show_user(user,'registry_date')
    expire_date = show_user(user,'expire_date')
    debt = float(available) - float(limit)
    if debt > 0:
        debt = -debt
    elif int(debt) == 0:
        debt = 0
    else:
        debt = abs(debt)
    freeze = '可用' if not user_manager.ATM_USER_INFO[user].get('freeze',False) else '已冻结'

    print('''\033[34;1m
                您的账户信息:
{}
            账    号:     [{}]
            姓    名:      [{}]
            信用额度:      [{}]
            可用额度:      [{}]
            取现额度:      [{}]
            注册日期:      [{}]
            过期日期:      [{}]
            当前欠款:      [{}]
            用户状态:      [{}]
{}
        \033[0m'''.format('#'*60,user,username,limit,available,int(available/2),registry_date,
                   expire_date,debt,freeze,'#'*60))
    if input('按下回车键,继续...'):pass


def main():
    '''
    主程序,主要用于普通用户登录后的操作
    :return:
    '''
    result = user_manager.atm_login()
    if result:
        flag = False
        while True:
            menu.show_atm(result[0])
            inp = input('请选择您要进行的操作序列:\n>>').strip()
            if inp == '1':   #提现
                draw_cash()
            elif inp == '2': #查询账单
                show_bill(user_manager.ATM_USER_STATUS['username'])
            elif inp == '3':  #查询欠款
                show_debt(user_manager.ATM_USER_STATUS['username'])
            elif inp == '4':  #转账
                transfer()
            elif inp == '5':  #现金还款
                repayment(user_manager.ATM_USER_STATUS['username'])
            elif inp == '6':  #查看账户详细信息
                show_user_detail(user_manager.ATM_USER_STATUS['username'])
            elif inp == '7':  #帮助信息
                show_help()
            elif inp == '8':  #退出程序
                print('Bye!')
                break
            else:
                print('\033[31;1m非法操作!\033[0m')
                continue


def reset_limit():
    '''
    调整用户额度函数,由ATM管理员调用
    :return: 成功为True, 失败为False
    '''
    user = input('请输入要调整额度的用户: ').strip()
    if user:
        if user not in user_manager.ATM_USER_INFO.keys():
            print('用户[ %s ]不存在!')
            return False
        else:
            print('[ %s ]用户,当前的额度为 [ %.2f ]'%(user,float(user_manager.ATM_USER_INFO[user].get('limit'))))
            inp_limit = input('请输入调整后的额度: ').strip()
            if int(inp_limit) <= 0 or not inp_limit:
                print('输入的金额不合法!')
                return False
            else:
                if float(inp_limit) < float(user_manager.ATM_USER_INFO[user]['limit']):
                    inp_diff = float(user_manager.ATM_USER_INFO[user]['limit']) - float(inp_limit)  #差值
                    if float(user_manager.ATM_USER_INFO[user]['available']) >= float(inp_diff):
                        user_manager.ATM_USER_INFO[user]['available'] -= float(inp_diff)
                    else:
                        print('\033[31;1m不能调整额度到此值,错误!\033[0m')
                        return False
                else:
                    inp_diff = float(inp_limit) - float(user_manager.ATM_USER_INFO[user]['limit'])   #差值
                    user_manager.ATM_USER_INFO[user]['available'] += float(inp_diff)

                user_manager.ATM_USER_INFO[user]['limit'] = float(inp_limit)

                json.dump(user_manager.ATM_USER_INFO,open(user_manager.ATM_USERDB,'w'))   #持久化到文件
                log.atm_log(user,time.localtime(),'info','信用卡账户: [%s]  调整额度: [%.2f]   调整后的额度: [ %.2f ]  操作员: [ %s ]' \
                            %(user,float(inp_limit),float(inp_limit),user_manager.ATM_ADMIN_STATUS['username']))   #打印日志
                print('\033[31;1m信用卡账户: [%s]额度调整成功, 调整后的额度: [ %.2f ]\033[0m'%(user,float(inp_limit)))
                return True


def freeze_user():
    '''
    冻结用户函数,由ATM管理员调用
    :return: 成功为True, 失败为False
    '''
    user = input('请输入要冻结的账号: ').strip()
    if user:
        if user not in user_manager.ATM_USER_INFO.keys():
            print('用户[ %s ]不存在!')
            return False
        else:
            freeze_status = '可用' if not user_manager.ATM_USER_INFO[user].get('freeze') else '已冻结'
            if freeze_status == '可用':
                print('[ %s ]用户,当前的状态为 [ %s ]'%(user,freeze_status))
                inp_limit = input('\033[31;1m确定要冻结用户[ %s ]吗? y/n:'%user).strip()
                if inp_limit == 'y' or inp_limit == 'Y':
                    user_manager.ATM_USER_INFO[user]['freeze'] = True
                    json.dump(user_manager.ATM_USER_INFO,open(user_manager.ATM_USERDB,'w'))   #持久化到文件
                    log.atm_log(user,time.localtime(),'info','信用卡账户: [%s]  已被冻结   操作员: [ %s ]' \
                                %(user,user_manager.ATM_ADMIN_STATUS['username']))   #打印日志
                    log.logger_atm.info('信用卡账户: [%s]  已被冻结   操作员: [ %s ]'%(user,user_manager.ATM_ADMIN_STATUS['username']))

                    print('\033[31;1m信用卡账户: [%s]已被成功冻结!\033[0m'%(user))
                    return True
                elif inp_limit == 'n' or inp_limit == 'N':
                    print('已放弃操作!')
                    return False
            else:
                print('\033[31;1m 信用卡账户[ %s ]已经是冻结状态!\033[0m'%user)
                return False


def unfreeze_user():
    '''
    解冻函数,由ATM管理员调用
    :return: 成功为True, 失败为False
    '''
    user = input('请输入要解冻的账号: ').strip()
    if user:
        if user not in user_manager.ATM_USER_INFO.keys():
            print('用户[ %s ]不存在!')
            return False
        else:
            freeze_status = '已冻结' if user_manager.ATM_USER_INFO[user].get('freeze') else '可用'
            if freeze_status == '已冻结':
                print('[ %s ]用户,当前的状态为 [ %s ]'%(user,freeze_status))
                inp_limit = input('\033[31;1m确定要解冻用户[ %s ]吗? y/n:'%user).strip()
                if inp_limit == 'y' or inp_limit == 'Y':
                    user_manager.ATM_USER_INFO[user]['freeze'] = False
                    json.dump(user_manager.ATM_USER_INFO,open(user_manager.ATM_USERDB,'w'))   #持久化到文件
                    log.atm_log(user,time.localtime(),'info','信用卡账户: [%s]  被成功解冻   操作员: [ %s ]' \
                                %(user,user_manager.ATM_ADMIN_STATUS['username']))   #打印日志
                    log.logger_atm.info('信用卡账户: [%s]  被成功解冻   操作员: [ %s ]'%(user,user_manager.ATM_ADMIN_STATUS['username']))

                    print('\033[31;1m信用卡账户: [%s]已被成功解冻!\033[0m'%(user))
                    return True
                elif inp_limit == 'n' or inp_limit == 'N':
                    print('已放弃操作!')
                    return False
            else:
                print('\033[31;1m 信用卡账户[ %s ]已经是可用状态!\033[0m'%user)
                return False


def unlock_user():
    '''
    解锁用户函数,主要是ATM管理员使用
    :return: 成功返回True,否则为False
    '''
    user_list = []
    flag = False
    user_input_name = input('请输入要解锁的用户名:').strip()
    if user_input_name:
        with open(user_manager.ATM_LOCK,'r') as f,open(user_manager.ATM_LOCK_NEW,'w+') as f1:
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
        os.rename(user_manager.ATM_LOCK_NEW,user_manager.ATM_LOCK)
        log.logger_shop.info('管理员成功解锁用户 %s '%user_input_name)
        return True
    if not flag:
        print('\033[31;1m用户名[ %s ]不在黑名单列表中!\033[0m'%user_input_name)
        return False



def admin_inp_menu():
    '''
    ATM 管理员选择操作函数
    :return:
    '''
    while True:
        menu.show_atm_admin()
        inp = input('请选择菜单\n >>').strip()
        if inp == '1': #添加账户
            atm_add_user()
        elif inp == '2':  #调整额度
            reset_limit()
        elif inp == '3':  #冻结账户
            freeze_user()
        elif inp == '4':  #解冻账户
            unfreeze_user()
        elif inp == '5':  #解锁账户
            unlock_user()
        elif inp == '6':  #退出后台
            break
        else:
            print('\033[31;1m非法输入!\033[0m')


def random_num():
    '''
    随机生成卡号1
    :return: 成功后return一个卡号
    '''
    card_num = ['6','2','2','2','0','2',]
    for i in range(3):
        num = random.randrange(0,9)
        card_num.append(str(num))
    result = "".join(card_num)

    if result not in user_manager.ATM_USER_INFO.keys():
        return result
    else:
        card_num = ['6','2','2','2','0',]
        for i in range(3):
            num = random.randrange(0,9)
            card_num.append(str(num))
        result = "".join(card_num)
        if result not in user_manager.ATM_USER_INFO.keys():
            return result


def atm_add_user():
    flag = False
    Count = 0
    while not flag:
        username = input('输入用户全名:\033[31;1m(必填项)\033[0m  ').strip()
        if not username:
            print('您输入的用户名不合法, 用户名不允许为空, 谢谢.')
            continue
        else:
            Count += 1
        password = input('来一个牛逼一点的密码 :\033[31;1m(必填项)\033[0m  ').strip()
        password_verify = input('重复一遍你牛逼的密码:\033[31;1m(必填项)\033[0m  ').strip()
        if password != password_verify:
            print('\033[31;1m你输入的两次牛逼的密码不一致!\033[0m')
            continue
        else:
            password = user_manager.md5(password)
            Count += 1

        if not password or not password_verify:
            continue
        else:
            Count += 1

        user_limit = input('请输入用户信用额度:').strip()
        if user_limit.isdigit() and int(user_limit) > 0:
            user_limit = float(user_limit)
            Count += 1
        else:
            print('额度输入不合法!')
            continue
        if Count >= 4:
            break

    card_num = random_num()  #随机生成卡号
    if card_num:
        registry_date = datetime.date.isoformat(datetime.datetime.now())
        year = time.localtime().tm_year
        month = time.localtime().tm_mon
        days = time.localtime().tm_mday
        expire_date = '%d-%d-%d' %(year+5,month,days)

        user_manager.ATM_USER_INFO[card_num]={
            "username":card_num,
            "user":username,
            "password":password,
            "limit":user_limit,
            "available":user_limit,
            "registry_date":registry_date,
            "expire_date":expire_date,
            "record":[]
        }

        json.dump(user_manager.ATM_USER_INFO,open(user_manager.ATM_USERDB,'w'))

        print('\033[31;1m用户添加成功,请牢记您的卡号和密码, 卡号:[ %s ], 用户名 [ %s ]\033[0m'%(card_num,username))

        log.logger_atm.info('%s用户添加成功,操作员[ %s ]' %(username,user_manager.ATM_ADMIN_STATUS['username']))
        return True


def run():
    while True:
        menu.show_atm_welcome()
        inp = input('请选择操作序列 \n>>')
        if inp == '2':    #用户登录
            main()
        elif inp == '3':  #帮助信息
            show_help()
        elif inp == '4':  #退出程序
            break
        elif inp == '1':  #管理后台
            result = user_manager.atm_admin_login()
            if result:
                admin_inp_menu()
        else:
            print('\033[31;1m非法输入!\033[0m')

