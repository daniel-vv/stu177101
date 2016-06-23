#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import os,sys,time,json,pickle,datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import user_manager
from core import commodity_list
from core import menu
from core import log
from conf import setting


COMMODITY_LIST = commodity_list.commodity_list      #加载商品字典
USERDB = os.path.join(setting.DBDIR,'shop_user.db')  #用户购买宝贝记录数据库文件,每个用户一个文件,用于持久化用户购买到的商品记录
BINDING_CARD_DB = os.path.join(setting.DBDIR,'binding_card.db')
ATM_USER_STATUS = {'user_status':False,'username':False}  #全局变量,用于判断用户是否登录了ATM信用卡账户
BINDING_CARD_SHOP_STATUS = json.load(open(BINDING_CARD_DB,'r'))   #绑定用户卡全局变量
user_shopp_car = []   #用户购物车
user_shopp = '{}       {}       {}      {}      {}'  #format格式化输出
CURR_DATE = datetime.date.isoformat(datetime.datetime.now())


def curr_datetime():
    '''
    返回当前日期账单时间函数
    :return: return一个日志值,如2016-05-22为5月份账单日期key
    '''
    year = time.localtime().tm_year
    month = time.localtime().tm_mon
    days = time.localtime().tm_mday

    if days >= 23:
        days = 22
        curr_date = '%d-%d-%d'%(year,month+1,22)
        return curr_date
    else:
        days = 22
        curr_date = '%d-%d-%d'%(year,month,22)
        return curr_date


def check_user_shopp(user):
    '''
    检查用户购物车函数
    :param user: 接受传入形参,基于用户名判断!
    :return: 返回用户的购物车总价
    '''
    if len(user_shopp_car) > 0:  #如果购物车不为空,进行下面操作
        print('您的购物车'.center(70))
        print('#'*70)
        print('\033[34;1m 序列        宝贝名        数量           小计          购买时间\033[0m')
        product_index = 1
        user_consume = 0  #定义一个值为0的用户消费金额的初始值,用于下面累加用户此次总共消费总金额
        for value in user_shopp_car:
            print(user_shopp.format(product_index,value[0],value[1],value[2],value[3]))
            product_index += 1
            user_consume += value[2]  #自增用户消费金额
        print('#'*70)
        if input('\033[34;1m偶,亲爱的用户[ %s ],您购物车商品总价: [ %.2f ]元, 回车继续... \033[0m'%(user,user_consume)):pass
        return user_consume
    else:   #如果购物车为空,提示用户购物车为空,并返回商品列表
        print('-'*50)
        print('抱歉,你还未购买任何宝贝,购物车里空到不行不行的~')
        print('-'*50)
        return False


def user_history(user):
    '''
    查看用户上一次购买记录函数,这块没做到记录用户所有的记录,只能保存用户最后一次的信息
    :param user: 接收用户传入形参,用户名
    :return:
    '''
    user_shop_file = os.path.join(setting.DBDIR,user)
    if os.path.exists(user_shop_file):
        result = pickle.load(open(user_shop_file,'rb'))
        # print(result)
        print('您的购物历史记录'.center(70))
        print('#'*70)
        print('\033[34;1m 序列        宝贝名        数量           小计          购买时间\033[0m')
        product_index = 1
        user_consume = 0  #定义一个值为0的用户消费金额的初始值,用于下面累加用户此次总共消费总金额
        for value in result:
            print(user_shopp.format(product_index,value[0],value[1],value[2],value[3]))
            product_index += 1
            user_consume += value[2]  #自增用户消费金额
        print('#'*70)
        if input('\033[34;1m啊哈,亲爱的VIP用户[ %s ],您在本商城共消费: [ %.2f ]元 ,回车继续...\033[0m'%(user,user_consume)):pass
    else:   #如果购物车为空,提示用户购物车为空,并返回商品列表
        print('-'*50)
        print('抱歉,你还未购买过任何宝贝,购买记录里空到不行不行的~')
        print('-'*50)


