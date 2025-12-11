---
number headings: auto, first-level 1, max 6, 1.1
---
#CMake 

本笔记仅为入门用途，更多详细用法需对接CMake官方文档

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

在CMake中，变量名



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

# 3 变量及基本操作

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
	- 每使用 `add_subdirectory` 添加一个目录时，都会创建一个新的目录作用域
	- 目录继承特性：
		- 所有父目录的普通变量均会被复制一份到子目录(即<font color="#c00000">副本</font>)
		- 而<font color="#c00000">子目录对副本的修改不会影响到父目录中</font>
- 函数作用域： ^i116pd
	- 每次定义并调用一个函数时，会产生函数作用域，类似于局部变量。
	- 特性：
		- 

不过需要注意的是，宏(`macro`)无作用域，其本质与C语言中的宏一致，为文本替换。



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

# 5 关键字

## 5.1 测试符

### 5.1.1 逻辑类测试符 ^url4xi



### 5.1.2 比较类测试符 ^omnc8n


### 5.1.3 文件操作类测试符 ^r5u82d

### 5.1.4 版本比较类测试符 ^7q3egc

### 5.1.5 路径比较类测试符 ^di61xr




# 6 函数

## 6.1 message






