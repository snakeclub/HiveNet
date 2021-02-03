## 框架级全局变量

- CONSOLE_GLOBAL_PARA ：控制台所获取的全局参数（simple_console.ConsoleServer框架）
  - execute_file_path - 执行文件所在目录
  - work_path - 当前工作目录，可以通过cd命令切换，通过pwd命令查看
  - config_encoding - 控制台配置文件编码
  - config_file - 控制台配置文件（含路径和文件名）
- HIVENET_TOOL ：HiveNetTool的实例对象，便于使用一些框架级公共方法及属性
- ENGINE_SERVER : EngineServerFW的服务引擎实例对象
- ENGINE_CONFIG : 服务引擎的配置字典
  - server_config - 完整的服务启动配置字典（server.xml的engine_server配置）
  - website_path - 网站的根目录
  - static_path - 网站的静态资源目录
  - server_path - 后台服务资源的根目录
  - temp_path - 临时目录路径，用于处理上传、下载、控件安装的临时文件
- INSTALLED_DOC ： 配置已安装应用库/控件库/应用清单的XML实例对象（HiveNetLib.SimpleXml）
- IMPORT_SERVICER : 已装载的后台服务索引字典
- BASE_CONTROL : 基础控件配置字典，对应installed_list.xml的base_control_config配置，可以通过HiveNetTool.get_base_control_class(name)获取指定基础控件的class
  - Installer - 安装控件配置
    - default_class - 默认class
    - control_name - 控件名
    - control_version - 控件版本要求
    - call_name - 模块调用名
    - class_name - 调用类名
  - ……
- PACKAGE_NODE_ROUTER ： 控件包/应用库包的节点处理类的访问路由对象实例