def del_shop():
    '''
    用户删除购物车商品函数
    :return:
    '''
    if user_shopp_car:
        '''
        for id,value in enumerate(user_shopp_car):
            print(id,value)
        '''
        user_consume = 0  #定义一个值为0的用户消费金额的初始值,用于下面累加用户此次总共消费总金额
        product_index = 0
        print('您的购物车信息'.center(70))
        print('\033[34;1m 序列        宝贝名        数量           小计          添加时间\033[0m')
        for value in user_shopp_car:
            print(user_shopp.format(product_index,value[0],value[1],value[2],value[3]))
            product_index += 1
            user_consume += value[2]  #自增用户消费金额
        print('#'*70)
        inp = input('\033[34;1m亲爱的用户[ %s ],您购物车所选商品总价: [ %s ]元, 请输入你要删除的商品序列:\n>>\033[0m').strip()
        if inp.isdigit() and int(inp) <= len(user_shopp_car):
            del_pro = user_shopp_car.pop(int(inp))
            print('\033[31;1m%s 删除成功\033[0m'%del_pro[0])
    else:
        print('购物车是空的啦,如何删除!')


    #if input('\033[34;1m亲爱的用户[ %s ],您购物车所选商品总价: [ %s ]元, \033[0m'%(user,user_consume)):pass


def save_user_shop(user):
    '''
    保存用户购物车信息模块,持久化到文件,一个用户一个文件,保存在db目录下的以用户名为名字的文件
    :param user: 接受用户传入形参,用户名,以此作为保存用户信息
    :return: True 保存成功
    '''
    user_shop_file = os.path.join(setting.DBDIR,user)
    if not os.path.exists(user_shop_file):
        if user_shopp_car:
            pickle.dump(user_shopp_car,open(user_shop_file,'wb'))
            user_shopp_car.clear()
            return True
        else:
            return False
    else:
        if user_shopp_car:
            result = pickle.load(open(user_shop_file,'rb'))
            for i in user_shopp_car:
                result.append(i)
            pickle.dump(result,open(user_shop_file,'wb'))
            user_shopp_car.clear()
            return True
        else:
            return False


