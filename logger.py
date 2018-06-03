#!/usr/bin/env python2.7
# coding: utf-8

import datetime
import inspect
import threading
import os
import traceback
import sys
from writter import Writer
from slog import SysLog


class Logger(object):
    __sep = None
    __env = None
    __process = None
    __report = None
    __lock = None
    __thread_local = None

    @classmethod
    def init(cls, env, target, file_name, file_size=100 * 1024 * 1024, max_file_count=-1, lock=None):
        try:
            if lock is None:
                lock = threading.RLock()

            if not os.path.exists(target):
                os.makedirs(target)
            if not os.path.exists(target):
                return False

            cls.__process = Writer(lock, target, file_name + '.process', file_size, max_file_count)
            if not cls.__process.open():
                return False
            cls.__report = Writer(lock, target, file_name + '.report', file_size, max_file_count)
            if not cls.__report.open():
                return False

            cls.__sep = '\x1E'
            cls.__env = env

            cls.__thread_local = threading.local()
            cls.__thread_local.the_id = None
            
            if not SysLog.open():
                return False
            return True
        except:
            print traceback.format_exc()

    @classmethod
    def close(cls):
        try:
            if not cls.__process:
                cls.__process.close()
                cls.__process = None

            if not cls.__report:
                cls.__report.close()
                cls.__report = None
                
            SysLog.close()
        except:
            print traceback.format_exc()

    @classmethod
    def __join_content(cls, vid, keyword, level, msg):
        try:
            if cls.__thread_local.the_id is None:
                the_pid = os.getpid()
                the_tid = threading.current_thread().ident
                cls.__thread_local.the_id = '%s_%s' % (the_pid, the_tid)
            the_id = cls.__thread_local.the_id
            content = ''
            content += '[%s]%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), cls.__sep)
            content += '[%s]%s' % (level, cls.__sep)
            content += '[%s]%s' % (the_id, cls.__sep)
            content += '[%s]%s' % (cls.__env, cls.__sep)
            content += '[%s]%s' % (vid, cls.__sep)
            content += '[%s]%s' % (keyword, cls.__sep)
            frame = inspect.currentframe().f_back.f_back
            info = traceback.extract_stack(f=frame, limit=1)[0]
            content += '[%s:%s:%s]%s' % (info[0], info[1], info[2], cls.__sep)
            content += '[%s]' % msg
            content += '\n'
            return content
        except:
            SysLog.error(traceback.format_exc())

    @classmethod
    def trace(cls, msg, vid='', keyword='normal'):
        try:
            content = cls.__join_content(vid=vid, keyword=keyword, level='info', msg=msg)
            if not content:
                return
            cls.__process.write(content)
        except:
            SysLog.error(traceback.format_exc())

    @classmethod
    def debug(cls, msg, vid='', keyword='normal'):
        try:
            content = cls.__join_content(vid=vid, keyword=keyword, level='debug', msg=msg)
            if not content:
                return
            cls.__process.write(content)
        except:
            SysLog.error(traceback.format_exc())

    @classmethod
    def info(cls, msg, vid='', keyword='normal'):
        try:
            content = cls.__join_content(vid=vid, keyword=keyword, level='info', msg=msg)
            if not content:
                return
            cls.__process.write(content)
        except:
            SysLog.error(traceback.format_exc())

    @classmethod
    def warn(cls, msg, vid='', keyword='normal'):
        try:
            content = cls.__join_content(vid=vid, keyword=keyword, level='warn', msg=msg)
            if not content:
                return
            cls.__process.write(content)
        except:
            SysLog.error(traceback.format_exc())

    @classmethod
    def error(cls, msg, vid='', keyword='normal'):
        try:
            content = cls.__join_content(vid=vid, keyword=keyword, level='error', msg=msg)
            if not content:
                return
            cls.__process.write(content)
        except:
            SysLog.error(traceback.format_exc())

    @classmethod
    def fatal(cls, msg, vid='', keyword='normal'):
        try:
            content = cls.__join_content(vid=vid, keyword=keyword, level='fatal', msg=msg)
            if not content:
                return
            cls.__process.write(content)
        except:
            SysLog.error(traceback.format_exc())

    @classmethod
    def report(cls, msg, vid='', keyword='normal'):
        try:
            content = cls.__join_content(vid=vid, keyword=keyword, level='report', msg=msg)
            if not content:
                return
            cls.__report.write(content)
        except:
            SysLog.error(traceback.format_exc())
