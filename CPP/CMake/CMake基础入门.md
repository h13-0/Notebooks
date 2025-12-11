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
```

其约定为：
- 尖括号占位符为必填参数
- 省略号 `...` 表示前面的参数可以重复多个
- 方括号占位符为可选参数

# 3 变量及基本操作

CMake按变量的作用域可以分为：
- 普通变量：
	- 存储位置：内存
	- 定义方式：通过不含 `CACHE` 关键字的 `set` 命令进行定义
	- 访问方式：通过 `${变量名}` 访问
	- 生命周期：仅在当前CMake处理过程中存在，CMake结束后消失
	- 作用域：总体类似于C语言函数：
		- 目录作用域：在当前目录及子目录存在
		- 函数作用域：仅可在函数中访问<font color="#d8d8d8">(除非使用 <code>PARENT_SCOPE</code> 关键字)</font>
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

## 3.1 变量定义(set&unset)

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

### 3.1.1 设置普通变量

在CMake中，普通环境变量的设置与取消对应如下的方法：

```CMake
# 设置普通变量
set(<variable> <value>... [PARENT_SCOPE])

# 取消环境变量
unset(ENV{<variable>})
```

#### 3.1.1.1 定义列表

当 `set` 定义列表时，可以使用如下的方式：

```CMake
set(LISTVALUE value1;value2)
set(LISTVALUE value1 value2) # 此时LISTVALUE为"value1;value2"
```

### 3.1.2 定义缓存条目

在CMake中，缓存条目的设置与取消对应如下的方法：

```CMake
# 设置缓存条目
set(CACHE{<variable>} [TYPE <type>] [HELP <helpstring>...] [FORCE] VALUE [<value>...])

# 取消缓存条目
unset(<variable> CACHE)
unset(CACHE{<variable>}) # CMake 4.2+
```

### 3.1.3 定义环境变量

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


## 3.2 列表操作(list)








## 3.3 数学运算()










# 4 关键字


# 5 函数

## 5.1 message






