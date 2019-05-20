@echo off
rem 将命令窗口字符集修改为UTF-8
chcp 65001
rem 设置nginx在当前批处理文件上的相对路径目录名
set NGINX_PATH=openresty-1.15.8.1-win64
rem 设置配置文件的路径
set CONF_PATH=D:\dev\github\HiveNet\nginx_conf\

rem 切换到当前批处理文件所在的盘符和路径
cd /d %~dp0
cd %NGINX_PATH%

@echo on
echo 关闭Nginx服务
nginx -s stop -c %CONF_PATH%nginx_static_server.conf
nginx -s stop -c %CONF_PATH%nginx_store_server.conf
nginx -s stop -c %CONF_PATH%nginx_proxy_server.conf

pause