#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2018 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
HiveNet Server Console (控制台)
@module console
@file console.py
"""

import sys
import os
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.base_tools.file_tool import FileTool
from HiveNetLib.simple_console.server import ConsoleServer
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


__MOUDLE__ = 'server_console'  # 模块名
__DESCRIPT__ = u'HiveNet Server Console (控制台)'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2019.09.21'  # 发布日期


def main(**kwargs):
    # 执行控制台服务，指定默认配置文件路径为运行程序目录下的“conf/client_console_config.xml”
    _cmd_opts = RunTool.get_kv_opts()
    _execute_file_path = os.path.realpath(FileTool.get_file_path(__file__))
    if 'base_path' in _cmd_opts.keys():
        _execute_file_path = os.path.realpath(_cmd_opts['base_path'])

    ConsoleServer.console_main(
        execute_file_path=_execute_file_path,
        default_config_file=os.path.join(_execute_file_path, 'conf/server_console_config.xml'),
        **kwargs
    )


if __name__ == '__main__':
    main()
