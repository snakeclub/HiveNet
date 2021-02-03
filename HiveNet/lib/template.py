#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2018 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
from abc import ABC, abstractmethod  # 利用abc模块实现抽象类
from tornado.template import Template, Loader, execute as Execute
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))


"""
模板处理模块，定义应用及控件的模板处理框架
@module template
@file template.py
"""

__MOUDLE__ = 'template'  # 模块名
__DESCRIPT__ = u'模板处理模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2019.09.20'  # 发布日期


class TemplateFW(ABC):
    """
    应用及控件的模板处理框架
    定义标准的模板处理方法
    """
    #############################
    # 实现类应重载的函数
    #############################
    @abstractmethod
    def __init__(self, template_str):
        """
        构造函数，生成模板对象

        @param {string} template_str - 创建模板的字符串
        """
        raise NotImplementedError

    @abstractmethod
    def generate(self, **kwargs):
        """
        根据传入的参数按模板生成实际显示信息

        @param {**kwargs} - 生成显示信息的具体入参

        @return {string} - 所生成的显示信息
        """
        raise NotImplementedError

    @abstractmethod
    def set_template_path(self, path):
        """
        设置模板文件路径

        @param {string} path - 设置模板文件的路径
        """
        raise NotImplementedError

    @abstractmethod
    def load(self, template_filename):
        """
        通过文件装载模板到本对象中

        @param {string} template_filename - 要装载的文件名
        """
        raise NotImplementedError

    @abstractmethod
    def load_to_template(self, template_filename):
        """
        通过文件装载模板到新的模板对象中（从当前模板对象的文件路径中获取）

        @param {string} template_filename - 要装载的文件名

        @return {TemplateFW} - 返回创建的模板对象
        """
        raise NotImplementedError

    @abstractmethod
    def render(self, template_filename, **kwargs):
        """
        将指定模板文件生成实际显示信息（从当前模板对象的文件路径中获取）

        @param {string} template_filename - 要装载的文件名
        @param {**kwargs} - 生成显示信息的具体入参

        @return {string} - 所生成的显示信息
        """
        raise NotImplementedError

    #############################
    # 实现类可选重载的函数
    #############################
    def execute(self, **kwargs):
        """
        将函数对象加载到模板处理支持中

        @param {**kwargs} - 要支持的函数清单，传参如下：
            支持函数名=支持函数对象
        """
        return


class TemplateTornado(TemplateFW):
    """
    tornado模板处理类
    定义tornado标准的模板处理方法
    """
    _template = None  # tornado的Template对象
    _loader = None  # tornado的Loader对象

    def __init__(self, template_str):
        """
        构造函数，生成模板对象

        @param {string} template_str - 创建模板的字符串
        """
        self._template = Template(template_str)
        self._loader = Loader('')

    def generate(self, **kwargs):
        """
        根据传入的参数按模板生成实际显示信息

        @param {**kwargs} - 生成显示信息的具体入参

        @return {string} - 所生成的显示信息
        """
        return self._template.generate(**kwargs)

    def set_template_path(self, path):
        """
        设置模板文件路径

        @param {string} path - 设置模板文件的路径
        """
        self._loader = Loader(path)

    def load(self, template_filename):
        """
        通过文件装载模板到本对象中

        @param {string} template_filename - 要装载的文件名
        """
        self._template = self._loader.load(template_filename)

    def load_to_template(self, template_filename):
        """
        通过文件装载模板到新的模板对象中（从当前模板对象的文件路径中获取）

        @param {string} template_filename - 要装载的文件名

        @return {TemplateFW} - 返回创建的模板对象
        """
        return self._loader.load(template_filename)

    def render(self, template_filename, **kwargs):
        """
        将指定模板文件生成实际显示信息（从当前模板对象的文件路径中获取）

        @param {string} template_filename - 要装载的文件名
        @param {**kwargs} - 生成显示信息的具体入参

        @return {string} - 所生成的显示信息
        """
        return self._loader.load(template_filename).generate(**kwargs)

    def execute(self, **kwargs):
        """
        将函数对象加载到模板处理支持中

        @param {**kwargs} - 要支持的函数清单，传参如下：
            支持函数名=支持函数对象
        """
        Execute(**kwargs)


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
