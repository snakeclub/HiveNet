#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2018 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
HiveNet Web Server
@module hivenet_server
@file hivenet_server.py
"""

import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define, options

__MOUDLE__ = 'hivenet_server'  # 模块名
__DESCRIPT__ = u'HiveNet Web服务主模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2019.05.20'  # 发布日期


#############################
# 定义全局变量options中的参数值
#############################
define('port', default=8083, help='run on the given port', type=int)
define('name', default='HiveNet_Server_01', help='host name of the server', type=str)
define('server-config', default='server.xml',
       help='hivenet server startup config file, could be with path')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    tornado.options.parse_command_line()  # 获取命令行参数到options中
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
