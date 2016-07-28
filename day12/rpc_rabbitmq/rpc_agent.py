#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import pika
import subprocess
import os

class FibonacciRpcAgent:
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

        self.connect = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,port=self.port))
        self.channel = self.connect.channel()     #虚拟连接,建立在上面的TCP连接基础上

        self.channel.queue_declare(queue=self.queue)    #默认监听rpc_queue,让服务器通过这个队列发送命令
        #公平调度, 告诉RabbitMQ，在同一时刻，不要发送超过一条消息给一个worker，直到它处理了上一条消息并且做出了响应。
        self.channel.basic_qos(prefetch_count=1)

        self.channel.basic_consume(self.on_request, no_ack=True, queue=self.queue)
        self.channel.start_consuming()

    def run_cmd(self,cmd):
        '''
        运行本地命令方法,通过subprocess.Popen实现
        :param cmd: 接受用户传过来的命令
        :return:
        '''
        obj = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = obj.stdout.read()
        if len(res) != 0:
            result = res
        else:
            result = obj.stderr.read()
        return result

    def close(self):
        '''
        关闭连接方法
        :return:
        '''
        self.channel.close()
        self.connect.close()


    def on_request(self, channel, method, props, body):
        '''
        请求方法, 在构造方法中 basic_consume调用
        :param channel: 虚拟通道
        :param method: 方法
        :param props:  属性相关
        :param body:   消息主题
        :return:
        '''
        #respone = run_cmd()
        self.respone = self.run_cmd(str(body,encoding='utf-8'))

        self.channel.basic_publish(
            exchange='',   #消息是不能直接发送到队列的,它需要发送到交换机(exchange),下面会谈这个,此处使用一个空字符串来标识
            routing_key = props.reply_to,   #必须指定为队列的名称, 此处选择一个指定的回消息队列
            properties = pika.BasicProperties(correlation_id=props.correlation_id),
            body=self.respone
        )


if __name__ == '__main__':
    print('RPC Agent is running(%s)..., Exit the program enter CTRL+C'%os.getpid())
    try:
        obj = FibonacciRpcAgent()
    except Exception:
        obj.close()