def shop_pay(user):
    '''
    用户支付模块
    :param user:传入形参商场用户身份
    :return:
    '''
    if not ATM_USER_STATUS['user_status']:
        # print(ATM_USER_STATUS)
        # atm_user,user_salary,available_money = user_manager.atm_login()
        result = user_manager.atm_login()
        if result:  #如果认证ATM成功,取出用户atm用户名,信用卡额度,可用额度
            atm_user,user_salary,available_money = result[0],result[1],result[2]
            ATM_USER_STATUS['username'] = atm_user
            ATM_USER_STATUS['user_status'] = True
            #user_manager.ATM_USER_INFO[atm_user]['user_status'] = True  #并更改全局变量,待后面程序判定
            #user_manager.ATM_USER_INFO[atm_user]['available'] = available_money  #用户可用额度
        else:
            return False
        price = check_user_shopp(user)
        if user_shopp_car:
            inp = input('\033[31;1m是否要支付? y/Y\033[0m').strip()
            if inp == 'y' or inp == 'Y':
                # print(price,user_salary,available_money)
                user_salary = float(user_salary)
                price = float(price)
                if price < user_manager.ATM_USER_INFO[atm_user]['available']:
                    user_manager.ATM_USER_INFO[atm_user]['available'] -= price  #可用额度减去消费金额

                    curr_time = curr_datetime()  #取出账单日期
                    if user_manager.ATM_USER_INFO[atm_user]['record'].get(curr_time,None):
                        if user_manager.ATM_USER_INFO[atm_user]['record'].get(curr_time).get('total_debt') and \
                                        user_manager.ATM_USER_INFO[atm_user]['record'].get(curr_time).get('total_debt') >= 0:
                            user_manager.ATM_USER_INFO[atm_user]['record'][curr_time]['total_debt'] += price #账单欠款金额增加
                        else:
                            user_manager.ATM_USER_INFO[atm_user]['record'].setdefault(curr_time,{'total_debt': price})
                    else:
                        user_manager.ATM_USER_INFO[atm_user]['record'].setdefault(curr_time,{'total_debt': price})

                    log.atm_log(atm_user,time.localtime(),'info','信用账户: %s  商城消费: %.2f'%(atm_user,price))
                    save_user_shop(user)
                    json.dump(user_manager.ATM_USER_INFO,open(user_manager.ATM_USERDB,'w'))  #持久化到文件

                    if input('\033[31;1m支付成功!本次消费[ %.2f ]元,  当前可用额度为: [ %.2f ]元\033[0m'\
                                     %(price,user_manager.ATM_USER_INFO[atm_user]['available'])):pass

                    return True
                else:
                    inp = input('\033[31;1m 抱歉, 用于额度不足, 无法支付所购买商品! 是否要删除购物车某商品? \n y/Y>>\033[0m').strip()
                    if inp == 'y' or inp == 'Y':
                        del_shop()
                    else:
                        print('无效操作!')
        else:
            print('购物车里空的!')
            return False
    else:
        # print(ATM_USER_STATUS)
        # print(user_manager.ATM_USER_INFO)
        user_salary = user_manager.ATM_USER_INFO[ATM_USER_STATUS['username']]['limit']  #用户额度
        # user_available = user_manager.ATM_USER_INFO[ATM_USER_STATUS['username']]['available'] #用户可用额度
        atm_user = ATM_USER_STATUS.get('username')
        print('\033[31;1m您已经登录ATM机[ %s ]用户\033[0m'%atm_user)
        price = check_user_shopp(user)
        if user_shopp_car:
            inp = input('\033[31;1m是否要支付? y/Y\033[0m').strip()
            if inp == 'y' or inp == 'Y':
                # print(price,user_salary,user_manager.ATM_USER_INFO[ATM_USER_STATUS['username']]['available'])
                # user_available = int(user_available)
                price = float(price)
                if price < user_manager.ATM_USER_INFO[atm_user]['available']:
                    user_manager.ATM_USER_INFO[ATM_USER_STATUS['username']]['available'] -= price

                    curr_time = curr_datetime()  #取出账单日期

                    if user_manager.ATM_USER_INFO[atm_user]['record'].get(curr_time,None):
                        if user_manager.ATM_USER_INFO[atm_user]['record'].get(curr_time).get('total_debt') and \
                                        user_manager.ATM_USER_INFO[atm_user]['record'].get(curr_time).get('total_debt') >= 0:
                            user_manager.ATM_USER_INFO[atm_user]['record'][curr_time]['total_debt'] += price #账单欠款金额增加
                        else:
                            user_manager.ATM_USER_INFO[atm_user]['record'].setdefault(curr_time,{'total_debt': price})
                    else:
                        user_manager.ATM_USER_INFO[atm_user]['record'].setdefault(curr_time,{'total_debt': price})

                    log.atm_log(atm_user,time.localtime(),'info','信用账户: %s  商城消费: %.2f'%(atm_user,price))
                    save_user_shop(user)
                    json.dump(user_manager.ATM_USER_INFO,open(user_manager.ATM_USERDB,'w'))  #持久化到文件
                    if input('\033[31;1m支付成功!本次消费[ %.2f ]元,  当前可用额度为: [ %.2f ]元\033[0m'\
                                     %(price,user_manager.ATM_USER_INFO[atm_user]['available'])):pass
                    # print(user_manager.ATM_USER_INFO)
                    return True
                else:
                    inp = input('\033[31;1m 抱歉, 用于额度不足, 无法支付所购买商品! 是否要删除购物车某商品? \n y/Y>>\033[0m').strip()
                    if inp == 'y' or inp == 'Y':
                        del_shop()
                    else:
                        print('无效操作!')
        else:
            print('购物车里是空的!')
            return False


