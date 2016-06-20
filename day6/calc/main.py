#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

'''
Author: DBQ(Du Baoqiang)
Blog: http://www.cnblogs.com/dubq/p/5587738.html
Github: https://github.com/daniel-vv/stu177101
'''

import re,time

# s1 = '8*12+(6-(5*6-2)/77+2)*(3-7)+8'
#先定义运算表达式,编译成匹配模式,待下面程序里调用,运算符有: 加减, 乘除, 乘负, 除负, 还有武sir课上提到的匹配括号,先匹配括号里不包含括号的表达式
expr1 = re.compile(r'(-?\d+)(\.\d+)?[-+](-?\d+)(\.\d+)?')  #此表达式匹配 + -
expr2 = re.compile(r'(-?\d+)(\.\d+)?[*/](-?\d+)(\.\d+)?')  #此表达式匹配 * / 号
expr3 = re.compile(r'(-?\d+)(\.\d+)?\*-(-?\d+)(\.\d+)?')   #此表达式匹配 乘负数
expr4 = re.compile(r'(-?\d+)(\.\d+)?/-(-?\d+)(\.\d+)?')    #此表达式匹配 除负数
expr5 = re.compile(r'\([^()]*\)')                          #此表达式匹配以括号开头括号结尾,中间不含括号
expr6 = re.compile(r'[a-zA-Z`~!@#$%^&,?<>{}|]+')   #              #此表达式匹配用户输入的内容是否属于包含特殊字符
#expr6 = re.compile(r'[^\d+-\*/\(\)]+')
# number = '8*12+(6-(5*6-2)/77+2)*(3-7)+8'
# result = expr5.search(number).group()
# print(result)




def single_calc(number):
    '''
    定义一个匹配算式运算符的函数,主要用于处理输入的表达式
    :param number: 接受用户传入字符串的形参
    :return:  匹配后return匹配到的值返回给用户,来下一步处理
    '''
    if number.count('+') == 1:   #加号算式匹配,find下标,并且转换为str之后拼接起来
        return str(float(number[:number.find('+')]) + float(number[number.find('+') + 1:]))
    elif number[1:].count('-') == 1:  #减号算式匹配,从第一个索引位开始find,防止用户输入第一个就是负数的错误匹配
        return str(float(number[:number.find('-',1)]) - float(number[number.find('-',1) + 1:]))
    elif number.count('*') == 1:  #查找乘号
        return str(float(number[:number.find('*')]) * float(number[number.find('*') + 1:]))
    elif number.count('/') == 1:  #匹配除法
        return str(float(number[:number.find('/')]) / float(number[number.find('/') + 1:]))



def main_calc(number):
    '''
    计算模块, 这个模块里不匹配括号,只用来计算被处理过的算式
    :return: 如果没有表达式则返回False,否则按照匹配规则,递归处理
    '''
    # 如果没有匹配到 加, 乘 , 除并且 从第一个位置开始find减都为0 证明表达式不对,返回False
    if number.count('+') + number.count('*') + number.count('/') == 0 and number[1:].find('-') < 0:
         return number
    elif number.count('--') + number.count('+-') + number.count('*-') + number.count('/-') > 0:
        number = number.replace('--','+')  #如果没有负数,就负负为正
        number = number.replace('+-','-')  #加减为减
        if number.count('/-') > 0:  #处理除负数, 先计算结果,然后转换为负数
            number = number.replace(expr4.search(number).group(),'-'+expr4.search(number).group().replace('/-','*'))
            #return main_calc(number)  #使用递归函数调用自己
        if number.count('*-') > 0:  #处理乘负数, 使用re.search
            number = number.replace(expr3.search(number).group(),'-'+expr3.search(number).group().replace('*-','*'))

        return main_calc(number)  #使用递归函数调用自己

    elif number.count('*') + number.count('/') > 0:   #先处理乘除,必须先匹配乘除,按照数学优先级
        result = expr2.search(number).group()
        number = number.replace(result, single_calc(result))
        return main_calc(number)  #递归

    elif number.count('+') != 0 or number.count('-') != 0:   #再处理加减
        result = expr1.search(number).group()
        number = number.replace(result, single_calc(result))
        return main_calc(number)  #递归




def bracket(number):
    '''
    匹配括号算式,先用上面定义的算式匹配,计算时先计算括号里面不含有括号的算式,直到匹配完括号
    :return:  return 结果
    '''
    if number.find('(') < 0:  #如果表达式中没有括号,调用main_calc函数计算,并把值return给用户
        return main_calc(number)
    else:
        result = expr5.search(number).group()  #取出最内层的括号表达式
        number = number.replace(result, main_calc(result[1:-1]))      #替换
        return bracket(number)  #递归


def match_str(number):
    '''
    匹配用户输入的是否是非法的字符
    :param number:接受用户传入的输入,用于下面判断
    :return: 如果匹配到字符串返回False,否则返回True
    '''
    result = re.findall(expr6,number)
    if result:
        return False
    else:
        return True


def main():
    '''
    主模块
    :return:
    '''
    while 1:
        print(' \033[32;1m计算器程序\033[0m '.center(87,'#'))
        inp = input('请输入要计算的表达式, 如: 8*12+(6-(5*6-2)/77+2)*(3-7)+8\nq/Q/quit(退出程序)\n>>').strip()


        inp = inp.replace(' ','')
        number = match_str(inp)  #在函数里判断是否包含特殊字符
        if inp == 'q' or inp == 'Q' or inp == 'quit':
            print('Bye!')
            time.sleep(1)
            break
        else:
            if number:
                result = bracket(inp)
                if result:
                    print('#'*80)
                    if input('您输入的表达式是: %s \033[32;1m\n运算结果为:%s\033[0m\n按下回车键继续...'%(inp,result)):pass
            else:
                print('\033[31;1m您输入的表达式错误, 表达式不能包含字母或者特殊字符!\033[0m')



if __name__ == '__main__':
     main()


