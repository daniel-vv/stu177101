#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)


def show_welcome():
    '''
    购物商城主菜单欢迎信息函数
    :return: 无
    '''
    print('欢迎来到这里,请选择操作菜单'.center(50))
    print('#'*60)
    print('''
                1. 管理员登录
                2. 购物商城
                3. 帮助
                4. 退出程序
    ''')
    print('#'*60)


def show_shop_admin(user):
    '''
    商城后台管理菜单
    :param user:
    :return:
    '''
    print('\033[32;1m[ {} ], 欢迎来到DBQ的商城管理后台,请选择操作菜单\033[0m'.center(50).format(user))
    print('\033[32;1m#\033[0m'*60)
    print('''\033[32;1m
                1. 添加用户
                2. 修改密码
                3. 删除用户
                4. 解锁用户
                5. 退出程序
    \033[0m''')
    print('\033[32;1m#\033[0m'*60)


def show_atm_welcome():
    '''
    atm程序主欢迎菜单
    :return:
    '''
    print('欢迎来到ATM系统,请选择操作菜单'.center(50))
    print('#'*60)
    print('''
                1. 管理后台
                2. 登录账户
                3. 帮助
                4. 退出程序
    ''')
    print('#'*60)


def show_atm_admin():
    '''
    atm管理后台菜单
    :return:
    '''
    print('\033[32;1m欢迎来到管理后台,请选择操作菜单\033[0m'.center(50))
    print('\033[32;1m#\033[0m'*60)
    print('''\033[32;1m
                1. 添加账户
                2. 调整额度
                3. 冻结账户
                4. 解冻账户
                5. 解锁用户
                6. 退出后台
    \033[0m''')
    print('\033[32;1m#\033[0m'*60)


def show_atm(user):
    '''
    ATM普通用户菜单
    :param user:
    :return:
    '''
    print('\033[32;1m尊敬的VIP客户[ %s ],欢迎来到ATM自动柜员机,请选择操作菜单\033[0m'.center(50)%user)
    print('#'*60)
    print('''
                1. 提取现金
                2. 查询账单
                3. 查询欠款
                4. 转账
                5. 现金还款
                6. 查询账户信息
                7. 帮助信息
                8. 退出ATM
    ''')
    print('#'*60)


def show_shop(user):
    '''
    商城欢迎菜单
    :param user:
    :return:
    '''
    print('\033[32;1m ~Bingo, 欢迎 [ %s ] 来到 DBQ 的百货店, 祝您购物愉快~ \033[0m'.center(70,'#')%user)
    print('#'*70)
    print('''
                1. 进入商城
                2. 查看购买历史
                3. 立即支付
                4. 绑定信用卡
                5. 帮助信息
                6. 退出商城
    ''')
    print('#'*70)


def show_shop_help():
    '''
    帮助模块
    :return:
    '''
    print(' HELP '.center(100,'@'))
    print('''\033[35;1m
                1. 管理员登录
                    进入商城管理后台, 可完成添加,删除,解锁,等用户管理操作
                2. 购物商城
                    普通用户登录商城用, 用户可选择喜欢的商品和数量
                3. 帮助
                    获取简单帮助信息
                4. 退出程序
                    退出主程序
    \033[0m''')
    print('@'*100)