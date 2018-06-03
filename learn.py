#!/usr/bin/env python2.
# coding: utf-8

import multiprocessing
import time
import threading
import os
import setproctitle
import gevent
from logger import Logger


lock = multiprocessing.Lock()


def gevent_func():
    pass

def process_func():
    setproctitle.setproctitle('MonitorWorker')
    print threading.current_thread().ident, os.getpid()

    l = list()
    for i in xrange(10):
        g = gevent.spawn(gevent_func)
    gevent.joinall(l)

    for i in xrange(100):
        time.sleep(1)
        Logger.trace("this is a trace message")
        Logger.debug("this is a debug message")
        Logger.info("this is a info message")
        Logger.warn("this is a warn message")
        Logger.error("this is a error message")
        Logger.fatal("this is a fatal message")
        Logger.report("this is a report message")


def __main__():
    setproctitle.setproctitle('MonitorMaster')
    if not Logger.init("develop", "logs", 'test', 1024, 10, lock):
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
    end = time.time()
    print end - start



if __name__ == '__main__':
    __main__()
