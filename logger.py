#!/usr/bin/env python2.7
# coding: utf-8

import datetime
import inspect
import threading
import multiprocessing
import setproctitle
from multiprocessing.managers import BaseManager
import os
import traceback
from writer import Writer
from slog import SysLog


class MTBaseManager(BaseManager):
    __MT_MANAGER_NAME = 'MT_MANAGER'

    @classmethod
    def set_manager_name(cls, manager_name):
        cls.__MT_MANAGER_NAME = manager_name

    def __init__(self):
        super(MTBaseManager, self).__init__()

    @classmethod
    def _run_server(cls, registry, address, authkey, serializer, writer,
                    initializer=None, initargs=()):
        setproctitle.setproctitle(cls.__MT_MANAGER_NAME)
        BaseManager._run_server(registry, address, authkey, serializer, writer,
                                initializer, initargs)


class LoggerImpl(object):
    def __init__(self):
        self.TRACE = 0
        self.DEBUG = 1
        self.INFO = 2
        self.WARN = 3
        self.ERROR = 4
        self.FATAL = 5
        self.REPORT = 6
        self.__all_log_level = {
            'trace': self.TRACE,
            'debug': self.DEBUG,
            'info': self.INFO,
            'warn': self.WARN,
            'error': self.ERROR,
            'fatal': self.FATAL,
            'report': self.REPORT,
        }
        self.__process = None
        self.__report = None
        self.__current_log_level = self.INFO

    def init(self, target, file_name, file_size=100 * 1024 * 1024, max_file_count=-1, multiprocess=False):
        try:
            if multiprocess:
                lock = multiprocessing.RLock()
            else:
                lock = threading.RLock()

            if not os.path.exists(target):
                os.makedirs(target)
            if not os.path.exists(target):
                return False

            self.__process = Writer(lock, target, file_name + '.process.log', file_size, max_file_count)
            if not self.__process.open():
                return False
            self.__report = Writer(lock, target, file_name + '.report.log', file_size, max_file_count)
            if not self.__report.open():
                return False

            if not SysLog.open():
                return False
            return True
        except:
            print traceback.format_exc()

    def set_level(self, level):
        if isinstance(level, int):
            if level < self.TRACE or level > self.REPORT:
                return False
            self.__current_log_level = level
            return True

        level_value = self.__all_log_level.get(level, None)
        if level_value is None:
            return False
        self.__current_log_level = level_value
        return True

    def close(self):
        try:
            if not self.__process:
                self.__process.close()
                self.__process = None

            if not self.__report:
                self.__report.close()
                self.__report = None

            SysLog.close()
        except:
            print traceback.format_exc()

    def trace(self, content):
        try:
            if self.TRACE < self.__current_log_level:
                return
            self.__process.write(content)
        except:
            SysLog.error(traceback.format_exc())

    def debug(self, content):
        try:
            if self.DEBUG < self.__current_log_level:
                return
            self.__process.write(content)
        except:
            SysLog.error(traceback.format_exc())

    def info(self, content):
        try:
            if self.INFO < self.__current_log_level:
                return
            self.__process.write(content)
        except:
            SysLog.error(traceback.format_exc())

    def warn(self, content):
        try:
            if self.WARN < self.__current_log_level:
                return
            self.__process.write(content)
        except:
            SysLog.error(traceback.format_exc())

    def error(self, content):
        try:
            if self.ERROR < self.__current_log_level:
                return
            self.__process.write(content)
        except:
            SysLog.error(traceback.format_exc())

    def fatal(self, content):
        try:
            if self.FATAL < self.__current_log_level:
                return
            self.__process.write(content)
        except:
            SysLog.error(traceback.format_exc())

    def report(self, content):
        try:
            if self.REPORT < self.__current_log_level:
                return
            self.__report.write(content)
        except:
            SysLog.error(traceback.format_exc())


class Logger(object):
    # logger env
    __env = None
    # share manager
    __manger = None
    # logger between multiple process
    __logger_instance = None
    """:type: LoggerImpl"""

    @classmethod
    def __join_content(cls, vid, keyword, level, msg):
        try:
            separator = '\x1E'
            the_id = '%s_%s' % (os.getpid(), threading.current_thread().ident)
            content = ''
            content += '[%s]%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), separator)
            content += '[%s]%s' % (level, separator)
            content += '[%s]%s' % (the_id, separator)
            content += '[%s]%s' % (cls.__env, separator)
            content += '[%s]%s' % (vid, separator)
            content += '[%s]%s' % (keyword, separator)
            frame = inspect.currentframe().f_back.f_back
            info = traceback.extract_stack(f=frame, limit=1)[0]
            content += '[%s:%s:%s]%s' % (info[0], info[1], info[2], separator)
            content += '[%s]' % msg
            content += '\n'
            return content
        except:
            SysLog.error(traceback.format_exc())

    @classmethod
    def init(cls, env, target, file_name, file_size=100 * 1024 * 1024, max_file_count=-1, multiprocess=False, logger_name='MTPythonLogger'):
        if multiprocessing:
            MTBaseManager.set_manager_name(logger_name)
            MTBaseManager.register('LoggerImpl', LoggerImpl)
            cls.manager = MTBaseManager()
            cls.manager.start()
            cls.__logger_instance = cls.manager.LoggerImpl()
        else:
            cls.__logger_instance = LoggerImpl()
        cls.__env = env
        return cls.__logger_instance.init(target, file_name, file_size, max_file_count, multiprocess)

    @classmethod
    def set_level(cls, level):
        if cls.__logger_instance:
            cls.__logger_instance.set_level(level)

    @classmethod
    def close(cls):
        if cls.__logger_instance:
            cls.__logger_instance.close()
            cls.__logger_instance = None
        if cls.__manger:
            cls.__manger.shutdown()
            cls.__manger = None

    @classmethod
    def trace(cls, msg, vid='', keyword='normal'):
        content = cls.__join_content(vid=vid, keyword=keyword, level='trace', msg=msg)
        if not content:
            return
        cls.__logger_instance.trace(content)

    @classmethod
    def debug(cls, msg, vid='', keyword='normal'):
        content = cls.__join_content(vid=vid, keyword=keyword, level='debug', msg=msg)
        if not content:
            return
        cls.__logger_instance.debug(content)

    @classmethod
    def info(cls, msg, vid='', keyword='normal'):
        content = cls.__join_content(vid=vid, keyword=keyword, level='info', msg=msg)
        if not content:
            return
        cls.__logger_instance.info(content)

    @classmethod
    def warn(cls, msg, vid='', keyword='normal'):
        content = cls.__join_content(vid=vid, keyword=keyword, level='warn', msg=msg)
        if not content:
            return
        cls.__logger_instance.warn(content)

    @classmethod
    def error(cls, msg, vid='', keyword='normal'):
        content = cls.__join_content(vid=vid, keyword=keyword, level='error', msg=msg)
        if not content:
            return
        cls.__logger_instance.error(content)

    @classmethod
    def fatal(cls, msg, vid='', keyword='normal'):
        content = cls.__join_content(vid=vid, keyword=keyword, level='fatal', msg=msg)
        if not content:
            return
        cls.__logger_instance.fatal(content)

    @classmethod
    def report(cls, msg, vid='', keyword='normal'):
        content = cls.__join_content(vid=vid, keyword=keyword, level='report', msg=msg)
        if not content:
            return
        cls.__logger_instance.report(content)
