#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

#自定义线程池

import queue       #导入队列queue模块
import threading   #导入threading线程模块
import time        #导入time时间模块
import contextlib  #导入contextlib模块, contextlib是为了加强with语句，提供上下文机制的模块，它是通过Generator实现的。

StopEvent = object()    #定义一个停止时间, 为一个类对象


class MyThreadPool:      #自定义一个类MyThreadPool
    def __init__(self,max_num, max_task_num = None ):
        '''
        构造函数
        :param max_num: 最大数
        :param max_task_num: 最大任务数量,如果用户输入的话,队列大小为最大任务数
        :return:
        '''
        if max_task_num:    #默认值为None,如果用户指定的话, 最大队列数为用户指定的max_task_num数量
            self.q = queue.Queue(max_task_num)   #默认FIFO队列类型
        else:
            self.q = queue.Queue()

        self.max_num = max_num        #初始化几个变量
        self.cancel = False           #执行完成撤销标志位
        self.terminal = False         #线程执行终止标志位
        self.generate_list = []       #定义一个生产列表
        self.free_list = []           #定义一个空闲列表

    def run(self,func, args, callback=None):
        '''
        线程池执行一个任务
        :param func: 任务函数
        :param args: 任务函数所需要的参数
        :param callback: 任务执行失败或者成功之后执行的回调函数, 回调函数有两个参数:
            1. 任务函数的执行状态
            2. 任务函数返回值(默认为None,即,不执行回调函数)
        :return: 如果线程已经终止, 则返回True,否则None
        '''
        if self.cancel:    #如果执行完成, 直接return True
            return True
        if len(self.free_list) == 0 and len(self.generate_list) < self.max_num: #如果空闲列表长度为0 并且生产列表的长度小于最大数
            self.generate_thread()      #创建线程
        w = (func, args, callback,)     #将传入的几个参数作为一个元组
        self.q.put(w)                   #put到队列中


    def generate_thread(self):
        '''
        创建线程方法
        :return:
        '''
        t = threading.Thread(target=self.call)      #创建线程, 调用call方法
        t.start()   #启动线程

    def call(self):
        '''
        循环去获取任务函数并执行任务函数
        '''
        current_thread = threading.currentThread    #获取当前的线程函数,此处不能加(), 不然就是获取当前线程的一个变量了,要获取线程的函数
        self.generate_list.append(current_thread)   #而后追加到生产列表中

        event = self.q.get()    #从队列中get用户传入的元组
        while event != StopEvent:      #循环,如果event 不等于 停止类object
            func, arguments, callback = event    #分离元组,分别赋值3个变量. func: 用户传入的action函数; arguments: 用户传入的func的执行参数; callback: 用户传入的执行函数
            #print('func: %s\narguments: %s\ncallback: %s'%(func,arguments,callback))
            try:
                res = func(*arguments)    #把用户传入的*arguments传给func函数,而后执行
                success = True            #一切正常的情况下,success为True
            except Exception:
                success = False           #出现异常, success为False, res为None
                res = None

            if callback is not None:     #如果callback不为空
                try:
                    callback(success, res)    #将上述func执行的结果和success标志位, 传给callback调用执行
                except Exception:
                    pass

            with self.worker_state(self.free_list, current_thread):     #with的方式调用worker_state方法, 传参进去,
                            # 一个free_list 列表, 一个当前线程的函数. 主要判断用户有没有terminal,而后给event赋值,是继续循环还是终止?
                if self.terminal:    #如果terminal终止值为真, event 值置为StopEvent. terminal值默认为False
                    event = StopEvent
                else:   #为假的话,证明用户没有触发 terminate
                    event = self.q.get()    #继续从队列获取值,进入下一次循环

        else:
            self.generate_list.remove(current_thread)    #循环正常退出之后, 从生产列表中移除当前线程函数

    def terminate(self):
        '''
        无论是否还有任务,终止线程
        :return:
        '''
        self.terminal = True       #如果触发方法, 先将terminal变量置为True, 在call方法的while循环中就会跳出
        while self.generate_list:  #而后循环,生产列表, 将队列中put停止事件put到队列中
            self.q.put(StopEvent)

        self.q.empty()      #获取队列是否为空, 为空返回True, 否则 False


    def close(self):
        '''
        执行完所有任务后,所有线程都停止
        :return:
        '''
        self.cancel = True     #如果用户调用close方法,证明执行正常退出, 将标志位置为True
        full_size = len(self.generate_list)     #获取生产列表的长度
        while full_size:          #循环
            self.q.put(StopEvent) #在队列中put生产列表长度的停止位
            full_size -= 1        #循环标志递减, 为0时退出循环



    #contextlib是为了加强with语句,提供上下文管理机制的模块, 是通过Generator实现的.通过定义类__enter__和 __exit__来进行上下文管理虽然不难,但是很繁琐.
    #contextlib中的contextmanager作为装饰器来提供一种针对函数级别的上下文管理机制.
    #如果在call方法中打印worker_state的类型的话, 是:GeneratorContextManage
    @contextlib.contextmanager
    def worker_state(self,state_list, worker_thread):
        '''
        用于记录线程中正在等候的线程数
        :param state_list: 形参,call 方法传入的空闲列表
        :param worker_thread:  形参, call方法传入的当前线程
        :return:
        '''
        state_list.append(worker_thread)      #call方法通过with上下文管理方式调用该方法, 将当前线程追加到空闲列表中
        try:
            yield                             #生成器模式,让call迭代
        finally:
            state_list.remove(worker_thread)  #无论成功与否,从空闲列表中移除当前线程


#########
#使用例子#
#########
if __name__ == '__main__':

    pool = MyThreadPool(5)   #实例化, 可接受传入参数max_num 最大线程数 , max_task_num = num 队列大小,默认为None,就是不限制

    def callback(status, result):
        # status, execute action status
        # result, execute action return value
        pass

    def action(i):  #执行函数, 接受用户传入形参, 在类中会将参数拿给action处理
        print(i)    #定义动作

    for i in range(30):    #测试
        res = pool.run(action, (i,))  #调用run方法, 传入参数 上面定义的action执行函数,和执行函数的参数, 可选: callback,针对action执行函数的结果的回调函数.

    time.sleep(2)
    pool.close()   #完成后正常关闭
