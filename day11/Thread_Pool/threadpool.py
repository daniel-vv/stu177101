#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Author: DBQ(Du Baoqiang)

'''
github地址: https://github.com/SpotlightKid/threadpool
第三方线程池
__author__ = "Christopher Arndt"
__version__ = '1.3.2'
__license__ = "MIT license"
'''


"""Easy to use object-oriented thread pool framework.

A thread pool is an object that maintains a pool of worker threads to perform
time consuming operations in parallel. It assigns jobs to the threads
by putting them in a work request queue, where they are picked up by the
next available thread. This then performs the requested operation in the
background and puts the results in another queue.

The thread pool object can then collect the results from all threads from
this queue as soon as they become available or after all threads have
finished their work. It's also possible, to define callbacks to handle
each result as it comes in.

The basic concept and some code was taken from the book "Python in a Nutshell,
2nd edition" by Alex Martelli, O'Reilly 2006, ISBN 0-596-10046-9, from section
14.5 "Threaded Program Architecture". I wrapped the main program logic in the
ThreadPool class, added the WorkRequest class and the callback system and
tweaked the code here and there. Kudos also to Florent Aide for the exception
handling mechanism.

Basic usage::

    >>> pool = ThreadPool(poolsize)
    >>> requests = makeRequests(some_callable, list_of_args, callback)
    >>> [pool.putRequest(req) for req in requests]
    >>> pool.wait()

See the end of the module code for a brief, annotated usage example.

Website : http://chrisarndt.de/projects/threadpool/

"""
__docformat__ = "restructuredtext en"

__all__ = [
    'makeRequests',
    'NoResultsPending',
    'NoWorkersAvailable',
    'ThreadPool',
    'WorkRequest',
    'WorkerThread'
]

__author__ = "Christopher Arndt"
__version__ = '1.3.2'
__license__ = "MIT license"


# standard library modules
import sys         #导入标准模块
import threading
import traceback

#导入队列模块, python2下是Queue, python3下是queue,所以,再次做判断来导入
try:
    import Queue            # Python 2
except ImportError:
    import queue as Queue   # Python 3中为queue,而后 别名为Queue


# exceptions
class NoResultsPending(Exception):   #定义异常类, 所有结果处理完成, 会主动触发这个类
    """All work requests have been processed."""
    pass

class NoWorkersAvailable(Exception):  #定义异常类, 没有可用workers, 会主动触发这个类
    """No worker threads available to process remaining requests."""
    pass


# internal module helper functions
def _handle_thread_exception(request, exc_info):   #内部帮助函数, 可以获取详细的异常信息
    """Default exception handler callback function.

    This just prints the exception info via ``traceback.print_exception``.

    """
    traceback.print_exception(*exc_info)


# utility functions
def makeRequests(callable_, args_list, callback=None,
        exc_callback=_handle_thread_exception):
    ''' 调用一些不同的参数来创建一些工作请求.对于同一创建多个工作请求方便的功能,可调用其中的参数,每次接受不同的值
    :param callable_:
    :param args_list: 包含每次可调用的参数, 可接受列表或者元组
    :param callback:  接受用户传入的callback参数,默认为None
    :param exc_callback:  接受用户传入的exc_callback参数, 默认值为_handle_thread_exception
    :return:
    '''
    requests = []  #定义一个请求的空列表
    for item in args_list:   #循环遍历用户提供的参数列表
        if isinstance(item, tuple):    #如果item的是一个元组的话
            requests.append(           #而后把每个项目实例化后追加到requests列表中, 注意这里有个item[0] 和 item[1]
                WorkRequest(callable_, item[0], item[1], callback=callback,
                    exc_callback=exc_callback)
            )
        else:                          #如果不是元组的话, 直接追加
            requests.append(
                WorkRequest(callable_, [item], None, callback=callback,
                    exc_callback=exc_callback)
            )
    return requests   #最后return requests列表


