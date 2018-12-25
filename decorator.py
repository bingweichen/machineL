#!/usr/bin/env python
# encoding: utf-8
"""
@author: bingweichen
@contact: bingwei.chen11@gmail.com
@file: decorator.py
@time: 2018/12/21 上午10:26
@desc:

装饰器： 插入日志、性能测试、事务处理、缓存、权限校验等场景
"""

# from time import ctime, sleep
#
#
# def timefun(func):
#     def wrappedfunc():
#         print("%s called at %s" % (func.__name__, ctime()))
#         func()
#
#     return wrappedfunc
#
#
# @timefun
# def foo():
#     print("I am foo")
#
#
# @timefun
# def getInfo():
#     return '----hahah---'
#
#
# foo()
# sleep(2)
# foo()
# print(getInfo())

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Start print log")
logger.debug("Do something")

if __name__ == '__main__':
    pass
    # type2()
