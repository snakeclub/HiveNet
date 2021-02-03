#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2018 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
tornado服务器的处理句柄模块
@module tornado_handler
@file tornado_handler.py
"""
import tornado.web


__MOUDLE__ = 'tornado_handler'  # 模块名
__DESCRIPT__ = u'tornado服务器的处理句柄模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2019.09.29'  # 发布日期


class HiveNetRequestHandler(tornado.web.RequestHandler):
    """
    重载RequestHandler基础类，作为HiveNet Tornado引擎的基础页面处理类
    """

    def write_error(self, status_code, **kwargs):
        """
        重载实现错误响应的页面重定向处理

        @param {int} status_code - 错误响应码
        """
        if status_code in [404]:
            # self.render('templates/error.html')
            self.write('HiveNetRequestHandler test write_error %d!' % status_code)
        else:
            return super().write_error(status_code, **kwargs)


class HiveNetStaticHandler(tornado.web.StaticFileHandler, HiveNetRequestHandler):
    """
    重载静态文件处理类
    注：目的是重定向异常页面，根据Python多继承二义性处理原则，会优先使用StaticFileHandler的方法
    """

    def write_error(self, status_code, **kwargs):
        """
        重载实现错误响应的页面重定向处理
        指定使用HiveNetRequestHandler的write_error方法进行处理

        @param {int} status_code - 错误响应码
        """
        HiveNetRequestHandler.write_error(self, status_code, **kwargs)


class HiveNetErrorHandler(HiveNetRequestHandler):
    """
    重写ErrorHandler(继承于HiveNetRequestHandler)
    Generates an error response with ``status_code`` for all requests.
    """

    def initialize(self, status_code: int) -> None:
        self.set_status(status_code)

    def prepare(self) -> None:
        raise tornado.web.HTTPError(self._status_code)

    def check_xsrf_cookie(self) -> None:
        # POSTs to an ErrorHandler don't actually have side effects,
        # so we don't need to check the xsrf token.  This allows POSTs
        # to the wrong url to return a 404 instead of 403.
        pass


class MainHandler(HiveNetRequestHandler):
    def get(self):
        self.write("Hello, world")


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