# classes
class WorkerThread(threading.Thread):      #定义工作线程类, 继承threading.Thread
    """连接请求/结果队列的后台线程类.工作线程在后台, 从一个队列中获取工作请求, 并把结果保存在另一个队列中, 直到接受关闭请求
    """

    def __init__(self, requests_queue, results_queue, poll_timeout=5, **kwds):
        '''
        构造方法, 设定线程工作在守护线程模式
        :param requests_queue: 和 results_queue 的 queue.Queue, 通过ThreadPool类实例化创建一个新的工作线程
        :param results_queue:
        :param poll_timeout:  超时时间
        :param kwds:
        :return:
        '''
        #``requests_queue`` and ``results_queue`` are instances of
        #``Queue.Queue`` passed by the ``ThreadPool`` class when it creates a
        #new worker thread.


        threading.Thread.__init__(self, **kwds)  #执行父类的构造方法
        self.setDaemon(1)                        #将当前线程设定为守护线程
        self._requests_queue = requests_queue    #定义请求队列变量
        self._results_queue = results_queue      #定义结果队列
        self._poll_timeout = poll_timeout        #超时时间
        self._dismissed = threading.Event()      #定义排除的变量的值为threading.Event() 作用: 多线程通信简单的机制,一个线程标识一个事件,其他线程一直处于等待状态.
        self.start()                             #开始线程

    def run(self):
        """反复处理作业队列,直到发送退出信号"""
        while True:    #进入死循环
            if self._dismissed.isSet():    #判断内部信号标识的状态为, 当Event对象使用set()方法后, isSet方法返回True,默认为False, 如果为真, 直接break退出循环
                break
            '''请求下一个工作请求, 如果在self._poll_timeout秒之内,从队列中不能获取到一个新的请求,讲跳出到本次循环, 提供一个线程退出的机会 '''
            try:
                request = self._requests_queue.get(True, self._poll_timeout)   #从队列中获取
            except Queue.Empty:  #如果队列为空, 跳出本次循环,进入下次
                continue
            else:  #如果没有异常情况的话
                if self._dismissed.isSet():     #还是判断内部信号标志位
                    self._requests_queue.put(request)    #将请求put到队列中,而后break
                    break
                try:
                    result = request.callable(*request.args, **request.kwds)   #调用callable方法, 把参数都传进去, 结果赋值给result
                    self._results_queue.put((request, result))    #而后把执行结果和request以元组的形式put到执行结果队列中
                except:
                    request.exception = True      #异常时
                    self._results_queue.put((request, sys.exc_info()))      #把请求和异常时系统的错误信息put到结果队列中

    def dismiss(self):
        '''
        线程完成方法, 设置一个标志位, 在线程完成当前任务之后, 告诉线程退出.  通过Event.set() 实现
        :return:
        '''
        self._dismissed.set()


class WorkRequest:
    """A request to execute a callable for putting in the request queue later.

    See the module function ``makeRequests`` for the common case
    where you want to build several ``WorkRequest`` objects for the same
    callable but with different arguments for each call.

    """

    def __init__(self, callable_, args=None, kwds=None, requestID=None,
            callback=None, exc_callback=_handle_thread_exception):
        # 构造函数
        """Create a work request for a callable and attach callbacks.

        A work request consists of the a callable to be executed by a
        worker thread, a list of positional arguments, a dictionary
        of keyword arguments.

        A ``callback`` function can be specified, that is called when the
        results of the request are picked up from the result queue. It must
        accept two anonymous arguments, the ``WorkRequest`` object and the
        results of the callable, in that order. If you want to pass additional
        information to the callback, just stick it on the request object.

        You can also give custom callback for when an exception occurs with
        the ``exc_callback`` keyword parameter. It should also accept two
        anonymous arguments, the ``WorkRequest`` and a tuple with the exception
        details as returned by ``sys.exc_info()``. The default implementation
        of this callback just prints the exception info via
        ``traceback.print_exception``. If you want no exception handler
        callback, just pass in ``None``.

        ``requestID``, if given, must be hashable since it is used by
        ``ThreadPool`` object to store the results of that work request in a
        dictionary. It defaults to the return value of ``id(self)``.

        """
        if requestID is None:    #如果用户没有传入requestID
            self.requestID = id(self)   #self.requestID为 自己本身的内存地址
        else:
            try:
                self.requestID = hash(requestID)   #如果提供了, 为hash之后的值
            except TypeError:       #如果不能hash, 触发异常
                raise TypeError("requestID must be hashable.")
        self.exception = False
        self.callback = callback
        self.exc_callback = exc_callback
        self.callable = callable_
        self.args = args or []
        self.kwds = kwds or {}

    def __str__(self):
        return "<WorkRequest id=%s args=%r kwargs=%r exception=%s>" % \
            (self.requestID, self.args, self.kwds, self.exception)