def binding_card(user):
    '''
    绑定用户商城和信用卡模块
    :return:
    '''
    if BINDING_CARD_SHOP_STATUS[user].get('bind_user'):   #进来先抓取值,看用户有无绑定信用卡账户
        ATM_USER_STATUS['user_status'] = True   #更改支付接口调用字典值
        ATM_USER_STATUS['username'] = BINDING_CARD_SHOP_STATUS[user].get('bind_user') #更改支付调用接口用户值
        print('你已经绑定了信用卡账号[ %s ]!'%BINDING_CARD_SHOP_STATUS[user].get('bind_user'))
        inp = input('\033[31;1m 是否需要删除绑定的信用卡账户, y/n').strip()
        if inp == 'y' or inp == 'Y':
            ATM_USER_STATUS['user_status'] = False   #更改支付接口调用字典值
            ATM_USER_STATUS['username'] = False #更改支付调用接口用户值
            log.logger_atm.info('商城用户 %s 与信用卡账户  %s 已解除绑定!'%(user,BINDING_CARD_SHOP_STATUS[user]['bind_user']))
            BINDING_CARD_SHOP_STATUS[user]['bind_user'] = False
            BINDING_CARD_SHOP_STATUS[user]['bind_card'] = False
            json.dump(BINDING_CARD_SHOP_STATUS,open(BINDING_CARD_DB,'w'))
            print('\033[31;1m您绑定的信用卡账户已成功删除! \033[0m')
    else:
        print('\033[31;1m下面操作将绑定用户信用卡账户到商城账户中!\033[0m')
        result = user_manager.atm_login()
        if result:
            ATM_USER_STATUS['user_status'] = True   #更改支付接口调用字典值
            ATM_USER_STATUS['username'] = result[0] #更改支付调用接口用户值
            BINDING_CARD_SHOP_STATUS[user]['bind_user'] = result[0]
            BINDING_CARD_SHOP_STATUS[user]['bind_card'] = True
            json.dump(BINDING_CARD_SHOP_STATUS,open(BINDING_CARD_DB,'w'))
            log.logger_atm.info('商城用户[ %s ]绑定信用卡账户[ %s ]成功!'%(user,BINDING_CARD_SHOP_STATUS[user]['bind_user']))
            if input('\033[32;1m操作成功,您绑定了信用卡账号[ %s ] 到您的商城用户中,谢谢使用!\033[0m'%result[0]):pass


def shop_help():
    '''
    帮助模块
    :return:
    '''
    print(' HELP '.center(100,'@'))
    print('''\033[35;1m
            1. 进入商城
            	进入商城，选择商品和购买数量,可完成支付,检查购物车等功能
            2. 查看购买记录
            	支持查看用户购买商品历史记录
            3. 立即支付
            	支付接口需要登录ATM用户,再次界面如果用户购物车有商品也可完成支付.如果用户
            	支付时账户可用额度不够, 调用删除购物车程序接口,可以删除某商品完成支付.
            4. 绑定信用卡
            	用户可以绑定自己的信用卡账号到商城用户,方便用户购买商品,不用再每次登陆都要登陆信用卡账户
            5. 帮助信息
            	获取购物商城帮助信息
            6. 退出商城
            	退出购物商城返回到商城首页菜单,如果再次进入商城还需要认证.

    \033[0m''')
    print('@'*100)


