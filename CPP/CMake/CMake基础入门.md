---
number headings: auto, first-level 1, max 6, 1.1
---
#CMake 

# 1 目录

```toc
```

# 2 变量

CMake按变量的提供者可以分为：
1. CMake中预先提供的变量
2. 通过 `set` 等方式用户自行定义的变量
按变量存储类型可以分为：




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
- 数字类型：

CMake中的变量区分大小写，其使用方式为 `${变量名}` 

### 2.1.1 set&unset




