---
number headings: auto, first-level 1, max 6, 1.1
---
#CMake 

# 1 目录

```toc
```

# 2 变量

CMake按变量的作用域可以分为：
- 普通变量：
	- 存储位置：内存
	- 定义方式：通过不含 `CACHE` 关键字的 `set` 命令进行定义
	- 生命周期：
	- 作用域
- 缓存变量：
	- 存储位置：构建目录下 `CMakeCache.txt` 文件中，在多次CMake之间是持久化的
	- 定义方式：
		- 通过 `cmake` 或 `cmake-gui` 进行配置
		- 或通过 `set` 配合 `CACHE` 关键字定义
	- 生命周期
	- 作用域：整个项目中可见
- 环境变量：
	- 存储位置：操作系统环境
	- 读取方式：通过 `$ENV{var_name}` 进行访问
	- 写入方式：`set(ENV{VAR_NAME} value)` ，<font color="#c00000">修改仅会影响当前CMake进程</font>
- 系统变量：
	- 存储位置：内存
	- 是CMake预定义的变量，包含系统信息、路径和构建状态等，且通常以 `CMAKE_` 开头

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
- 路径类型：
	- 可在 `set` 语句中配合关键字 `PATH` 或 `FILEPATH` 定义
- 数字类型：<font color="#c00000">看起来像数字的字符串</font>，可以通过 `math(EXPR ...)` 命令进行计算

CMake中的变量区分大小写，其使用方式为 `${变量名}` 

### 2.1.1 set&unset

# 3 关键字

需要注意，CMake的大多数关键字都大小写不敏感，。<font color="#c00000">但是为了安全性和可读性</font>，<span style="background:#fff88f"><font color="#c00000">需要始终保持大写</font></span>