def main():
    '''
    购物商城主模块,在此调用其他用户模块
    :return:
    '''
    user = user_manager.shop_login()    #调用登录商城函数
    flag = False
    flag2 = False
    if user:
        while True:
            menu.show_shop(user)  #调用商城菜单主界面
            inp = input('请选择一个操作序列 \n >>')
            if inp == '2':    #查询历史记录
                user_history(user)
            elif inp == '3':    #支付
                shop_pay(user)
            elif inp == '4':  #绑定信用卡
                binding_card(user)
            elif inp == '5':  #商城帮助信息
                shop_help()
            elif inp == '6': #退出购物商城
                print('Bye!')
                return False
            elif inp == '1':
                while True:
                    for id,keys in enumerate(COMMODITY_LIST.keys()):
                        print(id,keys)
                    User_id = input('\033[33;1m请选择您感兴趣的分类  Q/q(退出商城) C/c(检查购物车) B/b(返回)  p/P(支付) d/D(删除商品)\n>>\033[0m').strip()
                    if User_id == 'q' or User_id == 'Q':
                        print('欢迎下次再来 [ %s ], Bye!'%user)
                        # save_user_shop(user)
                        flag = True
                    elif User_id == 'c' or User_id == 'C':
                        check_user_shopp(user)
                    elif User_id == 'p' or User_id == 'Q':
                        shop_pay(user)
                    elif User_id == 'b' or User_id == 'B':
                        break
                    elif User_id == 'd' or User_id == 'D':
                        del_shop()
                    elif User_id.isdigit() and int(User_id) < len(COMMODITY_LIST.keys()): #用户如果输入的是列表中的序列
                        product = list(COMMODITY_LIST.keys())[int(User_id)]  #将字典转换为有序列表
                        while True:
                            for id2,keys2 in enumerate(COMMODITY_LIST[product].items()):  #显示三级菜单
                                print(id2,keys2)
                            User_id2 = input('\033[33;1m请选择您需要的宝贝序列,并添加到购物车中 B/b(返回) c/C(检查购物车) p/P(支付) d/D(删除商品)\n>>:\033[0m').strip()
                            if User_id2 == 'c' or User_id2 == 'C':
                                check_user_shopp(user)
                            elif User_id2 == 'b' or User_id2 == 'B':
                                break
                            elif User_id2 == 'p' or User_id2 == 'P':
                                shop_pay(user)
                            elif User_id2 == 'd' or User_id2 == 'D':  #删除购物车商品
                                del_shop()
                            elif User_id2.isdigit() and int(User_id2) < len(COMMODITY_LIST[product]):
                                product1 = list(COMMODITY_LIST[product].keys())[int(User_id2)]
                                price = float(COMMODITY_LIST[product][product1])  #取出商品价格
                                print('您选择了商品: \033[32;1m %s \033[0m , 宝贝价格(元):\033[32;1m %.2f \033[0m'%(product1,price)) #提示用户
                                product_num = input('请输入你要购买商品 \033[32;1m %s \033[0m 的数量: '%product1).strip() #提示用户购买数量
                                if product_num.isdigit() and product_num and int(product_num) != 0:
                                    price *= float(product_num)  #价格更新为单次商品数量的总和
                                    product_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())  #商品购买时间
                                    #添加用户选择商品到购物车列表中
                                    user_shopp_car.append([product1,product_num,price,product_time])
                                    print('恭喜您,成功购买商品:\033[32;1m %s \033[0m 数量: \033[32;1m%s \033[0m, 此次消费(元): \033[32;1m %.2f \033[0m' \
                                          %(product1,product_num,price))

                            else:
                                print('\033[31;1m输入不合法,请重试!\033[0m')
                                continue
                    else:
                        print('\033[31;1m输入不合法,请重试!\033[0m')
                    # if flag:break
            if flag:break


def shop_admin_login():
    '''
    商城管理员用户登录模块
    :return:
    '''
    user = user_manager.shop_admin_login()
    # user = 'admin'
    if user:
        flag = False
        while True:
            menu.show_shop_admin(user)
            inp = input('请选择操作序列 \n>>')
            if inp.isdigit() and inp == '1':
                user_manager.registry_user()
            elif inp.isdigit() and inp == '2':
                pass
            elif inp.isdigit() and inp == '3': #删除用户
                user_manager.del_user(user)
            elif inp.isdigit() and inp == '4':  #解锁用户
                user_manager.unlock_user()
            elif inp.isdigit() and inp == '5':  #退出程序
                break
            else:
                print('\033[31;1m输入不合法!\033[0m')


def run():
    '''
    调用接口函数
    :return:
    '''
    while True:
        menu.show_welcome()
        inp = input('请选择序列 \n>>')
        if inp == '2': #购物商城
            main()
        elif inp == '1': #进入商城管理员
            shop_admin_login()
        elif inp == '3':  #帮助信息
            menu.show_shop_help()
        elif inp == '4':  #退出程序
            break

