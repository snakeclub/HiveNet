# Javascript代码规范

规范英文名：HiveNet Javascript Coding Standards

规范中文名：HiveNet Javascript代码规范

**HiveNet标识名：hivenet_javascript_coding_standards**

**HiveNet版本：v1.0.0**

参考文档：JSDoc中文文档 http://www.css88.com/doc/jsdoc/index.html

## 代码风格规范 

本章定义的是Javascript代码的编写风格，旨在指导开发人员所编写的代码风格统一且保障较好的可读性（遵循JSDoc规范）。 

### 分号

- 每个代码行、定义块（例如类、函数等定义）结束后必须由 “ ; ” 显式标注语句结束。

  ```
  //代码行
  $.modalControl = new Object();
  
  //定义块
  (function ($) {
      ...
  })(jQuery);
  
  //函数定义
  function debug(str) {
      if ($.debug === true) {
          alert("debug：" + str);
      }
  };
  ```

- 在每个js文件的首行代码前面加上"; + 空格"，避免多个js文件加载时存在遗漏";"命令结束的问题。

  ```
  //以下为文件首行
  ; (function ($) {
      ...
  })(jQuery);
  ```


### 行长度

每行不超过80个字符，以下情况除外：

- 注释里的URL


### 缩进

用4个空格来缩进代码，绝对不要用tab，也不要tab和空格混用。对于行连接的情况，你应该要么垂直对齐换行的元素，或者使用4空格的悬挂式缩进(这时第一行不应该有参数) 。

       // 与起始变量对齐
       foo = long_function_name(var_one, var_two,
                                var_three, var_four)
    
       // 字典中与起始值对齐
       foo = {
           long_dictionary_key: value1 +
                                  value2,
           ...
       }
    
       // 4 个空格缩进，第一行不需要
       foo = long_function_name(
           var_one, var_two, var_three,
           var_four)
    
       // 字典中 4 个空格缩进
       foo = {
           long_dictionary_key:
               long_dictionary_value,
           ...
       }


### 空行

顶级定义之间空两行, 次级定义之间空一行。顶级定义指代码文件第1层的定义，包括类定义、函数定义、变量定义等，定义之间空两行；次级定义指在类内部或函数内部的方法、变量定义，定义之间空一行。函数或方法中, 某些地方要是你觉得合适, 就空一行。

文件最后以一行空行结束。

**注意：汇集在一起的变量定义无需空行，或可按块空一行。**



### 空格

不要在逗号, 分号, 冒号前面加空格, 但应该在它们后面加(除了在行尾)。 

在二元操作符两边都加上一个空格, 比如赋值(=), 比较(==, <, >, !=, <>, <=, >=, in, not in, is, is not), 布尔(and, or, not)。至于算术操作符两边的空格该如何使用, 需要你自己好好判断. 不过两侧务必要保持一致。

