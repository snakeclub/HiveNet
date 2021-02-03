#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
客户端控制台命令处理模块
@module client_cmd
@file client_cmd.py
"""

import sys
import os
import logging
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.simple_i18n import _
from HiveNetLib.simple_console.base_cmd import CmdBaseFW
from HiveNetLib.generic import CResult
from HiveNetLib.simple_xml import SimpleXml
from HiveNetLib.simple_log import Logger
from HiveNetLib.simple_grpc.grpc_client import SimpleGRpcConnection
from HiveNetLib.simple_grpc.grpc_tool import EnumCallMode, SimpleGRpcTools
from HiveNetLib.base_tools.exception_tool import ExceptionTool
from HiveNetLib.base_tools.string_tool import StringTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


__MOUDLE__ = 'client_cmd'  # 模块名
__DESCRIPT__ = u'客户端控制台命令处理模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2019.12.23'  # 发布日期


class ClientCmd(CmdBaseFW):
    """
    HiveNet 客户端处理命令
    """
    #############################
    # 内部变量定(函数内定义)
    # _logger # 日志对象
    # _client_config_dict # 服务器的初始化参数字典（console_server节点）
    #############################
    _current_server_id = ''  # 当前正在连接的服务端id

    #############################
    # 构造函数，在里面增加函数映射字典
    #############################

    def _init(self, **kwargs):
        """
        实现类需要覆盖实现的初始化函数

        @param {kwargs} - 传入初始化参数字典（config.xml的init_para字典）

        @throws {exception-type} - 如果初始化异常应抛出异常
        """
        self._CMD_DEALFUN_DICT = {
            '{{auto_run}}': self._auto_run_cmd_dealfun,
            'connect': self._connect_cmd_dealfun,
            'disconnect': self._disconnect_cmd_dealfun,
            'list': self._list_cmd_dealfun,
            'server': self._server_cmd_dealfun,
            'start': self._start_cmd_dealfun,
            'stop': self._stop_cmd_dealfun
        }
        self._console_global_para = RunTool.get_global_var('CONSOLE_GLOBAL_PARA')

        _client_config = ''
        if kwargs is not None and 'client_config' in kwargs.keys() and kwargs['client_config'] != '':
            # 传入配置文件路径
            _client_config = os.path.realpath(kwargs['client_config'])
        else:
            _client_config = os.path.join(
                self._console_global_para['execute_file_path'], 'conf/client.xml'
            )

        # 初始化参数
        self._config_dict = SimpleXml(
            _client_config, encoding=self._console_global_para['config_encoding']).to_dict()['console']

        self._logger = None
        if self._config_dict['use_cmd_logger'] == 'true':
            self._logger = self._prompt_obj._prompt_default_para['logger']
        elif 'logger' in self._config_dict.keys():
            self._logger = Logger.create_logger_by_dict(
                self._config_dict['logger'])

        # 客户端处理
        self._config_dict['servers'] = dict()

        for _server in self._config_dict['server_list']:
            # 创建控制台服务访问字典
            self._config_dict['servers'][_server['id']] = _server

    def _init_after_console_init(self):
        """
        实现类需要覆盖实现的simple_console初始化后要执行的函数
        """
        self._console_global_para['CMD_PARA']['connect']['word_para'] = dict()
        for _server in self._config_dict['server_list']:
            # connect的提示
            self._console_global_para['CMD_PARA']['connect']['word_para'][_server['id']] = None

    #############################
    # 实际处理函数
    #############################

    def _cmd_dealfun(self, message='', cmd='', cmd_para='', prompt_obj=None, **kwargs):
        """
        通用处理函数，通过cmd区别调用实际的处理函数

        @param {string} message='' - prompt提示信息
        @param {string} cmd - 执行的命令key值
        @param {string} cmd_para - 传入的命令参数（命令后的字符串，去掉第一个空格）
        @param {PromptPlus} prompt_obj=None - 传入调用函数的PromptPlus对象，可以通过该对象的一些方法控制输出显示
        @param {kwargs} - 传入的主进程的初始化kwargs对象

        @returns {CResult} - 命令执行结果，可通过返回错误码10101通知框架退出命令行, 同时也可以通过CResult对象的
            print_str属性要求框架进行打印处理
        """
        # 获取真实执行的函数
        self._prompt_obj = prompt_obj  # 传递到对象内部处理
        _real_dealfun = None  # 真实调用的函数
        if cmd == '{{on_exit}}':
            _real_dealfun = self._on_exit_cmd_dealfun
        else:
            if 'ignore_case' in kwargs.keys() and kwargs['ignore_case']:
                # 区分大小写
                if cmd in self._CMD_DEALFUN_DICT.keys():
                    _real_dealfun = self._CMD_DEALFUN_DICT[cmd]
            else:
                # 不区分大小写
                if cmd.lower() in self._CMD_DEALFUN_DICT.keys():
                    _real_dealfun = self._CMD_DEALFUN_DICT[cmd.lower()]

        # 执行函数
        if _real_dealfun is not None:
            return _real_dealfun(message=message, cmd=cmd, cmd_para=cmd_para, prompt_obj=prompt_obj, **kwargs)
        else:
            prompt_obj.prompt_print(_("'$1' is not support command!", cmd))
            return CResult(code='11404', i18n_msg_paras=(cmd, ))

    #############################
    # 实际处理函数
    #############################
    def _on_exit_cmd_dealfun(self, message='', cmd='', cmd_para='', prompt_obj=None, **kwargs):
        """
        Ctrl + D : exit,关闭命令行

        @param {string} message='' - prompt提示信息
        @param {string} cmd - 执行的命令key值
        @param {string} cmd_para - 传入的命令参数（命令后的字符串，去掉第一个空格）
        @param {PromptPlus} prompt_obj=None - 传入调用函数的PromptPlus对象，可以通过该对象的一些方法控制输出显示
        @param {kwargs} - 传入的主进程的初始化kwargs对象

        @returns {CResult} - 命令执行结果，可通过返回错误码10101通知框架退出命令行, 同时也可以通过CResult对象的
            print_str属性要求框架进行打印处理
        """
        _tip = _('You will shutdown $1 console, continue?(y/N)',
                 self._console_global_para['name'])
        _back = input(_tip)
        if _back.upper() == 'Y':
            # 退出, 先看看是否有链接，如果有则关闭连接
            if self._current_server_id != '':
                self._disconnect_server()
            prompt_obj.prompt_print(_("Exit $1 Console", self._console_global_para['name']))
            return CResult(code='10101')
        else:
            # 取消退出
            prompt_obj.prompt_print(_("Cancel Exit"))
            return CResult(code='00000')

    def _auto_run_cmd_dealfun(self, message='', cmd='', cmd_para='', prompt_obj=None, **kwargs):
        """
        启动命令行框架的自动执行函数

        @param {string} message='' - prompt提示信息
        @param {string} cmd - 执行的命令key值
        @param {string} cmd_para - 传入的命令参数（命令后的字符串，去掉第一个空格）
        @param {PromptPlus} prompt_obj=None - 传入调用函数的PromptPlus对象，可以通过该对象的一些方法控制输出显示
        @param {kwargs} - 传入的主进程的初始化kwargs对象

        @returns {CResult} - 命令执行结果，可通过返回错误码10101通知框架退出命令行, 同时也可以通过CResult对象的
            print_str属性要求框架进行打印处理
        """
        if self._config_dict['auto_connect_server'] != '':
            # 自动连接服务端
            return self._connect_server(self._config_dict['auto_connect_server'])
        else:
            return CResult(code='00000')

    def _connect_cmd_dealfun(self, message='', cmd='', cmd_para='', prompt_obj=None, **kwargs):
        """
        连接服务端控制台

        @param {string} message='' - prompt提示信息
        @param {string} cmd - 执行的命令key值
        @param {string} cmd_para - 传入的命令参数（命令后的字符串，去掉第一个空格）
        @param {PromptPlus} prompt_obj=None - 传入调用函数的PromptPlus对象，可以通过该对象的一些方法控制输出显示
        @param {kwargs} - 传入的主进程的初始化kwargs对象

        @returns {CResult} - 命令执行结果，可通过返回错误码10101通知框架退出命令行, 同时也可以通过CResult对象的
            print_str属性要求框架进行打印处理
        """
        return self._connect_server(cmd_para.lstrip().rstrip())

    def _disconnect_cmd_dealfun(self, message='', cmd='', cmd_para='', prompt_obj=None, **kwargs):
        """
        断开当前的 HiveNet 远程控制台连接

        @param {string} message='' - prompt提示信息
        @param {string} cmd - 执行的命令key值
        @param {string} cmd_para - 传入的命令参数（命令后的字符串，去掉第一个空格）
        @param {PromptPlus} prompt_obj=None - 传入调用函数的PromptPlus对象，可以通过该对象的一些方法控制输出显示
        @param {kwargs} - 传入的主进程的初始化kwargs对象

        @returns {CResult} - 命令执行结果，可通过返回错误码10101通知框架退出命令行, 同时也可以通过CResult对象的
            print_str属性要求框架进行打印处理
        """
        return self._disconnect_server()

    def _list_cmd_dealfun(self, message='', cmd='', cmd_para='', prompt_obj=None, **kwargs):
        """
        列出配置中的远程控制台连接清单

        @param {string} message='' - prompt提示信息
        @param {string} cmd - 执行的命令key值
        @param {string} cmd_para - 传入的命令参数（命令后的字符串，去掉第一个空格）
        @param {PromptPlus} prompt_obj=None - 传入调用函数的PromptPlus对象，可以通过该对象的一些方法控制输出显示
        @param {kwargs} - 传入的主进程的初始化kwargs对象

        @returns {CResult} - 命令执行结果，可通过返回错误码10101通知框架退出命令行, 同时也可以通过CResult对象的
            print_str属性要求框架进行打印处理
        """
        for _server in self._config_dict['server_list']:
            prompt_obj.prompt_print('%s%s%s%s' % (
                StringTool.fill_fix_string(_server['id'], 40, ' ', left=False),
                StringTool.fill_fix_string(_server['ip'], 20, ' ', left=False),
                StringTool.fill_fix_string(_server['port'], 8, ' ', left=False),
                _server['conn_str']
            ))
        return CResult(code='00000')

    def _server_cmd_dealfun(self, message='', cmd='', cmd_para='', prompt_obj=None, **kwargs):
        """
        显示当前连接的服务器名

        @param {string} message='' - prompt提示信息
        @param {string} cmd - 执行的命令key值
        @param {string} cmd_para - 传入的命令参数（命令后的字符串，去掉第一个空格）
        @param {PromptPlus} prompt_obj=None - 传入调用函数的PromptPlus对象，可以通过该对象的一些方法控制输出显示
        @param {kwargs} - 传入的主进程的初始化kwargs对象

        @returns {CResult} - 命令执行结果，可通过返回错误码10101通知框架退出命令行, 同时也可以通过CResult对象的
            print_str属性要求框架进行打印处理
        """

        if self._current_server_id == '':
            self._prompt_obj.prompt_print(_('has not connect to remote console!'))
        else:
            self._prompt_obj.prompt_print(self._current_server_id + '\n')
        return CResult(code='00000')

    def _start_cmd_dealfun(self, message='', cmd='', cmd_para='', prompt_obj=None, **kwargs):
        """
        启动 HiveNet 服务

        @param {string} message='' - prompt提示信息
        @param {string} cmd - 执行的命令key值
        @param {string} cmd_para - 传入的命令参数（命令后的字符串，去掉第一个空格）
        @param {PromptPlus} prompt_obj=None - 传入调用函数的PromptPlus对象，可以通过该对象的一些方法控制输出显示
        @param {kwargs} - 传入的主进程的初始化kwargs对象

        @returns {CResult} - 命令执行结果，可通过返回错误码10101通知框架退出命令行, 同时也可以通过CResult对象的
            print_str属性要求框架进行打印处理
        """
        _cmd_para = cmd_para.lstrip().rstrip()

        # 调用远程服务
        if _cmd_para == 'engine':
            return self._send_to_server(cmd=cmd, cmd_para=cmd_para)
        else:
            prompt_obj.prompt_print(_('unsupport start para [$1]!', _cmd_para))
            return CResult(code='11001')

    def _stop_cmd_dealfun(self, message='', cmd='', cmd_para='', prompt_obj=None, **kwargs):
        """
        关闭 HiveNet 服务

        @param {string} message='' - prompt提示信息
        @param {string} cmd - 执行的命令key值
        @param {string} cmd_para - 传入的命令参数（命令后的字符串，去掉第一个空格）
        @param {PromptPlus} prompt_obj=None - 传入调用函数的PromptPlus对象，可以通过该对象的一些方法控制输出显示
        @param {kwargs} - 传入的主进程的初始化kwargs对象

        @returns {CResult} - 命令执行结果，可通过返回错误码10101通知框架退出命令行, 同时也可以通过CResult对象的
            print_str属性要求框架进行打印处理
        """
        _cmd_para = cmd_para.lstrip().rstrip()
        # 调用远程服务
        if _cmd_para == 'engine':
            return self._send_to_server(cmd=cmd, cmd_para=cmd_para)
        else:
            prompt_obj.prompt_print(_('unsupport stop para [$1]!', _cmd_para))
            return CResult(code='11001')

    #############################
    # 内部函数
    #############################
    def _connect_server(self, server_id):
        """
        连接控制台服务

        @param {string} server_id - 要连接的服务端id
        """
        if self._current_server_id != '':
            _result = CResult(
                code='13001',
                msg=_(
                    "has connected to [$1], please use 'disconnect' to exit the current connection", self._current_server_id)
            )
        if server_id != '' and self._current_server_id == server_id:
            _result = CResult(
                code='13001',
                msg=_("current connection is [$1]", self._current_server_id)
            )
        elif server_id not in self._config_dict['servers'].keys():
            _result = CResult(
                code='13002',
                msg=_("can't find the remote console server [$1] in the config", server_id)
            )
        else:
            _result = CResult('00000')
            with ExceptionTool.ignored_cresult(
                result_obj=_result, logger=self._logger,
                self_log_msg=''
            ):
                # 进行连接
                _para = self._config_dict['servers'][server_id]
                _root_certificates = None
                _private_key = None
                _certificate_chain = None
                if _para['is_use_ssl'] == 'true':
                    if _para['root_certificates'] != '':
                        with open(_para['root_certificates'], 'rb') as f:
                            _root_certificates = f.read()
                    if _para['private_key'] != '':
                        with open(_para['private_key'], 'rb') as f:
                            _private_key = f.read()
                    if _para['certificate_chain'] != '':
                        with open(_para['certificate_chain'], 'rb') as f:
                            _certificate_chain = f.read()
                # 连接参数
                self._connect_para = SimpleGRpcConnection.generate_connect_para(
                    ip=_para['ip'], port=int(_para['port']),
                    conn_str=(None if _para['conn_str'] == '' else _para['conn_str']),
                    timeout=(None if _para['timeout'] == '' else float(_para['timeout'])),
                    is_use_ssl=(_para['is_use_ssl'] == 'true'),
                    root_certificates=_root_certificates,
                    private_key=_private_key, certificate_chain=_certificate_chain,
                    test_on_connect=(_para['test_on_connect'] == 'true'),
                    test_use_health_check=(_para['test_use_health_check'] == 'true'),
                    servicer_name='console_servicer',
                    logger=self._logger,
                    log_level=logging.INFO, is_use_global_logger=False
                )
                self._connect_para1 = SimpleGRpcConnection.generate_connect_para(
                    ip='127.0.0.1', port=50051
                )
                # 进行连接
                self._connection = SimpleGRpcConnection(self._connect_para)
                self._current_server_id = server_id

        if _result.is_success():
            self._prompt_obj.prompt_print(_('connect to [%s] success!', server_id))
        else:
            self._prompt_obj.prompt_print('%s: [%s] %s %s' % (
                _('connect to [$1] error', server_id),
                _result.code, _result.msg, '\n' + _result.trace_str
            ))

        # 返回结果
        return _result

    def _disconnect_server(self):
        """
        客户端断开服务器的连接
        """
        if self._current_server_id == '':
            self._prompt_obj.prompt_print(_('has not connect to remote console!'))
        else:
            _server_id = self._current_server_id
            self._current_server_id = ''
            self._connection.close()
            self._connection = None
            self._prompt_obj.prompt_print(_('disconnect to remote console [$1]!', _server_id))
        # 两种情况都算是成功
        return CResult(code='00000')

    def _send_to_server(self, cmd='', cmd_para=''):
        """
        客户端发送命令到服务端

        @param {string} cmd='' - 命令
        @param {string} cmd_para='' - 命令参数

        @return {CResult} - 服务端返回的显示信息
        """
        if self._current_server_id == '':
            self._prompt_obj.prompt_print(_('has not connect to remote console!'))
            return CResult(code='00000')

        _para_json = SimpleGRpcTools.parameters_to_json(
            [['cmd', cmd], ['cmd_para', cmd_para], ]
        )
        _rpc_request = SimpleGRpcTools.generate_request_obj(
            'remote_call',
            para_json=_para_json.para_json,
            has_para_bytes=_para_json.has_para_bytes,
            para_bytes=_para_json.para_bytes
        )
        _cresult_iterator = self._connection.call(
            _rpc_request,
            call_mode=EnumCallMode.ServerSideStream
        )
        for _result in _cresult_iterator:
            if _result.is_success():
                _real_result = StringTool.json_to_object(_result.return_json, class_ref=CResult)
                if _real_result.is_success():
                    self._prompt_obj.prompt_print(_real_result.msg)
                else:
                    self._prompt_obj.prompt_print('\n%s: [%s]%s%s' % (
                        _('remote call failed'),
                        _real_result.code, _real_result.msg, '\n' + _real_result.trace_str
                    ))
            else:
                self._prompt_obj.prompt_print('\n%s: [%s]%s%s' % (
                    _('remote call failed'),
                    _result.code, _result.msg, '\n' + _result.trace_str
                ))
        return CResult(code='00000')


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
