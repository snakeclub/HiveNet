#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2018 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import os
from enum import Enum
from HiveNetLib.generic import CResult
from HiveNetLib.base_tools.file_tool import FileTool
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.simple_xml import SimpleXml, EnumXmlObjType
from HiveNetLib.base_tools.exception_tool import ExceptionTool
from HiveNetLib.base_tools.validate_tool import ValidateTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from HiveNet.lib.hivenet_tool import HiveNetTool
from HiveNet.lib.control_router import BaseRouter

"""
控件包/应用库包的包处理模块
@module packager
@file packager.py
"""

__MOUDLE__ = 'packager'  # 模块名
__DESCRIPT__ = u'控件包/应用库包的包处理模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2019.11.14'  # 发布日期


class BasePackager(object):
    """
    所有包处理类的基类
    """
    #############################
    # 公共变量
    #############################
    # 基础信息的验证规则
    _base_info_verify_rules = {
        'base_info': {
            'name': 'str_not_null',
            'version': (
                'And', [
                    'str_not_null',
                    (
                        'str_check_regex',
                        r'^(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})\.[0-9]{4}(((0[13578]|1[02])(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)(0[1-9]|[12][0-9]|30))|(02(0[1-9]|[1][0-9]|2[0-8])))_(Base|Alpha|Beta|RC|Release)$',
                        None,
                        '[$2]("$1") not match the version format like "1.0.0.20191114_Release"'
                    ),
                ],
            ),
            'package_type': (
                'And', [
                    'str_not_null',
                    ('check_in_enum', (['Control', 'AppLib']), ),
                ]
            ),
            'package_deal_control_verion': (
                'Or', [
                    (
                        'str_check_regex',
                        r'^[><]{0,1}(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})$',
                        None,
                        '[$2]("$1") not match the version format like "1.0.0" or ">1.0.0" or "<1.0.0" or "1.0.0-2.0.0"'
                    ),
                    (
                        'str_check_regex',
                        r'^(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})-(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})$',
                        None,
                        '[$2]("$1") not match the version format like "1.0.0" or ">1.0.0" or "<1.0.0" or "1.0.0-2.0.0"'
                    ),
                ],
            )
        }
    }

    #############################
    # 静态工具函数
    #############################
    @staticmethod
    def get_package_conf(file_or_path, pwd=None, **kwargs):
        """
        获取指定包的配置文件对象

        @param {string} file_or_path - 要获取配置文件的包文件或解压后的包路径
        @param {bytes} pwd=None - 解压密码
            示例：pwd='123456'.encode('utf-8')
        @param {kwargs} - 动态参数，用于兼容扩展

        @return {HiveNetLib.SimpleXml} - 配置文件的xml对象

        @throw {KeyError} - 当压缩包中没有包含配置文件时，抛出该异常
        """
        # 获取文件的二进制
        _file_bytes = None
        if os.path.isfile(file_or_path):
            # 压缩包
            _file_bytes = FileTool.read_zip_file(file_or_path, 'hivenet-conf.xml', pwd=pwd)
        else:
            # 文件夹
            with open(os.path.join(os.path.realpath(file_or_path), 'hivenet-conf.xml'), 'r') as f:
                _file_bytes = f.read()

        # 返回xml对象
        return SimpleXml(_file_bytes, obj_type=EnumXmlObjType.Bytes,
                         encoding='utf-8', remove_blank_text=True)

    @staticmethod
    def get_package_base_info(file_or_path, pwd=None, **kwargs):
        """
        获取指定包的基本信息字典

        @param {string} file_or_path - 要获取类型的包文件或解压后的包路径
        @param {bytes} pwd=None - 解压密码
            示例：pwd='123456'.encode('utf-8')
        @param {kwargs} - 动态参数，用于兼容扩展

        @return {dict} - 包的基本信息字典

        @throws {Exception} - 当出现异常时将抛出特定异常
        """
        _xml_doc = BasePackager.get_package_conf(file_or_path, pwd=pwd, **kwargs)
        _dict = _xml_doc.to_dict(xpath='base_info')['base_info']

        # 修正一些漏填的信息
        _dict.setdefault('package_type', 'Control')
        _dict.setdefault('package_deal_control_name', 'HiveNetPackager')
        _dict.setdefault('package_deal_control_verion', '')
        _dict.setdefault('package_deal_class_name', '')
        if _dict['package_type'] == '':
            _dict['package_type'] = 'Control'
        if _dict['package_deal_control_name'] == '':
            _dict['package_deal_control_name'] = 'HiveNetPackager'
        if _dict['package_deal_class_name'] == '':
            if _dict['package_type'] == 'Control':
                _dict['package_deal_class_name'] = 'ControlPackager'
            elif _dict['package_type'] == 'AppLib':
                _dict['package_deal_class_name'] = 'AppLibPackager'

        # 返回字典
        return _dict

    @staticmethod
    def unpack(filename, dest_path=None, pwd=None, **kwargs):
        """
        解压缩指定包

        @param {string} filename - 要解压缩的文件
        @param {string} dest_path=None - 要解压缩到的目录
            注：为None时解压至文件所在路径，放入与文件名（去掉扩展名）相同的目录中
        @param {bytes} pwd=None - 解压密码
            示例：pwd='123456'.encode('utf-8')
        @param {kwargs} - 动态参数，用于兼容扩展
        """
        FileTool.unzip(filename, dest_path=dest_path, pwd=pwd, **kwargs)

    @classmethod
    def pack_to_package(cls, package_path, dest_path=None, is_verify=True, **kwargs):
        """
        将指定的目录打包为控件包/应用包

        @param {string} package_path - 要打包的目录
        @param {string} dest_path=None - 打包后包文件存储的目录，不传代表与打包目录在同一个目录下
        @param {bool} is_verify=True - 是否校验包配置是否准确
        @param {kwargs} - 动态参数，用于兼容扩展

        @return {CResult} - 生成结果，'00000' - 生成成功，其他 - 生成失败
            result.path 结果包的存储路径
            result.filename 结果包的文件名
        """
        _result = CResult('00000')
        with ExceptionTool.ignored_cresult(result_obj=_result):
            # 检查路径是否正确
            if not os.path.exists(package_path):
                return CResult('10801', i18n_msg_paras=(package_path))
            if not os.path.isdir(package_path):
                return CResult('10802', i18n_msg_paras=(package_path))

            _src_path, _src_file = os.path.split(os.path.realpath(package_path))
            if dest_path is None:
                dest_path = _src_path

            # 获取配置文件
            _xml_doc = cls.get_package_conf(package_path, **kwargs)

            # 校验包配置是否准确
            if is_verify:
                _result = cls.verify_package_unpacked(package_path, conf_xml_doc=_xml_doc, **kwargs)
                if not _result.is_success():
                    # 检查不通过
                    return _result

            # 执行打包
            _filename = '%s-%s-%s.zip' % (
                'applib' if _xml_doc.get_value('base_info/package_type') == 'AppLib' else 'control',
                _xml_doc.get_value('base_info/name'),
                _xml_doc.get_value('base_info/version')
            )
            FileTool.zip(package_path, dest_path=dest_path, dest_filename=_filename)
            _result.path = dest_path
            _result.filename = _filename

        return _result

    @classmethod
    def verify_package_unpacked(cls, package_path, conf_xml_doc=None, **kwargs):
        """
        校验指定包的配置是否正确(已解压的情况)

        @param {string} package_path - 要校验的包文件解压后的包路径
        @param {HiveNetLib.SimpleXml} conf_xml_doc=None - 包的配置文件对象，如果此前已获取过，可以直接传入
        @param {kwargs} - 动态参数，用于兼容扩展

        @return {CResult} - 校验结果，'00000' - 校验通过，其他 - 校验失败
        """
        _result = CResult('00000')
        with ExceptionTool.ignored_cresult(result_obj=_result):
            # 检查目录
            if not os.path.exists(package_path):
                return CResult('10801', i18n_msg_paras=(package_path))

            if not os.path.isdir(package_path):
                # 非目录，直接返回失败
                return CResult('10802', i18n_msg_paras=(package_path))

            # 获取conf_xml_doc
            if conf_xml_doc is None:
                conf_xml_doc = cls.get_package_conf(package_path, pwd=None, **kwargs)

            # 检查基础信息的必要要素
            _result = ValidateTool.check_by_rule(
                cls._base_info_verify_rules, conf_xml_doc.to_dict(xpath='base_info'), obj_id=''
            )

            if not _result.is_success():
                return _result

            # 调用继承类的检查方法
            _result = cls._verify_package_unpacked(
                package_path=package_path, conf_xml_doc=conf_xml_doc, **kwargs
            )

        return _result

    @classmethod
    def pre_install_package(cls, base_info: dict, package_path: str, **kwargs):
        """
        通过解压后的安装包路径进行预安装

        @param {dict} base_info - 通过BasePackager.get_package_base_info获取到的包基本配置信息
        @param {str} package_path - 安装包所在临时路径
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
        return cls._pre_install_package(base_info, package_path, **kwargs)

    #############################
    # 继承类需要实现的内部方法
    #############################
    @classmethod
    def _verify_package_unpacked(cls, package_path, conf_xml_doc, **kwargs):
        """
        继承类必须要实现的包校验方法(静态类)

        @param {string} package_path - 包的unpack路径
        @param {HiveNetLib.SimpleXml} conf_xml_doc - 包的配置文件对象
        @param {kwargs} - 动态参数，用于兼容扩展

        @return {CResult} - 校验结果，'00000' - 校验通过，其他 - 校验失败
        """
        return CResult(code='00000')

    @classmethod
    def _pre_install_package(cls, base_info: dict, package_path: str, **kwargs):
        """
        通过解压后的安装包路径进行预安装
        (需继承类实现个性化的安装处理, 如进行文件处理)

        @param {dict} base_info - 通过BasePackager.get_package_base_info获取到的包基本配置信息
        @param {str} package_path - 安装包所在临时路径
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