不要用空格来垂直对齐多行间的标记, 因为这会成为维护的负担(适用于:, #, =等) 。

系统关键字后有一个空格，例如 if/else/while/try 相邻的括号、大括号应与关键字之间有一个空格间隔开。

```
规范：
if (opts.fade) {
    ...
} else {
    ...
}

try {
    ...
} catch (e) {
    ...
}

while (condition) {
    ...
}
```



## 命名规范

Ø    所谓"内部(Internal)"表示仅模块内可用, 或者, 在类内是保护或私有的.

Ø    用单下划线(_)开头表示模块变量或函数是protected.

Ø    用双下划线(__)开头的实例变量或方法表示类内私有.

Ø    对类名使用大写字母开头的单词(如CapWords, 即Pascal风格), 但是文件名应该用小写加下划线的方式(如lower_with_under.js)。

| **Type**                                                     | **Public**         | **Internal**                                                 |
| ------------------------------------------------------------ | ------------------ | ------------------------------------------------------------ |
| File（文件）                                                 | lower_with_under   | _lower_with_unde                                             |
| Classes（类）                                                | CapWords           | _CapWords                                                    |
| Functions（函数）                                            | lower_with_under() | _lower_with_under()                                          |
| Global/Class   Constants（全局/类常量）                      | CAPS_WITH_UNDER    | _CAPS_WITH_UNDER                                             |
| Global/Class   Variables（全局/类变量）                      | lower_with_under   | _lower_with_under                                            |
| Instance   Variables（实例变量，即类型的成员变量，且是非静态(即非static)的） | lower_with_under   | _lower_with_under   (protected)    or    __lower_with_under   (private) |
| Method   Names（类方法）                                     | lower_with_under() | _lower_with_under()   (protected)    or    __lower_with_under()   (private) |
| Function/Method   （函数）Parameters（参数）                 | lower_with_under   |                                                              |
| Local Variables（局部变量）                                  | lower_with_under   |                                                              |

应该避免的名称：

Ø  单字符名称, 除了计数器和迭代器.

Ø  文件名中的连字符(-)

 

对于变量的命名，有以下要求：

1）bool类型的变量，以is_开头，例如：is_running



## 注释规范

确保对文件, 函数, 方法和行内注释使用正确的风格。 

### 块注释和行注释

最需要写注释的是代码中那些技巧性的部分。如果你在下次代码审查 的时候必须解释一下, 那么你应该现在就给它写注释。对于复杂的操作, 应该在其操作开始前写上若干行注释。对于不是一目了然的代码, 应在其行尾添加注释。 

为了提高可读性, 注释应该离开代码1个空格。另一方面, 绝不要描述代码。假设阅读代码的人比你更懂代码语言, 他只是不知道你的代码要做什么。 

```
// We use a weighted dictionary search to find out where i is in
// the array.  We extrapolate position based on the largest num
// in the array and the array size and then do binary search to
// get the exact number.
if (i && (i-1) === 0) { // true iff i is a power of 2
```

### @todo注释 

@todo表示需要做而未做的一些待完成的事项，有助于事后的检索，以及对整体项目做进一步的修改迭代。

格式如下：

- @todo注释应该在所有开头处包含“@todo”字符串，可以方在行注释，也可以在块注释
- 紧跟着是空格 + 用括号括起来的你的名字, email地址或其它标识符。
- 然后是一个可选的冒号. 接着必须有一行注释, 解释要做什么. 主要目的是为了有一个统一的TODO格式,
- 这样添加注释的人就可以搜索到(并可以按需提供更多细节)。

举例：

```
// @todo (kl@gmail.com): Use a "*" here for string repetition.
// @todo (Zeke) Change this to use relations.
```

###  @fixme注释

 @fixme表示需要修复的bug，优先级比@todo高，有助于发现问题时标记记录，避免发现问题后忘记进行修复。

格式如下：

- @fixme注释应该在所有开头处包含“@fixme”字符串,
- 紧跟着是空格 +用括号括起来的你的名字, email地址或其它标识符。
- 然后是一个可选的冒号. 接着必须有一行注释, 解释要做什么. 主要目的是为了有一个统一的@fixme格式,
- 这样添加注释的人就可以搜索到(并可以按需提供更多细节)。

举例：

```
// @fixme (kl@gmail.com): 这里存在被除数为0的异常情况未处理
// @fixme (Zeke) 未处理接口超时的情况
```

## Docstring规范

统一参考JSDoc的规范，减少多个规范的学习成本，JSDoc的详细标签格式可参考《[JSDoc中文文档](http://www.css88.com/doc/jsdoc/index.html)》。

### 参考类型

- number : Number（数字）

  - int :  整形
  - float ：浮点数
  - bool ：布尔值
  - complex ：复数

- string : String（字符串）

- array : Array（数组，var myCars = ["Saab","Volvo","BMW"];）可以与基础类型组合，例如int[]

- date : Date（日期对象）

- object ：Object实例

- function : 函数对象，函数的入参和返回值说明应在参数描述中说明

- null : Null（空类型）

- undefined : Undefined（未定义）

- 其他具体类实例：应为类的全路径，例如package.ClassName



### @typedef

@typedef标签在描述自定义类型时是很有用的，特别是如果你要反复引用它们的时候。这些类型可以在其它标签内使用，如 [@type](http://www.css88.com/doc/jsdoc/tags-type.html) 和 [@param](http://www.css88.com/doc/jsdoc/tags-param.html)。

该标签的位置应放置在应用该自定义类型的代码前面，例如放在文件开头的文件注释中。

```
/**
 * @typedef {(type1|type2)} typename - [type-descript]
 */
```

<descript> ： 整体描述

@typedef {(type1|type2)} typename - [type-descript] ：可以用"|"将多个类型组织起来，重新定义一种新数据类型，[type-descript]可根据需要是否增加补充描述



### 公共选填标签

以下标签为所有注释都可以选填的标签：

@summary <Summary goes here>：标签后完整描述的一个简写版本（一行内），位置必须紧跟[descript]

@example ： 提供一个如何使用描述项的例子，示例内容在标签下方

@deprecated [<some text>]：标签指明一个该对象在你代码中已经被弃用，可以后面带描述或没有

@since <versionDescription>： 标识对象在哪个特定版本开始添加进来的

@see <namepath/text]>: 表示可以参考另一个标识符的说明文档，或者一个外部资源。您可以提供一个标识符的namepath或自由格式的文本

@tutorial <tutorialID> : 插入一个指向向导教程的链接，作为文档的一部分

@version <text>：标签后面的文本将被用于表示该项的版本

@ignore ： 标签表示在你的代码中的注释不应该出现在文档中，注释会被直接忽略。这个标签优先于所有其他标签



### 文件（File）注释

注释的位置在文件头，格式如下：

```
/**
 * <descript>
 * @file <filename>
 * @author <name> [<emailAddress>] ：标签标识一个项目的作者
 * @version <text>：标签后面的文本将被用于表示该项的版本
 */
```

**必填标签：**

descript ：模块的具体描述

@file <filename> ：文件名，不含路径

@author <name> [<emailAddress>] ：标签标识一个项目的作者

@version <text>：标签后面的文本将被用于表示该项的版本

**选填标签：**

@license <identifier> : 标识你的代码采用何种软件许可协议

@copyright <some copyright text>: 标签是用来描述一个文件的版权信息

@requires <someModuleName>： 这个文件依赖的其他模块，每个依赖模块对应一个@requires 标签



### 类注释

注释放置在类定义前，使用块注释，格式如下：

```
/**
 * <descript>
 * @class [<type> <name>]
 */
```

**必填标签：**

descript ：类的具体描述

@class [<type> <name>] ：标明函数是一个构造器函数，意味着需要使用 `new` 关键字来返回一个实例，即使用 new 关键字实例化

**选填标签：**

@abstract ：标识类是抽象类，需子类重载实现相关内容



### 函数注释

注释放置在类定义前，使用块注释，格式如下：

```
/*
 * <descript>
 * @param {type} <paraname> - <descript>
 * @returns {type} - <descript>
 * @throws {exception-type} - <descript>
 */
```

**必填标签：**

@decorators <name> - [descript] : 说明函数所带的修饰符描述，每一个修饰符一个标签（非JSDoc标签）

@param {type} <paraname> - <descript> : 函数的参数定义

	type  ：为参数的数据类型，如果允许任何类型，填入*；如果支持几种特定类型，通过竖线"|"分隔
	
	paraname ： 参数名，如果为可选参数，paraname要用中括号"[ ]"标识（例如"[filepath]"）；如果参数有默认值，参数名后面带默认值，例如"[filepath]='c:/'"
	
	descript ： 参数描述
	
	注：paraname 与descript 之间用 “ - ”分隔；如果描述有多行，应进行格式的缩进处理

@returns {type} - <descript> :  标签描述一个函数的返回值，type与@param的定义一致

@throws {exception-type} - <descript> : 说明可能会被抛出什么样的错误，每一种异常一个标签

**选填标签：**

@api {action-type} <url> <api-name> : 标识函数是对外提供的api，action-type 为调用api的方法，根据实际设计提供（http方法有：get、post、delete）；url为api的访问地址；api-name为api的命名（或标识）

@abstract ：标识类是抽象对象，需子类重载实现相关内容

@override ：指明一个标识符覆盖其父类同名的标识符

@access <private|protected|public> ：指定该成员的访问级别（私有 private，公共 public，或保护 protected）

@static ： 标记方法是否静态方法

@interface [<name>] ：标签使一个标识符作为其他标识符的一个实现接口。 例如，你的代码可能定义一个父类，它的方法和属性被去掉。您可以将`@interface`标签添加到父类，以指明子类必须实现父类的方法和属性



## 编码规范

### 字符串

统一使用单引号（'）作为字符串引用标识，除非遇到需转义的情况



### 比较

任何情况下，做相等比较使用 === 和 !==



### 严格模式

建议在项目开始就使用严格模式，在JS文件或者<script>标签内输入 (注意需要引号)：

```
'use strict'
```

如果想以函数为单位启用严格模式，则可只在函数开始输入：

```
function foo() {
    'use strict';
    //
}
```



### 对象声明

使用对象 literals进行声明：

```
// 复杂声明
var person=new Object();
person.firstname="Bill";
person.lastname="Gates";
person.age=56;
person.eyecolor="blue";

// 替代方法
var person = {firstname:"John", lastname:"Doe", age:50, eyecolor:"blue"};
```



### 类型检查

采用以下方式进行变量的类型检查

```
//String
typeof variable === 'string'

//Number
typeof variable === 'number'

//Boolean
typeof variable === 'boolean'

//Object
typeof variable === 'object'

//null
variable === null

//undefined或null
variable == null

```

### 类型转换

- 在语句开始强制转换

```
// 不规范
const total_score = this.review_score + '';
// 规范
const total_score = String(this.review_score);

```

- 对Number类型使用parseInt()的时候，加入基数用于转换

```
const input_value = '4';

// 不规范
const val = new Number(input_value);
const val = +input_value;
const val = input_value >> 0;
const val = parseInt(input_value);

// 规范
const val = Number(input_value);
const val = parseInt(input_value, 10);

```

- 
  用Boolean()进行类型转换

```
const age = 0;
// 不规范
const has_age = new Boolean(age);

// 规范
const has_age = Boolean(age);
const has_age = !!age;
```

### 条件求值

- 判断数组长度不为空时

```
// 不规范
if (array.length > 0) {
    ...
}

// 规范（逻辑测试为真）
if (array.length) {
    ...
}

```

- 判断数组长度为空时

```
// 不规范
if (array.length === 0) {
    ...
}

// 规范（逻辑测试为真）
if (!array.length){
    ...
}

```

- 检查字符串是否为空时

```
// 不规范
if (string !== '') {
    // 代码
}

// 规范（逻辑测试为真/假）
if (string) {
    //
}
if (!string) {
    //
}

```



## 高阶编码技巧 （非规范）

### 函数参数传递

ES5中如果函数在调用时未提供隐式参数，参数会默认设置为： undefined，由于javascript在函数调用时不会检查参数，如果需要设置函数默认值可以采用以下方式：

```
// 设置参数默认值（ES5）
function myFunction(x, y) {
    if (y === undefined) {
          y = 0;
    } 
}

//或者
function myFunction(x, y) {
    y = y || 0;
}

//执行
myFunction(0, 2) // 输出 2
myFunction(5); // 输出 5, y 参数的默认值0
```

JavaScript 函数有个内置的对象 arguments  对象。argument 对象包含了函数调用的参数数组。通过这种方式你可以很方便的遍历所有入参：

```
x = sumAll(1, 123, 500, 115, 44, 88);

// 计算所有参数的和
function sumAll() {
    var i, sum = 0;
    for (i = 0; i < arguments.length; i++) {
        sum += arguments[i];
    }
    return sum;
}
```

