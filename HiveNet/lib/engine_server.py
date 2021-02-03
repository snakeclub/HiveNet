#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2018 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import os
import copy
import logging
import subprocess
import time
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.process
import platform
import threading
import asyncio
import ssl
from abc import ABC, abstractmethod  # 利用abc模块实现抽象类
from HiveNetLib.generic import CResult
from HiveNetLib.base_tools.exception_tool import ExceptionTool
from HiveNetLib.base_tools.string_tool import StringTool
from HiveNetLib.base_tools.file_tool import FileTool
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.simple_log import Logger
from HiveNetLib.simple_xml import SimpleXml, EnumXmlObjType
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from HiveNet.lib.tornado_handler import MainHandler, HiveNetStaticHandler, HiveNetErrorHandler
from HiveNet.lib.dealer_router import ServicerRouter

"""
HiveNet 引擎服务容器模块
@module server
@file server.py
"""

__MOUDLE__ = 'server'  # 模块名
__DESCRIPT__ = u'服务容器处理模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2019.09.22'  # 发布日期


class EngineServerFW(ABC):
    """
    服务容器处理处理框架
    定义标准的服务容器处理方法
    """
    #############################
    # 内部变量
    # _id : 服务器id
    # ENGINE_CONFIG : 服务引擎的配置字典
    #############################
    _config = None  # 服务器的初始化参数字典
    _is_running = False  # 是否已启动，注意继承对象应更新该状态变量

    #############################
    # 类函数
    #############################
    @classmethod
    def correct_config(cls):
        """
        修正服务器的初始化参数

        @param {dict} server_config_dict - 服务器的初始化参数
        """
        return

    #############################
    # 公共函数
    #############################

    def __init__(self, id, server_config_dict):
        """
        构造函数

        @param {string} id - 服务器id
        @param {dict} server_config_dict - 服务器的初始化参数
        """
        # 避免内部处理影响传入的参数对象
        self._config = server_config_dict
        self.correct_config()  # 自身的字典修正
        self._correct_config()  # 继承类的字典修正
        self._id = id

        # 引擎配置全局变量
        self.ENGINE_CONFIG = RunTool.get_global_var('ENGINE_CONFIG')

        # 调用继承类的自定义初始化函数
        self._init()

    def start(self, is_wait=False):
        """
        启动服务器及应用

        @param {bool} is_wait=False - 是否等待服务启动完成后再退出

        @returns {CResult} - 启动结果，result.code：'00000'-成功，'21401'-服务不属于停止状态，不能启动，其他-异常
        """
        return self._start(is_wait=is_wait)

    def stop(self, is_wait=True, overtime=0):
        """
        停止服务器及应用

        @param {bool} is_wait=True - 是否等待服务器所有处理完成后再关闭，True-等待所有处理完成，False-强制关闭
        @param {float} overtime=0 - 等待超时时间，单位为秒，0代表一直等待

        @returns {CResult} - 停止结果，result.code：'00000'-成功，'21402'-服务停止失败-服务已关闭，
            '31005'-执行超时，'29999'-其他系统失败
        """
        return self._stop(is_wait=is_wait, overtime=overtime)

    #############################
    # 内部函数
    #############################

    #############################
    # 需要重载的函数
    #############################

    def _correct_config(self):
        """
        修正服务器的初始化参数
        继承类可以修改该函数，利用setdefault进行参数的补全和修正
        """
        pass

    @abstractmethod
    def _init(self):
        """
        继承类自定义的初始化处理函数
        """
        raise NotImplementedError

    @abstractmethod
    def _start(self, is_wait=False):
        """
        继承类自定义启动服务器及应用处理函数

        @param {bool} is_wait=False - 是否等待服务启动完成后再退出

        @returns {CResult} - 启动结果，result.code：'00000'-成功，'21401'-服务不属于停止状态，不能启动，其他-异常
        """
        raise NotImplementedError

    @abstractmethod
    def _stop(self, is_wait=True, overtime=0):
        """
        继承类自定义停止服务器及应用

        @param {bool} is_wait=True - 是否等待服务器所有处理完成后再关闭，True-等待所有处理完成，False-强制关闭
        @param {float} overtime=0 - 等待超时时间，单位为秒，0代表一直等待

        @returns {CResult} - 停止结果，result.code：'00000'-成功，'21402'-服务停止失败-服务已关闭，
            '31005'-执行超时，'29999'-其他系统失败
        """
        raise NotImplementedError


