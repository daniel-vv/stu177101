#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

"""
Author: DBQ
Blog: http://www.cnblogs.com/dubq/articles/5520208.html
Github: https://github.com/daniel-vv/ops
"""

import json
import time
import os

CONF = './conf/haproxy.cfg'  #定义几个全局变量--配置文件,在下方引用
CONF_NEW = './conf/haproxy.cfg.new'
CONF_BAK = './conf/haproxy.cfg.bak'
FLAG = False    #标志位,用于下方判断add记录
RENAME = False  #定义一个标志位,用于判断下面判断是否告知用户配置文件更改


def get_backend(user_input_num):
    """
    获取用户输入backed
    :param num: 接受用户传入的backed实际参数
    :return: 返回用户输入backend的一个列表值,而后在main函数里循环打印出来
    """
    server_info = [] #定义一个空列表,用于下面判断用户输入的backend后,把serverinfo写入到列表中,而后循环打印出
    with open(CONF,'r') as f1:
        if user_input_num in f1.read():
            with open(CONF,'r') as f:
                backend_title = 'backend %s' %user_input_num  #定义一个局部变量,用户下面判断在文件中对比有backend的后端服务器
                #server_info = []
                Flag = False     #定义一个标志位,用于下面判断什么时候跳出循环,因为配置文件里不止一个backend
                for line in f:
                    line = line.strip()  #去除空格而后进行下面的判断
                    if line == backend_title:   #如果为真表示匹配到对应的backend,而后将标志位置为true,跳出本次进入下次循环
                        Flag = True
                        continue

                    if Flag and line.startswith('backend'):  #如果标志位为真并且line开头以backend字符开始,表示到了下一个backend位置
                        Flag = False  #将标志位置为False
                        break         #跳出循环

                    #基于标志位判断:
                    if Flag and line:   #如果标志位为真并且line为真,追加line下面server信息到列表中
                        server_info.append(line)
        else:
           server_info.append(user_input_num)

        return server_info  #return 用户输入backend列表


