# !/usr/bin/env python2.7
# coding: utf-8

import multiprocessing
import time
import threading
import os
import gevent
from logger import Logger


def gevent_func():
    for i in xrange(100):
        Logger.trace("this is a trace message")
        Logger.debug("this is a debug message")
        Logger.info("this is a info message")
        Logger.warn("this is a warn message")
        Logger.error("this is a error message")
        Logger.fatal("this is a fatal message")
        Logger.report("this is a report message")

def process_func():
    print threading.current_thread().ident, os.getpid()

    l = list()
    for i in xrange(10):
        g = gevent.spawn(gevent_func)
        l.append(g)
    gevent.joinall(l)


def __main__():
    if not Logger.init("develop", "logs", 'test', 100 * 1024 * 1024, 10, True):
        print 'init failed'
        return
    Logger.set_level(Logger.INFO)

    l = list()
    start = time.time()
    for i in xrange(10):
        p = multiprocessing.Process(target=process_func)
        p.start()
        l.append(p)
    for p in l:
        p.join()
    end = time.time()
    print 'time:', end - start
    print 'speed:', (10 * 10 * 100 * 7) / (end - start)


if __name__ == '__main__':
    __main__()
