#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
资源处理模块
@module resource_dealer
@file resource_dealer.py
"""

import os
import sys
from HiveNetLib.base_tools.file_tool import FileTool
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from HiveNet.lib.installer import BaseInstaller

__MOUDLE__ = 'resource_dealer'  # 模块名
__DESCRIPT__ = u'资源处理模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.02.17'  # 发布日期


class BaseResourceDealer(object):
    """
    资源处理基础框架类
    """
    #############################
    # 需要继承类实现的函数
    #############################
    @classmethod
    def get_pre_install_set(cls, class_id: str, node_dict: dict, base_info: dict,
                            package_path: str, is_self_control=False, self_control_name='', **kwargs):
        """
        资源节点预安装处理
        (继承类可以重载实现个性化的预安装处理)

        @param {string} class_id - 访问类ID
        @param {dict} node_dict - 要处理的配置节点字典
        @param {dict} base_info - 通过BasePackager.get_package_base_info获取到的包基本配置信息
        @param {str} package_path - 安装包所在临时路径
        @param {bool} is_self_control=False - 是否应用库的自有控件
        @param {string} self_control_name='' - 自有控件名
        @param {**kwargs} - 扩展参数

        @return {dict} - 需要添加的安装配置，资源文件复制清单，以及python模块装载信息
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
        raise NotImplementedError()


