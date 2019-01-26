# HiveNet控件定义规范

规范英文名：HiveNet Control Definition Standards

规范中文名：HiveNet 控件定义规范

**HiveNet标识名：hivenet_control_definition_standards**

**HiveNet版本：v1.0.0**



## 说明

执行本规范可基于控件定义文档（Control Definition Document）进行HiveNet标准控件的信息描述，基于控件定义文档可获取控件运行平台、依赖、继承、替代标准等信息，用于自动配置运行环境以及在HiveNet框架中便捷进行控件替换，并可将控件纳入HiveNet控件仓库（HiveNet Control Repository）统一管理。



## 文档命名规范

控件定义文档必须为utf-8格式的xml文件，命名规范为“控件名.xml”。

命名空间：用于标识组件的作用域，以支持