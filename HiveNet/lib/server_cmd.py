#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
服务端命令行处理
@module server_cmd
@file server_cmd.py
"""

import sys
import os
import shutil
import logging
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.simple_i18n import _
from HiveNetLib.simple_console.base_cmd import CmdBaseFW
from HiveNetLib.generic import CResult
from HiveNetLib.simple_xml import SimpleXml
from HiveNetLib.simple_log import Logger
from HiveNetLib.base_tools.import_tool import ImportTool
from HiveNetLib.simple_grpc.grpc_server import SimpleGRpcServicer, SimpleGRpcServer
from HiveNetLib.simple_grpc.grpc_tool import EnumCallMode, SimpleGRpcTools
from HiveNetLib.base_tools.exception_tool import ExceptionTool
from HiveNetLib.base_tools.file_tool import FileTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from HiveNet.lib.hivenet_tool import HiveNetTool
from HiveNet.lib.installer import BaseInstaller


__MOUDLE__ = 'server_cmd'  # 模块名
__DESCRIPT__ = u'服务端命令行处理'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2019.12.26'  # 发布日期


class ServerCmd(CmdBaseFW):
    """
    HiveNet 服务端处理命令
    """
    #############################
    # 内部变量定(函数内定义)
    # _logger # 日志对象
    # _engine_server  # 引擎服务实例对象
    # _servicer  # gRPC服务处理类
    # _server  # gRPC服务器
    # _server_opts  # gRPC服务启动参数
    # _server_config  # 配置文件路径
    # _config_dict  # 配置文件字典
    # ENGINE_CONFIG  # 引擎服务配置
    #############################

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
            'server': self._server_cmd_dealfun,
            'start': self._start_cmd_dealfun,
            'stop': self._stop_cmd_dealfun
        }
        self._console_global_para = RunTool.get_global_var('CONSOLE_GLOBAL_PARA')

        self._server_config = ''
        if kwargs is not None and 'server_config' in kwargs.keys() and kwargs['server_config'] != '':
            # 传入配置文件路径
            self._server_config = os.path.realpath(kwargs['server_config'])
        else:
            self._server_config = os.path.join(
                self._console_global_para['execute_file_path'], 'conf/server.xml'
            )

        # 设置通用工具对象全局变量
        RunTool.set_global_var('HIVENET_TOOL', HiveNetTool())

        # 初始化参数
        self.ENGINE_CONFIG = None
        self._engine_server = None
        self._engine_server_class = None
        self._config_dict = None
        self._init_engine_server()

        # 设置引擎服务处理对象的全局变量
        RunTool.set_global_var('ENGINE_SERVER', self._engine_server)

        self._logger = None
        if self._config_dict['use_cmd_logger'] == 'true':
            self._logger = self._prompt_obj._prompt_default_para['logger']
        elif 'logger' in self._config_dict.keys():
            self._logger = Logger.create_logger_by_dict(
                self._config_dict['logger'])

        if self._config_dict['remote_service']['remote_support'] == 'true':
            # 创建gRPC处理服务
            self._crearte_grpc_server()

    def start_grpc_server(self):
        """
        启动grpc服务

        @returns {CResult} - 启动结果，result.code：'00000'-成功，'21401'-服务不属于停止状态，不能启动，其他-异常
            '21403' - 服务不存在（remote-support为false的情况）
        """
        if hasattr(self, '_server') and self._server is not None:
            _result = self._server.start_server(
                self._server_opts, servicer_list={'console_servicer': self._servicer},
                is_wait=True
            )
        else:
            _result = CResult(
                code='21403',
                i18n_msg_paras=('GrpcServer')
            )

        if _result.is_success():
            self._prompt_obj.prompt_print(_('start remote grpc server success'))
        else:
            self._prompt_obj.prompt_print('%s: [%s] %s %s' % (
                _('start remote grpc server error'),
                _result.code, _result.msg, '\n' + _result.trace_str
            ))
        # 返回结果
        return _result

    def stop_grpc_server(self, is_wait=True, overtime=0):
        """
        停止grpc服务

        @param {bool} is_wait=True - 是否等待服务器所有线程都处理完成后再关闭，True-等待所有线程完成处理，False-强制关闭
        @param {float} overtime=0 - 等待超时时间，单位为秒，0代表一直等待

        @returns {CResult} - 停止结果，result.code：'00000'-成功，'21402'-服务停止失败-服务已关闭，
            '31005'-执行超时，29999'-其他系统失败，'21403' - 服务不存在（remote-support为false的情况）
        """
        if hasattr(self, '_server') and self._server is not None:
            _result = self._server.stop_server(
                is_wait=is_wait, overtime=overtime
            )
        else:
            _result = CResult(
                code='21403',
                i18n_msg_paras=('GrpcServer')
            )
        # 显示输出
        if _result.is_success():
            self._prompt_obj.prompt_print(_('stop remote grpc server success'))
        else:
            self._prompt_obj.prompt_print('%s: [%s] %s %s' % (
                _('stop remote grpc server error'),
                _result.code, _result.msg, '\n' + _result.trace_str
            ))
        # 返回结果
        return _result

    def start_engine_server(self, reinit=False):
        """
        启动engine服务
        @param {bool} reinit=False - 是否重新初始化对象

        @returns {CResult} - 启动结果，result.code：'00000'-成功，'21401'-服务不属于停止状态，不能启动，其他-异常
            '21403' - 服务不存在（没有送入engine对象的情况）
        """
        _result = CResult('00000')
        if self._engine_server is not None:
            if reinit:
                # 重新加载对象
                if self._engine_server._is_running:
                    return CResult('21401', msg='%s [%s] %s!' % (
                        _('engine server'), self._engine_server._id, _('has started')

                    ))

                with ExceptionTool.ignored_cresult(
                    result_obj=_result, logger=self._logger,
                    self_log_msg=_('force start engine server [$1] error', self._engine_server._id)
                ):
                    self._init_engine_server()

            # 启动服务
            _result = self._engine_server.start(is_wait=True)
        else:
            _result = CResult(
                code='21403',
                i18n_msg_paras=('EngineServer')
            )

        if _result.is_success():
            self._prompt_obj.prompt_print(_('start engine server success'))
        else:
            self._prompt_obj.prompt_print('%s: [%s] %s %s' % (
                _('start engine server error'),
                _result.code, _result.msg, '\n' + _result.trace_str
            ))
        # 返回结果
        return _result

    def stop_engine_server(self, is_wait=True, overtime=0):
        """
        停止engine服务

        @param {bool} is_wait=True - 是否等待服务器所有线程都处理完成后再关闭，True-等待所有线程完成处理，False-强制关闭
        @param {float} overtime=0 - 等待超时时间，单位为秒，0代表一直等待

        @returns {CResult} - 停止结果，result.code：'00000'-成功，'21402'-服务停止失败-服务已关闭，
            '31005'-执行超时，29999'-其他系统失败，'21403' - 服务不存在（没有送入engine对象的情况）
        """
        if self._engine_server is not None:
            _result = self._engine_server.stop(
                is_wait=is_wait, overtime=overtime
            )
        else:
            _result = CResult(
                code='21403',
                i18n_msg_paras=('EngineServer')
            )
        # 显示输出
        if _result.is_success():
            self._prompt_obj.prompt_print(_('stop engine server success'))
        else:
            self._prompt_obj.prompt_print('%s: [%s] %s %s' % (
                _('stop engine server error'),
                _result.code, _result.msg, '\n' + _result.trace_str
            ))
        # 返回结果
        return _result

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
            # 退出, 先看看是否有启动服务，如果有先关闭服务
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
        _result = CResult(code='00000')

        # 服务端处理先启动引擎服务
        if self._server_config_dict['auto_start_engine'] == 'true':
            _engine_result = self.start_engine_server()
            if not _engine_result.is_success():
                _result = _engine_result

        # 再启动远程服务支持
        if self._server_config_dict['auto_start_remote'] == 'true':
            _grpc_result = self.start_grpc_server()
            if not _grpc_result.is_success():
                _result = _grpc_result

        return _result

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
        if self._engine_server is not None:
            self._prompt_obj.prompt_print(
                _('current engine server id is [$1]', self._engine_server._id))
        else:
            self._prompt_obj.prompt_print(_('not init engine server yet'))

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
        _result = CResult(code='00000')
        _cmd_para = cmd_para.lstrip().rstrip()
        _paras = _cmd_para.split(' ')

        if _paras[0] == 'remote':
            _result = self.start_grpc_server()
            _name = _('remote console server')
        elif _paras[0] == 'engine':
            _name = _('engine server')
            if _paras[len(_paras) - 1] == '-f':
                _result = self.start_engine_server(reinit=True)
            else:
                _result = self.start_engine_server()
        else:
            prompt_obj.prompt_print(_('unsupport start para [$1]!', _cmd_para))
            return CResult(code='11001')

        if _result.is_success():
            prompt_obj.prompt_print('%s %s!' % (_name, _('start success')))
        else:
            prompt_obj.prompt_print(
                '%s %s: [%s]%s%s' % (
                    _name, _('start error'),
                    _result.code, _result.msg, '\n' + _result.trace_str
                )
            )

        return _result

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
        _result = CResult(code='00000')
        _cmd_para = cmd_para.lstrip().rstrip()

        if _cmd_para == 'remote':
            _result = self.stop_grpc_server(
                is_wait=True, overtime=0
            )
            _name = _('remote console server')
        elif _cmd_para == 'engine':
            _name = _('engine server')
            _result = self.stop_engine_server(is_wait=True, overtime=0)
        else:
            prompt_obj.prompt_print(_('unsupport stop para [$1]!', _cmd_para))
            return CResult(code='11001')

        if _result.is_success():
            prompt_obj.prompt_print('%s %s!' % (_name, _('stop success')))
        else:
            prompt_obj.prompt_print('%s %s: [%s]%s%s' % (
                _name, _('stop error'),
                _result.code, _result.msg, '\n' + _result.trace_str
            ))

        return _result

    #############################
    # 内部函数
    #############################
    def _init_engine_server(self):
        """
        加载配置文件并初始化引擎服务对象
        """
        self._config_dict = SimpleXml(
            self._server_config, encoding=self._console_global_para['config_encoding']).to_dict()['server']

        # 修正字典
        self._correct_config_dict(self._config_dict)

        # 设置引擎配置全局变量
        self.ENGINE_CONFIG = RunTool.get_global_var('ENGINE_CONFIG')
        if self.ENGINE_CONFIG is None:
            self.ENGINE_CONFIG = dict()
            RunTool.set_global_var('ENGINE_CONFIG', self.ENGINE_CONFIG)

        self.ENGINE_CONFIG['server_config'] = self._config_dict['engine_server']

        # 基础路径设置
        self.ENGINE_CONFIG['website_path'] = os.path.abspath(
            self.ENGINE_CONFIG['server_config']['website']['root'])
        self.ENGINE_CONFIG['static_path'] = os.path.abspath(os.path.join(
            self.ENGINE_CONFIG['website_path'],
            self.ENGINE_CONFIG['server_config']['website']['static']
        ))
        self.ENGINE_CONFIG['server_path'] = os.path.abspath(
            self.ENGINE_CONFIG['server_config']['bg_server']['root']
        )
        self.ENGINE_CONFIG['temp_path'] = os.path.abspath(
            self.ENGINE_CONFIG['server_config']['bg_server']['temp']
        )

        # 创建基础路径
        self._check_base_path()

        # 设置已安装控件/应用库/应用的全局变量
        _INSTALLED_DOC = SimpleXml(os.path.join(
            self.ENGINE_CONFIG['server_path'], 'installed/installed_list.xml'))
        RunTool.set_global_var('INSTALLED_DOC', _INSTALLED_DOC)

        # 设置基础控件的全局变量(基于installed_list.xml的base_control_config)
        _tool: HiveNetTool = RunTool.get_global_var('HIVENET_TOOL')
        _base_control_dict = _INSTALLED_DOC.to_dict(
            '/installed/base_control_config')['base_control_config']
        _BASE_CONTROL = RunTool.get_global_var('BASE_CONTROL')

        if _BASE_CONTROL is not None:
            # 清空IMPORT_SERVICER字典
            _tool.get_base_control_class('Installer').clear_import_servicer_dict()
            _BASE_CONTROL.clear()
        else:
            _BASE_CONTROL = dict()
            RunTool.set_global_var('BASE_CONTROL', _BASE_CONTROL)

        _tool.register_base_control(_base_control_dict)
        _installer: BaseInstaller = _tool.get_base_control_class('Installer')  # 获取到的是默认控件，需要安装最新控件
        if _BASE_CONTROL['Installer']['control_name'] != '':
            # 安装相应版本的控件
            _installed_dict = None
            _match_ver = _installer.get_installed_match_version(
                'Control', _BASE_CONTROL['Installer']['control_name'],
                _BASE_CONTROL['Installer']['control_version']
            )
            if _match_ver != '':
                _installed_dict = _installer.get_installed_dict(
                    'Control', _BASE_CONTROL['Installer']['control_name'],
                    _match_ver
                )

            if _installed_dict is not None:
                # 先执行装载，注意不执行任何装载的处理
                _installer.import_servicer(
                    'Control', _BASE_CONTROL['Installer']['control_name'], _match_ver,
                    _installed_dict['servicer'], run_after_import=False, run_after_install=False
                )

                # 重新获取一次installer对象
                _installer: BaseInstaller = _tool.get_base_control_class('Installer')

        # 装载已安装后台服务
        _installer.import_installed_servicers()

        # 包节点处理路由基础服务
        RunTool.set_global_var(
            'PACKAGE_NODE_ROUTER',
            _tool.get_base_control_class('PackageNodeRouter')()
        )

        # 装载引擎服务模块库
        _module_name = self._config_dict['engine_server']['module']['module_name']
        _class_name = self._config_dict['engine_server']['module']['class_name']
        _extend_path = self._config_dict['engine_server']['module']['extend_path']
        self._engine_server_class = None
        if ImportTool.check_module_imported(_module_name):
            # 模块已存在
            self._engine_server_class = ImportTool.get_member_from_module(
                ImportTool.get_imported_module(_module_name),
                _class_name
            )
        else:
            # 动态装载模块
            self._engine_server_class = ImportTool.get_member_from_module(
                ImportTool.import_module(
                    _module_name,
                    extend_path=_extend_path
                ),
                _class_name
            )

        if self._engine_server_class is None:
            raise ImportError(
                '%s: %s' % (
                    _('config file [$1] error', self._server_config),
                    _("can't import engine_server module")
                )
            )

        # 初始化引擎服务对象
        self._engine_server = self._engine_server_class(
            self._config_dict['engine_server']['name'], self._config_dict['engine_server'])

    def _correct_config_dict(self, config_dict):
        """
        修正传入的参数字典

        @param {dict} config_dict - 要修正的参数字典
        """
        # website 网站路径配置
        config_dict['engine_server'].setdefault(
            'website',
            {'root': os.path.join(os.getcwd(), 'website/'), 'static': 'static/'}
        )
        config_dict['engine_server']['website'].setdefault(
            'root', os.path.join(os.getcwd(), 'website/'))
        config_dict['engine_server']['website'].setdefault('static', 'static/')

        # bg_server 后台服务配置
        config_dict['engine_server'].setdefault(
            'bg_server',
            {
                'root': os.path.join(os.getcwd(), 'server/'),
                'temp': os.path.join(os.getcwd(), 'server/', 'temp/')
            }
        )
        config_dict['engine_server']['bg_server'].setdefault(
            'root', os.path.join(os.getcwd(), 'server/'))
        config_dict['engine_server']['bg_server'].setdefault(
            'temp', os.path.join(os.getcwd(), 'server/', 'temp/'))

    def _crearte_grpc_server(self):
        """
        创建grpc服务器
        """
        # grpc处理服务
        self._servicer = SimpleGRpcServicer(
            logger=self._logger,
            log_level=logging.INFO,
            is_use_global_logger=False
        )
        self._servicer.add_service(
            call_mode=EnumCallMode.ServerSideStream,
            name='remote_call',
            fun=self._remote_call,
            recv_logging_para={},
            resp_logging_para={}
        )

        # gRPC 服务启动参数
        _is_use_ssl = (self._config_dict['remote_service']['is_use_ssl'] == 'true')
        _private_key_certificate_chain_pairs = None
        _root_certificates = None
        if _is_use_ssl:
            # 服务器密钥证书对
            if len(self._config_dict['remote_service']['private_key_certificate_chain_pairs']) > 0:
                _private_key_certificate_chain_pairs = list()
                for _item in self._config_dict['remote_service']['private_key_certificate_chain_pairs']:
                    _private_key_certificate_chain_pairs.append(
                        SimpleGRpcTools.get_private_key_certificate_chain_pair(
                            key_file=_item['key_file'],
                            crt_file=_item['cert_file']
                        )
                    )
            # 客户端反向认证证书
            if self._config_dict['remote_service']['root_certificates'] != '':
                with open(self._config_dict['remote_service']['root_certificates'], 'rb') as f:
                    _root_certificates = f.read()

        self._server_opts = SimpleGRpcServer.generate_server_opts(
            ip=self._config_dict['remote_service']['ip'],
            port=int(self._config_dict['remote_service']['port']),
            max_workers=int(self._config_dict['remote_service']['max_workers']),
            max_connect=int(self._config_dict['remote_service']['max_connect']),
            is_health_check=(
                self._config_dict['remote_service']['is_health_check'] == 'true'),
            is_use_ssl=_is_use_ssl,
            private_key_certificate_chain_pairs=_private_key_certificate_chain_pairs,
            root_certificates=_root_certificates
        )

        # gRPC Server
        self._server = SimpleGRpcServer(
            logger=self._logger,
            log_level=logging.INFO,
            server_name='ConsoleRemoteServer'
        )

    def _remote_call(self, cmd, cmd_para, **kwargs):
        """
        执行远程调用命令

        @param {string} cmd - 远程调用命令
        @param {string} cmd_para - 远程调用命令参数

        @return {string_iter} - 返回需要向远端显示的内容序列
        """
        self._CMD_PARA = self._console_global_para['CMD_PARA']
        if cmd in self._CMD_PARA.keys():
            return self._CMD_PARA[cmd]['deal_fun'](message='', cmd=cmd, cmd_para=cmd_para, prompt_obj=self._prompt_obj)
        else:
            return CResult(code='11404', msg="'$1' is not support command!", i18n_msg_paras=(cmd, ))

    def _check_base_path(self):
        """
        检查并创建基础目录
        """
        # 静态资源目录
        _path = os.path.join(self.ENGINE_CONFIG['static_path'], 'applib')
        if not os.path.exists(_path):
            FileTool.create_dir(_path)

        _path = os.path.join(self.ENGINE_CONFIG['static_path'], 'control')
        if not os.path.exists(_path):
            FileTool.create_dir(_path)

        _path = os.path.join(self.ENGINE_CONFIG['static_path'], 'app')
        if not os.path.exists(_path):
            FileTool.create_dir(_path)

        # 后台资源目录
        _path = os.path.join(self.ENGINE_CONFIG['server_path'], 'resources/applib')
        if not os.path.exists(_path):
            FileTool.create_dir(_path)

        _path = os.path.join(self.ENGINE_CONFIG['server_path'], 'resources/control')
        if not os.path.exists(_path):
            FileTool.create_dir(_path)

        _path = os.path.join(self.ENGINE_CONFIG['server_path'], 'resources/app')
        if not os.path.exists(_path):
            FileTool.create_dir(_path)

        # 已安装控件目录
        _path = os.path.join(self.ENGINE_CONFIG['server_path'], 'installed/applib')
        if not os.path.exists(_path):
            FileTool.create_dir(_path)

        _path = os.path.join(self.ENGINE_CONFIG['server_path'], 'installed/control')
        if not os.path.exists(_path):
            FileTool.create_dir(_path)

        _path = os.path.join(self.ENGINE_CONFIG['server_path'], 'installed/installed_list.xml')
        if not os.path.exists(_path):
            # 没有安装文件配置, 复制一个默认配置过去
            shutil.copyfile(
                os.path.join(
                    self._console_global_para['execute_file_path'], 'default_config_xml/installed_list.xml'
                ),
                _path
            )

        # 临时文件处理目录
        if not os.path.exists(self.ENGINE_CONFIG['temp_path']):
            FileTool.create_dir(self.ENGINE_CONFIG['temp_path'])


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
