---
number headings: auto, first-level 1, max 6, 1.1
---
#CMake 

本笔记仅为入门用途，更多详细用法需对接CMake官方文档。
截止章节[[CPP/CMake/CMake基础入门#^g41y0l|关键字]]之前为基础学习内容，需要理解记忆；从章节[[CPP/CMake/CMake基础入门#^g41y0l|关键字]]**及之后**为查阅性内容，无须记忆。

# 1 目录

```toc
```

# 2 基本规则

## 2.1 大小写规则

在CMake中，<font color="#c00000">不区分大小写</font>的有：
- 函数/命令
而<span style="background:#fff88f"><font color="#c00000">应当</font></span><font color="#c00000">区分大小写</font>的有：
- 变量名(严格区分)
- 关键字(大部分不区分)

注：
1. CMake的大多数关键字都大小写不敏感，但是/虽然：
	- 部分例如 `STATUS` 的关键字依旧敏感
	- 新版本的CMake放宽了部分关键字的大小写限制
	<font color="#c00000">因此为了安全性和可读性</font>，<span style="background:#fff88f"><font color="#c00000">需要始终保持大写</font></span>。

## 2.2 变量名规则

在CMake中，变量名有如下规则
1. 变量名<span style="background:#fff88f"><font color="#c00000">允许使用任何字符串，甚至emoji</font></span>：
	- 一般情况下不需要带字符串
	- 花里胡哨时只需要使用字符串包裹即可
2. <font color="#c00000">变量名区分大小写</font>

注：
1. 变量名可以包含空格，只不过后续使用该变量名时必须加双引号 `""` 或者加转义符 `\ ` ，例如：
	- `set("my var" xxx)` 或 `set([[my var]] xxx)` 
	- `${"my var"}` 或 `${my\ var}`

## 2.3 函数声明规则

在CMake的官方文档中，通常会有类似于如下的函数声明：

```CMake
set(CACHE{<variable>} [TYPE <type>] [HELP <helpstring>...] [FORCE] VALUE [<value>...])

list(FILTER <list> {INCLUDE | EXCLUDE} REGEX <regex>)
```

其文档约定为：
- 尖括号 `< >` 占位符为必填参数
- 省略号 `...` 表示前面的参数可以重复多个
- 方括号 `[ ]` 占位符为可选参数
- 花括号 `{ }` 则有如下的用法：
	- `{INCLUDE | EXCLUDE}` 表示<font color="#c00000">必须且单选</font>(互斥)
	- `{A B}` 表示<font color="#c00000">顺序序列</font>，必须先写 `A` 再写 `B`

# 3 变量、宏

CMake按变量的作用域可以分为：
- 普通变量：
	- 存储位置：内存
	- 定义方式：通过不含 `CACHE` 关键字的 `set` 命令进行定义
	- 访问方式：通过 `${变量名}` 访问
	- 生命周期：仅在当前CMake处理过程中存在，CMake结束后消失
	- 作用域：总体类似于C语言函数：
		- [[CPP/CMake/CMake基础入门#^2d7hmf|目录作用域]]：在当前目录及子目录存在
		- [[CPP/CMake/CMake基础入门#^i116pd|函数作用域]]：仅可在函数中访问<font color="#d8d8d8">(除非使用 <code>PARENT_SCOPE</code> 关键字)</font>
- 缓存变量：
	- 存储位置：构建目录下 `CMakeCache.txt` 文件中，在多次CMake之间是持久化的
	- 定义方式：
		- 通过 `cmake` 或 `cmake-gui` 进行配置
		- 或通过 `set` 配合 `CACHE` 关键字定义
	- 生命周期：伴随 `CMakeCache.txt` 而存在
	- 作用域：整个项目中可见
- 环境变量：
	- 存储位置：操作系统环境
	- 访问方式：
		- 读取方式：通过 `$ENV{var_name}` 进行访问
		- 写入方式：`set(ENV{VAR_NAME} value)` ，<font color="#c00000">修改仅会影响当前CMake进程</font>，<font color="#c00000">且不会影响到Shell</font>
	- 作用域：整个项目中可见
- 系统变量：
	- 存储位置：内存
	- 是CMake预定义的变量，包含系统信息、路径和构建状态等，且通常以 `CMAKE_` 开头
	- 作用域：整个项目中可见

而在CMake中，<span style="background:#fff88f"><font color="#c00000">其底层有且仅有一种类型</font></span>，<font color="#c00000">那就是字符串</font>。而在字符串之上，其通过如下的方式实现了不同的类型用途：
- 字符串类型：直接实现
- 列表类型：<font color="#c00000">实质上是通过分号</font> `;` <font color="#c00000">分隔的字符串</font>
- 布尔类型：<span style="background:#fff88f"><font color="#c00000">通过判断是否为特定值</font></span><font color="#c00000">从而表达</font> `True` <font color="#c00000">和</font> `False` ：
	- 视为 `True` 的有：
		- `1` 等<font color="#c00000">非零数字</font>的字符串
		- `ON` 、`Y` 、`YES` 、`TRUE` 等含义字符串，<font color="#c00000">且其对大小写不敏感</font>
	- 视为 `False` 的有：
		- `0` (字符串)
		- `OFF` 、`N` 、`NO` 、`FALSE` 等含义字符串
		- `IGNORE` 、`NOTFOUND` 等特殊字符串
		- `""` 空字符串
	需要再次强调，<font color="#c00000">其对大小写不敏感</font>
- 路径类型：<font color="#c00000">配合</font> `CACHE` 和 `PATH` 或 `FILEPATH` <font color="#c00000">定义的特殊字符串类型</font>
	- 其可在 `cmake-gui` 工具中有特殊的处理(例如弹出路径选择框等)
	- <font color="#c00000">需要注意</font>：
		- 其可在 `set` 语句中配合关键字 `PATH` 或 `FILEPATH` 定义
		- 定义时<font color="#c00000">必须携带</font> `CACHE` <font color="#c00000">关键字</font>
- 数字类型：<font color="#c00000">看起来像数字的字符串</font>，可以通过 `math(EXPR ...)` 命令进行计算

## 3.1 变量作用域

CMake中有如下前两种变量作用域：
- 目录作用域： ^2d7hmf
	- 每使用 `add_subdirectory` 添加一个目录时，都会创建一个新的目录作用域：
		- 由于 `add_subdirectory` 时，目标目录必须包含 `CMakeLists.txt` ，因此直接定义在 `CMakeLists.txt` 中的变量即为目录作用域变量
	- 目录继承特性：
		- 所有父目录的普通变量均会被复制一份到子目录(即<font color="#c00000">副本</font>)
		- 而<font color="#c00000">子目录对副本的修改不会影响到父目录中</font>，除非使用 `PARENT_SCOPE` 关键字
- 函数作用域： ^i116pd
	- 每次定义并调用一个函数时，会产生函数作用域，类似于局部变量。
	- 特性：
		- 函数内部可以读取调用者拥有的变量，<font color="#c00000">访问的也是副本</font>
		- 当需要修改外部变量时，也必须显式使用 `PARENT_SCOPE` 关键字
明显地， `PARENT_SCOPE` 关键字只能向上传递一级，若需要连续传递则需要连续使用。

不过需要注意的是，宏(`macro`)和 ` Include ` 等无作用域，其本质与C语言中的一致，为文本替换。

## 3.2 变量定义(set&unset)

在CMake中，变量定义主要通过 `set` 函数定义，其形式为：

```CMake
# 设置普通变量
set(<variable> <value>... [PARENT_SCOPE])

# 设置缓存条目
set(CACHE{<variable>} [TYPE <type>] [HELP <helpstring>...] [FORCE] VALUE [<value>...])

# 设置环境变量
set(ENV{<variable>} [<value>])
```

在CMake中，可以使用 `set` 重复定义一个变量，也可以使用 `unset` 取消设置一个变量，其形式为：

```CMake
# 取消普通变量
unset(<variable> [PARENT_SCOPE])

# 取消缓存条目
unset(<variable> CACHE)
unset(CACHE{<variable>}) # CMake 4.2+

# 取消环境变量
unset(ENV{<variable>})
```

### 3.2.1 设置普通变量

在CMake中，普通环境变量的设置与取消对应如下的方法：

```CMake
# 设置普通变量
set(<variable> <value>... [PARENT_SCOPE])

# 取消环境变量
unset(ENV{<variable>})
```

#### 3.2.1.1 定义列表

当 `set` 定义列表时，可以使用如下的方式：

```CMake
set(LISTVALUE value1;value2)
set(LISTVALUE value1 value2) # 此时LISTVALUE为"value1;value2"
```

### 3.2.2 定义缓存条目

在CMake中，缓存条目的设置与取消对应如下的方法：

```CMake
# 设置缓存条目
set(CACHE{<variable>} [TYPE <type>] [HELP <helpstring>...] [FORCE] VALUE [<value>...])

# 取消缓存条目
unset(<variable> CACHE)
unset(CACHE{<variable>}) # CMake 4.2+
```

### 3.2.3 定义环境变量

在CMake中，环境变量的设置与取消对应如下的方法：

```CMake
# 设置环境变量
set(ENV{<variable>} [<value>])

# 取消环境变量
unset(ENV{<variable>})
```

例如：

```CMake
set(ENV{CXX} g++)
unset(ENV{CXX})
```


## 3.3 列表操作(list)

CMake提供了如下的列表操作：

```CMake
Reading
  list(LENGTH <list> <out-var>)
  list(GET <list> <element index> [<index> ...] <out-var>)
  list(JOIN <list> <glue> <out-var>)
  list(SUBLIST <list> <begin> <length> <out-var>)

Search
  list(FIND <list> <value> <out-var>)

Modification
  list(APPEND <list> [<element>...])
  list(FILTER <list> {INCLUDE | EXCLUDE} REGEX <regex>)
  list(INSERT <list> <index> [<element>...])
  list(POP_BACK <list> [<out-var>...])
  list(POP_FRONT <list> [<out-var>...])
  list(PREPEND <list> [<element>...])
  list(REMOVE_ITEM <list> <value>...)
  list(REMOVE_AT <list> <index>...)
  list(REMOVE_DUPLICATES <list>)
  list(TRANSFORM <list> <ACTION> [...])

Ordering
  list(REVERSE <list>)
  list(SORT <list> [...])
```

其参数：
- `<out-var>` 是输出变量的占位符
- `<index>` <font color="#c00000">可以是负数</font>，例如 `-1` 表示倒数第一个元素

其中：
- `list(GET)` 中， `<element index> [<index> ...]` 代表需要读取的一个或多个索引
- `list(JOIN)` 可以将列表中各个元素按照 `<glue>` 的值拼接为一个字符串，例如：
```CMake
set(MY_LIST a;b;c)
list(JOIN MY_LIST " -> " RESULT) # 则 RESULT = "a -> b -> c"
```
- `list(SUBLIST)` 为<font color="#c00000">切片操作</font>
- `list(FIND)` 为<font color="#c00000">查找操作</font>，当没有找到时会返回 `-1`
- `list(FILTER)` 为<font color="#c00000">正则筛选功能</font>，选择 `INCLUDE` 或 `EXCLUDE` 进行筛选
- `list(TRANSFORM)` 为<font color="#c00000">对列表中每个元素执行操作</font>，例如：
	- `TOUPPER` ：转大写
	- `PREPEND` ：加前缀
- `list(REVERSE)` ：<font color="#c00000">让列表元素顺序翻转</font>(注意与下方的 `SORT` 进行区分)
- `list(SORT)` ：<font color="#c00000">让列表元素排序</font>，其有如下的常用选项：
	- 缺省：<font color="#c00000">默认为按ASCII表排序</font>
	- `COMPARE:NATURAL` ：自然排序，可以识别版本号，例如 `v2 < v10`
	- `CASE:INSENSITIVE` ：忽略大小写

## 3.4 数学运算()

#TODO 

## 3.5 宏(macro)

在CMake中，宏(`macro`)的基本性质与C语言中的宏类似，为文本替换，其使用方法如下：

```CMake
macro(<name> [<arg1> ...])
  <commands>
endmacro()
```

其中：
- `<arg1>` 为变量占位符，<font color="#c00000">替换时CMake会自动传入对应的</font><span style="background:#fff88f"><font color="#c00000">变量名</font></span>(因此需要 `${}` 解引用)
- `<commands>` 为替换出来的命令，<font color="#c00000">即任何可以被CMake所识别的语句</font>。

其Demo如下：

```CMake
macro(clear list)
    set(${list} "")   # 清空数组
endmacro()

set(var "a;b;c")      # 定义数组
message("var=${var}") # 输出：var=a;b;c

clear(var)
message("var=${var}") # 输出：var=
```

其本质上是被替换成了：

```CMake
set(var "a;b;c")
message("var=${var}")

# clear(var)
set(var "")            # 替换处
message("var=${var}")
```

需要注意：
1. <font color="#c00000">宏传入的是变量名</font>，<span style="background:#fff88f"><font color="#c00000">需要解引用</font></span>
2. 尽管宏不区分大小写，但是还是尽量使用全小写名称。
3. 通常来说要避免使用宏，因此会读即可。

# 4 流程控制

CMake中有如下的流程控制
- if系列：
	- `if(<condition>)` 、 `endif()`
	- `else()`
	- `elseif(<condition>)`
	其中：
	- `<condition>` 为[[CPP/CMake/CMake基础入门#^9wij0or|条件语句]]，<font color="#c00000">特性及注意事项需阅读对应章节</font>
- while系列：
	- `while(<condition>)` 、`endwhile()`
- for系列：
	- `foreach` 可接受参数类型有：
		- `foreach(<loop_var> <items>)`
		- `foreach(<loop_var> RANGE <stop>)`
		- `foreach(<loop_var> RANGE <start> <stop> [<step>])` 
		- `foreach(<loop_var> IN [LISTS [<lists>]] [ITEMS [<items>]])` 
		其中：
		- `<loop_var>` <font color="#c00000">为循环变量</font>，类似于 `for(int i=0; i<100; i++)` 中的 `i` 
	- `endforeach()` 
- `continue`
- `break`

<span style="background:#fff88f"><font color="#c00000">需要注意</font></span>：
- 由于在早期的CMake中，`${}` 是作为求值指令的，因此在 `if` 、 `while` 等语句中会自动添加求值符 `${}` ，即：
	- `if(VAR1)` 表示对 `VAR1` 的值进行判断
	- `if(${VAR2})` 表示对 `VAR2` <font color="#c00000">字符串对应的变量值进行判断</font>，例如
```CMake
set(var1 OFF)
set(var2 "var1")
if(var1)    # 即 if(OFF) ，为FALSE
if(${var2}) # 即 if(var1)，也为FALSE
```

## 4.1 条件语句 ^9wij0or

在CMake中，条件语句不仅可以配合：
- `NOT` 、 `OR` 、 `AND` 等[[CPP/CMake/CMake基础入门#^url4xi|逻辑类测试符]]
- `LESS` 、`GREATER` 等[[CPP/CMake/CMake基础入门#^omnc8n|比较类测试符]]
等关键字进行使用，还可以配合如下的函数类关键字使用：
- [[CPP/CMake/CMake基础入门#^r5u82d|文件操作类测试符]]：`EXISTS` 、`IS_READABLE`、`IS_EXECUTABLE` 等
- [[CPP/CMake/CMake基础入门#^7q3egc|版本比较类测试符]]：`VERSION_LESS` 、`VERSION_GREATER` 等
- [[CPP/CMake/CMake基础入门#^di61xr|路径比较类测试符]]：`PATH_EQUAL`

此外，<font color="#c00000">条件语句的评估顺序为</font>：
1. 括号
2. 一元测试符
3. 二元测试符
4. 一元逻辑运算符 `NOT`
5. 二元逻辑运算符 `AND` 和 `OR` ，从左到右，无短路

# 5 CMake项目组织

## 5.1 .cmake文件与include

`*.cmake` 类似于C语言中的头文件，与C语言的 `*.h` 文件和 `#include` 指令一致的是，其：
- <font color="#c00000">规则是</font> `*.cmake` <font color="#c00000">文件复制到</font> `include` <font color="#c00000">命令所在的位置</font>
- 通常用于导入脚本或导入库
因此 `*.cmake` 文件中通常存放宏、函数定义和导入预置包等。

与C语言中的 `Include` <span style="background:#fff88f"><font color="#c00000">相似但不同的是</font></span>，`include` 支持两种导入文件的方式：
1. 当 `include` 的<font color="#c00000">参数中包含路径分隔符</font>(`/`)<font color="#c00000">或文件名后缀</font>(`.cmake `)时，CMake<font color="#c00000">会按照绝对路径或相对路径对参数进行解析</font>，从而导入文件
2. 当 `include` 的<font color="#c00000">参数为单纯的一个模块名时</font>，其会<font color="#c00000">按照下方的优先级</font>查找模块对应的 `.cmake` 文件从而进行导入：
	1. 用户指定的 `CMAKE_MODULE_PATH` 变量中查找：
		- 该变量是一个列表变量
		- 默认为空，需要在 `CMakeLists.txt` 等中手动配置
	2. 从CMake内置的 `${CMAKE_ROOT}/Modules` 中寻找模块。具体路径可在脚本中打印
	注意，<font color="#c00000">CMake不会从系统的</font> `PATH` <font color="#c00000">路径中寻找模块</font>

## 5.2 CMakeLists.txt与add_subdirectory

在实际工程中，项目通常都为树形组织结构，父级目录需要包含子级目录提供的头文件声明与二进制定义等。

针对上述问题，CMake定义了如下概念：
- <font color="#9bbb59">目标</font>：即 `target` ，是<span style="background:#fff88f"><font color="#c00000">逻辑上的</font></span><font color="#c00000">一个库</font>，<font color="#c00000">通过</font> `add_library` <font color="#c00000">定义</font>
	- 其允许包含头文件从而<font color="#c00000">提供静态/动态链接库</font>，<font color="#c00000">也允许是纯头文件库</font>
- <font color="#9bbb59">子文件夹</font>：头文件、源文件等的<font color="#c00000">文件系统容器</font>，其包含 `CMakeLists.txt` 
需要注意：
- <font color="#9bbb59">目标</font>和<font color="#9bbb59">子文件夹</font><font color="#c00000">是两个不同的概念</font>，一个子文件夹的 `CMakeLists.txt` <font color="#c00000">中可以定义零个或多个目标</font>

随后有如下的使用流程：
1. 在子文件的 `CMakeLists.txt` 中定义零个或多个<font color="#9bbb59">目标</font>(`target`)
2. 在子文件的 `CMakeLists.txt` 中<span style="background:#fff88f"><font color="#c00000">为每个目标</font></span><span style="background:#fff88f"><b><font color="#c00000">分别</font></b></span><font color="#c00000">通过如下的命令暴露库信息</font>(例如头文件路径等)：
	- `target_include_directories` ：暴露头文件路径
	- `target_link_libraries` ：暴露依赖库
	- `target_compile_definitions` ：暴露预处理器宏定义
	- `target_compile_options` ：暴露编译选项
	- `target_compile_features` ：暴露编译特性
3. 随后<font color="#c00000">父级使用</font> `add_subdirctory` <font color="#c00000">包含</font> `CMakeLists.txt` <font color="#c00000">的子文件夹</font>
4. 随后子文件夹 `CMakeLists.txt` 中<span style="background:#fff88f"><font color="#c00000">所有目标</font></span><font color="#c00000">暴露的库信息均会自动导入到父级中</font>

说明demo如下：
- 工程结构假设如下：
```
Project/
├── CMakeLists.txt      (父级/主程序)
├── main.cpp
└── my_lib/             (全是库文件的文件夹)
    ├── CMakeLists.txt  (子目标的CMakeLists)
    ├── math_utils.cpp
    ├── math_utils.h
    └── string_utils.cpp
```
- 子目标 `CMakeLists.txt` 负责组织自身工程及暴露库信息：
```CMake
# 1. 定义一个库目标 `MyLib`，并为库目标导入源文件 (允许纯头文件库，即不添加源文件参数)
#    允许通过多次调用 `add_library` 定义多个不同的目标
add_library(MyLib 
    math_utils.cpp 
    string_utils.cpp
)

# 2. 为目标 `MyLib` 添加查找路径
#    PUBLIC、INTERFACE、PRIVATE等为导入规则，传播控制关键字章节会讲解，暂时不用了解
target_include_directories(MyLib PUBLIC 
    ${CMAKE_CURRENT_SOURCE_DIR}
)
```
- 随后父级 `CMakeLists.txt` 直接使用 `add_subdirectory` 即可导入：
```CMake
cmake_minimum_required(VERSION 3.10)
project(MainApp)

# 1. 添加子目录，此时子目录暴露的 `MyLib` 、以及头文件路径等均已自动导入
add_subdirectory(my_lib)

# 2. 定义主程序
add_executable(App main.cpp)

# 3. 将子目标提供的 `MyLib` 参与链接
target_link_libraries(App PRIVATE MyLib)
```

### 5.2.1 传播控制及其关键字




[[CPP/CMake/CMake基础入门#^7ylkgd]]

## 5.3 项目组织常用命令

### 5.3.1 添加头文件路径




### 5.3.2 



# 6 关键字 ^g41y0l

## 6.1 测试符

### 6.1.1 逻辑类测试符 ^url4xi



### 6.1.2 比较类测试符 ^omnc8n


### 6.1.3 文件操作类测试符 ^r5u82d

### 6.1.4 版本比较类测试符 ^7q3egc

### 6.1.5 路径比较类测试符 ^di61xr

## 6.2 传播控制关键字 ^7ylkgd

传播控制关键字主要有 `PUBLIC` 、`INTERFACE` 、`PRIVATE` 这三种，其区别如下：
- `PUBLIC` ：共享关键字，<font color="#c00000">当前目标及使用了该目标的范围内可用</font>
- `INTERFACE` ：转发/接口关键字，<font color="#c00000">仅传递给依赖该目标的父级</font>
- `PRIVATE` ：独享关键字，<font color="#c00000">仅目标自身范围内可用</font>



# 7 函数

## 7.1 message