class ControlPackager(BasePackager):
    """
    控件包具体处理类
    """
    #############################
    # 继承类需要实现的内部方法
    #############################
    @classmethod
    def _verify_package_unpacked(cls, package_path, conf_xml_doc, **kwargs):
        """
        继承类必须要实现的包校验方法(静态类)

        @param {string} package_path - 包的unpack路径
        @param {HiveNetLib.SimpleXml} conf_xml_doc - 包的配置文件对象
        @param {kwargs} - 动态参数，用于兼容扩展

        @return {CResult} - 校验结果，'00000' - 校验通过，其他 - 校验失败
        """
        # TODO({$AUTHOR$}): 待后续增加校验规则

        return CResult(code='00000')

    @classmethod
    def _pre_install_package(cls, base_info: dict, package_path: str, **kwargs):
        """
        通过解压后的安装包路径进行预安装
        (需继承类实现个性化的安装处理, 如进行文件处理)

        @param {dict} base_info - 通过BasePackager.get_package_base_info获取到的包基本配置信息
        @param {str} package_path - 安装包所在临时路径
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
        # 准备预安装的信息
        _install_set = {
            'install_conf': dict(),
            'static_copy': list(),
            'server_copy': list()
        }

        # 基本遍历
        _hivenet_tool: HiveNetTool = RunTool.get_global_var('HIVENET_TOOL')
        _package_node_router: BaseRouter = _hivenet_tool.package_node_router

        # 遍历control_info中的每个节点进行处理
        _conf_doc = cls.get_package_conf(package_path, **kwargs)
        _control_info_dict = _conf_doc.to_dict('/hivenet/control_info')['control_info']
        for _node in _control_info_dict.keys():
            _node_install_set = _package_node_router.get_pre_install_set(
                _node, _control_info_dict[_node], base_info,
                package_path, **kwargs
            )

            # 更新到预安装字典中
            _install_set['install_conf'].update(_node_install_set.get('install_conf', {}))
            _install_set['static_copy'].extend(_node_install_set.get('static_copy', {}))
            _install_set['server_copy'].extend(_node_install_set.get('server_copy', {}))

        # 返回预安装字典
        return _install_set


class AppLibPackager(BasePackager):
    """
    应用库包具体处理类
    """
    pass


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))

    _base_info_verify_rules = {
        'base_info': {
            'name': 'str_not_null',
            'version': (
                'And', [
                    'str_not_null',
                    (
                        'str_check_regex',
                        r'^(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})\.[0-9]{4}(((0[13578]|1[02])(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)(0[1-9]|[12][0-9]|30))|(02(0[1-9]|[1][0-9]|2[0-8])))_(Base|Alpha|Beta|RC|Release)$',
                        None,
                        '[$2]("$1") not match the version format like "1.0.0.20191114_Release"'
                    ),
                ],
            ),
            'package_type': (
                'And', [
                    'str_not_null',
                    ('check_in_enum', (['Control', 'AppLib']), ),
                ]
            ),
            'package_deal_control_verion': (
                'Or', [
                    (
                        'str_check_regex',
                        r'^[><]{0,1}(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})$',
                        None,
                        '[$2]("$1") not match the version format like "1.0.0" or ">1.0.0" or "<1.0.0" or "1.0.0-2.0.0"'
                    ),
                    (
                        'str_check_regex',
                        r'^(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})-(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})$',
                        None,
                        '[$2]("$1") not match the version format like "1.0.0" or ">1.0.0" or "<1.0.0" or "1.0.0-2.0.0"'
                    ),
                ],
            )
        }
    }

    _obj = {
        'base_info': {
            'name': 'abc',
            'version': '1.0.0.20191114_Release',
            'package_type': 'Control',
            'package_deal_control_verion': '1.3.0-1..0'
        }
    }

    print(
        ValidateTool.check_by_rule(_base_info_verify_rules, _obj, obj_id='')
    )

    import re
    a = re.match(r'^(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})\.(0|[1-9][0-9]{0,})', '1.0.0.3r34333333')
    print(a)

    print(os.path.abspath(os.path.join('a/bcd/efg/abc.txt', '..')))
    print(os.path.abspath(os.path.join('a/bcd/efg', '..')))