def add_backend(user_input_server):
    '''
    添加backend server函数
    :param user_input_server:   #接受用户传入的字典信息,针对于keys值和values做进一步处理
    :return:  添加成功返回值为True,否则返回默认None,标明添加失败;
    '''
    #使用上下文管理同时打开两个文件,一个用户之前的配置文件从里面读取数据,而后写入新数据到另一个文件中,做备份
    #从用户输入的字典中取出各个值,并赋值给变量
    backend_title = 'backend %s' % user_input_server['backend']
    record_IP = str(user_input_server['record']['server'])
    record_weight = str(user_input_server['record']['weight'])
    record_maxconn = str(user_input_server['record']['maxconn'])
    #server 100.1.7.9 100.1.7.9 weight 20 maxconn 3000
    record = 'server' + ' ' + record_IP + ' ' + record_IP + ' ' + 'weight' + ' ' + record_weight + ' ' + 'maxconn' + ' ' + record_maxconn
    flag = False
    backend_dict = {}
    backend_list = []
    #server_list = []
    global FLAG  #声明使用全局变量,备份配置文件之后更改全局变量标志位
    if not FLAG:   #第一次进来之后,先做个备份,把原有文件备份起来
        os.system('cp ./conf/haproxy.cfg ./conf/haproxy.cfg.bak') #备份配置文件
        FLAG = True  #置标志位为真, 在本程序执行的中途不在备份文件
    #写入不修改的内容到新文件中
    with open(CONF,'r') as readonly_f , open(CONF_NEW,'w+') as writable_f:
        for line in readonly_f:
            if line.strip() == backend_title:  #如果匹配到用户输入的backend,置标志位为真
                flag = True
                if flag and line.startswith('backend '): #进一步判断,如果标志位为真,并且line是以backend开头的跳出本次,进入下次循环
                    continue
            if not flag or line.startswith('backend'): #如果flag为假,或者line是以backend开头的,匹配到不修改的行,并写入到新文件
                flag = False
                writable_f.write(line)  #把line写入到新文件

    backend_dict = {}
    backend_list = []
    with open(CONF,'r') as f:
        if backend_title in f.read():   #判断用户输入的backend是否在配置问价内,如果在的话进入下面的判断;
            with open(CONF,'r') as readonly_file , open(CONF_NEW,'a+') as writable_file:  #再次打开文件,这次是追加模式(写文件)
                flag = False
                Count = 0  #添加计数器用于判断,这块好绕啊
                add_count = 0
                for line1 in readonly_file:
                    if line1.strip() == backend_title:
                        flag = True
                        Count = 1
                        continue
                    if flag and line1.startswith('backend'):   #如果上述两个判断ok,基于标志位来将现有server信息追加到空列表中,而后把用户现在的输入信息追加到列表中;
                        # print(line1)
                        break
                    if Count == 1: #上面判断如果计数器为1,从第二行开始追加server记录到空列表中,并添加一个计数器add_count值为1
                        backend_list.append(line1.strip())
                        add_count = 1
                if add_count == 1:   #如果计数器为2,将原有的backend中的server的记录追加到list中,而后
                    backend_list.append(record)
                    backend_dict[backend_title] = backend_list  #将列表中的记录添加到字典,作为value
                    for i in range(backend_list.count('')):  #删除列表中的空元素,在这里卡了有一小会,不然基于list长度判断是否删除backend记录老不对
                        backend_list.remove('')  #删除列表中的空字符
                for i in range(len(backend_list)):  #循环server的列表长度,用for自增的形式来将列表字典中的元素追加到新配置文件中去
                    if i == 0: #第一次循环,写入 backend title信息
                        writable_file.write('\n' + backend_title + '\n')
                        writable_file.write(' '*8 + backend_dict[backend_title][i] + '\n')
                    else: #下面逐个追加server信息到文件中
                        writable_file.write(' '*8 + backend_dict[backend_title][i] + '\n')
                else:
                    writable_file.flush()
                    flag = True
                #     return True
        else:  #如果用户输入的backend不在配置文件,那么直接在新文件尾部追加
            backend_list.append(record) #先将用户输入的追加到空列表中去
            backend_dict[backend_title] = backend_list #追加
            # print(backend_list)
            # print(backend_dict)
            with open(CONF_NEW,'a+') as f_w:   #追加模式打开new配置文件
                R = len(backend_list)
                if R > 1:
                    for i in range(R):
                        if i == 0:
                            f_w.write('\n' + backend_title + '\n') #写入,主要判断用户一次输入几个server后端值,如果是多个的话,也能实现;
                            f_w.write(' '*8 + backend_dict[backend_title][i])

                        else:
                            f_w.write(' '*8 + backend_dict[backend_title][i] + '\n')
                    else:
                        f_w.flush()
                        flag = True
                else:
                     f_w.write('\n' + backend_title + '\n') #写入,主要判断用户一次输入几个server后端值,如果是多个的话,也能实现;
                     f_w.write(' '*8 + backend_dict[backend_title][0])
                     flag = True
                     #print(backend_title)
                     #print(backend_dict.get(backend_title))


    if flag:  #如果标志位为真, 重命名文件
        os.rename('./conf/haproxy.cfg.new','./conf/haproxy.cfg')
        return True

