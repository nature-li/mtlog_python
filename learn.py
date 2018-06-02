#!/usr/bin/env python2.7
# coding: utf-8

import multiprocessing
import time
import threading
import os
from logger import Logger


lock = multiprocessing.Lock()


def process_func():
    print threading.current_thread().ident, os.getpid()
    for i in xrange(1000):
        Logger.trace("this is a trace message")
        Logger.debug("this is a debug message")
        Logger.info("this is a info message")
        Logger.warn("this is a warn message")
        Logger.error("this is a error message")
        Logger.fatal("this is a fatal message")
        Logger.report("this is a report message")


def __main__():
    if not Logger.init("env", "logs", 'test', lock, 1024 * 1024 * 100, -1):
    # if not Logger.init("env", "logs", 'test', None, 1024 * 1024 * 100, -1):
        print 'init failed'
        return

    l = list()
    start = time.time()
    for i in xrange(10):
        p = multiprocessing.Process(target=process_func)
        p.start()
        l.append(p)
    for p in l:
        p.join()
    Logger.close()
    end = time.time()
    print end - start



if __name__ == '__main__':
    __main__()
