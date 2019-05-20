@echo off
rem 将命令窗口字符集修改为UTF-8
chcp 65001
rem 设置nginx在当前批处理文件上的相对路径目录名
set NGINX_PATH=openresty-1.15.8.1-win64
rem 设置配置文件的路径
set CONF_PATH=D:\dev\github\HiveNet\nginx_conf\
rem 设置HiveNet Web服务的路径
set HIVENET_PATH=D:\dev\github\HiveNet\HiveNet\

rem 切换到当前批处理文件所在的盘符和路径
cd /d %~dp0
cd %NGINX_PATH%

@echo on
echo 启动Nginx服务
start nginx -c %CONF_PATH%nginx_static_server.conf
start nginx -c %CONF_PATH%nginx_store_server.conf
start nginx -c %CONF_PATH%nginx_proxy_server.conf

echo 启动HiveNet Web服务
start "" cmd /k "python %HIVENET_PATH%hivenet_server.py --port=8083 --name=HiveNet_Server_1"

pause