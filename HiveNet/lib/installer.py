#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2018 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import os
import shutil
import logging
import uuid
import re
from HiveNetLib.generic import CResult
from HiveNetLib.simple_i18n import _
from HiveNetLib.base_tools.exception_tool import ExceptionTool
from HiveNetLib.base_tools.file_tool import FileTool
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.base_tools.value_tool import ValueTool
from HiveNetLib.base_tools.import_tool import ImportTool
from HiveNetLib.simple_xml import SimpleXml
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from HiveNet.lib.hivenet_tool import HiveNetTool, MemoryStringStream
from HiveNet.lib.packager import BasePackager

"""
控件库/应用库的安装模块
@module installer
@file installer.py
"""

__MOUDLE__ = 'installer'  # 模块名
__DESCRIPT__ = u'控件库/应用库/HiveNet应用的安装模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2019.11.12'  # 发布日期


class BaseInstaller(object):
    """
    定义控件库/应用库/HiveNet应用的安装框架类
    """
    #############################
    # 装载后台服务相关处理函数
    # IMPORT_SERVICER : 全局变量已导入后台服务字典IMPORT_SERVICER的引用，字典定义如下:
    #    Control : 已导入的控件后台服务字典
    #        [Control_name] : 控件名下已导入的后台服务字典
    #             [version] : 对应控件版本下已导入的后台服务字典
    #                 $as_class_name$ : 类别名转换配置字典
    #                     [call_name] : 涉及转换的访问名
    #                          [AsClassName] : 访问该类的别名，value值为真实类名
    #                 [call_name] : 后台服务的访问名，对应的value值为对应后台服务的模块对象moudle_obj
    #    AppLib : 已导入的应用后台服务
    #        [AppLib_name] : 应用库名下已导入的后台服务字典
    #             [version] : 对应应用版本下已导入的后台服务字典
    #                 $as_class_name$ : 类别名转换配置字典
    #                     [call_name] : 涉及转换的访问名
    #                          [AsClassName] : 访问该类的别名，value值为真实类名
    #                 [call_name] : 后台服务的访问名，对应的value值为对应后台服务的模块对象moudle_obj
    #                 $self_control$ : 自有控件已导入的后台服务字典
    #                     [Control_name] : 控件名下已导入的后台服务字典
    #                         $as_class_name$ : 类别名转换配置字典
    #                             [call_name] : 涉及转换的访问名
    #                                  [AsClassName] : 访问该类的别名，value值为真实类名
    #                         [call_name] : 后台服务的访问名，对应的value值为对应后台服务的模块对象moudle_obj
    #############################
    @classmethod
    def get_import_servicer_dict(cls):
        """
        获取IMPORT_SERVICER字典
        """
        # 从全局变量获取字典
        _IMPORT_SERVICER = RunTool.get_global_var('IMPORT_SERVICER')
        if _IMPORT_SERVICER is None:
            _IMPORT_SERVICER = dict()
            RunTool.set_global_var('IMPORT_SERVICER')

        # 修正字典
        _IMPORT_SERVICER.setdefault('Control', {})
        _IMPORT_SERVICER.setdefault('AppLib', {})

        # 返回字典
        return _IMPORT_SERVICER

    @classmethod
    def clear_import_servicer_dict(cls):
        """
        清空IMPORT_SERVICER字典
        """
        _IMPORT_SERVICER = RunTool.get_global_var('IMPORT_SERVICER')
        if _IMPORT_SERVICER is not None:
            _IMPORT_SERVICER['Control'].clear()
            _IMPORT_SERVICER['AppLib'].clear()

    @classmethod
    def import_installed_servicers(cls):
        """
        装载已安装控件及应用的后台服务
        """
        _INSTALLED_DOC = RunTool.get_global_var('INSTALLED_DOC')

        # 遍历已安装的控件包，装载相应的控件
        _controls = _INSTALLED_DOC.to_dict('/installed/Control_list')['Control_list']
        _sorted_controls = cls._get_sorted_control_list(_controls)
        for _item in _sorted_controls:
            _name = _item[0]
            _ver = _item[1]
            cls._import_installed_package_servicer(
                _controls[_name][_ver],
                run_after_import=True, run_after_install=False
            )

        # 遍历已安装的应用包，装载相应的控件
        _applibs = _INSTALLED_DOC.to_dict('/installed/AppLib_list')['AppLib_list']
        for _name in _applibs.keys():
            for _ver in _applibs[_name].keys():
                if _applibs[_name][_ver].get('install_status', '') != 'done':
                    # 只装载完成状态的节点
                    continue

                cls._import_installed_package_servicer(
                    _controls[_name][_ver],
                    run_after_import=True, run_after_install=False
                )

    @classmethod
    def import_servicer(cls, package_type: str, name: str, version: str, servicer_dict: dict,
                        is_self_control=False, self_control_name='',
                        execution_dict={}, init_para={}, install_para={},
                        run_after_import=True, run_after_install=False):
        """
        装载指定的后台服务

        @param {string} package_type - 类型，目前支持2种类型: Control - 控件包; AppLib - 应用包
        @param {string} name - 控件名或应用名
        @param {string} version - 控件版本号, "主版本号.次版本号.修订版本号"
        @param {dict} servicer_dict - installed_list.xml的servicer节点
        @param {bool} is_self_control=False - 是否私有控件（仅AppLib会使用）
        @param {string} self_control_name='' - 私有控件时，私有控件的名称
        @param {dict} execution_dict={} - 该后台服务对应节点的运行函数配置字典
        @param {dict} init_para={} - 运行after_import函数初始化配置字典
        @param {dict} install_para={} - 运行after_install函数配置字典
        @param {bool} run_after_import=True - 是否运行after_import函数
        @param {bool} run_after_install=False - 是否运行after_install函数
        """
        # as_class_name 类别名转换配置
        cls._import_as_class_name(
            package_type, name, version,
            servicer_dict.get('as_class_name', {}),
            is_self_control=is_self_control, self_control_name=self_control_name
        )

        # 装载后台服务
        cls._import_servicer(
            package_type, name, version,
            servicer_dict,
            is_self_control=is_self_control, self_control_name=self_control_name
        )

        # 运行函数
        if run_after_install and 'after_install' in execution_dict.keys():
            # 执行安装后的运行函数
            _call_name = execution_dict['after_install'].get('call_name', '')
            _class_name = execution_dict['after_install'].get('class_name', '')
            _fun_name = execution_dict['after_install'].get('fun_name', '')
            if _call_name != '':
                cls.execute_import_servicer(
                    package_type, name, version, _call_name, _class_name, _fun_name,
                    run_para=install_para, is_self_control=is_self_control,
                    self_control_name=self_control_name
                )

        if run_after_import and 'after_import' in execution_dict.keys():
            # 执行装载后的运行函数
            _call_name = execution_dict['after_import'].get('call_name', '')
            _class_name = execution_dict['after_import'].get('class_name', '')
            _fun_name = execution_dict['after_import'].get('fun_name', '')
            if _call_name != '':
                cls.execute_import_servicer(
                    package_type, name, version, _call_name, _class_name, _fun_name,
                    run_para=init_para, is_self_control=is_self_control,
                    self_control_name=self_control_name
                )

    @classmethod
    def unimport_servicer(cls, package_type: str, name: str, version: str, servicer_dict: dict,
                          is_self_control=False, self_control_name='', execution_dict={},
                          init_para={}, install_para={}, run_before_uninstall=False):
        """
        卸载指定的后台服务
        注：仅从索引中移除, 不会直接删除模块，如果需要模块也被移除需重启应用

        @param {string} package_type - 类型，目前支持2种类型: Control - 控件包; AppLib - 应用包
        @param {string} name - 控件名或应用名
        @param {string} version - 控件版本号, "主版本号.次版本号.修订版本号"
        @param {dict} servicer_dict - installed_list.xml的servicer节点
        @param {bool} is_self_control=False - 是否私有控件（仅AppLib会使用）
        @param {string} self_control_name='' - 私有控件时，私有控件的名称
        @param {dict} execution_dict={} - 该后台服务对应节点的运行函数配置字典
        @param {dict} init_para={} - 运行函数初始化配置字典
        @param {dict} install_para={} - 运行before_uninstall函数配置字典
        @param {bool} run_before_uninstall=False - 是否运行before_uninstall函数
        """
        _IMPORT_SERVICER = cls.get_import_servicer_dict()

        # 是否先执行函数
        if run_before_uninstall and 'before_uninstall' in execution_dict.keys():
            # 执行卸载前的运行函数
            _call_name = execution_dict['before_uninstall'].get('call_name', '')
            _class_name = execution_dict['before_uninstall'].get('class_name', '')
            _fun_name = execution_dict['before_uninstall'].get('fun_name', '')
            if _call_name != '':
                cls.execute_import_servicer(
                    package_type, name, version, _call_name, _class_name, _fun_name,
                    run_para=install_para, is_self_control=is_self_control,
                    self_control_name=self_control_name
                )

        # 直接删除在全局变量中的信息
        try:
            if package_type == 'AppLib' and is_self_control:
                # 自有控件
                del _IMPORT_SERVICER[package_type][name][version]['$self_control$'][self_control_name]
            else:
                # 控件或应用的后台服务
                del _IMPORT_SERVICER[package_type][name][version]
        except:
            pass

    @classmethod
    def execute_import_servicer(cls, package_type: str, name: str, version: str, call_name: str,
                                class_name: str, fun_name: str, run_para={},
                                is_self_control=False, self_control_name=''):
        """
        执行导入的后台服务

        @param {string} package_type - 类型，目前支持2种类型: Control - 控件包; AppLib - 应用包
        @param {string} name - 控件名或应用名
        @param {string} version - 控件版本号, "主版本号.次版本号.修订版本号"
        @param {string} call_name - 模块使用获取名
        @param {string} class_name - 要执行服务的类名
        @param {string} fun_name - 要只能给服务的函数
            注：class_name和fun_name至少要有一个有值：
            1.如果两个都有值，代表执行指定类的静态函数;
            2.如果仅class_name有值，代表执行类构造函数；
            3.如果仅fun_name有值，代表直接执行包的函数；
        @param {dict} run_para={} - 运行参数
        @param {bool} is_self_control=False - 是否私有控件（仅AppLib会使用）
        @param {string} self_control_name='' - 私有控件时，私有控件的名称
        """
        _fun_obj = None  # 要执行的函数
        if class_name != '':
            # 执行类相关方法
            _class_obj = cls.get_import_servicer_class(
                class_name, package_type, name, version, call_name, is_self_control=is_self_control,
                self_control_name=self_control_name
            )
            if fun_name == '':
                _fun_obj = _class_obj
            else:
                _fun_obj = getattr(_class_obj, fun_name)
        else:
            # 执行模块根函数
            if fun_name == '':
                raise AttributeError('class_name or fun_name at least have one value')

            _module_obj = cls.get_import_servicer_module(
                package_type, name, version, call_name, is_self_control=is_self_control,
                self_control_name=self_control_name
            )
            _fun_obj = getattr(_module_obj, fun_name)

        # 执行函数
        _fun_obj(package_type, name, version, is_self_control, self_control_name, **run_para)

    @classmethod
    def execute_app_run_init(cls, package_type: str, name: str, version: str, call_name: str,
                             class_name: str, fun_name: str, app_name: str, app_init_para={},
                             is_self_control=False, self_control_name=''):
        """
        执行app的对所依赖控件的初始化函数(app_run_init)

        @param {string} package_type - 类型，目前支持2种类型: Control - 控件包; AppLib - 应用包
        @param {string} name - 控件名或应用名
        @param {string} version - 控件版本号, "主版本号.次版本号.修订版本号"
        @param {string} call_name - 模块使用获取名
        @param {string} class_name - 要执行服务的类名
        @param {string} fun_name - 要只能给服务的函数
            注：class_name和fun_name至少要有一个有值：
            1.如果两个都有值，代表执行指定类的静态函数;
            2.如果仅class_name有值，代表执行类构造函数；
            3.如果仅fun_name有值，代表直接执行包的函数；
        @param {str} app_name - 应用名
        @param {dict} app_init_para={} - app对应的初始化参数
        @param {bool} is_self_control=False - 是否私有控件（仅AppLib会使用）
        @param {string} self_control_name='' - 私有控件时，私有控件的名称
        """
        _fun_obj = None  # 要执行的函数
        if class_name != '':
            # 执行类相关方法
            _class_obj = cls.get_import_servicer_class(
                class_name, package_type, name, version, call_name, is_self_control=is_self_control,
                self_control_name=self_control_name
            )
            if fun_name == '':
                _fun_obj = _class_obj
            else:
                _fun_obj = getattr(_class_obj, fun_name)
        else:
            # 执行模块根函数
            if fun_name == '':
                raise AttributeError('class_name or fun_name at least have one value')

            _module_obj = cls.get_import_servicer_module(
                package_type, name, version, call_name, is_self_control=is_self_control,
                self_control_name=self_control_name
            )
            _fun_obj = getattr(_module_obj, fun_name)

        # 执行函数
        _fun_obj(
            package_type, name, version, is_self_control, self_control_name, app_name, **app_init_para
        )

    @classmethod
    def get_real_class_name(cls, class_name: str, package_type: str, name: str, version: str,
                            call_name: str, is_self_control=False, self_control_name=''):
        """
        获取已装载的控件或应用的后台服务的类或变量别名的真实调用名

        @param {string} class_name - 类或变量名
        @param {string} package_type - 类型，目前支持2种类型: Control - 控件包; AppLib - 应用包
        @param {string} name - 控件名或应用名
        @param {string} version - 控件版本号, "主版本号.次版本号.修订版本号"
        @param {string} call_name - 模块使用获取名
        @param {bool} is_self_control=False - 是否私有控件（仅AppLib会使用）
        @param {string} self_control_name='' - 私有控件时，私有控件的名称

        @return {string} - 返回真实的调用类或变量名，如果找不到别名则返回自身的名称
        """
        try:
            _IMPORT_SERVICER = cls.get_import_servicer_dict()

            _dict = None
            if package_type == 'Control':
                _dict = _IMPORT_SERVICER['Control'][name][version]['$as_class_name$'][call_name]
            elif package_type == 'AppLib':
                if is_self_control:
                    _dict = _IMPORT_SERVICER['AppLib'][name][version]['$self_control$'][self_control_name]['$as_class_name$'][call_name]
                else:
                    _dict = _IMPORT_SERVICER['AppLib'][name][version]['$as_class_name$'][call_name]

            if _dict is not None:
                if class_name in _dict.keys():
                    return _dict[class_name]
        except:
            pass

        return class_name

    @classmethod
    def get_import_servicer_module(cls, package_type: str, name: str, version: str, call_name: str,
                                   is_self_control=False, self_control_name=''):
        """
        获取已安装的后台服务模块

        @param {str} package_type - 类型，目前支持2种类型: Control - 控件包; AppLib - 应用库
        @param {str} name - 控件或应用库名
        @param {str} version - 装载的版本
        @param {str} call_name - 模块的访问名
        @param {bool} is_self_control=False - 是否私有控件（仅AppLib会使用）
        @param {string} self_control_name='' - 私有控件时，私有控件的名称

        @return {Moudle} - 返回获取到的模块，如果找不到则返回None
        """
        try:
            _IMPORT_SERVICER = cls.get_import_servicer_dict()

            # 获取合适的版本
            _match_version = BaseInstaller.get_installed_match_version(
                package_type, name, version=version
            )

            if package_type == 'Control':
                return _IMPORT_SERVICER[package_type][name][_match_version][call_name]
            elif package_type == 'AppLib':
                if is_self_control:
                    # 私有控件
                    return _IMPORT_SERVICER[package_type][name][_match_version]['$self_control$'][self_control_name][call_name]
                else:
                    return _IMPORT_SERVICER[package_type][name][_match_version][call_name]
        except:
            pass

        # 没有找到
        return None

    @classmethod
    def get_import_servicer_class(cls, class_name: str, package_type: str, name: str, version: str,
                                  call_name: str, is_self_control=False, self_control_name=''):
        """
        获取已装载的控件或应用的python模块的指定类或变量

        @param {string} class_name - 类或变量名
        @param {string} package_type - 类型，目前支持2种类型: Control - 控件包; AppLib - 应用包
        @param {string} name - 控件名或应用名
        @param {string} version - 控件版本号, "主版本号.次版本号.修订版本号"
        @param {string} call_name - 模块使用获取名
        @param {bool} is_self_control=False - 是否私有控件（仅AppLib会使用）
        @param {string} self_control_name='' - 私有控件时，私有控件的名称

        @return {obj} - 返回获取到的类或变量，如果找不到则返回None
        """
        _module = cls.get_import_servicer_module(
            package_type, name, version, call_name, is_self_control=is_self_control,
            self_control_name=self_control_name
        )
        if _module is None:
            return None
        else:
            try:
                _real_class_name = cls.get_real_class_name(
                    class_name, package_type, name, version, call_name,
                    is_self_control=is_self_control, self_control_name=self_control_name
                )
                return getattr(_module, _real_class_name)
            except:
                return None

    #############################
    # 内部函数
    #############################
    @classmethod
    def _import_as_class_name(cls, package_type: str, name: str, version: str, as_class_name_dict: dict,
                              is_self_control=False, self_control_name=''):
        """
        装载指定节点的类别名配置

        @param {str} package_type - 类型，目前支持2种类型: Control - 控件包; AppLib - 应用库
        @param {str} name - 控件或应用库名
        @param {str} version - 装载的版本
        @param {dict} as_class_name_dict - 安装的as_class_name字典
        @param {bool} is_self_control=False - 是否应用库的自有控件
        @param {string} self_control_name='' - 自有控件名
        """
        _IMPORT_SERVICER = cls.get_import_servicer_dict()
        if package_type == 'AppLib':
            # AppLib类型
            for _call_name in as_class_name_dict.keys():
                for _as_class_name in as_class_name_dict[_call_name].keys():
                    if is_self_control:
                        ValueTool.set_dict_nest_value(
                            _IMPORT_SERVICER,
                            'AppLib', name, version, '$self_control$', self_control_name,
                            '$as_class_name$', _call_name, _as_class_name,
                            as_class_name_dict[_call_name][_as_class_name]
                        )
                    else:
                        ValueTool.set_dict_nest_value(
                            _IMPORT_SERVICER,
                            'AppLib', name, version, '$as_class_name$', _call_name, _as_class_name,
                            as_class_name_dict[_call_name][_as_class_name]
                        )
        else:
            # Control类型
            for _call_name in as_class_name_dict.keys():
                for _as_class_name in as_class_name_dict[_call_name].keys():
                    ValueTool.set_dict_nest_value(
                        _IMPORT_SERVICER,
                        'Control', name, version, '$as_class_name$', _call_name, _as_class_name,
                        as_class_name_dict[_call_name][_as_class_name]
                    )

    @classmethod
    def _import_servicer(cls, package_type: str, name: str, version: str, servicer_dict: dict,
                         is_self_control=False, self_control_name=''):
        """
        装载后台服务
        (通过处理类加载到内存，以及加入配置到全局变量中)

        @param {str} package_type - 类型，目前支持2种类型: Control - 控件包; AppLib - 应用库
        @param {str} name - 控件或应用库名
        @param {str} version - 装载的版本
        @param {dict} servicer_dict - install_list.xml中的servicer节点
        @param {bool} is_self_control=False - 是否应用库的自有控件
        @param {string} self_control_name='' - 自有控件名
        """
        _IMPORT_SERVICER = cls.get_import_servicer_dict()

        _import_dict = dict()
        # 先处理加载路径
        _extend_paths = servicer_dict.get('extend_path', '').split('|')
        for _path in _extend_paths:
            if _path != '':
                _lib_path = os.path.realpath(_path)
                if _lib_path not in sys.path:
                    sys.path.append(_lib_path)

        # 装载模块
        _modules = servicer_dict.get('module', {})
        for _call_name in _modules.keys():
            _module_obj = ImportTool.import_module(_modules[_call_name], is_force=True)
            _import_dict[_call_name] = _module_obj

        # 增加到全局变量中
        if package_type == 'Control':
            for _call_name in _import_dict.keys():
                ValueTool.set_dict_nest_value(
                    _IMPORT_SERVICER,
                    'Control', name, version, _call_name, _import_dict[_call_name]
                )
        elif package_type == 'AppLib':
            if is_self_control:
                for _call_name in _import_dict.keys():
                    ValueTool.set_dict_nest_value(
                        _IMPORT_SERVICER,
                        'AppLib', name, version, '$self_control$', self_control_name,
                        _call_name, _import_dict[_call_name]
                    )
            else:
                for _call_name in _import_dict.keys():
                    ValueTool.set_dict_nest_value(
                        _IMPORT_SERVICER,
                        'AppLib', name, version, _call_name, _import_dict[_call_name]
                    )

    @classmethod
    def _import_installed_package_servicer(cls, installed_dict: dict, run_after_import=True,
                                           run_after_install=False):
        """
        根据安装节点装载后台服务

        @param {dict} installed_dict - 安装配置文件installed_list.xml的对应节点字典
        @param {bool} run_after_import=True - 是否运行after_import函数
        @param {bool} run_after_install=False - 是否运行after_install函数
        """
        _package_type = installed_dict['base_info']['package_type']
        _name = installed_dict['base_info']['name']
        _ver = cls.get_main_version(installed_dict['base_info']['version'])

        if _package_type == 'Control':
            # 控件处理
            if 'servicer' in installed_dict.keys():
                cls.import_servicer(
                    _package_type, _name, _ver,
                    installed_dict['servicer'].get('as_class_name', {}),
                    is_self_control=False, self_control_name='',
                    execution_dict=installed_dict['base_info'].get('execution', {}),
                    init_para=installed_dict['base_info'].get('init_para', {}),
                    install_para=installed_dict['base_info'].get('install_para', {}),
                    run_after_import=run_after_import, run_after_install=run_after_install
                )
        else:
            # 应用库处理
            if 'self_control' in installed_dict.keys():
                # 自有控件情况，需要按顺序排序(通过order字段)
                _self_controls = installed_dict['self_control']
                _sorted_controls = sorted(
                    _self_controls.items(), key=lambda kv: (kv[1].get('order', 0), kv[0]['order'].get('order', 0))
                )
                for _control_name in _sorted_controls.keys():
                    if 'servicer' in installed_dict['self_control'][_control_name].keys():
                        cls.import_servicer(
                            _package_type, _name, _ver,
                            installed_dict['self_control'][_control_name]['servicer'],
                            is_self_control=True, self_control_name=_control_name,
                            execution_dict=installed_dict['self_control'][_control_name]['base_info'].get(
                                'execution', {}),
                            init_para=installed_dict['self_control'][_control_name]['base_info'].get(
                                'init_para', {}),
                            install_para=installed_dict['self_control'][_control_name]['base_info'].get(
                                'install_para', {}),
                            run_after_import=run_after_import, run_after_install=run_after_install
                        )

            # 应用包模块
            if 'servicer' in installed_dict.keys():
                cls.import_servicer(
                    _package_type, _name, _ver,
                    installed_dict['servicer'],
                    is_self_control=False, self_control_name='',
                    execution_dict=installed_dict['base_info'].get('execution', {}),
                    init_para=installed_dict['base_info'].get('init_para', {}),
                    install_para=installed_dict['base_info'].get('install_para', {}),
                    run_after_import=run_after_import, run_after_install=run_after_install
                )

    @classmethod
    def _get_sorted_control_list(cls, controls: dict):
        """
        获取已按依赖关系排好序的控件列表

        @param {dict} controls - 控件配置列表字典(installed_list.xml的Control_list)

        @return {list} - 排序后的控件列表, 每个对象为(name, ver)
        """
        # 依赖索引字典, 登记控件的依赖关系
        # key - 'name{split}ver'
        # value - dict()
        #    order - 排序，默认为0(不依赖其他控件), 数字越大排越后
        #    depend - 当前控件的所有子孙控件的key列表, ['name{split}ver', ...]
        _depend_dict = dict()

        # 遍历执行依赖字典的信息更新
        for _name in controls.keys():
            for _ver in controls[_name].keys():
                if controls[_name][_ver].get('install_status', '') != 'done':
                    # 只装载完成状态的节点
                    continue

            _name_ver = '%s{split}%s' % (_name, _ver)

            # 添加到列表清单
            if _name_ver not in _depend_dict.keys():
                _depend_dict[_name_ver] = dict()
                _depend_dict[_name_ver]['order'] = 0
                _depend_dict[_name_ver]['depend'] = list()

            # 处理当前控件的依赖
            _dependencies = controls[_name][_ver]['dependencies']
            for _parent_name in _dependencies.keys():
                _parent_ver = cls.get_installed_match_version(
                    'Control', _parent_name, _dependencies[_parent_name].get('version', '')
                )
                _parent_name_ver = '%s{split}%s' % (_parent_name, _parent_ver)

                if _parent_name_ver not in _depend_dict.keys():
                    # 把父控件加到清单中
                    _depend_dict[_parent_name_ver] = dict()
                    _depend_dict[_parent_name_ver]['order'] = 0
                    _depend_dict[_parent_name_ver]['depend'] = list()

                # 把自己加入父节点的依赖子孙列表中
                _depend_dict[_parent_name_ver]['depend'].append(_name_ver)

                # 处理当前节点的顺序, 至少比父节点的顺序号大
                _order = _depend_dict[_parent_name_ver]['order'] + 1
                cls._update_depend_dict_order(_name_ver, _order, _depend_dict)

        # 对字典进行排序处理, 转换为列表
        _sorted_dict = sorted(_depend_dict.items(), key=lambda kv: (kv[1]['order'], kv[0]['order']))
        _sorted_list = list()
        for _name_ver in _sorted_dict:
            _sorted_list.append(
                _name_ver.replace('{split}', '\n').split('\n')
            )

        return _sorted_list

    @classmethod
    def _update_depend_dict_order(cls, name_ver: str, order: int, depend_dict: dict):
        """
        更新依赖索引字典的顺序号

        @param {str} name_ver - 控件索引'name{split}ver'
        @param {int} order - 要更新为的顺序
        @param {dict} depend_dict - 要更新的字典
        """
        if depend_dict[name_ver]['order'] < order:
            # 先更新子孙节点的顺序, 要比自己大
            for _child_name_ver in depend_dict[name_ver]['depend']:
                cls._update_depend_dict_order(_child_name_ver, order + 1, depend_dict)

            # 再更新自己
            depend_dict[name_ver]['order'] = order

    #############################
    # 静态工具
    #############################
    @classmethod
    def get_installed_match_version(cls, install_type, name, version=''):
        """
        获取已安装的适配版本号

        @param {string} install_type - 类型，目前支持3种类型: Control - 控件包; AppLib - 应用包; App - 应用
        @param {string} name - 控件名或应用名
        @param {string} version='' - 控件版本，传入不同值有以下区别:
            '' - 代表只检查是否已安装该名字的包或应用
            '主版本号.次版本号.修订版本号' - 检查指定版本的包或应用是否存在
            '>主版本号.次版本号.修订版本号' - 检查是否有大于或等于该版本号的包或应用存在
            '<主版本号.次版本号.修订版本号' - 检查是否有小于或等于该版本号的包或应用存在
            '主版本号.次版本号.修订版本号 - 主版本号.次版本号.修订版本号' - 检查是否有存在于版本号之间的包或应用存在

        @return {string} - 返回适配的版本号, 如果找不到版本返回''
        """
        _xml_doc = RunTool.get_global_var('INSTALLED_DOC')
        _install_dict = _xml_doc.to_dict(xpath='/installed/%s_list/%s' % (install_type, name))

        # 需要清除掉安装中状态的版本
        for _ver in _install_dict[name].keys():
            if _install_dict[name][_ver].get('install_status', '') != 'done':
                del _install_dict[name][_ver]

        if len(_install_dict) == 0:
            # 没有找到安装的信息，直接返回无版本
            return ''

        # 排序后的已安装版本，第1个版本最高，最后一个版本最低
        _install_ver = list(_install_dict[name].keys()).reverse()

        if version == '':
            # 对版本无要求，直接返回最高版本即可
            return _install_ver[0]
        elif version[0: 1] == '>':
            # 大于等于的情况，满足条件则直接获取最高版本
            if version[1:] <= _install_ver[0]:
                return _install_ver[0]
            else:
                return ''
        elif version[0: 1] == '<':
            # 小于等于的情况, 从最高版本循环遍历
            for _ver in _install_ver:
                if version[1:] >= _ver:
                    return _ver
            # 遍历完都找不到，返回空
            return ''
        elif version.find('-') >= 0:
            # 区间的情况
            _index = version.find('-')
            _min = version[0: _index]
            _max = version[_index + 1:]
            for _ver in _install_ver:
                if _ver >= _min and _ver <= _max:
                    return _ver
            # 遍历完都找不到，返回空
            return ''
        else:
            # 直接等于的情况，只要key在列表中就是存在
            if version in _install_dict.keys():
                return version
            else:
                return ''

    @classmethod
    def is_installed(cls, install_type, name, version=''):
        """
        检查包是否已安装

        @param {string} install_type - 类型，目前支持3种类型: Control - 控件包; AppLib - 应用包; App - 应用
        @param {string} name - 控件名或应用名
        @param {string} version=None - 控件版本，传入不同值有以下区别:
            '' - 代表只检查是否已安装该名字的包或应用
            '主版本号.次版本号.修订版本号' - 检查指定版本的包或应用是否存在
            '>主版本号.次版本号.修订版本号' - 检查是否有大于或等于该版本号的包或应用存在
            '<主版本号.次版本号.修订版本号' - 检查是否有小于或等于该版本号的包或应用存在
            '主版本号.次版本号.修订版本号 - 主版本号.次版本号.修订版本号' - 检查是否有存在于版本号之间的包或应用存在

        @return {bool} - 是否已安装指定版本的包
        """
        _match_ver = cls.get_installed_match_version(install_type, name, version=version)
        if _match_ver == '':
            return False
        else:
            return True

    @classmethod
    def get_main_version(cls, version: str):
        """
        获取标准的3段式版本
        从"<主版本号>.<次版本号>.<修订版本号>.<修订日期>_阶段版本"中获取<主版本号>.<次版本号>.<修订版本号>

        @param {string} version - '<主版本号>.<次版本号>.<修订版本号>.<修订日期>_阶段版本'格式的版本号

        @return {string} - 3段式版本, 如'<主版本号>.<次版本号>.<修订版本号>'
        """
        _match_obj = re.match(
            r'^(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})',
            version
        )
        if _match_obj is None:
            # 匹配不到，直接返回原字符串
            return version
        else:
            return _match_obj.group()

    @classmethod
    def remove_install_config(cls, install_type: str, name: str, version: str, is_uninstall=False):
        """
        删除安装配置信息
        (同时也会删除已安装的后台服务和前台服务)

        @param {string} install_type - 类型，目前支持3种类型: Control - 控件包; AppLib - 应用包; App - 应用
        @param {string} name - 控件名或应用名
        @param {string} version - 要删除的控件版本
        @param {bool} is_uninstall=False - 是否卸载操作

        @return {dict} - 被删除的安装配置字典, installed_list.xml的[name] -> [ver]
        """
        _xml_doc: SimpleXml = RunTool.get_global_var('INSTALLED_DOC')
        _ver = cls.get_main_version(version)
        _xpath = '/installed/%s_list/%s/%s' % (install_type, name, _ver)
        _install_dict = _xml_doc.to_dict(xpath=_xpath)[_ver]

        # 先尝试卸载后台服务
        if _install_dict.get('install_status', '') == 'done':
            if install_type == 'AppLib' and 'self_control' in _install_dict.keys():
                # AppLib的私有控件处理
                for _self_control_name in _install_dict['self_control'].keys():
                    if 'servicer' in _install_dict['self_control'][_self_control_name].keys():
                        cls.unimport_servicer(
                            install_type, name, _ver,
                            _install_dict['self_control'][_self_control_name]['servicer'],
                            is_self_control=True, self_control_name=_self_control_name,
                            execution_dict=_install_dict['self_control'][_self_control_name]['base_info'].get('execution', {
                            }),
                            init_para=_install_dict['self_control'][_self_control_name]['base_info'].get('init_para', {
                            }),
                            install_para=_install_dict['self_control'][_self_control_name]['base_info'].get(
                                'install_para', {}),
                            run_before_uninstall=is_uninstall
                        )

            if 'servicer' in _install_dict.keys():
                cls.unimport_servicer(
                    install_type, name, _ver, _install_dict['servicer'],
                    is_self_control=False, self_control_name='',
                    execution_dict=_install_dict['base_info'].get('execution', {}),
                    init_para=_install_dict['base_info'].get('init_para', {}),
                    install_para=_install_dict['base_info'].get('install_para', {}),
                    run_before_uninstall=is_uninstall
                )

        # 直接删除配置，不用考虑卸载前后台服务的处理情况
        _xml_doc.remove(xpath=_xpath)
        _xml_doc.save()

        return _install_dict

    @classmethod
    def get_installed_dict(cls, install_type: str, name: str, version: str):
        """
        获取已安装控件/应用库的配置字典

        @param {string} install_type - 类型，目前支持3种类型: Control - 控件包; AppLib - 应用包; App - 应用
        @param {string} name - 控件名或应用名
        @param {string} version - 控件版本，传入不同值有以下区别:
            '' - 代表只检查是否已安装该名字的包或应用
            '主版本号.次版本号.修订版本号' - 检查指定版本的包或应用是否存在
            '>主版本号.次版本号.修订版本号' - 检查是否有大于或等于该版本号的包或应用存在
            '<主版本号.次版本号.修订版本号' - 检查是否有小于或等于该版本号的包或应用存在
            '主版本号.次版本号.修订版本号 - 主版本号.次版本号.修订版本号' - 检查是否有存在于版本号之间的包或应用存在

        @return {dict} - 安装配置字典(对应的版本下的字典), 如果找不到，返回None
        """
        _match_ver = cls.get_installed_match_version(
            install_type, name, version=version
        )
        if _match_ver == '':
            return None

        _xml_doc: SimpleXml = RunTool.get_global_var('INSTALLED_DOC')
        return _xml_doc.to_dict(
            xpath='/installed/%s_list/%s/%s' % (install_type, name, _match_ver)
        )[_match_ver]

    #############################
    # 构造函数
    #############################

    def __init__(self, **kwargs):
        """
        构造函数

        @param {kwargs} - 扩展变量，目前支持参数包括：
            console_print=False {bool} - 是否使用控制台对象prompt_obj进行打印，False时使用logger进行打印
            prompt_obj=None {PromptPlus} - 命令行框架时传入调用函数的PromptPlus对象，可以通过该对象的一些方法控制输出显示
            logger=None - {logger}  - 日志对象
        """
        self._console_print = kwargs.get('console_print', False)
        self._prompt_obj = kwargs.get('prompt_obj', None)
        self._logger = kwargs.get('logger', None)

        # 当前实例创建的临时目录清单
        self._create_path_list = list()

        # 设置IMPORT_SERVICER全局变量
        self.get_import_servicer_dict()

        # 公共的配置参数
        self.ENGINE_CONFIG = RunTool.get_global_var('ENGINE_CONFIG')
        self.ENGINE_SERVER = RunTool.get_global_var('ENGINE_SERVER')

        # 执行继承类的实现方法
        self._init(**kwargs)

    def __del__(self):
        """
        类销毁函数
        """
        # 执行实现类的销毁函数
        self._del()

        # 删除临时目录
        for _path in self._create_path_list:
            if os.path.exists(_path):
                try:
                    FileTool.remove_dir(_path)
                except:
                    # 异常不抛出
                    pass

    #############################
    # 通用工具
    #############################
    def install_package_cmd(self, package_file, pwd=None, install_para={}, init_para={}, rewrite=False,
                            refresh_depend_template=False, **kwargs):
        """
        安装指定控件包或应用包(以命令行方式显示结果)

        @param {string} packager_file - 包文件路径(只支持压缩包)
        @param {string} pwd=None - 压缩包密码
        @param {dict} install_para={} - 安装包的传入参数
        @param {dict} init_para={} - 控件装载时的默认初始化参数，字典形式的参数
        @param {bool} rewrite=False - 如果同一版本的包已存在，是否覆盖
        @param {bool} refresh_depend_template=False - 是否重新刷新直接依赖该包的已安装控件/应用的模板
        @param {kwargs} - 扩展参考

        @return {CResult} - 安装结果
        """
        _result = CResult(code='00000')
        with ExceptionTool.ignored_cresult(
            result_obj=_result, logger=None,
            self_log_msg=_('install package [$1] error:', package_file)
        ):
            # 获取安装包的基本信息
            _temp_result = self.get_package_base_info(package_file, pwd=pwd)
            if not _temp_result.is_success():
                # 获取信息失败
                self._logging_print(
                    _(_temp_result.i18n_msg_id, *_temp_result.i18n_msg_paras)
                )
                return _temp_result

            _base_info: dict = _temp_result.base_info

            # 解压包到临时目录并检查控件是否通过可通过包校验
            _temp_result = self.check_package_verify(package_file, _base_info, pwd)
            if not _temp_result.is_success():
                # 校验失败，执行打印处理
                self._logging_print(
                    _(_temp_result.i18n_msg_id, *_temp_result.i18n_msg_paras)
                )
                return _temp_result

            _packager_class: BasePackager = _temp_result.packager_class  # 包处理类
            _temp_path = _temp_result.temp_path  # 解压包的临时路径

            # 检查控件依赖关系是否会存在冲突(相互依赖形成死循环)
            # TODO(lhj): Todo Descript

            # 检查该控件版本是否已安装过
            _install_version = self.get_main_version(_base_info['version'])
            _temp_result = self.check_package_has_installed(
                _base_info, _install_version, rewrite
            )
            if not _temp_result.is_success():
                self._logging_print(
                    _(_temp_result.i18n_msg_id, *_temp_result.i18n_msg_paras)
                )
                return _temp_result
            _is_installed = _temp_result.is_installed

            # 执行预安装，获取需要添加的安装配置，资源文件复制清单，以及python模块装载信息
            _temp_result = self.pre_install_package(
                _base_info, _packager_class, _temp_path, install_para=install_para, init_para=init_para, **kwargs
            )
            if not _temp_result.is_success():
                self._logging_print(
                    _(_temp_result.i18n_msg_id, *_temp_result.i18n_msg_paras)
                )
                return _temp_result

            _install_set = _temp_result.install_set

            # 检查控件是否通过允许后台安装的限制
            _temp_result = self.check_allow_bg_service(_install_set)

            if _temp_result.code == '13006':
                # 需要用户确认
                _back = input(_('the $1 has bg services, continue to install? (y/N)',
                                _base_info['package_type']))
                if _back.upper() != 'Y':
                    # 用户取消安装
                    _result.change_code(code='10100')
                    return _result
            elif not _temp_result.is_success():
                self._logging_print(
                    _(_temp_result.i18n_msg_id, *_temp_result.i18n_msg_paras)
                )
                return _temp_result

            # 遍历安装依赖包
            # TODO(lhj): 待处理

            # 清除已安装包信息
            _temp_result = self.uninstall_pacakge_execute(
                _base_info['package_type'], _base_info['name'], _install_version, _is_installed
            )
            if not _temp_result.is_success():
                self._logging_print(
                    _(_temp_result.i18n_msg_id, *_temp_result.i18n_msg_paras)
                )
                return _temp_result

            # 根据预安装信息执行安装操作
            _temp_result = self.install_package_execute(
                _base_info, _temp_path, _install_set, **kwargs
            )
            if not _temp_result.is_success():
                self._logging_print(
                    _(_temp_result.i18n_msg_id, *_temp_result.i18n_msg_paras)
                )
                return _temp_result

            # 对依赖的控件、应用库、应用重新执行模板静态化处理
            # TODO(lhj): Todo Descript

    #############################
    # 安装包的分步处理
    #############################

    def get_package_base_info(self, package_file, pwd=None):
        """
        获取包的基本信息字典

        @param {string} packager_file - 包文件路径(只支持压缩包)
        @param {string} pwd=None - 压缩包密码
            示例：pwd='123456'.encode('utf-8')

        @return {CResult} - 返回处理结果, 错误码13004代表获取包基本信息失败
            注：返回值中会包含一些后续过程要用到的对象，通过CResult属性方式提供
                base_info - 包的基本信息字典
        """
        _result = CResult(code='00000')
        _self_log_msg = 'get package [$1] base info error'
        with ExceptionTool.ignored_cresult(
            result_obj=_result, logger=None,
            error_map={'DEFAULT': ('13004', _self_log_msg, (package_file, ))},
            self_log_msg=_self_log_msg, i18n_msg_paras=(package_file, )
        ):
            _base_info = BasePackager.get_package_base_info(package_file, pwd=pwd)
            _result.base_info = _base_info

        # 返回值
        return _result

    def check_package_verify(self, package_file, base_info, pwd=None):
        """
        解压包到临时目录并检查包是否通过可通过包校验

        @param {string} package_file - 要检查的包文件
        @param {dict} base_info - 通过BasePackager.get_package_base_info获取到的包基本配置信息
        @param {bytes} pwd=None - 压缩包密码
            示例：pwd='123456'.encode('utf-8')

        @return {CResult} - 返回处理结果, 错误码13003代表校验失败
            注：返回值中会包含一些后续过程要用到的对象，通过CResult属性方式提供
                packager_class - 包处理类
                temp_path - 解压包的临时路径
        """
        _result = CResult(code='00000')
        _self_log_msg = 'package [$1] verify error'
        with ExceptionTool.ignored_cresult(
            result_obj=_result, logger=None,
            error_map={'DEFAULT': ('13003', _self_log_msg, (package_file, ))},
            self_log_msg=_self_log_msg, i18n_msg_paras=(package_file, )
        ):
            _packager_ver = self.get_installed_match_version(
                base_info['package_type'],
                base_info['package_deal_control_name'],
                version=base_info['package_deal_control_verion']
            )

            if _packager_ver == '':
                # 找不到处理包的已安装匹配版本
                return CResult(
                    code='13003', msg='the match version of $1 [$2 $3] is not install',
                    i18n_msg_paras=(
                        base_info['package_type'], base_info['package_deal_control_name'],
                        base_info['package_deal_control_verion']
                    )
                )

            _packager_class: BasePackager = self.get_import_servicer_class(
                base_info['package_deal_class_name'],
                base_info['package_type'],
                base_info['package_deal_control_name'],
                _packager_ver,
                base_info['package_deal_control_call_name']
            )

            if _packager_class is None:
                # 无法正常获取包处理类
                return CResult(
                    code='13003', msg="can't get the packager class [$1] on $2 [$3 $4]",
                    i18n_msg_paras=(
                        base_info['package_deal_class_name'], base_info['package_type'],
                        base_info['package_deal_control_name'], base_info['package_deal_control_verion']
                    )
                )

            # 解压缩包到指定目录
            _temp_path = os.path.join(self.ENGINE_CONFIG['temp_path'], uuid.uuid1())
            _packager_class.unpack(package_file, dest_path=_temp_path, pwd=pwd)
            self._create_path_list.append(_temp_path)  # 将创建的临时目录加到清单，实例销毁的时候统一删除

            _verify_result = _packager_class.verify_package_unpacked(_temp_path)
            if not _verify_result.is_success():
                return _verify_result

            # 返回的属性值
            _result.packager_class = _packager_class
            _result.temp_path = _temp_path

        # 返回检查结果
        return _result

    def check_package_has_installed(self, base_info, install_version, rewrite):
        """
        检查包是否已安装

        @param {dict} base_info - 通过BasePackager.get_package_base_info获取到的包基本配置信息
        @param {str} install_version - 安装版本
        @param {bool} rewrite - 是否允许覆盖

        @return {CResult} - 返回处理结果, 错误码为13001代表包已安装且不允许覆盖
            当执行成功时，CResult.is_installed 返回原包是否已安装的信息

        """
        _result = CResult(code='00000')
        _self_log_msg = 'check package has installed error'
        with ExceptionTool.ignored_cresult(
            result_obj=_result, logger=None,
            error_map={'DEFAULT': ('21399', _self_log_msg)},
            self_log_msg=_self_log_msg
        ):
            _is_installed = self.is_installed(
                base_info['package_type'], base_info['name'], version=install_version)

            if _is_installed:
                if not rewrite:
                    # 已安装且不允许覆盖
                    _result.change_code(
                        code='13001', msg="current package $1 [$2 $3] has installed",
                        i18n_msg_paras=(
                            base_info['package_type'],
                            base_info['name'], install_version
                        )
                    )

            _result.is_installed = _is_installed

        return _result

    def pre_install_package(self, base_info: dict, packager_class: BasePackager, package_path: str,
                            install_para={}, init_para={}, **kwargs):
        """
        预安装包，获取安装配置信息

        @param {dict} base_info - 通过BasePackager.get_package_base_info获取到的包基本配置信息
        @param {BasePackager} packager_class - 包对应的处理类
        @param {str} package_path - 安装包所在临时路径
        @param {dict} install_para={} - 包安装参数，字典形式的参数
        @param {dict} init_para={} - 控件装载时的默认初始化参数，字典形式的参数
        @param {**kwargs} - 扩展参数

        @return {CResult} - 返回处理结果
            注：返回值中会包含一些后续过程要用到的对象，通过CResult属性方式提供
                install_set {dict} - 需要添加的安装配置，资源文件复制清单，以及python模块装载信息
                    install_conf {dict} - 完成包安装后, 需要加载到安装配置文件(install_list.xml)的配置信息
                        key - 配置的xpath路径字符串(从安装包配置根节点开始的相对路径, 不应使用'/'开头)
                        value - 配置值
                    static_copy {list} - 需要复制的静态资源文件(或目录)列表
                        [0] - 要复制的资源文件或目录, 按package_path为根目录的相对路径, 不应使用'/'开头
                        [1] - 目标文件或目录， 按static_path下包安装路径为根目录的相对路径，不应使用'/'开头
                    server_copy {list} - 需要复制的后台资源文件(或目录)列表
                        [0] - 要复制的资源文件或目录, 按package_path为根目录的相对路径, 不应使用'/'开头
                        [1] - 目标文件或目录， 按server_path下包安装路径为根目录的相对路径，不应使用'/'开头
        """
        _result = CResult(code='00000')
        _self_log_msg = 'pre_install package error'
        with ExceptionTool.ignored_cresult(
            result_obj=_result, logger=None,
            error_map={'DEFAULT': ('21399', _self_log_msg)},
            self_log_msg=_self_log_msg
        ):
            # 更新安装参数和初始化参数
            base_info['install_para'].update(install_para)
            base_info['init_para'].update(init_para)

            # 执行预安装
            _result.install_set = packager_class.pre_install_package(
                base_info, package_path, **kwargs
            )

        return _result

    def check_allow_bg_service(self, install_set: dict):
        """
        检查是否能通过允许后台服务安装要求

        @param {dict} install_set - 预安装信息集

        @return {CResult} - 返回处理结果, 错误码13005代表控制检查失败，错误码13006代表需要用户确认
        """
        _result = CResult(code='00000')
        _self_log_msg = 'check allow bg service error'
        with ExceptionTool.ignored_cresult(
            result_obj=_result, logger=None,
            error_map={'DEFAULT': ('13005', _self_log_msg)},
            self_log_msg=_self_log_msg
        ):
            _allow_bg_service = self.ENGINE_CONFIG['server_config']['bg_server']['allow_bg_service']

            # 判断是否允许安装存在后台服务的控件
            _has_bg_server = False
            if len(install_set['server_copy']) > 0:
                _has_bg_server = True
            else:
                for _xpath in install_set.keys():
                    ''.index('/')
                    if _xpath.startswith('servicer/') or re.search('^self_control/.*/servicer/.*', _xpath) is not None:
                        _has_bg_server = True
                        break

            if _has_bg_server:
                if _allow_bg_service == 'false':
                    # 禁止安装
                    _result.change_code(
                        code='13005', msg='not allow install control/applib with bg service'
                    )
                elif _allow_bg_service == 'sign':
                    # 检查控件是否经过安全认证
                    # TODO(lhj): 获取包的hash值，与HiveNet安全认证服务进行校验
                    pass
                elif _allow_bg_service == 'prompt':
                    # 提示客户选择
                    _result.change_code(code='13006')

        return _result

    def install_package_execute(self, base_info, package_path: str, install_set: dict, **kwargs):
        _result = CResult(code='00000')
        _self_log_msg = 'install package error'
        with ExceptionTool.ignored_cresult(
            result_obj=_result, logger=None,
            error_map={'DEFAULT': ('21399', _self_log_msg)},
            self_log_msg=_self_log_msg
        ):
            _tool: HiveNetTool = RunTool.get_global_var('HIVENET_TOOL')
            _installed_doc: SimpleXml = _tool.installed_doc
            _ver = self.get_main_version(base_info['version'])
            _name = base_info['name']
            _install_type = base_info['package_type']

            # 将配置添加到installed_list.xml，注意install_status为installing
            install_set['install_conf']['install_status'] = 'installing'
            _tool.para_to_install_dict(
                base_info, install_set['install_conf'], xpath_prefix='base_info')
            _installed_doc.set_value_by_dict(
                '/installed/%s_list/%s/%s' % (_install_type, _name, _ver),
                install_set['install_conf']
            )
            _installed_doc.save()

            # 复制后台文件
            _server_path = os.path.realpath(
                os.path.join(_tool.server_path, _install_type.lower(), _name, _ver)
            )
            for _server_file in install_set['server_copy']:
                _src = os.path.join(package_path, _server_file[0])
                _dest = os.path.join(_server_path, _server_file[1])
                if os.path.isfile(_src):
                    shutil.copyfile(_src, _dest)
                else:
                    FileTool.copy_all_with_path(_src, _dest)

            # 增加基础目录的__init__.py文件
            _tool.create_init_py_file(os.path.join(_tool.server_path, _install_type.lower(), _name))
            _tool.create_init_py_file(_server_path)

            # 复制静态文件
            _static_path = os.path.realpath(os.path.join(
                _tool.static_path, _install_type.lower(), _name, _ver))
            for _static_file in install_set['static_copy']:
                _src = os.path.join(package_path, _static_file[0])
                _dest = os.path.join(_static_path, _static_file[1])
                if os.path.isfile(_src):
                    shutil.copyfile(_src, _dest)
                else:
                    FileTool.copy_all_with_path(_src, _dest)

            # 装载后台服务
            _installed_dict = _installed_doc.to_dict(
                '/installed/%s_list/%s/%s' % (_install_type, _name, _ver)
            )[_ver]
            self._import_installed_package_servicer(
                _installed_dict,
                run_after_import=True, run_after_install=True
            )

            # 执行模板的静态化处理
            # TODO(lhj): Todo Descript

            # 完成安装，设置安装状态
            _installed_doc.set_value(
                '/installed/%s_list/%s/%s/install_status' % (_install_type, _name, _ver),
                'done'
            )
            _installed_doc.save()

        return _result

    #############################
    # 卸载包的分步处理
    #############################
    def uninstall_pacakge_execute(self, install_type: str, name: str, version: str, is_installed: bool):
        """
        真正执行卸载包操作的执行步骤

        @param {string} install_type - 类型，目前支持3种类型: Control - 控件包; AppLib - 应用包; App - 应用
        @param {string} name - 控件名或应用名
        @param {string} version - 要删除的控件版本
        @param {bool} is_installed - 包是否已安装

        @return {CResult} - 返回处理结果
            注：返回值中会包含一些后续过程要用到的对象，通过CResult属性方式提供
            install_dict {dict} - 被删除的安装配置字典, installed_list.xml的[name] -> [ver]
        """
        _result = CResult(code='00000')
        _self_log_msg = 'uninstall pacakge error'
        with ExceptionTool.ignored_cresult(
            result_obj=_result, logger=None,
            error_map={'DEFAULT': ('21399', _self_log_msg)},
            self_log_msg=_self_log_msg
        ):
            _tool: HiveNetTool = RunTool.get_global_var('HIVENET_TOOL')

            # 删除配置及已装载的服务
            _result.install_dict = self.remove_install_config(
                install_type, name, version, is_uninstall=is_installed)

            # 删除相关文件
            _ver = _tool.installer_class.get_main_version(version)
            _server_path = os.path.realpath(os.path.join(
                _tool.server_path, install_type.lower(), name, _ver))

            try:
                FileTool.remove_sub_dirs(path=_server_path)
            except FileNotFoundError:
                pass

            _static_path = os.path.realpath(os.path.join(
                _tool.static_path, install_type.lower(), name, _ver))
            try:
                FileTool.remove_sub_dirs(path=_static_path)
            except FileNotFoundError:
                pass

        return _result

    #############################
    # 内部函数
    #############################
    def _logging_print(self, *args, sep=' ', end='\n', line_head=False, level=logging.INFO,
                       format_print=False, style=None, flush=False, my_logger=None):
        """
        使用内置打印函数进行输出打印

        @param {*args} - 要打印的内容值，可以传多个值进行打印
        @param {string} sep=' ' - 多个值之间的分隔符
        @param {string} end='\n' - 打印值结尾追加的字符串，默认以'\n'换行
        @param {bool} line_head=False - 是否将打印内容重置至行头(覆盖当行已打印的内容)
            注: 该参数对于使用logger打印的情况无效，即初始化对象时定义了logger的情况
        @param {int} level=logging.INFO - 输出日志级别，该参数仅对使用logger的情况有效
        @param {bool} format_print=False - 是否格式化打印，对于使用logger打印的情况无效
        @param {dict} style=None - 格式字符串的样式字典，例如以下字典指定两个格式类:
                {
                    'aaa': '#ff0066',
                    'bbb': '#44ff00 italic',
                }
            然后再传入format_html_text(<aaa>Hello</aaa> <bbb>world</bbb>!)
        @param {logger} my_logger=None - 如果该参数传入值，则使用该日志对象进行打印

        """
        if self._console_print and self._prompt_obj is not None:
            # 直接使用控制台的打印对象处理
            self._prompt_obj.prompt_print(
                *args, sep=sep, end=end, line_head=line_head, level=level,
                format_print=format_print, style=style, flush=flush, force_logging=False,
                my_logger=my_logger
            )
        else:
            # 使用自带的打印处理
            _logger = self._logger
            if my_logger is not None:
                _logger = my_logger
            if _logger is None or self._console_print:
                # 没有日志类，直接输出
                if line_head and len(args) > 0:
                    args[0] = '\r%s' % str(args[0])
                print(*args, sep=sep, end=end, flush=flush)
            else:
                _print_str = MemoryStringStream()
                print(*args, sep=sep, end=end, file=_print_str, flush=flush)
                _logger.log(level, _print_str)

    #############################
    # 继承类需要实现的方法
    #############################
    def _init(self, **kwargs):
        """
        继承类可以实现的构造函数初始化处理函数
        """
        pass

    def _del(self):
        """
        继承类可以实现的类销毁函数
        """
        pass


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
