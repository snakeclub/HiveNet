#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
常用代码工具模块
@module hivenet_tool
@file hivenet_tool.py
"""

import sys
import os
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.base_tools.file_tool import FileTool
from HiveNetLib.base_tools.import_tool import ImportTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))


__MOUDLE__ = 'hivenet_tool'  # 模块名
__DESCRIPT__ = u'常用代码工具模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.02.05'  # 发布日期


class HiveNetTool(object):
    """
    提供快捷访问的一些工具代码函数
    注：应实例化对象后才能使用相关属性
    """
    #############################
    # 静态工具函数
    #############################
    @classmethod
    def para_to_install_dict(cls, para: dict, install_dict: dict, xpath_prefix=''):
        """
        将字典参数写入安装字典

        @param {dict} para - 字典参数
        @param {dict} install_dict - 安装字典，需要加载到安装配置文件(install_list.xml)的配置信息
            key - 配置的xpath路径字符串(从安装包配置根节点开始的相对路径, 不应使用'/'开头)
            value - 配置值
        @param {string} xpath_prefix='' - xpath的前置字符串
        """
        # 处理xpath_prefix
        _prefix = '' if xpath_prefix == '' else xpath_prefix + '/'

        for _key in para.keys():
            _value = para[_key]
            if type(_value) == dict:
                # 如果值为字典，按下一个层级处理
                HiveNetTool.para_to_install_dict(
                    _value, install_dict, xpath_prefix='%s%s' % (_prefix, _key)
                )
            else:
                # 按字符串处理
                install_dict['%s%s' % (_prefix, _key)] = str(_value)

    @classmethod
    def set_config_xml_value(cls, config_obj: object, config_dict: dict, base_xpath=''):
        """
        设置配置文件的值

        @param {SimpleXml} config_obj - 配置文件对象
        @param {dict} config_dict - 配置字典, key为xpath, value为设置值
        @param {string} base_xpath='' - 配置所在的路径前缀(注意结尾不要带/)
        """
        for _xpath in config_dict:
            config_obj.set_value(
                _xpath if base_xpath == '' else '%s/%s' % (base_xpath, _xpath),
                config_dict[_xpath]
            )
        config_obj.save()

    @classmethod
    def register_base_control(cls, config_dict: dict):
        """
        装载基础控件配置
        @param {dict} config_dict - 配置字典, installed_list.xml的base_control_config
        """
        _BASE_CONTROL = RunTool.get_global_var('BASE_CONTROL')
        for _name in config_dict.keys():
            # 默认类
            _module_name = config_dict[_name]['default_class']['module_name']
            _extend_path = config_dict[_name]['default_class'].get('extend_path', '')
            _class_name = config_dict[_name]['default_class']['class_name']
            _module = ImportTool.import_module(
                _module_name,
                extend_path=(None if _extend_path == '' else _extend_path)
            )
            _class = getattr(_module, _class_name)

            _BASE_CONTROL[_name] = {
                'default_class': _class,
                'control_name': config_dict[_name]['control_name'],
                'control_version': config_dict[_name]['control_version'],
                'call_name': config_dict[_name]['call_name'],
                'class_name': config_dict[_name]['class_name']
            }

    @classmethod
    def get_base_control_class(cls, name: str):
        """
        获取基础控件对应类

        @param {str} name - 基础控件名

        @return {object} - 基础控件对应的类，如果找不到返回None
        """
        _BASE_CONTROL = RunTool.get_global_var('BASE_CONTROL')
        if name not in _BASE_CONTROL.keys():
            return None

        _class = _BASE_CONTROL[name]['default_class']  # 默认类
        _installer = cls.get_base_control_class('Installer')

        if _BASE_CONTROL[name]['control_name'] != '':
            # 获取指定版本的控件
            _control_class = _installer.get_import_servicer_class(
                _BASE_CONTROL[name]['class_name'], 'Control',
                _BASE_CONTROL[name]['control_name'], _BASE_CONTROL[name]['control_version'],
                _BASE_CONTROL[name]['call_name']
            )
            if _control_class is not None:
                _class = _control_class

        return _class

    #############################
    # 实例对象属性
    #############################
    @property
    def base_control(self):
        """
        返回基础控件实例对象索引字典
        @property {dict} - key为对象名, value为实例对象
            Installer - 安装控件
        """
        return RunTool.get_global_var('BASE_CONTROL')

    @property
    def installed_doc(self):
        """
        返回安装应用库/控件库/应用清单的XML实例对象
        @property {SimpelXml}
        """
        return RunTool.get_global_var('INSTALLED_DOC')

    @property
    def package_node_router(self):
        """
        返回控件包/应用库包的节点处理类的访问路由对象实例
        @property {PackageNodeRouter}
        """
        return RunTool.get_global_var('PACKAGE_NODE_ROUTER')

    @property
    def server_path(self):
        """
        返回服务端路径
        """
        return RunTool.get_global_var('ENGINE_CONFIG')['server_path']

    @property
    def static_path(self):
        """
        返回静态资源服务器文件路径
        """
        return RunTool.get_global_var('ENGINE_CONFIG')['static_path']


class MemoryStringStream(object):
    """
    内存中的字符串流定义类
    用于将流内容输出到字符串中
    """

    def __init__(self, encoding=None):
        """
        构造函数
        """
        self._encoding = encoding
        self._buff = ''

    def write(self, out_stream):
        """
        将内容写入流

        @param {string} out_stream - 要输出的流内容
        """
        if self._encoding is None:
            self._buff += out_stream
        else:
            self._buff += str(out_stream, encoding=self._encoding)

    def __str__(self):
        """
        输出内容
        """
        return self._buff


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