def del_backend(user_input_server):
    '''
    删除用户输入backend server信息函数
    :param user_input_server:  接受用户输入的字典信息
    :return: 操作成功返回True, 否则返回默认的None
    '''
    backend_list = [] #定义backend空列表,用于存储用户输入的backend后端的server信息
    backend_dict = {} #定义backend空字典,用于存储用户输入的backend信息
    backend_title = 'backend %s' % user_input_server['backend']
    record_IP = str(user_input_server['record']['server'])
    record_weight = str(user_input_server['record']['weight'])
    record_maxconn = str(user_input_server['record']['maxconn'])
    global FLAG  #声明使用全局变量,备份配置文件之后更改全局变量标志位
    if not FLAG:  #循环中,如果用户第一次选择删除操作的话,也是先备份,本程序这次运行中不再备份,也不再备份中写入任何数据
        os.system('cp ./conf/haproxy.cfg ./conf/haproxy.cfg.bak') #备份配置文件
        FLAG = True
    #把用户输入的信息摘出来,然后拼接起来赋值
    record = 'server' + ' ' + record_IP + ' ' + record_IP + ' ' + 'weight' + ' ' + record_weight + ' ' + 'maxconn' + ' ' + record_maxconn
    flag = False
    Flag = False
    with open(CONF) as f:
        if backend_title in f.read():
            with open(CONF,'r') as readonly_del_f, open(CONF_NEW,'w+') as writable_del_f:
                for line in readonly_del_f:
                    if line.strip() == backend_title:  #如果匹配到用户输入的backend,置标志位为真
                        flag = True
                        if flag and line.startswith('backend '): #进一步判断,如果标志位为真,并且line是以backend开头的跳出本次,进入下次循环
                            continue
                    if not flag or line.startswith('backend'): #如果flag为假,或者line是以backend开头的,匹配到不修改的行,并写入到新文件
                        flag = False
                        writable_del_f.write(line)  #把line(除了用户输入的backend以外的内容)写入到新文件

            backend_list = []
            backend_dict = {}
            with open(CONF,'r') as readonly_file , open(CONF_NEW,'a+') as writable_del_f:  #再次打开文件,这次是追加模式(写文件)
                flag = False
                Count = 0  #添加计数器用于判断,这块好绕啊
                add_count = 0 #添加计数器,用于判断用户删除记录后写入文件
                for line1 in readonly_file:
                    if line1.strip() == backend_title:
                        flag = True
                        Count = 1
                        continue
                    if flag and line1.startswith('backend'):   #如果上述两个判断ok,基于标志位来将现有server信息追加到空列表中,而后把用户现在的输入信息追加到列表中;
                        break
                    if Count == 1: #上面判断如果计数器为1,从第二行开始追加server记录到空列表中,并添加一个计数器add_count值为1
                        backend_list.append(line1.strip())
                        backend_dict[backend_title] = backend_list  #将列表中的记录添加到字典,作为value
                        add_count = 1

                if add_count == 1 and record in backend_list:   #如果计数器为2,判断用户输入的record值是否在列表中,而后进一步操作
                    record_index = backend_list.index(record)
                    user_input=input('\033[31;1m记录在列表中,是否删除? y/Y\033[0m').strip()
                    if user_input == 'y' or user_input == 'Y':
                        del backend_list[record_index]
                        for i in range(backend_list.count('')):  #删除列表中的空元素,在这里卡了有一小会,不然基于list长度判断是否删除backend记录老不对
                            backend_list.remove('')  #删除列表中的空字符
                        else:  #循环体执行完成后判断如果列表为空标明server中没有记录了,然后将计数器置为2
                            add_count = 2 if len(backend_list) == 0 else 1 #来一下三目运算 ^_^
                    else:
                        return False  #如果用户输入y/Y以外的值的话,就返回False
                else:
                    if input('\033[31;1m记录不存在,输入任意键继续....\033[0m'):pass
                    add_count = 1

                if add_count == 2: #如果计数器为2,提示用户是否要删除
                    user_input_reuse=input('%s 下面没有任何记录了,是否要删除backend? y/Y' %backend_title).strip()
                    if user_input_reuse == 'y' or user_input_reuse == 'Y':
                        del backend_dict  #删除字典
                        add_count = 3 #删除记录之后计数器为3,用于下面判断,是否改名字
                    else:
                        writable_del_f.write(backend_title) #写入backend到文件中
                        add_count = 3
                else:  #如果标志位不为2,证明列表中还有其他值,因此循环取出,也是先删除下空字符,否则格式好恶心
                    for i in range(backend_list.count('')):  #删除列表中的空元素,在这里卡了有一小会,不然基于list长度判断是否删除backend记录老不对
                        backend_list.remove('')  #删除列表中的空字符
                    for i in range(len(backend_list)):
                        if i == 0:
                            writable_del_f.write('\n' + backend_title + '\n') #写入,主要判断用户一次输入几个server后端值,如果是多个的话,也能实现;
                            writable_del_f.write(' '*8 + backend_dict[backend_title][i] + '\n')
                        else:
                            writable_del_f.write(' '*8 + backend_dict[backend_title][i] + '\n')
                    else:  #循环体正常执行完后,标志位置为3
                        add_count = 3
            if add_count == 3:  #而后该文件名
                os.rename('./conf/haproxy.cfg.new','./conf/haproxy.cfg')
                return True


