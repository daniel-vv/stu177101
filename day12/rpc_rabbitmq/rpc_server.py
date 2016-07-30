#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import pika
import uuid

class FibonacciRpcServer:
    def __init__(self,host=None,port=None,queue=None):
        '''
        构造函数
        :param host: 接受用户传入一个RabbitMQ队列的主机IP或者可以解析的主机名, 如果不传值,默认为172.16.30.162
        :param port: 接受用户传入一个RabbitMQ队列的端口,如果不传值,默认为5672
        :param port: 接受用户传入一个默认传入命令的队列名, 如果不传值, 默认为 rpc_queue
        :return:
        '''
        if host is None:
            self.host = '172.16.30.162'
        else:
            self.host = host

        if port is None:
            self.port = 5672
        else:
            self.port = port

        if queue is None:
            self.queue = 'rpc_queue'
        else:
            self.queue = queue
        self.connect = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,port=self.port))  #和RabbitMQ建立TCP连接
        self.channel = self.connect.channel()                 #创建虚拟连接
        result = self.channel.queue_declare(exclusive=True)   #创建一个独有的队列用于客户端发送命令返回结果的回调队列
        self.callback_queue = result.method.queue             #回调队列

        self.channel.basic_consume(self.on_respones, no_ack=True, queue=self.callback_queue)

    def on_respones(self,ch, method, props, body):
        '''
        判断用户返回到队列中的数据的correlationID是否和命令的一致,如果一致,则取回,否则丢弃.主要为了确保输入命令和结果的一致性
        :param ch:
        :param method:
        :param props:
        :param body:
        :return:
        '''
        if self.corr_id == props.correlation_id:
            self.respone = body

    def close(self):
        '''
        关闭连接方法
        :return:
        '''
        self.channel.close()
        self.connect.close()


    def run(self,comm):
        '''
        run方法,用户发送用户输入的命令到队列中,并发送一些指定的属性
        :param comm: 接受用户
        :return:
        '''
        self.respone = None
        self.corr_id = str(uuid.uuid4())       #随机生成一个全局唯一标示并转换为str类型

        self.channel.basic_publish(            #发送用户输入的命令到队列中
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(   #发送属性值, 发送命令请求的时候同时发送一个回调队列的地址
                reply_to=self.callback_queue,  #回复目标
                correlation_id=self.corr_id,   #并发送一个关联标识, 全局唯一标识uuid值. 用于将RPC请求和响应关联起来
            ),
            body=comm                          #发送命令
        )

        while self.respone is None:              #不停的去刷返回结果的队列
            self.connect.process_data_events()   #不阻塞,监听句柄是否活动,有信息返回结果
        return self.respone


if __name__ == '__main__':
    fibonacci_rpc = FibonacciRpcServer(host='172.16.30.162')   #实例化
    while True:
        command = input('Please enter a RPC command, q/Q(quit)\n>>>').strip()
        if command == 'q' or command == 'Q':
            print('Bye')
            fibonacci_rpc.close()
            break
        elif len(command) == 0:
            continue
        else:
            response = fibonacci_rpc.run(command)
            print('\033[32;1m%s\033[0m' %str(response,encoding='utf-8'))