class ThreadPool:   #d定义线程池类
    """A thread pool, distributing work requests and collecting results.

    See the module docstring for more information.

    """

    def __init__(self, num_workers, q_size=0, resq_size=0, poll_timeout=5):
        '''
        构造方法
        :param num_workers: 开始线程池和启动工作线程的workers数量
        :param q_size: 队列大小, 如果q_size>0的时候(0)为不受限, 请求队列是受限的, 如果队列请求满的话,其余的请求就会阻塞等待队列空闲, \
        并且还会把更多的请求put进来,虽然是阻塞, 除非你使用了timeout值到putRequest中.  更多查看putRequest方法
        :param resq_size: 请求完成处理的队列的大小
        :param poll_timeout:  超时时间
        :return:
        PS: 如果同时设置了两个q_size和resq_size为不等于0的两个值, 那么可能会出现死锁, 我们这个结果队列不是一个定期拉取的,
        并且更多的jobs会put到工作请求队列. 为了预防这个问题, 一般会设置timeout>0的值, 适当的时候调用 ThreadPool.putRequest()
        并捕捉Queue.Full异常
        '''
        self._requests_queue = Queue.Queue(q_size)    #队列, q_size 大小
        self._results_queue = Queue.Queue(resq_size)  #处理完成后的队列的大小
        self.workers = []                             #定义workers 的空列表,用于存放工作线程
        self.dismissedWorkers = []                    #workers完成后的空列表
        self.workRequests = {}                        #worker请求的空字典
        self.createWorkers(num_workers, poll_timeout) #调用方法createworkers, 把workers数量和超时时间作为参数传进去


    def createWorkers(self, num_workers, poll_timeout=5):
        '''
        添加worker数量到线程池,
        :param num_workers:  工作线程数
        :param poll_timeout: 超时时间
        :return:
        '''

        for i in range(num_workers):   #循环输入的num_workers
            self.workers.append(WorkerThread(self._requests_queue,   #调用WorkerThread方法, 把参数穿进去,而后把整个追加到workers的列表中
                self._results_queue, poll_timeout=poll_timeout))

    def dismissWorkers(self, num_workers, do_join=False):
        '''
        告知工作线程在完成当前线程后退出任务
        :param num_workers:
        :param do_join:
        :return:
        '''
        dismiss_list = []    #定义一个空的完成任务空列表
        for i in range(min(num_workers, len(self.workers))):  #循环处理, 次数从最小num_workers到workers的长度
            worker = self.workers.pop()        #从列表中随机取出一个值,pop会随机取, 并删除取出的值
            worker.dismiss()                   #触发dismiss方法, 更改isSet标志位
            dismiss_list.append(worker)        #把完成的worker追加到完成任务的列表

        if do_join:      #如果do_join为真,, 默认为假
            for worker in dismiss_list:    #循环阻塞,等待子线程完成请求后再退出
                worker.join()              #join()方法是WorkerThread继承父类的(threading.Thread)
        else:                              #否则把这个完成任务列表扩展到dismissedWorkers列表
            self.dismissedWorkers.extend(dismiss_list)

    def joinAllDismissedWorkers(self):
        '''
        执行Thread.join()所有的工作线程
        :return:
        '''
        """Perform Thread.join() on all worker threads that have been dismissed.
        """
        for worker in self.dismissedWorkers:   #循环dismissedWorkers列表
            worker.join()                      #执行join
        self.dismissedWorkers = []             #而后把列表置为空

    def putRequest(self, request, block=True, timeout=None):
        """Put work request into work queue and save its id for later."""
        assert isinstance(request, WorkRequest)           #断言, 如果请求是一个WorkRequest实例的话
        # don't reuse old work requests                   #不重复使用旧的work请求
        assert not getattr(request, 'exception', None)    #断言, 如果request异常的话
        self._requests_queue.put(request, block, timeout) #put请求, block标志位, 超时时间到请求队列中
        self.workRequests[request.requestID] = request    #添加以请求.请求ID为key,值为request到self.workRequests的字典中

    def poll(self, block=False):
        '''
        处理结果队列
        :param block:
        :return:
        '''
        while True:
            # still results pending?
            if not self.workRequests:   #如果字典为空, 主动触发异常: NoResultsPending
                raise NoResultsPending
            # are there still workers to process remaining requests?
            elif block and not self.workers:   #block为真并且 self.workers为空, 触发异常: NoWorkersAvailable , 没有可用的Workers
                raise NoWorkersAvailable
            try:
                # get back next results
                request, result = self._results_queue.get(block=block)    #从队列中获取request, result结果
                # has an exception occured?
                if request.exception and request.exc_callback:      #如果exception 和 exc_callback回调函数存在的话, 将请求和result交给其处理
                    request.exc_callback(request, result)
                # hand results to callback, if any
                if request.callback and not \
                       (request.exception and request.exc_callback): #如果用户传入了 callback, 并且 exception 和 exc_callback都未假
                    request.callback(request, result)    #将result 和 request传给callback执行
                del self.workRequests[request.requestID] #而后删除字典中的请求和请求id为key的值
            except Queue.Empty:   #捕获到队列为空的异常直接跳出循环
                break

    def wait(self):
        """阻塞等待结果"""
        while 1:  #死循环处理
            try:
                self.poll(True)   #传入True到poll方法循环处理
            except NoResultsPending:  #出现NoResultsPending异常后break出循环
                break


