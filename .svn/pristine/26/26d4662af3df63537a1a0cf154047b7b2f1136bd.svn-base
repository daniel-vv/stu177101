#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Author: DBQ
Blog: http://www.cnblogs.com/dubq/articles/5474785.html
Github: https://github.com/daniel-vv/ops
'''

import time  #导入time模块,用于在下面退出时,休眠1秒
dic = {       #定义一个字典,其中嵌套字典和列表,用于存储三级菜单内容
    '华北':{
        '北京市':['朝阳区','海淀区','丰台区'],
        '天津市':['和平区','河西区','河东区',],
        '山西省':['太原市','运城市','大同市',]
    },
    '东北':{
        '黑龙江省':['哈尔滨市',],
        '吉林省':['吉林市','长春市'],
        '辽宁省':['沈阳市','大连市','铁岭市'],
    },
    '华东':{
        '山东省':['青岛市','济南市','日照市'],
        '江苏省':['南京市','常州市','苏州市'],
        '上海市':['虹口区','黄埔区','徐汇区'],
    },
     '华南':{
        '广东省':{
            '广州市':['','',''],
            '东莞市':['','',''],
            '珠海市':['','','']
        },
        '广西省':{
            '南宁市':['','',''],
            '桂林市':['','',''],
            '柳州市':['','','']
        },
        '香港特别行政区':{
            '中西区':['','',''],
            '湾仔区':['','',''],
            '九龙城区':['','',''],
            '深水埗区':['','','']
        }
    }
}


Welcome = '欢迎来到天朝'   #定义欢迎信息,用于下方字符串格式化


area_check = ('0','1','2','3')  #定义一个元组,用于检测用户输入序列号是否在合法范围内;
Flag = False   #定义标志位,用于进入循环

while not Flag: #进入循环体
    print('%s'% Welcome.center(30,'>'))
    for id,china in enumerate(dic.keys()):    #循环字典keys,并且用enumerate方法列出索引序号,而后打印出来,供用户选择
        print(id,china)
    print('#'*65)
    UserInput = input('请输入一个您感兴趣的一个区域序号:   退出(q/Q)   返回(b/B): ').strip()  #提示用户选择序列号
    print('#'*65)
    Num = UserInput
    if Num == 'q' or Num == 'Q':   #判断用户输入是否是退出?
        print('欢迎下次再来~,Bye')
        time.sleep(1)
        Flag = True                #将标志位置为True,用于退出整个循环
        #break
    elif Num == 'b' or Num == 'B': #如果顶级菜单用户输入回退,提示顶级菜单,重新进入循环
        print('已经最最顶层菜单了')
        continue
    elif Num in area_check:   #如果用户输入的是元组内的索引序列的话,进入下一层循环体
        Province = list(dic.keys())[int(Num)]  #进入循环体之前先将省字典转换为列表,不然无法进行索引
        while not Flag:   #循环进入第二级菜单:
            for ID,Provi in enumerate(dic[Province]):
                print(ID,Provi)
            print('#'*65)
            UserInput = input('请输入一个您感兴趣的城市编号:   退出(q/Q)   返回(b/B): ').strip()
            print('#'*65)
            Num = UserInput
            if Num == 'q' or Num == 'Q':
                print('欢迎下次再来~,Bye')
                time.sleep(1)
                Flag = True
            elif Num == 'b' or Num == 'B':
                break
            elif Num in area_check:
                City = list(dic[Province].keys())[int(Num)]  #将用户输入和字典转换为列表
                while not Flag:    #进入三级菜单
                    print('---> %s' % City)
                    for ID,city in enumerate(dic[Province][City]):  #循环,并使用enumerate打印出菜单和序列号,供用户选择
                        print(ID,city)
                    print('#'*65)
                    UserInput = input('请输入一个您感兴趣的一个区域序号:   退出(q/Q)   返回(b/B): ').strip()
                    print('#'*65)
                    if UserInput == 'q' or UserInput == 'Q':  #输入Q,标志位置为1
                        Flag = True
                        #break
                    elif UserInput == 'b' or UserInput == 'B': #输入B,break,返回到生一层循环
                        break
                    elif UserInput == '':   #判断用户输入是否为空,如果为空,则提示为空,进入下一次循环
                        print('输入为空')
                        continue
                    else:
                        print('已经到了最后一层啦,哈哈')
    if Flag:  #如果标志位为真,退出循环体
        break
