Author: DBQ(Du Baoqiang)
Blog:   http://www.cnblogs.com/dubq/p/5680489.html
Github: https://github.com/daniel-vv/stu177101


作业：线程池

要求：
	1. 线程池
		- 自己实现， 课上讲的第二种线程池
 		- 第三方模块   # 每一句加注释
 		- 武sir发的模块

解决方案:
    1. 找的是一个第三方的模块, threadpool,
        官方站点: https://chrisarndt.de/
        github: https://github.com/SpotlightKid/threadpool
        安装方式:
            pip3 install threadpool
            或者去下载源码,而后使用python3 setup.py install 安装
        使用方式:
                >>> pool = ThreadPool(poolsize)   #实例化, 接受一个线程池大小
                >>> requests = makeRequests(some_callable, list_of_args, callback)
                >>> [pool.putRequest(req) for req in requests]
                >>> pool.wait()
        PS: 源码中含有使用示例.

    2. 武sir写的线程池, 含注释
        使用方式:
            pool = MyThreadPool(5)   #实例化, 接受一个线程池大小
            def callback(status, result):
                # status, execute action status
                # result, execute action return value
                pass

            def action(i):  #执行函数, 接受用户传入形参, 在类中会将参数拿给action处理
                print(i)    #定义动作

            for i in range(30):    #测试
                res = pool.run(action, (i,))  #调用run方法, 传入参数 上面定义的action执行函数,和执行函数的参数,
                                              #可选: callback,针对action执行函数的结果的回调函数.

            time.sleep(2)
            pool.close()   #完成后正常关闭
        PS: 源码中含有使用示例.

程序运行说明:
    本程序在如下平台上测试通过:
        Ubuntu(LTS 14.04)/Debian(wheezy,jessie)
        Mac 终端(Python3.5解释器)中测试通过.
        Mac下的PyCharm(5.0.3 Pro)

    编写代码时,将两个模块文件,放入到sys.path环境变量中的目录下,而后, import 导入即可

文件及目录说明:
    |____Thread_Pool    #程序目录
    | |______init__.py
    | |____MyThreadPool.py   #武sir实现的线程池, 含注释
    | |____Readme.txt        #自述文件
    | |____threadpool.py     #第三方线程池threadpool