class StaticResourceDealer(BaseResourceDealer):
    """
    静态资源处理类
    """

    #############################
    # 需要继承类实现的函数
    #############################
    @classmethod
    def get_pre_install_set(cls, class_id: str, node_dict: dict, base_info: dict,
                            package_path: str, is_self_control=False, self_control_name='', **kwargs):
        """
        资源节点预安装处理
        (继承类可以重载实现个性化的预安装处理)

        @param {string} class_id - 访问类ID
        @param {dict} node_dict - 要处理的配置节点字典
        @param {dict} base_info - 通过BasePackager.get_package_base_info获取到的包基本配置信息
        @param {str} package_path - 安装包所在临时路径
        @param {bool} is_self_control=False - 是否应用库的自有控件
        @param {string} self_control_name='' - 自有控件名
        @param {**kwargs} - 扩展参数

        @return {dict} - 需要添加的安装配置，资源文件复制清单，以及python模块装载信息
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
        _install_set = {
            'static_copy': list()
        }
        _package_path = os.path.realpath(package_path)
        _copy_list = node_dict['copy_list'].split('|')

        # 考虑处理的资源是否自有控件
        _copy_prefix = 'web-static'
        _file_prefix = ''
        if is_self_control:
            _copy_prefix = 'self-control/%s/web-static' % self_control_name
            _file_prefix = 'self-control/%s' % self_control_name

        for _file in _copy_list:
            if _file == '':
                continue

            _copy_file = os.path.join(_package_path, _copy_prefix, _file)
            _dest_file = os.path.join(_file_prefix, _file)

            if os.path.exists(_copy_file):
                _install_set['static_copy'].append(
                    (_copy_file, _dest_file)
                )

        return _install_set


class PyServicerResourceDealer(BaseResourceDealer):
    """
    python类后台服务资源处理类
    """

    #############################
    # 需要继承类实现的函数
    #############################
    @classmethod
    def get_pre_install_set(cls, class_id: str, node_dict: dict, base_info: dict,
                            package_path: str, is_self_control=False, self_control_name='', **kwargs):
        """
        资源节点预安装处理
        (继承类可以重载实现个性化的预安装处理)

        @param {string} class_id - 访问类ID
        @param {dict} node_dict - 要处理的配置节点字典
        @param {dict} base_info - 通过BasePackager.get_package_base_info获取到的包基本配置信息
        @param {str} package_path - 安装包所在临时路径
        @param {bool} is_self_control=False - 是否应用库的自有控件
        @param {string} self_control_name='' - 自有控件名
        @param {**kwargs} - 扩展参数

        @return {dict} - 需要添加的安装配置，资源文件复制清单，以及python模块装载信息
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
        _install_set = {
            'install_conf': dict(),
            'server_copy': list()
        }

        # 考虑applib的情况
        _prefix = 'servicer'
        if is_self_control:
            _prefix = 'self_control/%s/servicer' % self_control_name

        # 类别名配置
        if 'as_class_name' in node_dict.keys():
            _as_class_dict = node_dict['as_class_name']
            for _call_name in _as_class_dict.keys():
                for _as_name in _as_class_dict[_call_name].keys():
                    _xpath = '%s/as_class_name/%s/%s' % (_prefix, _call_name, _as_name)
                    _install_set['install_conf'][_xpath] = _as_class_dict[_call_name][_as_name]

        # 模块处理
        if node_dict['import_type'] == 'lib':
            # 类库模式, 增加搜索路径
            cls._add_install_extend_path(
                _install_set, node_dict.get('module_path', ''), prefix=_prefix
            )

            # 增加模块配置
            cls._add_install_module(
                _install_set, base_info,
                node_dict.get('module_name', ''),
                node_dict.get('call_name', ''),
                package_path, is_file=False,
                is_self_control=is_self_control, self_control_name=self_control_name,
                prefix=_prefix
            )
        elif node_dict['import_type'] == 'file':
            # 文件模式
            _file_list = node_dict['file_list'].split('|')
            for _file in _file_list:
                # 按文件逐个处理
                _fileinfo = _file.split('^')
                _filename = _fileinfo[0]
                if _filename == '':
                    continue

                _call_name = ''
                if len(_fileinfo) > 1:
                    _call_name = _fileinfo[1]

                # 增加__init__.py以及文件复制参数
                cls._add_install_copy_file(
                    _install_set, _file, package_path,
                    is_self_control=is_self_control, self_control_name=self_control_name
                )

                # 增加模块配置
                cls._add_install_module(
                    _install_set, base_info,
                    _filename,
                    _call_name,
                    package_path, is_file=True,
                    is_self_control=is_self_control, self_control_name=self_control_name,
                    prefix=_prefix
                )
        elif node_dict['import_type'] == 'path':
            # 路径模式
            _path_list = node_dict['path_list'].split('|')
            if node_dict['path_list'] == '':
                # 空代表装载整个service目录
                _path_list = ['']

            # 逐个路径执行处理
            for _path in _path_list:
                # 获取真实路径
                if is_self_control:
                    _prefix_path = os.path.join('self-control', self_control_name, 'service', _path)
                else:
                    _prefix_path = os.path.join('service', _path)

                _real_path = os.path.realpath(os.path.join(package_path, _prefix_path))

                # 添加__init__.py文件
                cls.add_python_package_file(
                    _install_set, _real_path, package_path
                )

                # 增加复制配置
                _install_set['server_copy'].append(
                    (_real_path, _prefix_path)
                )

                # 遍历目录下的所有文件形成安装配置
                cls._add_install_path(
                    _install_set, base_info, _path, package_path,
                    is_self_control=is_self_control, self_control_name=self_control_name,
                    prefix=_prefix
                )

        return _install_set

    #############################
    # 静态工具
    #############################
    @classmethod
    def create_init_py_file(cls, deal_path, install_set: dict, package_path: str, add_copy_info=False):
        """
        在制定目录创建__init__.py文件

        @param {str} deal_path - 要处理的路径
        @param {dict} install_set - 预安装配置字典
        @param {str} package_path - 安装包所在临时路径
        @param {bool} add_copy_info=False - 是否在预安装配置字典添加复制信息
        """
        if os.path.exists(os.path.join(deal_path, '__init__.py')):
            # 文件已经存在，不处理
            pass
        else:
            _file_content = '%s\n%s\n\n%s\n' % (
                '#!/usr/bin/env python3',
                '# -*- coding: UTF-8 -*-',
                '__all__ = []'
            )
            # 写入文件
            with open(os.path.join(deal_path, '__init__.py'), 'w', encoding='utf-8') as _file:
                _file.write(_file_content)
                _file.flush()

        # 添加预安装信息
        if add_copy_info:
            _init_file = os.path.realpath(os.path.join(deal_path, '__init__.py'))
            _cut_len = len(os.path.realpath(package_path))
            _copy_info = (
                _init_file,
                _init_file[_cut_len:].lstrip('/\\')
            )
            if _copy_info not in install_set['server_copy']:
                install_set['server_copy'].append(_copy_info)

    @classmethod
    def add_init_py_by_file(cls, file: str, install_set: dict, package_path: str):
        """
        基于指定文件，向上级逐个增加__init__.py文件

        @param {str} file - <description>
        @param {dict} install_set - <description>
        @param {str} package_path - <description>
        """
        _file = os.path.realpath(file)
        _deal_path = ''
        if os.path.isdir(_file):
            # 本身就是路径
            _deal_path = _file
        else:
            if FileTool.get_file_ext(_file) != 'py':
                # 不是py文件，不进行处理
                return

            # 获取所在路径
            _deal_path = FileTool.get_parent_dir(_file)

        # 在所在路径增加__init__.py文件
        cls.create_init_py_file(
            _deal_path, install_set, package_path, add_copy_info=True
        )

        # 判断上一级路径是否处理
        _deal_path = FileTool.get_parent_dir(_deal_path).rstrip('/\\')
        _package_path = os.path.realpath(package_path).rstrip('/\\')
        if len(_deal_path) > len(_package_path):
            # 不是根目录，可以继续处理
            cls.add_init_py_by_file(_deal_path, install_set, package_path)

    @classmethod
    def add_python_package_file(cls, install_set: dict, deal_path: str, package_path: str):
        """
        对指定目录及子目录检查并增加python的init.py文件

        @param {dict} install_set - 预安装配置字典
        @param {str} deal_path - 要处理的路径

        @return {bool} - 返回指示当前目录或子目录是否具有.py文件
        """
        _has_py = False
        # 先检查当前目录
        _file_list = FileTool.get_filelist(path=deal_path, regex_str=r'.*\.py$', is_fullname=False)
        if len(_file_list) > 0:
            _has_py = True

        # 递归处理子目录
        _dir_list = FileTool.get_dirlist(path=deal_path, is_fullpath=True)
        for _sub_dir in _dir_list:
            _sub_has_py = cls.add_python_package_file(install_set, _sub_dir, package_path)
            if not _has_py and _sub_has_py:
                _has_py = True

        # 判断当前目录是否增加__init__.py
        if _has_py:
            cls.create_init_py_file(deal_path, install_set, package_path, add_copy_info=False)

        return _has_py

    #############################
    # 内部函数
    #############################
    @classmethod
    def _get_module_sub_name(cls, module_name: str):
        """
        获取短模块名(不含包名)

        @param {string} module_name - 完整模块名

        @return {string} - 返回不含包名的模块名
        """
        _index = module_name.rfind('.')
        if _index == -1:
            return module_name
        else:
            return module_name[_index + 1:]

    @classmethod
    def _file_name_to_module_name(cls, file_name: str):
        """
        文件名转换为模块名

        @param {str} file_name - 要转换的文件名

        @return {str} - 转换后的模块名
        """
        _file_name = file_name
        if file_name.endswith('.py'):
            _file_name = _file_name[0: -3]
        return _file_name.replace('\\', '/').replace('/', '.')

    @classmethod
    def _add_install_extend_path(cls, install_set: dict, path: str, prefix='servicer'):
        """
        将路径增加到安装配置字典的模块搜索路径中

        @param {dict} install_set - 预安装配置字典
        @param {str} path - 要添加的搜索路径
        @param {str} prefix='servicer' - xpath的前缀，针对私有控件的情况应传入'self_control/Control_name/servicer'
        """
        if path != '':
            # 添加搜索路径
            _xpath = '%s/extend_path' % prefix
            if _xpath in install_set['install_conf'].keys() and install_set['install_conf'][_xpath] != '':
                install_set['install_conf'][_xpath] = '%s|%s' % (
                    install_set['install_conf'][_xpath], path
                )
            else:
                install_set['install_conf'][_xpath] = path

    @classmethod
    def _add_install_module(cls, install_set: dict, base_info: dict, module_name: str, call_name: str,
                            package_path: str, is_file=False,
                            is_self_control=False, self_control_name='', prefix='servicer'):
        """
        将模块信息增加到预安装字典

        @param {dict} install_set - 预安装配置字典
        @param {dict} base_info - 要安装的包的基本信息
        @param {str} module_name - 模块名(或文件名，是相service下的相对路径)
        @param {str} call_name - 模块调用名
        @param {str} package_path - 安装包所在临时路径
        @param {bool} is_file=False - 是否文件名
        @param {bool} is_self_control=False - 是否应用库的自有控件
        @param {string} self_control_name='' - 自有控件名
        @param {str} prefix='servicer' - xpath的前缀，针对私有控件的情况应传入'self_control/Control_name/servicer'
        """
        _call_name = call_name
        _module_name = module_name
        if is_file:
            # 通过文件获取模块名 control.controlName.Version.service
            if is_self_control:
                _module_name = os.path.join(
                    'self-control', self_control_name, 'service', _module_name)
            else:
                _module_name = os.path.join('service', _module_name)

            _module_name = '%s/%s/%s/%s' % (
                'control' if base_info['package_type'] == 'Control' else 'applib',
                base_info['name'],
                BaseInstaller.get_main_version(base_info['version']),
                _module_name
            )
            _module_name = cls._file_name_to_module_name(_module_name)

        if _module_name != '':
            if _call_name == '':
                _call_name = cls._get_module_sub_name(_module_name)

            # 增加配置
            install_set['install_conf']['%s/module/%s' % (prefix, _call_name)] = _module_name

    @classmethod
    def _add_install_copy_file(cls, install_set: dict, file: str, package_path: str,
                               is_self_control=False, self_control_name=''):
        """
        将py文件复制信息增加到预安装配置字典
        （包括__init__.py文件的处理）

        @param {dict} install_set - 预安装配置字典
        @param {str} file - 文件名(service下的相对路径)
        @param {str} package_path - 安装包所在临时路径
        @param {bool} is_self_control=False - 是否应用库的自有控件
        @param {string} self_control_name='' - 自有控件名
        """
        # 文件的相对路径
        _file_path = ''
        if is_self_control:
            _file_path = os.path.join('self-control', self_control_name, 'service', file)
        else:
            _file_path = os.path.join('service', file)

        # 文件的真实路径
        _real_file_path = os.path.realpath(os.path.join(package_path, _file_path))

        # 添加复制配置
        install_set['server_copy'].append((_real_file_path, _file_path))

        # 对应添加__init__.py文件
        cls.add_init_py_by_file(_real_file_path, install_set, package_path)

    @classmethod
    def _add_install_path(cls, install_set: dict, base_info: dict, path: str, package_path: str,
                          is_self_control=False, self_control_name='', prefix='servicer'):
        """
        讲路径复制信息增加到预安装配置字典

        @param {dict} install_set - 预安装配置字典
        @param {dict} base_info - 要安装的包的基本信息
        @param {str} path - 要处理的路径（service下的相对路径）
        @param {str} package_path - 安装包所在临时路径
        @param {bool} is_self_control=False - 是否应用库的自有控件
        @param {string} self_control_name='' - 自有控件名
        @param {str} prefix='servicer' - xpath的前缀，针对私有控件的情况应传入'self_control/Control_name/servicer'
        """
        # 路径处理
        _prefix_path = ''
        if is_self_control:
            _prefix_path = os.path.join('self-control', self_control_name, 'service', path)
        else:
            _prefix_path = os.path.join('service', path)

        _real_path = os.path.realpath(os.path.join(package_path, _prefix_path))

        # 处理文件，加入到装载模块配置
        _file_list = FileTool.get_filelist(path=_real_path, regex_str=r'.*\.py$', is_fullname=False)
        for _file in _file_list:
            if _file == '__init__.py':
                continue

            cls._add_install_module(
                install_set, base_info,
                os.path.join(path, _file),
                '',
                package_path, is_file=True,
                is_self_control=is_self_control, self_control_name=self_control_name,
                prefix=prefix
            )

        # 处理子目录
        _dir_list = FileTool.get_dirlist(path=_real_path, is_fullpath=False)
        for _dir in _dir_list:
            cls._add_install_path(
                install_set, base_info,
                os.path.join(path, _dir),
                package_path, is_self_control=is_self_control,
                self_control_name=self_control_name, prefix=prefix
            )


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
