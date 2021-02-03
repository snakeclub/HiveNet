#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
控件访问类路由基础模块
@module control_router
@file control_router.py
"""
import sys
import os
import copy
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.base_tools.import_tool import ImportTool
from HiveNetLib.base_tools.value_tool import ValueTool
from HiveNetLib.simple_xml import SimpleXml
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from HiveNet.lib.hivenet_tool import HiveNetTool

__MOUDLE__ = 'control_router'  # 模块名
__DESCRIPT__ = u'控件访问类路由基础模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.02.20'  # 发布日期


class BaseRouter(object):
    """
    访问路由框架类
    """
    #############################
    # 公共变量
    # init_para : 初始化参数(init的kwargs)
    # HIVENET_TOOL : HiveNetTool工具实例
    # INSTALLED_DOC : installed_list.xml的访问对象
    # router_id : 路由id, 将影响在installed_list.xml的存储标签, 需要在实例类中设置
    # router_dict : 路由字典（对应访问类的配置）
    #       key - 访问类ID
    #       value - 类配置信息字典
    #           init_object - 已初始化的类实例对象, 如果无需实例化为None
    #           init_para - 初始化参数
    #           default_class - 默认处理类，直接提供一个已安装或已存在的类对象; 路由类会尝试先获取最新的可用控件进行处理,
    #               如果没有设置可用控件或找不到可用版本，就会使用默认处理类进行处理
    #           control_name - 获取处理类的HiveNet控件名
    #           control_version - 可支持的控件版本，可配置的方式如下:
    #             空代表支持所有版本的处理
    #             主版本号.次版本号.修订版本号 : 仅支持指定版本处理
    #             >主版本号.次版本号.修订版本号 : 支持指定版本以上的版本处理
    #             <主版本号.次版本号.修订版本号 : 支持指定版本以下的版本处理
    #             主版本号.次版本号.修订版本号-主版本号.次版本号.修订版本号 : 支持指定两个版本之间的版本版本处理
    #           call_name - 模块的访问名
    #           class_name - 处理类名
    #############################

    #############################
    # 公共函数
    #############################
    def __init__(self, **kwargs):
        """
        构造函数
        """
        self.init_para = kwargs
        self.HIVENET_TOOL: HiveNetTool = RunTool.get_global_var('HIVENET_TOOL')
        self.INSTALLED_DOC: SimpleXml = self.HIVENET_TOOL.installed_doc
        self.router_dict = dict()
        self.router_id = ''

        # 调用继承类的初始化函数
        self._init(**kwargs)

        # 执行路由装载处理
        if self.router_id == '':
            raise ValueError('must set the value of router_id in _init() function')

        _router_config = self.INSTALLED_DOC.to_dict(
            '/installed/router_%s' % self.router_id
        )['router_%s' % self.router_id]
        _router_config.update(
            {
                'is_init': 'false',
                'init_para': {}
            }
        )
        for _class_id in _router_config.keys():
            self.register_router(
                _class_id, is_init=(_router_config[_class_id]['is_init'] == 'true'),
                default_class_module=_router_config[_class_id]['default_class']['module_name'],
                default_class_path=_router_config[_class_id]['default_class']['extend_path'],
                default_class_name=_router_config[_class_id]['default_class']['class_name'],
                control_name=_router_config[_class_id]['control_name'],
                control_version=_router_config[_class_id]['control_version'],
                call_name=_router_config[_class_id]['call_name'],
                class_name=_router_config[_class_id]['class_name'],
                is_write_install=False
            )

    def register_router(self, class_id: str, is_init=False, init_para={}, default_class_module='',
                        default_class_path='', default_class_name='',
                        control_name='', control_version='',
                        call_name='', class_name='', is_write_install=True):
        """
        注册一个访问类路由配置

        @param {string} class_id - 访问类ID
            注意：如果class_id已经配置过，将覆盖原来的配置
        @param {bool} is_init=False - 是否实例化类
        @param {dict} init_para={} - 实例化对象的传入参数字典
        @param {string} default_class_module='' - 默认处理类的模块名(含包路径)
        @param {string} default_class_path='' - 默认处理类的模块所在路径(增加搜索路径)
        @param {string} default_class_name='' - 默认处理类的处理类名
        @param {string} control_name='' - 获取处理类的HiveNet控件名
        @param {string} control_version='' - 可支持的控件版本，可配置的方式如下:
            空代表支持所有版本的处理
            主版本号.次版本号.修订版本号 : 仅支持指定版本处理
            >主版本号.次版本号.修订版本号 : 支持指定版本以上的版本处理
            <主版本号.次版本号.修订版本号 : 支持指定版本以下的版本处理
            主版本号.次版本号.修订版本号-主版本号.次版本号.修订版本号 : 支持指定两个版本之间的版本版本处理
        @param {string} call_name='' - 模块的访问名
        @param {string} class_name='' - 处理类名
        @param {bool} is_write_install=True - 是否写入installed_list.xml配置
        """
        if self.router_id == '':
            raise ValueError('must set the value of router_id in _init() function')

        # 写入installed_list.xml配置
        if is_write_install:
            _base_path = '/installed/router_%s/%s' % (self.router_id, class_id)
            self.HIVENET_TOOL.set_config_xml_value(
                self.INSTALLED_DOC,
                {
                    'is_init': ('true' if is_init else 'false'),
                    'default_class/module_name': default_class_module,
                    'default_class/extend_path': default_class_path,
                    'default_class/class_name': default_class_name,
                    'control_name': control_name,
                    'control_version': control_version,
                    'call_name': call_name,
                    'class_name': class_name
                },
                base_xpath=_base_path
            )

            # 写入初始化参数
            self.INSTALLED_DOC.set_value_by_dict(
                _base_path,
                init_para
            )
            self.INSTALLED_DOC.save()

        # 加入到路由表
        _class = self._get_router_default_class(
            default_class_module, default_class_path, default_class_name
        )
        _init_para = copy.deepcopy(init_para)
        self.router_dict[class_id] = {
            'init_object': None,
            'init_para': _init_para,
            'default_class': _class,
            'control_name': control_name,
            'control_version': control_version,
            'call_name': call_name,
            'class_name': class_name
        }

        # 执行对象初始化
        if is_init:
            _class = self.get_service_deal_class(class_id)
            if _class is not None:
                self.router_dict[class_id]['init_object'] = _class(**_init_para)

    def get_class(self, class_id: str):
        """
        获取访问类

        @param {string} class_id - 访问类ID

        @return {object} - 可使用的访问类, 如果获取不到返回None
        """
        if class_id not in self.router_dict.keys():
            return None

        _router_dict = self.router_dict[class_id]
        _deal_class = None
        if _router_dict['control_name'] != '':
            _deal_class = self.HIVENET_TOOL.get_base_control_class('Installer').get_import_servicer_class(
                _router_dict['class_name'], 'Control', _router_dict['control_name'],
                _router_dict['control_version'], _router_dict['call_name']
            )

        if _deal_class is None:
            _deal_class = _router_dict['default_class']

        return _deal_class

    def get_init_object(self, class_id: str):
        """
        获取访问类实例对象

        @param {string} class_id - 访问类ID

        @return {object} - 可使用的访问类实例对象, 如果获取不到返回None
        """
        if class_id not in self.router_dict.keys():
            return None

        return self.router_dict[class_id]['init_object']

    def get_pre_install_set(self, class_id: str, node_dict: dict, base_info: dict, package_path: str, **kwargs):
        """
        获取制定配置节点的预安装配置结果

        @param {string} class_id - 访问类ID
        @param {dict} node_dict - 要处理的配置节点字典
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

        # 执行实例对象或类方法
        return self._get_pre_install_set(
            class_id, node_dict, base_info, package_path, **kwargs
        )

    #############################
    # 内部函数
    #############################
    def _get_router_default_class(self, module_name: str, extend_path: str, class_name: str):
        """
        获取路由的默认处理类

        @param {string} module_name - 模块名(含包路径)
        @param {string} extend_path - 模块所在路径(增加搜索路径)
        @param {string} class_name - 处理类名

        @return {Object} - 处理类对象，如果获取不到返回None
        """
        try:
            if module_name == '':
                return None

            _module = ImportTool.import_module(
                module_name, extend_path=(None if extend_path == '' else extend_path)
            )

            return getattr(_module, class_name)
        except:
            return None

    #############################
    # 需继承类实现的函数
    #############################
    def _init(self, **kwargs):
        """
        继承类自有构造函数处理
        (需继承类实现个性化的初始化处理, 注意必须设置self.router_id的值)

        @param {kwargs} - 扩展参数
        """
        pass

    def _get_pre_install_set(self, class_id: str, node_dict: dict, base_info: dict,
                             package_path: str, **kwargs):
        """
        继承类自有预安装处理
        (继承类可以重载实现个性化的预安装处理)

        @param {string} class_id - 访问类ID
        @param {dict} node_dict - 要处理的配置节点字典
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
        _class_obj = self.get_init_object(class_id)
        if _class_obj is None:
            # 没有初始化的情况，尝试获取类对象，执行静态方法
            _class_obj = self.get_class(class_id)

        if _class_obj is None:
            # 找不到访问类，返回空配置
            return dict()

        return _class_obj.get_pre_install_set(
            class_id, node_dict, base_info, package_path, **kwargs
        )


class PackageNodeRouter(BaseRouter):
    """
    控件包/应用库包节点处理对象访问路由
    """

    #############################
    # 需继承类实现的函数
    #############################
    def _init(self, **kwargs):
        """
        继承类自有构造函数处理
        (需继承类实现个性化的初始化处理, 注意必须设置self.router_id的值)

        @param {kwargs} - 扩展参数
        """
        self.router_id = 'package_node'


class ResourceListRouter(BaseRouter):
    """
    资源类节点(resource_list)的处理对象访问路由
    """

    #############################
    # 需继承类实现的函数
    #############################
    def _init(self, **kwargs):
        """
        继承类自有构造函数处理
        (需继承类实现个性化的初始化处理, 注意必须设置self.router_id的值)

        @param {kwargs} - 扩展参数
        """
        self.router_id = 'resource_list'

    def _get_pre_install_set(self, class_id: str, node_dict: dict, base_info: dict,
                             package_path: str, **kwargs):
        """
        继承类自有预安装处理
        (继承类可以重载实现个性化的预安装处理)

        @param {string} class_id - 访问类ID
        @param {dict} node_dict - 要处理的配置节点字典
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
        # 由PackageNodeRouter发起的调用，class_id会是'resource_list', 直接循环处理resource_list中的数组
        for _resource in node_dict:
            _class_id = _resource.get('type', '')
            _class_obj = self.get_init_object(_class_id)
            if _class_obj is None:
                # 没有初始化的情况，尝试获取类对象，执行静态方法
                _class_obj = self.get_class(_class_id)

            if _class_obj is None:
                # 找不到访问类，返回空配置
                return dict()

            # 调用节点的实际处理dealer
            return _class_obj.get_pre_install_set(
                _class_id, _resource, base_info, package_path, **kwargs
            )


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
