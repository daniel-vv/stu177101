#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import os
import commodity_list  #导入商城商品列表
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from conf import setting
import user_manager
from core import menu
import time
import json


COMMODITY_LIST = commodity_list.commodity_list
USERDB = os.path.join(setting.DBDIR,'shop_user.db')

user_shopp_car = {}
user_shopp = '{}       {}       {}      {}      {}'

def check_user_shopp(user):
    '''
    检查用户购物车函数
    :param user: 接受传入形参,基于用户名判断!
    :return:
    '''
    if len(user_shopp_car) > 0:  #如果购物车不为空,进行下面操作
        print('您的购物车'.center(70))
        print('#'*70)
        print('\033[34;1m 序列        宝贝名        数量           小计          购买时间\033[0m')
        product_index = 1
        user_consume = 0  #定义一个值为0的用户消费金额的初始值,用于下面累加用户此次总共消费总金额
        for value in user_shopp_car[user].keys():
            print(user_shopp.format(product_index,value,user_shopp_car[user][value][0],user_shopp_car[user][value][1],user_shopp_car[user][value][2]))
            product_index += 1
            user_consume += user_shopp_car[user][value][1]  #自增用户消费金额
        print('#'*70)
        print('\033[34;1m偶,亲爱的用户[ %s ],您购物车商品总价: [ %s ]元 \033[0m'%(user,user_consume))
    else:   #如果购物车为空,提示用户购物车为空,并返回商品列表
        print('-'*50)
        print('抱歉,你还未购买任何宝贝,购物车里空到不行不行的~')
        print('-'*50)

def shop_pay(user):
    user_manager.atm_login()


def save_user_shop(user):
    user_shop_file = os.path.join(setting.DBDIR,user)
    if not os.path.exists(user_shop_file):
        json.dump(user_shopp_car,open(user_shop_file,'w'))
    else:
        json.dump(user_shopp_car,open(user_shop_file,'w'))




def main():
    user = user_manager.shop_login()
    flag = False
    flag2 = False
    if user:
        while True:
            print('\033[32;1m ~Bingo, 欢迎 [ %s ] 来到 DBQ 的百货店,请选择您需要的宝贝以及数量,祝您购物愉快~ \033[0m'.center(70,'#')%user)
            for id,keys in enumerate(COMMODITY_LIST.keys()):
                print(id,keys)
            User_id = input('\033[33;1m请选择您感兴趣的分类  Q/q(退出程序) C/c(检查购物车)  p/P(支付)\n>>\033[0m').strip()
            if User_id == 'q' or User_id == 'Q':
                print('欢迎下次再来 [ %s ], Bye!'%user)
            elif User_id == 'c' or User_id == 'C':
                check_user_shopp(user)
            elif User_id == 'p' or User_id == 'Q':
                shop_pay(user)
            elif User_id.isdigit() and int(User_id) < len(COMMODITY_LIST.keys()): #用户如果输入的是列表中的序列
                product = list(COMMODITY_LIST.keys())[int(User_id)]  #将字典转换为有序列表
                while True:
                    for id2,keys2 in enumerate(COMMODITY_LIST[product].items()):  #显示三级菜单
                        print(id2,keys2)
                    User_id2 = input('\033[33;1m请选择您需要的宝贝序列,并添加到购物车中 Q/q(退出程序) B/b(返回) c/C(检查购物车) p/P(支付)\n>>:\033[0m').strip()
                    if User_id2.isdigit() and int(User_id2) < len(COMMODITY_LIST[product]):
                        product1 = list(COMMODITY_LIST[product].keys())[int(User_id2)]
                        price = int(COMMODITY_LIST[product][product1])  #取出商品价格
                        print('您选择了商品: \033[32;1m %s \033[0m , 宝贝价格(元):\033[32;1m %s \033[0m'%(product1,price)) #提示用户
                        product_num = input('请输入你要购买商品 \033[32;1m %s \033[0m 的数量: '%product1).strip() #提示用户购买数量
                        if product_num.isdigit() and product_num and int(product_num) != 0:
                            price *= int(product_num)  #价格更新为单次商品数量的总和
                            product_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())  #商品购买时间
                            if not user_shopp_car.get(user,None):  #用户如果不在购物车字典中,则直接添加
                                user_shopp_car[user] = {product1:[product_num,price,product_time]}
                            else:
                                user_shopp_car[user].setdefault(product1,[product_num,price,product_time,])
                                product_num += user_shopp_car[user][product1][0]
                                price += user_shopp_car[user][product1][1]

                                user_shopp_car[user][product1][0],user_shopp_car[user][product1][1],user_shopp_car[user][product1][2] = \
                                product_num,price,product_time
                            print('恭喜您,成功购买商品:\033[32;1m %s \033[0m 数量: \033[32;1m%s \033[0m, 此次消费(元): \033[32;1m %s \033[0m' \
                                  %(product1,product_num,price))
                    elif User_id2 == 'c' or User_id2 == 'C':
                        check_user_shopp(user)
                    elif User_id2 == 'q' or User_id2 == 'Q':
                        print('Bye!')
                        save_user_shop(user)
                        flag = True
                        break
                    elif User_id2 == 'b' or User_id2 == 'B':
                        break
                    else:
                        print('\033[31;1m输入不合法,请重试!\033[0m')
                        continue
            else:
                print('\033[31;1m输入不合法,请重试!\033[0m')

            if flag:break


main()
# for id,keys in enumerate(COMMODITY_LIST.keys()):
#     print(id,keys)



