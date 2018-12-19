#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
#  Copyright 2018 黎慧剑
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.


"""The setup.py file for Python HiveNet."""

from setuptools import setup, find_packages


LONG_DESCRIPTION = """
HiveNet（蜂巢）的目标是建立一个基于HTML模板控件和灵活配置的快速Web应用
框架，降低Web应用开发的成本和周期，让产品及开发人员更专注于后端实际业务
逻辑的实现，而无需在界面开发上投入过多精力
""".strip()

SHORT_DESCRIPTION = """
基于HTML模板控件和灵活配置的快速Web应用框架.""".strip()

DEPENDENCIES = [
    'tornado>=5.0.2'
]

# DEPENDENCIES = []

TEST_DEPENDENCIES = []

VERSION = '0.1.0'
URL = 'https://github.com/snakeclub/HiveNet'

setup(
    # pypi中的名称，pip或者easy_install安装时使用的名称
    name="HiveNet",
    version=VERSION,
    author="黎慧剑",
    author_email="snakeclub@163.com",
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license="Mozilla Public License 2.0",
    keywords="HiveNet Frameworks",
    url=URL,
    # 需要打包的目录列表, 可以指定路径packages=['path1', 'path2', ...]
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
    package_data={'': ['*.json']},  # 这里将打包所有的json文件
    # 此项需要，否则卸载时报windows error
    zip_safe=False
)