################
# USAGE EXAMPLE
################

if __name__ == '__main__':
    import random
    import time

    # the work the threads will have to do (rather trivial in our example)
    def do_something(data):   #定义任意函数任意方法
        time.sleep(random.randint(1,5))  #休眠随机1,5秒
        result = round(random.random() * data, 5)      #随机数,并使用round返回随机数的四舍五入值,保留小数点后5位
        # just to show off, we throw an exception once in a while
        if result > 5:   #如果result 大于5, 触发异常
            raise RuntimeError("Something extraordinary happened!")
        return result   #returl result值

    # this will be called each time a result is available
    def print_result(request, result):   #打印结果
        print("**** Result from request #%s: %r" % (request.requestID, result))

    # this will be called when an exception occurs within a thread
    # this example exception handler does little more than the default handler
    def handle_exception(request, exc_info):
        if not isinstance(exc_info, tuple):
            # Something is seriously wrong...
            print(request)
            print(exc_info)
            raise SystemExit
        print("**** Exception occured in request #%s: %s" % \
          (request.requestID, exc_info))

    # assemble the arguments for each job to a list...
    data = [random.randint(1,10) for i in range(20)] #从1-10, 循环20次,生成20个1-10之间的任意数的列表
    # ... and build a WorkRequest object for each item in data
    requests = makeRequests(do_something, data, print_result, handle_exception)  #创建请求, 传入上面定义的值
    # to use the default exception handler, uncomment next line and comment out
    # the preceding one.
    #requests = makeRequests(do_something, data, print_result)

    # or the other form of args_lists accepted by makeRequests: ((,), {})
    data = [((random.randint(1,10),), {}) for i in range(20)]  #生成20个值为元组的列表, 元组中的值是1-10之间的随机数和一个空字典
    requests.extend(
        makeRequests(do_something, data, print_result, handle_exception)
        #makeRequests(do_something, data, print_result)
        # to use the default exception handler, uncomment next line and comment
        # out the preceding one.
    )

    # we create a pool of 3 worker threads
    print("Creating thread pool with 3 worker threads.")
    main = ThreadPool(3)   #创建三个工作线程

    # then we put the work requests in the queue...
    for req in requests:     #put请求到队列中
        main.putRequest(req)
        print("Work request #%s added." % req.requestID)
    # or shorter:
    # [main.putRequest(req) for req in requests]

    # ...and wait for the results to arrive in the result queue
    # by using ThreadPool.wait(). This would block until results for
    # all work requests have arrived:
    # main.wait()

    # instead we can poll for results while doing something else:
    i = 0
    while True:
        try:
            time.sleep(0.5)
            main.poll()    #执行pool方法
            print("Main thread working...")
            print("(active worker threads: %i)" % (threading.activeCount()-1, ))
            if i == 10:
                print("**** Adding 3 more worker threads...")
                main.createWorkers(3)     #执行createWorkers方法, 添加3到线程池
            if i == 20:
                print("**** Dismissing 2 worker threads...")
                main.dismissWorkers(2)    #执行dismissWorkers方法
            i += 1
        except KeyboardInterrupt:
            print("**** Interrupted!")
            break
        except NoResultsPending:
            print("**** No pending results.")   #处理完任务之后跳出循环,执行下面操作
            break
    if main.dismissedWorkers:
        print("Joining all dismissed worker threads...")
        main.joinAllDismissedWorkers()