def get_help():
    '''
    用户帮助函数,只输出一些程序帮助信息
    :return: 无返回值,默认None
    '''
    print('\033[31;1mHELP\033[0m'.center(110,'#'))
    print('''
        1. 查看后端server, 请使用 FQDN 完全合格域名格式,输入您要查找的记录,如: www.dbq168.com

        2. 增加后端server,需要输入下面的格式,注意,需要{}里的引号务必是双引号,请严格遵守程序的规范输入;

       {"backend": "www.oldboy.com","record":{"server": "100.1.7.9","weight": 20,"maxconn": 30}}

        3. 删除server, 格式同第二点相同

        4. 获取程序帮助

        5. 退出程序

        请严格按照程序要求格式输入,谢谢您的配合!
    ''')
    print('#'*100)
    if input('\033[32;1m按下任意键继续...\033[0m'):pass

def main():
    """
    主函数,用于根据用户输入判断,而后传实体参数给各个函数;
    :return: 暂定没返回值,默认是None
    """
    global RENAME
    flag = False
    while not flag:
        print("""
        1. 查看Haproxy后端Server
        2. 添加Haproxy后端Server
        3. 删除Haproxy后端Server
        4. 获取帮助信息
        5. 退出程序
        """)
        user_input_num = input('请输入一个你想要实现的操作序列?').strip()  #接受用户传入序列
        if user_input_num == '1':
            user_input_server = input('请输入你要查询的backend配置:').strip()
            server_info = get_backend(user_input_server)

            #如果输入主机头不在server_info的列表里,证明get函数有获取到backend的信息,而后进入下面程序,打印用户主机后端服务器信息
            if user_input_server not in server_info and server_info:
                print('你查询的backend [ %s ] 的Server信息如下:' %user_input_server)
                print('#'*50)
                for i in range(len(server_info)): #做循环,用于打印多个用户输入的信息
                    print('\033[34;1m %s \033[0m'%server_info[i])
                else:
                    print('#'*50)
                    if input('\033[32;1m按下任意键继续...\033[0m'):pass

            else:
                if len(user_input_server) != 0: #如果列表不为空,并且输入不在文件backend中,打印下面的信息,提示用户可以添加主机
                    print('\033[31;1m您输入的主机名 [ %s ] 不存在,输入序列2添加吧~~\033[0m' %user_input_server)
        if user_input_num == '2':
            user_input_server = input("""格式:
            \033[35;1m{"backend": "test.oldboy.org","record":{"server": "100.1.7.9","weight": 20,"maxconn": 30}}\033[0m
            请输入要增加的Server记录:""").strip()
            if user_input_server:
                user_input_server = json.loads(user_input_server) #使用json将用户输入的内容转换为本身的类型,也就是字典格式
                result = add_backend(user_input_server)  #作为实体参数传给add_backend
                if result:
                    if input('\033[32;1m记录添加成功,按下任意键继续...\033[0m'):pass

                    RENAME = True
                else:
                    print('记录没有添加成功')
        if user_input_num == '3':
            user_input_server = input("""格式:
            \033[35;1m{"backend": "test.oldboy.org","record":{"server": "100.1.7.9","weight": 20,"maxconn": 30}}\033[0m
            请输入要删除的Server记录:""").strip()
            if user_input_server:
                user_input_server = json.loads(user_input_server)
                result = del_backend(user_input_server)
                if result:
                    if input('\033[31;1m[%s] 删除成功,按下任意键继续...\033[0m'%user_input_server):pass
                    # global RENAME
                    RENAME = True
        if user_input_num == '4':
            get_help()
        if user_input_num == '5' or user_input_num == 'quit':
            if CONF_BAK and RENAME:
                edit_flag = input('\033[31;1m原配置文件做了更改,是否保存? (y/Y):\033[0m').strip()
                if edit_flag == 'y' or edit_flag == 'Y' and not edit_flag:
                    time.sleep(1)
                    print('配置文件修改完成,原文件已备份\033[31;1m[ %s ]\033[0m, 欢迎下次再来, Bye!'%CONF_BAK)
                    break
                else:
                    print('您放弃了保存...... Bye!')
                    os.rename('./conf/haproxy.cfg.bak','./conf/haproxy.cfg')
                    break
            else:
                print('欢迎下次再来, Bye!')
            break

if __name__ == '__main__':
    main()



print()