class TornadoServer(EngineServerFW):
    #############################
    # 内部变量
    # _app : Tornado应用对象
    # _http_server : Tornado的http服务对象
    # _instance : tornado异步io服务实例
    # _setting : Tornado的路由配置
    # _logger : 日志对象
    #############################
    _instance = None

    #############################
    # 重载服务类对象
    #############################
    def _init(self):
        """
        继承类自定义的初始化处理函数
        """
        # 日志对象
        self._logger = None
        if 'logger' in self._config.keys():
            self._logger = Logger.create_logger_by_dict(
                self._config['logger'])

        # Tornado应用路由配置
        # 设置静态路径
        self._setting = {
            # 'static_path': ENGINE_CONFIG['static_path'],
            # 设置URL匹配不到路由时的默认错误处理类
            'default_handler_class': HiveNetErrorHandler,
            'default_handler_args': {"status_code": 404},
        }
        self._app = tornado.web.Application([
            (r"/", MainHandler),
            (r"/static/(.*)", HiveNetStaticHandler, {"path": self.ENGINE_CONFIG['static_path']}),
            (r"/api/(.*)", MainHandler),  # RestFul Api访问
        ], **self._setting)

        if self._config['api']['sub_domain'] != '':
            # 通过二级域名访问RestFul Api
            self._app.add_handlers(self._config['api']['sub_domain'], r"/", MainHandler)

        # SSL配置
        self._ssl_options = None
        if self._config['extend']['is_use_ssl'] == 'true':
            # _ssl_options = {
            #     'certfile': os.path.abspath(self._config['extend']['cert_file']),
            #     'keyfile': os.path.abspath(self._config['extend']['key_file'])
            # }
            self._ssl_options = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self._ssl_options.load_cert_chain(
                os.path.abspath(self._config['extend']['cert_file']),
                os.path.abspath(self._config['extend']['key_file'])
            )

    def _start(self, is_wait=False):
        """
        继承类自定义启动服务器及应用处理函数

        @param {bool} is_wait=False - 是否等待服务启动完成后再退出

        @returns {CResult} - 启动结果，result.code：'00000'-成功，'21401'-服务不属于停止状态，不能启动，其他-异常
        """
        if self._is_running:
            return CResult('21401', msg='engine server [%s] 已启动!')

        _result = CResult(code='00000')
        with ExceptionTool.ignored_cresult(
            result_obj=_result, logger=self._logger,
            self_log_msg='start engine server [%s] error' % self._id
        ):
            self._server_thread = threading.Thread(
                target=self.__start_server_thread_fun,
                args=(1,),
                name='Thread-Engine-Server'
            )
            self._server_thread.setDaemon(True)
            self._server_thread.start()

        # 登记标签
        if _result.is_success():
            self._is_running = True

        # 返回结果
        return _result

    def __start_server_thread_fun(self, id):
        """
        启动Tornado服务的线程

        @param {int} id - 线程id
        """
        asyncio.set_event_loop(asyncio.new_event_loop())  # 在线程中启动tornado会有问题，需要增加这行适配
        _result = CResult(code='00000')
        with ExceptionTool.ignored_cresult(
            result_obj=_result, logger=self._logger,
            self_log_msg='engine server [%s] error' % self._id
        ):
            # HTTP服务配置
            if platform.system() != 'Windows':
                tornado.process.fork_processes(int(self._config['extend']['process_num']))
            self._http_server = tornado.httpserver.HTTPServer(
                self._app, ssl_options=self._ssl_options)
            self._http_server.bind(
                int(self._config['extend']['port']),
                address=(
                    None if self._config['extend']['ip'] == '' else self._config['extend']['ip']
                )
            )
            self._is_running = True
            self._http_server.start()  # 注意这行必须要早于tornado.ioloop.IOLoop.instance()执行，否则无法正常服务
            self._instance = tornado.ioloop.IOLoop.instance()
            self._instance.start()

        # 结束处理
        self._is_running = False

    def _stop(self, is_wait=True, overtime=0):
        """
        继承类自定义停止服务器及应用

        @param {bool} is_wait=True - 是否等待服务器所有处理完成后再关闭，True-等待所有处理完成，False-强制关闭
        @param {float} overtime=0 - 等待超时时间，单位为秒，0代表一直等待

        @returns {CResult} - 停止结果，result.code：'00000'-成功，'21402'-服务停止失败-服务已关闭，
            '31005'-执行超时，'29999'-其他系统失败
        """
        if not self._is_running:
            return CResult('21402', 'engine server [%s] 已关闭!')
        # 需要用线程启动
        _result = CResult(code='00000')
        with ExceptionTool.ignored_cresult(
            result_obj=_result, logger=self._logger,
            self_log_msg='stop engine server [%s] error' % self._id
        ):
            self._http_server.stop()
            self._instance.stop()

        # 登记标签
        if _result.is_success():
            self._is_running = False

        # 返回结果
        return _result

    #############################
    # 内部函数
    #############################


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
