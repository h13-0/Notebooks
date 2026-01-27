---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 #Linux驱动开发 #操作系统

参考书籍：
- LINUX设备驱动程序（第三版），Jonathan Corbet，Alessandro Rubini，Greg Kroah-Hartman著；魏永明，耿岳，钟书毅译。
本笔记为入门学习笔记。

# 1 目录

```toc
```

# 2 Linux基础

## 2.1 Linux版本编号规则

Linux版本编号规则为：

```text
VERSION.PATCHLEVEL.SUBLEVEL[-EXTRAVERSION]
```

其中：
- PATCHLEVEL有奇偶数之分，偶数是用于发行的稳定版本，奇数是开发过程中的快照版本
TODO


# 3 驱动设计的硬件基础
## 3.1 设备的分类及特点

Linux将设备分为了如下三个大类：
- 字符设备
- 块设备
- 网络设备

### 3.1.1 字符设备

字符设备是指必须以<font color="#c00000">字节流顺序访问</font>的设备，如字符终端( `/dev/console` )、串口( `/dev/tty*` )、触摸屏、磁带驱动器、鼠标等。
- 其驱动程序至少需要实现 `open` 、 `close` 、 `read` 、 `write` 系统调用。
- 字符设备可以通过文件系统节点来访问(通常在 `/dev` 下)。
- 字符设备可以使用 `open()` 、 `read()` 、 `write()` 等方式进行访问。

### 3.1.2 块设备

块设备允许按照任意顺序进行访问，以块为单位进行操作，如硬盘、eMMC等。
- 块设备有两种访问方式：
	1. 使用类似于 `dd` 的命令操作设备的块
	2. 在块设备上建立 `FAT` 、 `EXT4` 等文件系统后，使用文件系统的方式进行访问。
- 块设备也可以通过文件系统节点来访问(通常在 `/dev` 下)。
- 块设备可以使用 `open()` 、 `read()` 、 `write()` 等方式进行访问。

### 3.1.3 网络设备

网络设备面向数据包的发送和接收设计，内核与网络设备之间的通信主要使用Socket。
- 一个纯软件实现的网络设备的例子为回环接口( `loopback` )。
- 网络设备并不是面向流的设备，因此通常不会被映射到Linux文件系统的文件和目录上，通常会被分配一个唯一的名字，如 `eth0` 。
- 网络设备会使用另外一套操作函数而不是 `read()` 、 `write()` 等。

## 3.2 处理器

### 3.2.1 通用处理器(GPP)

当前的通用处理器主要采用了冯诺依曼架构和哈佛架构两种架构形式，其对应的常见的CPU系列有：
- 冯诺依曼架构：Intel、ARM7、MIPS
- 哈佛架构：AVR、ARM9-11、Arm Cortex A
具体区别可见[[常见CPU架构及其对比]]。

#### 3.2.1.1 不同架构处理器下的数据类型大小

| arch    | char | short | int | long | ptr | long long | u8  | u16 | u32 | u64 |
| ------- | :--: | :---: | :-: | :--: | :-: | :-------: | :-: | :-: | :-: | :-: |
| i386    |  1   |   2   |  4  |  4   |  4  |     8     |  1  |  2  |  4  |  8  |
| alpha   |  1   |   2   |  4  |  8   |  8  |     8     |  1  |  2  |  4  |  8  |
| armv4l  |  1   |   2   |  4  |  4   |  4  |     8     |  1  |  2  |  4  |  8  |
| ia64    |  1   |   2   |  4  |  8   |  8  |     8     |  1  |  2  |  4  |  8  |
| m68k    |  1   |   2   |  4  |  4   |  4  |     8     |  1  |  2  |  4  |  8  |
| mips    |  1   |   2   |  4  |  4   |  4  |     8     |  1  |  2  |  4  |  8  |
| ppc     |  1   |   2   |  4  |  4   |  4  |     8     |  1  |  2  |  4  |  8  |
| sparc   |  1   |   2   |  4  |  4   |  4  |     8     |  1  |  2  |  4  |  8  |
| sparc64 |  1   |   2   |  4  |  8   |  8  |     8     |  1  |  2  |  4  |  8  |
| x86_64  |  1   |   2   |  4  |  8   |  8  |     8     |  1  |  2  |  4  |  8  |

### 3.2.2 数字信号处理器(DSP)


## 3.3 存储器

常用存储器分类可见[[常用存储器#常用存储器]]。


# 4 Linux内核及内核编程

## 4.1 Linux内核文件结构

### 4.1.1 Linux 6

- arch：与体系结构相关的代码，例如arm、arm64、x86等。
- block：存放块设备相关代码。
- crypto：存放加密算法的目录。
- Documentation：存放官方Linux内核文档。
- drivers：驱动目录
- firmware：存放固件
- include：公共头文件目录
- init：存放Linux内核启动和初始化的代码
- ipc：进程间通信的代码
- kernel：存放内核本身的代码
- lib：存放库函数的文件夹
- mm：内存管理相关代码
- net：网络相关代码
- scripts：脚本
- security
- tools：
- usr：
- virt：

## 4.2 Linux项目组织与编译系统

### 4.2.1 Linux编译系统



### 4.2.2 Kconfig基础语法

可见[[Kconfig基础语法]]。

# 5 Linux内核模块

## 5.1 Linux内核模块简介

Linux的组件可以选择编译进Linux内核或者编译为Linux内核模块，编译为Linux内核模块的好处有：
1. 在<font color="#c00000">系统启动后</font>也可以随时<font color="#c00000">增</font><span style="background:#fff88f"><font color="#c00000">删</font></span><font color="#c00000">功能</font>
2. 在后续新增功能时，可以直接编译为模块而不需要重新替换内核
3. 在发布系统时，也不需要为所有可选功能做排列组合编译多个内核

Linux内核模块的加载、卸载以及查看基本信息等操作：
- Linux内核的加载使用 `insmod` 或 `modprobe` 命令，<font color="#c00000">其中后者可以在加载目标模块的同时把依赖的模块也加载了</font>。
- Linux内核的卸载使用 `rmmod` 命令
- 查看Linux内核模块的信息使用 `modinfo` 命令
- 列出内核中已加载的模块使用 `lsmod` 命令

由于Linux内核模块是直接以内核模式运行的，因此可以出于安全考虑，在编译Linux内核时，禁用加载模块功能。

## 5.2 Linux内核的额外注意事项

相比于普通的应用程序开发，Linux内核的开发需要额外注意以下几点：
1. <font color="#c00000">所有资源必须在模块卸载函数中手动释放</font>，操作系统不会帮内核模块管理资源。
2. 模块加载函数需要尽量快速的执行。
3. Linux内核模块代码必须是可重入的，因为他可能会被多个程序调用，会被同时在多个上下文中执行。
4. 内核所拥有的栈非常小，模块要和内核共用这些空间。
5. 内核模块中<font color="#c00000">不建议</font>(<font color="#c00000">且大多数情况下不允许</font>)使用浮点运算，如果需要开启浮点支持，则在某些架构上进入和退出内核空间时需要保存和恢复浮点处理器状态。

## 5.3 Linux内核模块程序结构

一个Linux内核模块应当具有且实现以下几个组成部分：
1. 模块加载函数<font color="#c00000">(必须)</font>
2. 模块卸载函数<span style="background:#fff88f"><font color="#c00000">(<u>可选</u>)</font></span>，<font color="#c00000">注意不是必须</font>。
3. 模块许可证声明<font color="#c00000">(必须)</font>
4. 模块参数(可选)
5. 模块导出符号(可选)
6. 模块作者信息(可选)

### 5.3.1 模块加载函数

```C
static int __init init_func(void)
{
	// 具体实现...
	// 初始化成功时应当返回0
	// 执行失败时应当选择 <linux/errno.h> 中的错误代码
}
// 指定初始化函数
module_init(init_func);
```

注意：
- 模块的加载函数中通常会遇到错误，在遇到错误后，<font color="#c00000">应当停止后续的加载并释放已经加载的内存</font>。在这里通常使用 `goto` 语句实现，也可以编写统一的 `cleanup` 函数检查资源是否被成功分配并释放资源(<font color="#c00000">推荐后者</font>)。一般 `cleanup` 函数不会被注册为卸载函数，因此<font color="#c00000">不能被标记为</font> `__exit` 。
- 错误码应当使用 `<linux/errno.h>` 中的错误码，这样方便用户使用 `perror` 之类的函数将错误转换为有意义的字符串。
- 关于 `__init` 标识符的用途可见章节[[Linux驱动开发笔记#4 3 6 其他常用特性|4.3.6 其他常用特性]]中的解释。

### 5.3.2 模块卸载函数

```C
static void __exit exit_function(void)
{
	// ...模块卸载，释放资源
}
// 指定模块卸载函数
module_exit(exit_function);
```

注意：
- <font color="#c00000">如果未定义模块卸载函数，则内核不允许卸载该模块。</font>
- 关于 `__exit` 标识符的用途可见章节[[Linux驱动开发笔记#4 3 6 其他常用特性|4.3.6 其他常用特性]]中的解释。

### 5.3.3 模块参数

#### 5.3.3.1 传递单个参数值

##### 5.3.3.1.1 传递单个普通参数

模块在加载时可以传入一些命令行参数，其主要通过如下方式进行定义与加载：

```C
#include "linux/moduleparam.h"

// 相当于缺省参数
static int port = 8080;


/**
 * module_param - typesafe helper for a module/cmdline parameter
 * @name: the variable to alter, and exposed parameter name.
 * @type: the type of the parameter
 * @perm: visibility in sysfs.
 *
 * @name becomes the module parameter, or (prefixed by KBUILD_MODNAME and a
 * ".") the kernel commandline parameter.  Note that - is changed to _, so
 * the user can use "foo-bar=1" even for variable "foo_bar".
 *
 * @perm is 0 if the variable is not to appear in sysfs, or 0444
 * for world-readable, 0644 for root-writable, etc.  Note that if it
 * is writable, you may need to use kernel_param_lock() around
 * accesses (esp. charp, which can be kfreed when it changes).
 *
 * The @type is simply pasted to refer to a param_ops_##type and a
 * param_check_##type: for convenience many standard types are provided but
 * you can create your own by defining those variables.
 *
 * Standard types are:
 *	byte, hexint, short, ushort, int, uint, long, ulong
 *	charp: a character pointer
 *	bool: a bool, values 0/1, y/n, Y/N.
 *	invbool: the above, only sense-reversed (N = true).
 */
module_param(port, int, S_IRUGO);
```

在 `module_param` 函数中，` perm` 为访问许可配置，其被定义与 `include/linux/sta.h` 中，<font color="#c00000">其基本定义与用户态的权限定义一致</font>。具体如下：
- 文件拥有者：
	- `S_IRWXU` ：文件拥有者具有可读、可写、可执行权限
	- `S_IRUSR` ：文件拥有者具有可读权限
	- `S_IWUSR` ：文件拥有者具有可写权限
	- `S_IXUSR` ：文件拥有者具有可执行权限
- 拥有者<font color="#c00000">以外的</font>同组用户：
	- `S_IRWXG` ：同组用户具有可读、可写、可执行权限
	- `S_IRGRP` ：同组用户具有可读权限
	- `S_IWGRP` ：同组用户具有可写权限
	- `S_IXGRP` ：同组用户具有可执行权限
- 拥有者和同组<font color="#c00000">以外的</font>其他用户：
	- `S_IRWXO` ：其他用户具有可读、可写、可执行权限
	- `S_IROTH` ：其他用户具有可读权限
	- `S_IWOTH` ：其他用户具有可写权限
	- `S_IXOTH` ：其他用户具有可执行权限
- 所有用户(UGO，本质为把USR、GRP、OTH进行了或运算)：
	- `S_IRWXUGO` ：所有用户具有可读、可写、可执行权限
	- `S_IALLUGO` ：所有用户具有全部权限
	- `S_IRUGO` ：所有用户具有可读权限
	- `S_IWUGO` ：所有用户具有可写权限
	- `S_IXUGO` ：所有用户具有可执行权限

而在 `module_param` 函数中，通常使用如下的权限符：
- `S_IRUGO` 表示任何人都可以读取该参数(<span style="background:#fff88f"><font color="#c00000">最常用</font></span>)
- `S_IRUGO|S_IWUSR` 表示root用户可以修改该参数。<font color="#c00000">但是当参数发生修改时</font>，<font color="#c00000">内核不会通知内核模块参数被修改</font>，因此<font color="#c00000">通常</font>不使用。

在加载时可以通过如下命令指定模块参数：

```Shell
insmod xxx.ko port=value #例如：port=80
```

内核模块支持的加载参数列表如下：
- `bool` 
- `invbool` ：<font color="#c00000">关联int型</font>，反转bool值，输入为 `true` 则传入为 `false` 。
- `byte` ：8位无符号
- `charp` ：<font color="#c00000">关联char*</font>，<span style="background:#fff88f"><font color="#c00000">内核会为用户提供的字符串分配内存并设置指针</font></span>。
- `int` 
- `long`
- `short`
- `uint` ：关联unsigned int，u表示无符号。
- `ulong` 
- `ullong` 
- `hexint` 
- `ushort`

##### 5.3.3.1.2 传递单个参数并指定参数名

```C
#include "linux/moduleparam.h"

static int udp_port = 8081;
// 相当于缺省参数
static int tcp_port = 8080;


/**
 * module_param_named - typesafe helper for a renamed module/cmdline parameter
 * @name: a valid C identifier which is the parameter name.
 * @value: the actual lvalue to alter.
 * @type: the type of the parameter
 * @perm: visibility in sysfs.
 *
 * Usually it's a good idea to have variable names and user-exposed names the
 * same, but that's harder if the variable must be non-static or is inside a
 * structure.  This allows exposure under a different name.
 */
module_param_named(port, tcp_port, int, S_IRUGO);
```

其中：
- `name` ：在<span style="background:#fff88f"><font color="#c00000">加载模块时</font></span>使用的参数名。<font color="#c00000">要求必须符合C语言标识符规范</font>。
- `value` ：在源码中实际存储时使用的参数。

随后在加载内核时使用：

```Shell
insmod xxx.ko port=value #例如：port=80
```

进行加载。<span style="background:#fff88f"><font color="#c00000">此时参数名为</font></span> `name` <span style="background:#fff88f"><font color="#c00000">中指定的参数</font></span>而非 `value` 的名称。

在本质上，`module_param(name, type, perm)` <font color="#c00000">等价于</font> `module_param_named(name, name, type, perm)` ，在内核中定义如下：

```C
#define module_param(name, type, perm)                       \  
        module_param_named(name, name, type, perm)
```

#### 5.3.3.2 传递数组

##### 5.3.3.2.1 传递普通数组

普通数组的传递方式如下：

```C
#include "linux/moduleparam.h"

static int arr[10] = { 0 };
static int arr_size = 0;

/**
 * module_param_array - a parameter which is an array of some type
 * @name: the name of the array variable
 * @type: the type, as per module_param()
 * @nump: optional pointer filled in with the number written
 * @perm: visibility in sysfs
 *
 * Input and output are as comma-separated values.  Commas inside values
 * don't work properly (eg. an array of charp).
 *
 * ARRAY_SIZE(@name) is used to determine the number of elements in the
 * array, so the definition must be visible.
 */
// module_param_array(name, type, nump, perm)
module_param_array(arr, int, &arr_size, S_IRUGO);
```

其中：
- `name` ：存放数组的变量，并且为参数名
- `type` ：数组中元素的类型
- `nump` ：为<span style="background:#fff88f"><font color="#c00000">存放实际接收元素数量的变量地址</font></span>
- `perm` ：权限符

上述示例调用如下：

```Shell
insmod xxx.ko arr=value1,value2,...
```

<font color="#c00000">注意</font>：
1. 传入数组大小小于等于10个时，参数正常传输，arr_size也为正常大小。
2. <font color="#c00000">当传入数组大小大于10时</font>，a<font color="#c00000">rr_size为传入数组的大小</font>(<span style="background:#fff88f"><font color="#c00000">会超过10</font></span>)，<font color="#c00000">需要开发者自行处理逻辑</font>。<font color="#c00000">内核只保证前10个数据会被有效接收</font>。

##### 5.3.3.2.2 传递普通数组并指定参数名

```C
#include "linux/moduleparam.h"

/**
 * module_param_array_named - renamed parameter which is an array of some type
 * @name: a valid C identifier which is the parameter name
 * @array: the name of the array variable
 * @type: the type, as per module_param()
 * @nump: optional pointer filled in with the number written
 * @perm: visibility in sysfs
 *
 * This exposes a different name than the actual variable name.  See
 * module_param_named() for why this might be necessary.
 */
module_param_array_named(name, array, type, nump, perm)
```

其中：
- `name` ：加载模块时使用的参数名
- `array` ：实际存放的数组位置
- `type` ：数组中元素的类型
并在后续章节不再单独拆除普通方式和指定参数名的方式。

##### 5.3.3.2.3 传递字符串

```C
#include "linux/moduleparam.h"

/**
 * module_param_string - a char array parameter
 * @name: the name of the parameter
 * @string: the string variable
 * @len: the maximum length of the string, incl. terminator
 * @perm: visibility in sysfs.
 *
 * This actually copies the string when it's set (unlike type charp).
 * @len is usually just sizeof(string).
 */
module_param_string(name, string, len, perm)
```

其中：
- `name` ：加载模块时使用的参数名
- `string` ：实际存放的字符串
- `len` ：<font color="#c00000">为最大的可存放的字符串大小</font>，`sizeof(string) - 1` 。
不过<span style="background:#fff88f"><font color="#c00000">还是推荐使用</font></span> `module_param` 配合 `charp` 的方式，这样不用手动管理内存，也不用提前为字符串分配一个足够大的内存区域，<span style="background:#fff88f"><font color="#c00000">且不需要在模块退出时手动释放这部分内存</font></span>。

#### 5.3.3.3 设置参数提示信息

使用：

```C
#include "linux/moduleparam.h"

MODULE_PARM_DESC(_parm, desc);
```

进行描述，其中：
- `_parm` 为要描述的参数名称
- `desc` 为参数信息

<font color="#c00000">随后使用</font> `modinfo` <font color="#c00000">即可查看模块参数提示信息</font>。

### 5.3.4 模块导出符号

```C
int add_int(int a, int b)
{
	return a + b;
}
// 导出符号
EXPORT_SYMBOL(add_int);

int add_int_gpl(int a, int b)
{
	return a + b;
}
// 导出包含GPL许可证的符号
EXPORT_SYMBOL_GPL(add_int);
```

<font color="#c00000">导出符号后的函数可以被其他内核模块使用</font>，使用前只需要声明一下函数定义即可(通常是用引用头文件方式)。
注：
- 使用 `EXPORT_SYMBOL_GPL` 导出的符号不可以被非GPL模块引用。
- 使用 `cat /proc/kallsyms` 即可查看导出符号表。

### 5.3.5 模块常用信息

模块许可证声明：

```C
MODULE_LICENSE("GPL v2");
```

模块作者信息：

```C
MODULE_AUTHOR("xxtech");
```

模块描述：

```C
MODULE_DESCRIPTION("...");
```

模块版本：

```C
MODULE_VERSION("V1.0");
```

模块别名：
```C
MODULE_ALIAS("...");
```

### 5.3.6 其他常用特性

1. 定义只在初始化阶段就需要的数据：
```C
static int var_name __initdata = 0;
```
上述 `__initdata` 和模块加载函数的 `__init` 都标识<font color="#c00000">在内核被加载完毕后</font>，<font color="#c00000">其所定义的变量或函数会被从内存中扔掉</font>。
2. 与上一条相似的是，内核中也有 `__exitdata` 与 `__exit` 。上述四个特性均会被放置到特殊ELF端。

### 5.3.7 简单模块示例与编译

进行内核模块编译时，通常有如下几种选择方式：
1. 直接使用内核源码进行构建
	- 优点：
		1. 一定不存在模块代码与内核代码之间的兼容性问题
		2. 可以根据需求开启部分内核功能，例如内存泄漏检测
	- 缺点：
		1. 内核编译极其浪费时间
		2. 通常还需要用编译好的内核替换当前内核，模块使用的源码必须和当前内核一致
		3. 可能因为内核配置不当存在性能问题
		4. 即使只修改了其中一两个模块，但是在一定时间后也需要全量重新编译一遍内核
2. 使用当前内核自带头文件进行构建
	- 优点：
		1. 构建速度快，性能与储存需求低
	- 缺点：
		1. 只能编译内核，而无法修改内核配置
3. DKMS


#### 5.3.7.1 使用内核源码构建

各发行版修改后的内核源码拉取方式不一致，可见对应子章节，也可以直接使用主线内核。

##### 5.3.7.1.1 Ubuntu

Ubuntu可以使用 `apt` 和 `git` 两种方式获取源码，也可以使用当前系统配合主线版本内核进行编译。

**使用apt获取源码**：
直接搜索linux内核，并找出当前使用的内核包名

```Shell
sudo apt search linux-image
```

返回结果为：

```Shell
Sorting... Done
Full Text Search... Done
linux-image-generic-hwe-24.04/noble,now 6.8.0-31.31 amd64 [installed,automatic]
  Generic Linux kernel image
```

则直接使用apt下载上述内核包的源码即可。

```Shell
apt-get install linux-source-6.8.0
```

该内核源码会被下载到 `/usr/src` 目录，复制并解压即可。

**使用git获取源码**：
在获取源码之前，需要获取当前系统信息：

```Shell
uname -a
```

```
Linux h13-VMware-Virtual-Platform 6.8.0-31-generic #31-Ubuntu SMP PREEMPT_DYNAMIC Sat Apr 20 00:40:06 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux
```

上述结果指明目前使用的内核版本为 `6.8.0-31-generic` 。

Ubuntu所使用的内核源码仓库页面为：[https://kernel.ubuntu.com/git/](https://kernel.ubuntu.com/git/)
从上述页面中：
1. 找到当前ubuntu系统的codename及其对应架构的仓库
2. 从历史版本中找到当前内核版本
随后可以考虑：
- 完整clone再回退版本
```Shell
git clone https://git.launchpad.net/~canonical-kernel/ubuntu/+source/linux-intel/+git/noble
git checkout 7fdb45c9bbbc95a3300b4d8de3f751f4c05c98e2
```
- <span style="background:#fff88f"><font color="#c00000">只clone目标版本</font></span>
```Shell
# 先创建目录
mkdir noble
# 初始化git仓库
git init
# 连接到git仓库
git remote add origin https://git.launchpad.net/~canonical-kernel/ubuntu/+source/linux-intel/+git/noble
# 只clone目标版本
git fetch --depth 1 origin 7fdb45c9bbbc95a3300b4d8de3f751f4c05c98e2
# 将工作目录切换到目标commit的内容
git checkout FETCH_HEAD
```

<font color="#c00000">只做内核驱动/模块开发建议使用后者</font>，完整clone速度过慢。
以上述命令为例，截止2024年05月30日：
- 完整clone共计10192670个object
- 只clone目标版本共计88631个object。

**提取当前内核配置并使用主线内核代码**：
主线代码获取方式略。在获取到主线内核代码后，可以使用如下方式获取当前系统的config：

```Shell
cp -v /boot/config-$(uname -r) .config
```

通常建议在学习开发Linux内核模块/驱动时使用自己的内核，除了方便版本匹配以外，还有更多的原因：
	![[Linux驱动开发笔记#^daooag]]
直接在内核源代码目录下执行：

```Shell
make modules
make modules-install
make install
```

随后重启，通常不建议卸载原内核，当内核配置出错无法启动后，可以在引导处切换内核。

#### 5.3.7.2 使用内核头文件构建

对于大多数内核模块，其均可以使用内核头文件进行构建，只需要使用如下的Makefile即可，其中 `target.o` 为源文件对应的中间文件。

```Makefile
obj-m += target.o

KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean
```

在进行驱动开发时，驱动会依赖一些linux的框架，例如摄像头驱动会依赖 `videobuf2` 相关的框架。而这些框架对应的模块通常需要手动加载到内核，这些模块其通常位于包 `linux-modules-extra-$(uname -r)` 中，通常系统会自带这些依赖的模块。若当系统未自带时可直接使用如下的命令进行安装：

```Shell
sudo apt-get install linux-modules-extra-$(uname -r)
```

#### 5.3.7.3 普通模块示例

本实例为一个基础普通模块的示例。
Linux已经在 `lib/test_module.c` 放置了一个基础的Hello World模块，其主要代码如下：

```C
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/module.h>
#include <linux/printk.h>

static int __init test_module_init(void)
{
	pr_warn("Hello, world\n");

	return 0;
}

module_init(test_module_init);

static void __exit test_module_exit(void)
{
	pr_warn("Goodbye\n");
}

module_exit(test_module_exit);

MODULE_AUTHOR("Kees Cook <keescook@chromium.org>");
MODULE_LICENSE("GPL");
```

并在 `lib/Makefile` 中已经添加了如下代码：

```Makefile
obj-$(CONFIG_TEST_LKM) += test_module.o
```

经过搜索发现， `CONFIG_TEST_LKM` 在如下几个文件中被定义为 `m` ：
- `tools/testing/selftests/kmod/config`
- `tools/testing/selftests/splice/config`
也就是在一定条件下，上述Makefile中的指令会变成：

```Makefile
obj-m += test_module.o
```

因此当需要编译自己的内核模块时，可以直接在Makefile中添加如下代码：

```Makefile
obj-m += xxx.o
```

因此可以直接在 `lib` 目录下直接建立一个新文件 `hello_module.c` ，并编写如下代码：

```C
#include <linux/init.h>
#include <linux/module.h>
#include <linux/printk.h>

static int __init hello_module_init(void)
{
    printk("Hello module inited.\n");
    return 0;
}

static void __exit hello_module_exit(void)
{
    printk("Hello module exited.\n");
}

module_init(hello_module_init);
module_exit(hello_module_exit);
MODULE_LICENSE("GPL v2");
MODULE_AUTHOR("h13");
MODULE_DESCRIPTION("hello word module.");
MODULE_VERSION("V1.0");
```

<font color="#c00000">注意</font> `printk` <font color="#c00000">需要以</font> `\n` <font color="#c00000">结尾，否则不会及时刷新</font>。
在  `lib/Makefile` 的末尾增加如下代码：

```Makefile
# Hello world module
obj-m += hello_module.o
```

回到linux代码根目录，执行：

```Shell
make modules -j8 #8线程
```

即可在 `lib` 路径下得到 `hello_module.ko` ，使用

使用 `modinfo hello_module.ko` 查看模块信息：

```Shell
# modinfo hello_module.ko
filename:       .../lib/hello_module.ko
version:        V1.0
description:    hello word module.
author:         h13
license:        GPL v2
srcversion:     C6A36BCF3E2045DD1DE8E30
depends:
retpoline:      Y
intree:         Y
name:           hello_module
vermagic:       6.8.1+ SMP preempt mod_unload modversions
```

注：
1. 关于代码中的 `pr_fmt(fmt)` ：[[pr_fmt应用及原理解析]]

##### 5.3.7.3.1 测试内核模块

使用 `dmesg` 抓取当前日志：

```Shell
dmesg
```

在原终端加载模块：

```Shell
# 使用ismod或modprobe均可
# insmod hello_module.ko
# 但是推荐使用modprobe，因为modprobe会自动安装目标模块所依赖的模块，而ismod不能
modprobe hello_module.ko
```

无报错，再使用 `dmesg` 抓取当前日志，会发现新增日志：

```Shell
[   85.532987] Hello module inited.
```

使用 `lsmod` 也可以正常获取模块信息

```Shell
lsmod | grep hello
```

```Shell
hello_module           12288  0
```

卸载mod也可以正常输出日志

```Shell
rmmod hello_module
```

```Shell
[  411.289281] Hello module exited.
```

再次使用 `lsmod | grep hello` 则无结果。

若抓取日志，会发现一个警告，是由于没有签名造成的：

```Shell
dmesg | grep hello
[   85.531743] hello_module: module verification failed: signature and/or required key missing - tainting kernel
```

可以选择在 `Makefile` 文件中添加如下配置，关闭强制签名。

```Makefile
CONFIG_MODULE_SIG=n
```

注：
- 若使用 `cat /proc/kmsg` 无输出，则可以使用 `lsof /proc/kmsg` 检查是否有进程在不停获取该文件输出
- 若 `dmesg` 也无输出，则应当检查内核编译时是否开启 `CONFIG_PRINTK`

#### 5.3.7.4 字符驱动模块示例

见章节：[[Linux驱动开发笔记#5 7 字符设备的分配、注册与回收]]

## 5.4 内核模块补充

### 5.4.1 多文件编程

当内核模块 `test_module.ko` 由多个源文件 `file1.c` 、 `file2.c` 、 `...`  构成时，Makefile中可以如下编写：

```Makefile
obj-m += test_module.o
module-objs += file1.o file2.o ...
```

### 5.4.2 内核态驱动与用户态驱动

用户态驱动的优点：
1. <font color="#c00000">可以链接整个C语言库甚至非标准库</font>。内核中无法使用完整的C语言库。
2. 可以使用普通的gdb等调试器调试驱动程序，而不是像内核模块一样printk。
3. 用户态驱动发生问题通常不会影响系统稳定性。
4. 用户态驱动程序可以换出，当驱动程序不使用时可以换出到硬盘。
5. 方便用户规避GPL协议，方便实现闭源驱动。
6. 用户态驱动已经可以实现大多数设备驱动所需，且有一些被广泛应用的用户态驱动，例如 `libusb` 等。同时可以先在用户态完成大部分驱动开发与调试，随后移植到内核态。

用户态驱动的缺点：
1. 用户态驱动不可使用中断。但是部分架构上有对应的解决方案，例如IA32的 `vm86` 。
2. 只有通过 `mmap` 映射 `/dev/mem` 才可以直接访问物理内存，但是需要对应权限(不一定需要root，可以配置访问权限)。
3. 只有使用 `ioperm` 或 `ioctl` 才可以访问IO端口，但是并非所有平台都有此支持，性能较差且需要对应权限。
4. 响应速度慢，内核直接与硬件交互，但是用户态需要切换内核态，切换上下文后才可以与硬件交互。
5. <font color="#c00000">一旦用户态驱动被换出磁盘，其响应速度会极其慢</font>。使用特权用户的 `mlock` 或许可以缓解，但是用户态驱动通常会链接多个库，需要占用多个page。
6. 用户空间无法完成重要设备的驱动，例如网络设备和块设备。

## 5.5 内核开发常用技巧

### 5.5.1 内核内存泄露检测器 ^s9jjo0

在编译内核的 `menuconfig` 中，通常在以下路径开启内核内存泄露检测：

```text
Kernel hacking -> Memory Debugging -> Kernel memory leak detector
```

即开启了 `CONFIG_DEBUG_KMEMLEAK` 宏。

随后当内存泄露发生时，内核日志会提示： `kmemleak: 11 new suspected memory leaks (see /sys/kernel/debug/kmemleak)` 并在对应文件输出类似如下内容：

```text
unreferenced object 0xffff9e37cb0b5400 (size 1024):
  comm "v4l_id", pid 3660, jiffies 4294772526
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace (crc 8c508e7):
    [<ffffffffa91dbd0a>] kmemleak_alloc+0x4a/0x90
    [<ffffffffa844c031>] kmalloc_trace+0x2e1/0x390
    [<ffffffffc0e6a3be>] v4l2_m2m_ctx_init+0x5e/0x160 [v4l2_mem2mem]
    [<ffffffffc0dc165f>] mm2m_open+0x3f/0x120 [minimal_m2m_device]
    [<ffffffffc0decabb>] v4l2_open+0x9b/0x160 [videodev]
    [<ffffffffa84d857f>] chrdev_open+0xcf/0x250
    [<ffffffffa84c9e6d>] do_dentry_open+0x21d/0x570
    [<ffffffffa84cc6c3>] vfs_open+0x33/0x50
    [<ffffffffa84e92a1>] path_openat+0xb11/0x1190
    [<ffffffffa84ea43f>] do_filp_open+0xaf/0x170
    [<ffffffffa84cca33>] do_sys_openat2+0xb3/0xe0
    [<ffffffffa84ccef5>] __x64_sys_openat+0x55/0xa0
    [<ffffffffa8005eb8>] x64_sys_call+0x1eb8/0x25c0
    [<ffffffffa91cc4df>] do_syscall_64+0x7f/0x180
    [<ffffffffa920012b>] entry_SYSCALL_64_after_hwframe+0x73/0x7b
unreferenced object 0xffff9e37c1d90800 (size 1024):
  comm "wireplumber", pid 2069, jiffies 4294772531
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
...
```

# 6 简易的字符设备驱动程序

本章节的字符设备驱动程序将以一个简易的进程间管道通信为例。
基本设定：
1. 仅支持2个进程访问，超过2个时拒绝打开pipe文件。
2. 为了简化代码，无需其他鉴权等复杂操作。

## 6.1 主设备号和次设备号

可以使用 `cat /proc/devices` 查看当前系统中的设备列表，例如：

```Shell
Character devices:
  1 mem
  4 /dev/vc/0
  4 tty
  4 ttyS
  5 /dev/tty
  5 /dev/console
  5 /dev/ptmx
  5 ttyprintk
  6 lp
  7 vcs
 10 misc
 13 input
 14 sound/midi
 14 sound/dmmidi
 21 sg
 29 fb
 89 i2c
 99 ppdev
108 ppp
116 alsa
128 ptm
136 pts
180 usb
...

Block devices:
  2 fd
  7 loop
  8 sd
  9 md
 11 sr
 65 sd
 66 sd
 67 sd
 68 sd
 69 sd
 70 sd
 71 sd
 ...
```

此外还有使用 `ls` 命令查看设备的方法(<font color="#c00000">但是该方法无法查看未注册文件节点的设备，以及子目录设备</font>，故不推荐)：

在 `/dev` 目录下执行 `ls -l` ，可以得到如下结果：

```Shell
...
drwxrwxrwt   2 root root          40 Jun  4 01:31 shm/
crw-------   1 root root     10, 231 Jun  4 01:31 snapshot
drwxr-xr-x   3 root root         200 Jun  4 01:31 snd/
brw-rw----+  1 root cdrom    11,   0 Jun  4 01:31 sr0
lrwxrwxrwx   1 root root          15 Jun  4 01:31 stderr -> /proc/self/fd/2
lrwxrwxrwx   1 root root          15 Jun  4 01:31 stdin -> /proc/self/fd/0
lrwxrwxrwx   1 root root          15 Jun  4 01:31 stdout -> /proc/self/fd/1
crw-rw-rw-   1 root tty       5,   0 Jun  4 01:35 tty
crw--w----   1 root tty       4,   0 Jun  4 01:31 tty0
crw--w----   1 root tty       4,   1 Jun  4 01:31 tty1
crw--w----   1 root tty       4,  10 Jun  4 01:31 tty10
...
```

在上述结果的各列对应关系如下：

```Shell
| 权限     | 文件数 | 所有者 | 用户组 | 文件大小或设备数 | 修改日期     | 文件名 |
drwxrwxrwt   2      root    root          40         Jun  4 01:31 shm/
crw-------   1      root    root     10, 231         Jun  4 01:31 snapshot
```

在上述栏目中，列 `权限` 第一个字母及其对应关系如下：
- c：字符设备文件
- b：块设备文件
- l：符号链接
- d：目录
- s：套接字
- p：命名管道

在上述栏目中，列 `文件大小或设备数` 在文件类型不同时其意义也不同：
- 对于普通文件，其显示的是文件大小
- 对于<font color="#c00000">设备文件</font>，其显示的是 `主设备号, 次设备号`
在Linux系统中，大多数情况下，<font color="#c00000">主设备号相同的设备使用相同的驱动程序</font>。主次设备号可以用于标识一个设备，同时在Linux内核中，也可以通过次设备号获取对应设备的直接指针。

## 6.2 设备编号的内部表达

在Linux 2.6.0到最新的Linux 6.10中， `dev_t` 被定义为一个 `u32` 类型，其：
- 前12位用于表示主设备号
- 后20位用于表示从设备号
本质位运算，因此Linux也提供了对应的宏方便开发者转换：

```C
dev_t dev = MKDEV(major, minor);
int major = MAJOR(dev);
int minor = MINOR(dev);
```

在Linux 2.5系列的修改中，设备编号从原先的8+8=16位变成了如今的32位。

## 6.3 分配和释放设备编号

分配设备号主要有两种方式，分别为静态分配和动态分配。

### 6.3.1 静态分配设备号

<font color="#c00000">静态分配需要指定主设备号</font>，主设备号的选择可以查看 `Documentation/admin-guide/devices.txt` 中的示例。
静态分配设备号的<font color="#c00000">前提是要知道哪些设备号可用</font>，再去指定想要申请的设备号。
查询空闲设备号需要读取 `/proc/devices` 文件未使用的设备号。
其主要的API有如下两个

```C
// 该函数会从from下的从设备号作为起始从设备号，向from所指的主设备下连续申请count个设备
int register_chrdev_region(dev_t from, unsigned count, const char *name)
```

```C
// 该函数会在指定的主设备号下注册一个从设备，此时要求主设备号大于0。
// 设备信息为该函数的第二、三个参数。
// 在此种用法下，函数的成功返回值为0，失败为负值。
// 该函数也可以用于动态分配设备号，见下一章节。
static inline int register_chrdev(unsigned int major, const char *name,
								 const struct file_operations *fops)
```

上述函数的 `struct file_operations` 用于建立文件操作和驱动程序操作的连接。具体可见绑定文件操作章节。

### 6.3.2 动态分配设备号(推荐)

动态分配不需要指定主设备号，根据 `Documentation/admin-guide/devices.txt` 中的说明，<font color="#c00000">对于字符设备而言</font>，<font color="#c00000">动态分配的主设备号会从254开始向下分配直到234，分配完毕后再从511开始向下分配直到384</font>。

为了考虑驱动在多台设备上的兼容性，避免冲突，应当优先考虑动态分配设备号。

```C
// 该函数会从baseminor开始，向dev所指主设备下连续注册count个设备
// baseminor通常为0
int alloc_chrdev_region(dev_t *dev, unsigned baseminor, unsigned count,
			const char *name)
```

```C
// 该函数会自动，此时要求主设备号等于0。
// 设备信息为该函数的第二、三个参数。
// 在此种用法下，函数的成功返回值为0，失败为负值。
// 该函数也可以用于动态分配设备号，见下一章节。
static inline int register_chrdev(unsigned int major, const char *name,
								 const struct file_operations *fops)
```

### 6.3.3 释放设备编号

对于上述的所有分配设备编号的方法，均可以使用如下的函数进行释放： 

```C
void unregister_chrdev_region(dev_t from, unsigned count)
```

## 6.4 创建设备节点

使用上述的注册设备号的方法仅会在系统中注册一个字符设备，但是并不会在文件系统中注册对应的设备。

### 6.4.1 创建设备节点

#### 6.4.1.1 device_create

`device_create` 函数的声明如下：

```C
#include <linux/device.h>

__printf(5, 6) struct device *
device_create(const struct class *cls, struct device *parent, dev_t devt,
	      void *drvdata, const char *fmt, ...);
```

其中：
- 参数：
	- `const struct class *cls` ：设备所属类型，该类型需要自行定义。
	- `struct device *parent` ：父设备指针，如果没有则设置为 `NULL` 。
	- `dev_t devt` ：需要创建设备节点的设备号
	- `void *drvdata` ：设备私有数据指针，传入后可使用 `dev_set_drvdata` 和 `dev_get_drvdata` 进行读写。
	- `const char *fmt` 及其可变参数：用于构造设备名称
- 返回值：
	- 新创建的 `struct device` 指针。出现错误时返回 `NULL` 。

### 6.4.2 删除设备(device_destroy)

`device_destory` 函数的声明为：

```C
#include <linux/device.h>

void device_destroy(const struct class *cls, dev_t devt);
```

其中：
- 参数：
	- `const struct class *cls` ：设备所属类型
	- `dev_t devt` ：需要销毁的设备节点的设备号

## 6.5 绑定文件操作(file_operations 数据结构) ^u7i5mc

如上述章节所述， `struct file_operations` 用于建立文件操作和驱动程序操作的连接，该数据结构的定义如下(Linux 6.10版本)：

```C
struct file_operations {
	struct module *owner;
	fop_flags_t fop_flags;
	loff_t (*llseek) (struct file *, loff_t, int);
	ssize_t (*read) (struct file *, char __user *, size_t, loff_t *);
	ssize_t (*write) (struct file *, const char __user *, size_t, loff_t *);
	ssize_t (*read_iter) (struct kiocb *, struct iov_iter *);
	ssize_t (*write_iter) (struct kiocb *, struct iov_iter *);
	int (*iopoll)(struct kiocb *kiocb, struct io_comp_batch *,
			unsigned int flags);
	int (*iterate_shared) (struct file *, struct dir_context *);
	__poll_t (*poll) (struct file *, struct poll_table_struct *);
	long (*unlocked_ioctl) (struct file *, unsigned int, unsigned long);
	long (*compat_ioctl) (struct file *, unsigned int, unsigned long);
	int (*mmap) (struct file *, struct vm_area_struct *);
	int (*open) (struct inode *, struct file *);
	int (*flush) (struct file *, fl_owner_t id);
	int (*release) (struct inode *, struct file *);
	int (*fsync) (struct file *, loff_t, loff_t, int datasync);
	int (*fasync) (int, struct file *, int);
	int (*lock) (struct file *, int, struct file_lock *);
	unsigned long (*get_unmapped_area)(struct file *, unsigned long, unsigned long, unsigned long, unsigned long);
	int (*check_flags)(int);
	int (*flock) (struct file *, int, struct file_lock *);
	ssize_t (*splice_write)(struct pipe_inode_info *, struct file *, loff_t *, size_t, unsigned int);
	ssize_t (*splice_read)(struct file *, loff_t *, struct pipe_inode_info *, size_t, unsigned int);
	void (*splice_eof)(struct file *file);
	int (*setlease)(struct file *, int, struct file_lease **, void **);
	long (*fallocate)(struct file *file, int mode, loff_t offset,
			  loff_t len);
	void (*show_fdinfo)(struct seq_file *m, struct file *f);
#ifndef CONFIG_MMU
	unsigned (*mmap_capabilities)(struct file *);
#endif
	ssize_t (*copy_file_range)(struct file *, loff_t, struct file *,
			loff_t, size_t, unsigned int);
	loff_t (*remap_file_range)(struct file *file_in, loff_t pos_in,
				   struct file *file_out, loff_t pos_out,
				   loff_t len, unsigned int remap_flags);
	int (*fadvise)(struct file *, loff_t, loff_t, int);
	int (*uring_cmd)(struct io_uring_cmd *ioucmd, unsigned int issue_flags);
	int (*uring_cmd_iopoll)(struct io_uring_cmd *, struct io_comp_batch *,
				unsigned int poll_flags);
} __randomize_layout;
```

其主要成员及用法为：

| <center>成员</center> | <center>可否为空</center>            | <center>备注</center> | <center>成员作用</center>                                                                                                                                                                                                                                                                                                                      |
| ------------------- | -------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `owner`             | 不可                               | 常用 `THIS_MODULE`    | 用于存储提供该文件操作的模块的指针，避免模块在使用时被卸载。                                                                                                                                                                                                                                                                                                             |
| `fop_flags`         |                                  |                     |                                                                                                                                                                                                                                                                                                                                            |
| `llseek`            |                                  |                     | 用于修改当前文件的读写位置，并返回修改后的新位置。                                                                                                                                                                                                                                                                                                                  |
| `read`              | 可为空<sup>1</sup>                  |                     | 用于从设备中读取数据，返回值为读取的字节数。<br>在该函数的实现中，<font color="#c00000">不需要驱动程序使用</font> `file->fmode` 鉴<font color="#c00000">别是否可读写，</font>此工作内核已完成。                                                                                                                                                                                                     |
| `aio_read`          | 可为空<sup>1</sup>                  |                     | 用于从设备中<font color="#c00000">异步</font>读取数据，数据读取完毕后调用参数指定的回调函数。                                                                                                                                                                                                                                                                              |
| `write`             | 可为空<sup>1</sup>                  |                     | 用于写入数据，返回值为写入的字节数。                                                                                                                                                                                                                                                                                                                         |
| `aio_write`         | 可为空<sup>1</sup>                  |                     | 用于从设备中<font color="#c00000">异步</font>写入数据，数据写入完毕后调用参数指定的回调函数。                                                                                                                                                                                                                                                                              |
| `readdir`           | 可为空                              |                     | 读取目录操作。<font color="#c00000">对于文件类型，该参数应当为NULL</font>。                                                                                                                                                                                                                                                                                     |
| `iopoll`            | 可为空                              |                     | [[IO模型#3 3 IO多路复用 IO Multiplexing\|非阻塞IO多路复用模型]]的后端实现。用于查询请求某个事件/操作是否会被阻塞。<br>为NULL时则意味告诉内核请求该设备任何事件/操作都不会发生阻塞。                                                                                                                                                                                                                            |
| `ioctl`             | 可为空<sup>1</sup>                  |                     | <span style="background:#fff88f"><font color="#c00000">为内核/用户提供该设备的特殊命令操作</font></span>。                                                                                                                                                                                                                                                   |
| `mmap`              | 可为空<sup>1</sup>                  |                     | 将设备内存映射到进程地址空间。                                                                                                                                                                                                                                                                                                                            |
| `open`              | <font color="#c00000">可为空</font> |                     | 如果该函数为NULL，<span style="background:#fff88f"><font color="#c00000">则打开该设备的请求无论如何都会成功</font></span>，且驱动程序不会知道本设备被打开。                                                                                                                                                                                                                         |
| `flush`             | 可为空                              |                     | 含义同用户态的 `flush` 。如果该函数为NULL，则内核会忽略用户的 `flush` 请求。<br>flush会被在用户态的每次close时都会被调用一次。<br>(但是<font color="#c00000">用户态的每次close不一定会触发release</font>，见下例)                                                                                                                                                                                         |
| `release`           | 可为空                              |                     | <span style="background:#fff88f"><font color="#c00000">注意是没有close函数的，也就是该函数并不对应open函数</font></span>。<br>有时file文件在一次打开后会被共享(如使用了 `folk` 、 `dup` 等)，<font color="#c00000">此时内核中维护的计数器+1</font>，<br><font color="#c00000">并且当计数器归0时才会真正调用release函数</font>，<font color="#c00000">但是每次关闭都会调用一次上方的flush函数</font>。<br>该函数也是可以被设置为NULL的，效果与open相似。 |
| `fsync`             | 可为空<sup>1</sup>                  |                     | `fsync` 的后端调用。                                                                                                                                                                                                                                                                                                                             |
| `aio_fsync`         | 可为空<sup>1</sup>                  |                     | `fsync` 的异步版本。                                                                                                                                                                                                                                                                                                                             |
| `lock`              | 常为空                              |                     | 用于实现文件锁定。                                                                                                                                                                                                                                                                                                                                  |
|                     |                                  |                     |                                                                                                                                                                                                                                                                                                                                            |
注：
1. 当指定的函数为 `NULL` 时，则会告诉内核该设备不支持对应操作，当用户调用时会抛出错误。

## 6.6 file 数据结构

注意本章节所述的 `file` 类型与C标准库的 `FILE` 类型无任何关联。`file` 是内核提供的一个数据结构，不会暴露给用户态程序。而 `FILE` 是C语言标准库中所定义的，不会出现在内核态的代码中。
在内核中，`struct file` 指针通常被称为 `file` 或 `filep` 。`struct file` 数据结构的定义如下(Linux 6.10版本)：

```C
struct file {
	union {
		/* fput() uses task work when closing and freeing file (default). */
		struct callback_head 	f_task_work;
		/* fput() must use workqueue (most kernel threads). */
		struct llist_node	f_llist;
		unsigned int 		f_iocb_flags;
	};

	/*
	 * Protects f_ep, f_flags.
	 * Must not be taken from IRQ context.
	 */
	spinlock_t		f_lock;
	fmode_t			f_mode;
	atomic_long_t		f_count;
	struct mutex		f_pos_lock;
	loff_t			f_pos;
	unsigned int		f_flags;
	struct fown_struct	f_owner;
	const struct cred	*f_cred;
	struct file_ra_state	f_ra;
	struct path		f_path;
	struct inode		*f_inode;	/* cached value */
	const struct file_operations	*f_op;

	u64			f_version;
#ifdef CONFIG_SECURITY
	void			*f_security;
#endif
	/* needed for tty driver, and maybe others */
	void			*private_data;

#ifdef CONFIG_EPOLL
	/* Used by fs/eventpoll.c to link all the hooks to this file */
	struct hlist_head	*f_ep;
#endif /* #ifdef CONFIG_EPOLL */
	struct address_space	*f_mapping;
	errseq_t		f_wb_err;
	errseq_t		f_sb_err; /* for syncfs */
} __randomize_layout
```

其主要成员及其用法为：

| <center>成员</center> | <center>可否为空</center> | <center>备注</center> | <center>成员作用</center>                                                                                                  |
| ------------------- | --------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `f_lock`            |                       |                     |                                                                                                                        |
| `f_mode`            |                       |                     | 标志位，表示该文件是否是否可读或可写，<font color="#c00000">由内核配置</font>。                                                                 |
| `f_pos`             |                       |                     | 当前的读写位置。<font color="#c00000">除上一章节</font> `llseek` <font color="#c00000">函数以外不应当直接修改该成员</font>。                       |
| `f_flags`           |                       |                     | 标志位，表示用户请求的属性(如只读、阻塞等)。<br>会被用户请求改变该标志位的值，<font color="#c00000">内核不需要提前配置该标志位的值</font>，内核只负责读取该值。                      |
| `f_op`              | 不可                    |                     | 存储上一章节中所定义的 `struct file_operations` 。<br><font color="#c00000">该成员允许随时修改</font>，从而在需要的时候重载各种需要的操作(例如 `/dev/null` 文件)。 |
| `private_data`      |                       |                     | 主要用于跨系统调用时保存或传递相关信息，或存储驱动自身所需要保存的信息。<br><font color="#c00000">该指针所分配的资源需要在release方法中手动释放</font>。                       |
| `f_dentry`          |                       |                     | 文件对应的目录项结构，大多数设备文件无需关心。                                                                                                |

## 6.7 inode 数据结构

`inode` 即Linux的混合索引分配的节点，不过设备文件通常不需要关心混合索引分配的文件系统管理相关的内容(电科爱考)，因此需要关注的成员主要有如下两个：

| <center>成员</center> | <center>可否为空</center> | <center>备注</center> | <center>成员作用</center>      |
| ------------------- | --------------------- | ------------------- | -------------------------- |
| `i_rdev`            |                       |                     | 包含了上述的 `dev_t` 可以用于存储设备号等。 |
| `i_cdev`            |                       |                     | 字符设备的 `struct cdev` 类型。    |

由于Linux在2.5系列中修改了 `dev_t` 的位数，因此出于可移植性考虑，<font color="#c00000">建议使用如下的接口获取设备号</font>(而不是先获取 `dev_t` 再获取设备号)：

```C
unsigned int iminor(struct inode *inode);
unsigned int imajor(struct inode *inode);
```

## 6.8 字符设备的分配、注册与回收

通常来说(但不绝对)，注册一个字符设备需要完成<font color="#c00000">申请结构体空间</font>、配置结构体、注册设备、反注册设备、<font color="#c00000">回收空间</font>几个任务。注意错误处理和资源回收即可。字符设备需要使用 `cdev_t` ，其定义于 `<linux/cdev.h>` 中。
需要注意的是字符设备使用的 `cdev_t` 有两种内存分配方式：
- 静态分配，直接静态定义 `cdev_t` 结构体：
	1. 静态定义 `cdev_t` 结构体
	2. 使用 `cdev_init` 初始化该结构体，同时指定 `file_operations`
	3. 配置 `owner`
	4. 使用 `cdev_add` 添加字符设备
- 动态分配，动态分配和管理内存：
	1. 定义 `cdev_t*` 指针
	2. 使用 `cdev_alloc` 分配内存空间，<span style="background:#fff88f"><font color="#c00000">此时无需再使用</font></span> `cdev_init` 初始化
	3. 配置 `cdev` 的 `file_operations`
	4. 配置 `owner`
	5. 使用 `cdev_add` 添加字符设备
在字符设备的回收时，同一使用 `cdev_del` 即可解除注册并可能回收内存。但是需要额外注意以下几点：
1. 使用 `cdev_init` 初始化静态分配的结构体时，结构体的 `kobj_type` 会被注册为<font color="#c00000">静态分配类型</font>，并指定release函数为 `cdev_default_release` 。
2. 使用 `cdev_alloc` 为指针分配内存时， `kobj_type` 会被注册为<font color="#c00000">动态分配类型</font>，并指定release函数为 `cdev_dynamic_release` 。
3. 因此无论静态还是动态分配，都可以用 `cdev_del` 解除注册，<font color="#c00000">且无需担心动态内存回收问题</font>。
4. 使用 `cdev_del` 解除注册后，<font color="#c00000">设备不一定会被立即移除</font>，<font color="#c00000">内核会等待用户停止使用该设备后才会移除</font>。但是使用 `cdev_del` <font color="#c00000">解除注册后，内核模块不应当再调用该模块</font>。
综上，可编写如下的字符设备模块的加载和卸载函数：

```C
static int __init mpipe_init(void)
{
    int ret = 0;

    // allocate char dev region.
    ret = alloc_chrdev_region(&dev, 0, 1, "mpipe");
    if(ret)
        goto failed;

    // allocate cdev
    if((_cdev = cdev_alloc()) == NULL)
        goto cdev_alloc_failed;

    _cdev->ops = &fops;
    _cdev->owner = THIS_MODULE;

    // register a character device.
    ret = cdev_add(_cdev, dev, 1);
    if(ret)
        goto cdev_add_failed;

cdev_add_failed:
    cdev_del(_cdev);

cdev_alloc_failed:
    unregister_chrdev_region(dev, 1);

failed:
    return ret;
}

static void __exit mpipe_exit(void)
{
    cdev_del(_cdev);
    unregister_chrdev_region(dev, 1);
}
```

## 6.9 open和release方法

open应当完成如下任务：
1. 首次open时应当初始化硬件
2. 检查硬件错误
3. 在必要时更新 `file_operations` 中的指针
4. 在必要时向 `filep` 中填写应当存放在 `private_data` 中的数据

对应地，release应当完成如下任务：
1. 清除在 `filep` 中寄存的数据
2. 关闭设备

需要注意的是，<font color="#c00000">一旦用户态对某个文件</font><span style="background:#fff88f"><font color="#c00000">发起</font></span><font color="#c00000">close操作</font>(<font color="#c00000">即使close并未完成</font>)，<font color="#c00000">该文件的其他所有操作均会被返回为错误信息</font>。

## 6.10 read和write方法

read和write方法的函数指针如下所示：

```C
ssize_t (*read) (struct file *, char __user *, size_t, loff_t *);
ssize_t (*write) (struct file *, const char __user *, size_t, loff_t *);
```

需要注意的是：
1. `char __user *` 是<span style="background:#fff88f"><font color="#c00000">用户空间的指针，在内核代码中<b>永远不要</b>直接操作它们</font></span>，原因如下：
	- 用户空间是分页的，<font color="#c00000">表面上连续的内存空间在实际上却不连续</font>
	- <font color="#c00000">用户空间的内存可能会被换出外存</font>，<font color="#c00000">此时目标内存地址甚至可能不在内存</font>
	- 用户空间的应用可能是恶意应用，直接引用对应的内存空间可能会间接访问后门
	- <font color="#c00000">用户传来的地址可能是无效地址</font>
	<font color="#c00000">因此应当使用专用的函数来访问对应的内存空间</font>(见下方的两个copy方法)。
	更多的内存管理相关内容将在后续章节讲述。
2. `loff_t *` 是长偏移类型的偏移量，是<font color="#c00000">在文件中的偏移量</font>，因此与内存中常用的 `ssize_t` 不同。
3. 在read和write操作成功完成时，应当更新 `*offp` 所表示的文件位置。
4. read和write方法的返回值规定见下方两个子章节。

内核和用户之间的copy方法如下：

```C
unsigned long copy_to_user(void __user *to, const void *from, unsigned long count);
unsigned long copy_from_user(void *to, const void __user *from, unsigned long count);
```

上述两个函数在Linux 6.10中均由汇编实现。

### 6.10.1 read方法返回值

read方法的返回值应符合如下几种情况：
1. 当返回值大于0时，其含义为从字符设备读取到的字节数，该值不能大于 `count` 。
	1. 当返回值等于 `count` 时表示读取成功。
	2. 当返回值小于 `count` 时，<span style="background:#fff88f"><font color="#c00000">在部分情况下程序可能会重复执行read</font></span>直到凑够 `count` ，例如使用标准库的 `fread` 读取设备文件就会<font color="#c00000">自动执行此流程</font>。
2. 当返回值为0时，表示读取到文件末尾。
3. 当返回值小于0时，其用于表示错误。错误值定义于 `<linux/errno.h>`
此外，read方法也可以实现阻塞读取方式。

### 6.10.2 write方法返回值

write和read方法的返回值及其注意事项相似。

## 6.11 readv和writev方法

在Linux中已对用户态提供了readv和writev两个批量读写的api。内核驱动可以自行选择是否实现批量版本的读写方法。若内核驱动不实现该方法，则readv和writev会自动<span style="background:#fff88f"><font color="#c00000">在用户态多次调用</font></span>对应的read和write方法进行实现。<font color="#c00000">随之带来的问题就是执行一次readv或writev会多次切换CPU状态</font>。
而对于用户而言，使用readv、writev而不是read、write的主要原因是前者可以<font color="#c00000">批量复制位于不连续内存空间</font>上的数据。

在Linux 2.6.18的 `struct file_operations` 中还保留有 `readv` 和 `writev` 的定义：

```C
ssize_t (*readv) (struct file *, const struct iovec *, unsigned long, loff_t *);
ssize_t (*writev) (struct file *, const struct iovec *, unsigned long, loff_t *);
```

<font color="#c00000">上述支持在Linux 2.6.19中已经删除</font>。

# 7 内核调试技术

## 7.1 内核的调试技术支持

内核中集成了很多可选的调试技术支持。这些调试技术或多或少的都会对内核的运行速度有所影响，因此<font color="#c00000">通常发行版的Linux一般不会开启这些支持</font>，这也是推荐使用自行编译的内核而非发行版内核的一个原因。 ^daooag

内核中的调试选项都在 `menuconfig` 下的 `Kernel hacking` 中，可选的调试选项如下：
TODO，用到再说


## 7.2 printk调试技术

















# 8 并发和竞态

Linux内核驱动的多个函数在实际运行中均非独占运行，一个 `open` 或 `read` 函数均可能会被多个线程的多个不同的上下文同时调用，因此要做好并发环境下的临界区管理。
在内核程序中通常也会依靠信号量或互斥锁进行临界区访问管理，但是需要注意的是，<span style="background:#fff88f"><font color="#c00000">内核态程序也会随时被切换为休眠状态，即使此时还处于内核的临界区内</font></span>。在执行一些操作时被切换为休眠状态是一个非常危险的事情。而Linux内核也给出了允许进入休眠态的互斥锁和不允许进入休眠态的互斥锁。
~~内核程序是这样的，用户态的程序临界区管理只需要上互斥锁就可以，而内核程序需要考虑的就很多了，内核程序在占用互斥锁后退出临界区之前会不会随时被切换为休眠状态、在使用禁止休眠的锁机制的临界区内被调用的其他内核组件会不会被切换为休眠状态等，都是需要考虑的事情。~~

## 8.1 Linux内核信号量与互斥锁的实现

Linux内核所使用的信号量和互斥锁应当使用头文件 `<asm/semaphore.h>` ，其相关用法见如下几个子章节所述。

### 8.1.1 普通信号量的初始化

普通信号量的动态初始化可以用如下的函数进行：

```C
void sema_init(struct semaphore *sem, int val);
```

该函数中的 `val` 为该信号量的初始值。

### 8.1.2 互斥锁的静态初始化

互斥锁可以按照如下的方式使用静态<font color="#c00000">定义</font>：

```C
#include <asm/semaphore.h>

// 定义初始值为1的互斥量，即mutex
DECLARE_MUTEX(name);
// 定义初始值为0的互斥量，在获取该互斥量之前必须先显式的解锁
DECLARE_MUTEX_LOCK(name);
```

由于该宏的实际用途为定义，但命名却使用了 `DECLARE` ，因此在Linux 2.6.36之后就删除了该接口。

### 8.1.3 互斥锁的动态初始化

同样的，Linux也提供了互斥锁动态初始化的方法：

```C
void init_MUTEX(struct semaphore *sem);
void init_MUTEX_LOCKED(struct semaphore *sem);
```

不过这两个函数也在之后的版本被移除。

### 8.1.4 互斥锁的操作

互斥锁本质就是信号量的增加与减少。互斥锁的减少可以使用如下的函数：

```C
void down(struct semaphore *sem);
int down_interruptible(struct semaphore *sem);
int down_trylock(struct semaphore *sem);
```

函数 `down` 会阻塞等待直至成功获取到对应的互斥量，且<font color="#c00000">该操作不允许被用户空间中断</font>。
函数 `down_interruptible` 也会互斥等待，但是<font color="#c00000">允许等待该信号量的操作被用户空间程序中断</font>。<font color="#c00000">在其因用户空间的程序中断的时候该函数的返回值为非零值</font>，<font color="#c00000">且此时内核程序并未获得该互斥量</font>。
函数 `down_trylock` 则永远不会休眠，成功获得互斥资源时返回值为0，其他情况为非0。

互斥资源操作时，在非必要情况下应当使用允许中断的版本。
<span style="background:#fff88f"><font color="#c00000">注意上述的中断指的是可否被用户中断，而不是可否被阻塞休眠</font></span>。<font color="#c00000">不可休眠的是自旋锁</font>。

互斥锁的增加直接使用如下函数即可：

```C
void up(struct semaphore *sem);
```

### 8.1.5 读写锁

读写锁与普通的信号量有些不同，因此其需要使用头文件 `<linux/rwsem.h>` ，其初始化方法与操作方法如下：

```C
void init_rwsem(struct rw_semaphore *sem);

// 读者API
void down_read(struct rw_semaphore *sem);
int down_read_trylock(struct rw_semaphore *sem);
void up_read(struct rw_semaphore *sem);

// 写者API
void down_write(struct rw_semaphore *sem);
int down_write_trylock(struct rw_semaphore *sem);
void up_write(struct rw_semaphore *sem);
void downgrade_write(struct rw_semaphore *sem);
```

其中， `downgrade_write` 是<font color="#c00000">将写者降级为读者</font>。

### 8.1.6 completion事件

在内核编程时常用的一个设计方法是在别的线程初始化某个活动，原线程会等待该活动结束后才会继续执行后续任务。尽管使用信号量就可以解决这个需求，但是内核也提供了更好的解决方案，即completion接口，头文件为 `<linux/completion.h>` ，用法如下：

```C
// 静态初始化
DECLARE_COMPLETION(my_completion);

// 动态初始化
struct completion my_completion;
init_completion(&my_completion);
```

随后可以如下使用：

```C
void wait_for_completion(struct completion *c);
void complete(struct completion *c);
void complete_all(struct completion *c);
```

## 8.2 自旋锁

这里将自旋锁与普通的互斥锁分开讨论的主要原因是由于自旋锁和互斥锁的特性(<font color="#c00000">不可休眠</font>)、实现、应用场景及约定均有所不同，因此在后续的讨论中会将轮询实现的自旋锁和信号量分开讨论。

### 8.2.1 自旋锁

在用户态，自旋锁主要用于避免快速上锁/释放锁的场景下线程进入阻塞状态后，因调度算法导致进程再次获得处理机所需要的较长时间。而无论内核态还是用户态，<span style="background:#fff88f"><font color="#c00000">自旋锁是都用于避免被阻塞休眠的</font></span>。<font color="#c00000">在内核中，有些工作不能进入阻塞状态，例如中断处理程序等</font>。
自旋锁的头文件位于 `<linux/spinlock.h>` ，用法如下：

```C
// 静态初始化
spinlock_t lock = SPIN_LOCK_UNLOCKED;

// 动态初始化
void spin_lock_init(spinlock_t *lock);
```

<font color="#c00000">自旋锁只是在申请和等待锁时不会被休眠</font>，<span style="background:#fff88f"><font color="#c00000">但是自旋锁并不负责保护临界区代码不会被休眠</font></span>。<span style="background:#fff88f"><font color="#c00000">并且在使用自旋锁时应当避免代码被休眠</font></span>，<font color="#c00000">否则极有可能引发死锁并引起内核崩溃</font>，<u>例如在中断服务函数中使用了一个自旋锁，但是该锁被其他进程持有，且该进程被中断服务抢占CPU时间，导致中断永远无法结束，进程也永远无法获得CPU时间从而导致死锁</u>。

但是避免休眠很难做到，例如：
- 使用常见的可能休眠的函数导致休眠
	- `copy_form_user`
	- `kmalloc`
- <font color="#c00000">被高优先级进程抢占处理器时间</font>
- 触发处理器中断
等，因此需要做如下的额外处理：
1. <font color="#c00000">避免使用任何的可能导致休眠的函数</font>
2. <font color="#c00000">使用自旋锁时应当关闭中断</font>
3. <font color="#c00000">尽可能的减少持有该锁的时间</font>

因此自旋锁的操作除了如下的两个基础API：

```C
void spin_lock(spinlock_t *lock);
void spin_unlock(spinlock_t *lock);
```

以外，还有相较高级一些的API：

```C
// 获得自旋锁的函数
void spin_lock_irqsave(spinlock_t *lock, unsigned long long flags);
void spin_lock_irq(spinlock_t *lock);
void spin_lock_bh(spinlock_t *lock);

// 释放自旋锁的函数
void spin_unlock_irqsave(spinlock_t *lock, unsigned long long flags);
void spin_unlock_irq(spinlock_t *lock);
void spin_unlock_bh(spinlock_t *lock);
```

其中：
- `spin_lock_irqsave` 会在获得自旋锁之前禁止中断，先前的状态会被保存于 `flags` 中。<font color="#c00000">该函数是宏函数</font>，因此 `flags` <font color="#c00000">会被修改</font>。其本质调用为 `flags = _raw_spin_lock_irqsave(lock);` 
- `spin_lock_irq` <font color="#c00000">和上述函数的实际调用一致</font>，只是忽略了需要保存的 `flags` 。
- `spin_lock_bh` 会关闭所有软件中断，但不会关闭硬中断。
- `spin_unlock_irqsave` 可以将由 `spin_lock_irqsave` 保存的 `flags` 恢复。

还有非阻塞式的函数：

```C
int spin_trylock(spinlock_t *lock);
int spin_trylock_bh(spinlock_t *lock);
```

上述函数在成功获得自旋锁时会返回0，其他情况为非0。

### 8.2.2 自旋读写锁

自旋读写锁的头文件依旧位于 `<linux/spinlock.h>` ，其常用方法如下：

```C
// 静态初始化
rwlock_t lock = RE_LOCK_UNLOCKED;

// 动态初始化
rwlock_t lock;
rwlock_init(&lock);
```

```C
void read_lock(rwlock_t *lock);
void read_lock_irqsave(rwlock_t *lock, unsigned long flags);
void read_lock_irq(rwlock_t *lock);
void read_lock_bh(rwlock_t *lock);
```

```C
void read_unlock(rwlock_t *lock);
void read_unlock_irqsave(rwlock_t *lock, unsigned long flags);
void read_unlock_irq(rwlock_t *lock);
void read_unlock_bh(rwlock_t *lock);
```

```C
void write_lock(rwlock_t *lock);
void write_lock_irqsave(rwlock_t *lock, unsigned long flags);
void write_lock_irq(rwlock_t *lock);
void write_lock_bh(rwlock_t *lock);
int write_trylock(rwlock_t *lock);
```

```C
void write_unlock(rwlock_t *lock);
void write_unlock_irqsave(rwlock_t *lock, unsigned long flags);
void write_unlock_irq(rwlock_t *lock);
void write_unlock_bh(rwlock_t *lock);
```

## 8.3 并发管理的常见问题

并发管理向来不是一个轻松的任务，并发及互斥锁的常见问题有如下几个章节：

### 8.3.1 递归调用问题(可重入锁)

在编写代码时，很容易会写出一个已经持有互斥锁的函数去调用另外一个需要持有互斥锁才能运行的函数，这种通常称为递归调用。而在上述给出的并发管理工具中并未给出类似于POSIX中的递归锁或可重入锁，因此在内核编程中应更加着重注意此类问题。<font color="#c00000">通常的做法是在所有暴露给内核的API中做互斥管理，然后在这些API中所调用的内部实现均假设该互斥资源已被占有</font>。

### 8.3.2 互斥资源的获取顺序问题

一个API需要同时获取多个互斥资源是一个很常见的事情，且<font color="#c00000">非常容易触发操作系统中的类似于哲学家吃饭问题的死锁问题</font>，通常的处理方式是一个内核程序统一按照一个有序的方式申请资源(即资源的有序分配法)。
并且，需要注意的是，在<font color="#c00000">同时应当获得一个信号量和一个自旋锁时</font>，<font color="#c00000"><b>必须</b>优先获取信号量</font>，<font color="#c00000">随后再去申请自旋锁</font>。<font color="#c00000">因为持有自旋锁的进程被信号量阻塞是一件<b>严重错误且非常危险</b>的事情</font>。
当然，最好的处理此类需要获取多个互斥资源的方法就是尽量避免这种现象。

### 8.3.3 互斥锁的粒度管理问题

关于互斥资源管理的粒度问题，可以直接以Linux对SMP的支持进行举例。
在第一个支持多处理器的Linux2.0，整个内核有且仅有一个巨大的临界区(<font color="#c00000">BKL</font>，Big Kernel Lock)。当需要操作内核临界区时都需要申请该互斥锁。而在后来的Linux2.2中，互斥锁管理的粒度逐渐细化，例如I/O子系统共用一个互斥锁，网络系统共用一个互斥锁等。到了现在的版本，Linux内核中已经拥有了上千个互斥锁。
互斥资源管理粒度的细化无疑会提升CPU资源的利用率，但是在实际的工程中，<font color="#c00000">不应当过早的细化互斥资源的管理</font>，<font color="#c00000">因为项目最终的性能瓶颈往往不会出现在互斥资源的管理上</font>。<font color="#c00000">而混乱的互斥资源管理反而会导致更多严重问题的出现</font>。

## 8.4 并发管理的优化

### 8.4.1 使用原子变量或非锁方法

例如若要实现一个如下图所示的循环缓冲区，可以使用读写锁，仅使用原子变量表示读写index，并使用该原子index做到[[Berstein条件]]即可。
	![[msedge_Mbwk30DDuN.png]]
而原子操作对应的头文件为 `<asm/atomic.h>` ，常见的操作方法如下：

```C
// 设置初始值
void atomic_set(atomic_t *v, int i);
// 可用于但不仅用于静态初始化
atomic_t v = ATOMIC_INIT(0);
// 读取
int atomic_read(atomic_t *v);
// 加减运算
void atomic_add(int i, atomic_t *v);
void atomic_sub(int i, atomic_t *v);
// 自增自减
void atomic_inc(atomic_t *v);
void atomic_dec(atomic_t *v);
// 带判定是否为0的减法及自增自减方法，返回值仅有0或1，与 atomic_*_and_return 方法不同
// (注意不存在加法函数，即不存在 `atomic_add_and_test` 方法)
int atomic_inc_and_test(atomic_t *v);
int atomic_dec_and_test(atomic_t *v);
int atomic_sub_and_test(int i, atomic_t *v);
// 执行加法并判定是否为负，返回值仅有0或1
int atomic_add_negative(int i, atomic_t *v);
// 执行自增自减或加减并返回结果，与 atomic_*_and_test 不同
int atomic_add_return(int i, atomic_t *v);
int atomic_sub_return(int i, atomic_t *v);
int atomic_inc_return(atomic_t *v);
int atomic_dec_return(atomic_t *v);
```

此外，内核还提供了一组<font color="#c00000">原子位操作</font>，可以用于<font color="#c00000">操作非原子变量</font>。这些原子位操作速度非常快，在架构支持的情况下仅需要一个机器指令就可以完成，则这些平台进行此类操作的时候就可以不关闭中断。但是其实现也高度依赖于具体平台，用于表述目标位的 `nr` 参数通常为 `int` ，但是有时会被定义为 `unsigned long` ；要修改的元素通常用 `unsigned long *` 来做指针，但在一些平台中会被定义为 `void*` 。其主要的API如下：

```C
void set_bit(nr, void* addr);
void clear_bit(nr, void* addr);
void change_bit(nr, void* addr);
test_bit(nr, void* addr);
int test_and_set_bit(nr, void* addr);
int test_and_clear_bit(nr, void* addr);
int test_and_change_bit(nr, void* addr);
```

通常来说并不建议使用原子位操作，而建议改用自旋锁进行操作。

### 8.4.2 顺序锁(seqlock)

seqlock与信号量不同，其不需要任何阻塞操作。其通常用于处理读者写者问题，但是<font color="#c00000">只能解决仅有一个写者的情况</font>。
seqlock的使用与原理如下：

```C
int seq = 0;

void reader()
{
	int value = 0;
	// 等待进入临界区，进入临界区条件为seq为偶数
	while(seq % 2);
	// 进入临界区
	do {
		if(seq_old != seq)
			seq_old = seq;
		value = Read();
	} while(seq_old != seq);
}

void writer()
{
	seq ++;
	write();
	seq ++;
}
```

在上述原理中，写者：
1. 进入临界区之前将seq++，使此时seq为奇数。
2. 写入数据。
3. <font color="#c00000">再次seq++</font>，使seq值为偶数并且与原先seq值不重复。
读者：
1. 进入临界区之前判定顺序锁的值是否为偶数，不为偶数时等待写者离开(此时写者占有互斥资源)
2. 顺序锁为偶数，进入临界区，并在读取操作前备份seq值
3. 读取数据
4. <font color="#c00000">校验seq是否被更改</font>，若被更改则证明在此期间写者已修改数据，原数据失效，需要重新读取。

<span style="background:#fff88f"><font color="#c00000">注意：不要用seqlock保护一个指针，因为指针在writer里面很可能会被修改为NULL等一旦访问就会触发错误的值</font></span>。

seqlock的头文件位于 `<linux/seqlock.h>` ，使用方法如下：
初始化：

```C
// 静态初始化
seqlock_t lock = SEQLOCK_UNLOCKED;
// 动态初始化
seqlock_t lock;
seqlock_init(&lock);
```

执行读取任务：

```C
int reader()
{
	unsigned int seq = 0;
	do {
		// 下一句可能会进行自旋操作，直到写者退出
		seq = read_seqbegin(&lock);
		// Do sth...
		read();
	} while read_seqretry(&lock, seq);
}
```

上述代码中的 `read_seqbegin` 、 `read_seqretry` 分别可以换成如下的任意版本：

```C
unsigned int read_seqbegin_irqsave(seqlock_t *lock, unsigned long flags);
```

```C
int read_seqretry_irqrestore(seqlock_t *lock, unsigned long flags);
```

执行写入任务直接使用如下API即可

```C
void write_seqlock(seqlock_t *lock);
void write_sequnlock(seqlock_t *lock);

void write_seqlock_irqsave(seqlock_t *lock, unsigned long flags);
void write_seqlock_irq(seqlock_t *lock);
void write_seqlock_bh(seqlock_t *lock);

void write_sequnlock_irqrestore(seqlock_t *lock, unsigned long flags);
void write_sequnlock_irq(seqlock_t *lock);
void write_sequnlock_bh(seqlock_t *lock);
```

### 8.4.3 RCU方法(读取-复制-更新方法)

RCU方法是一个高级的互斥机制，尽管它很少的被用于驱动程序设计中。不过在路由表和Starmode的射频IP驱动仍使用了该方法。
RCU是一个支持<font color="#c00000">一个写者</font>和多个读者<font color="#c00000">同时进行操作</font>的一个互斥机制(但不意味着至多只有一个写者)。<font color="#c00000">RCU适用于需要频繁的读取数据</font>，<font color="#c00000">而修改数据并不多的情景</font>。例如在文件系统中，经常需要查找定位目录，而对目录的修改相对来说并不多，这就是RCU发挥作用的最佳场景。

RCU的基本流程：
读者：
1. 获取RCU锁(关中断，保持原子操作)
2. 使用读者和写者所用指针读取数据
3. 释放RCU锁(开中断)

写者：
1. 为新数据分配新的内存地址
2. 将读者和写者所用指针指向新的地址

资源回收：
1. 等待所有CPU完成一次任务调度
2. 清除所有过时资源

注意，<font color="#c00000">Linux的RCU并不依赖引用计数器</font>，因为引用计数器本身的互斥保护也是一个麻烦的事情。在Linux中，<font color="#c00000">RCU的基本规则是所有读者对该数据的访问均以原子操作进行</font>，从而保证在进行读者的原子操作时不会被抢占。随后，当所有处理器都完成一次任务调度后(此时保证了所有读者完成对资源的读取)即可进行资源的清除工作。<font color="#c00000">RCU的性能表现比自旋锁要好</font>。

资源的清除工作通过预先设置的回调函数实现，通常该函数的工作内容就是调用 `kfree` 。

```C
void call_rcu(struct rcu_head* head, void(*func)(void *arg), void *arg);
```

### 8.4.4 per-CPU变量 ^3z1la0

per-CPU变量如字面意思一样，是每个CPU都有一份实例的变量，per-CPU确保这些变量在每个CPU上独立且只能自己可见。若需要进行数据同步操作则需要额外的互斥等机制进行实现。

<span style="background:#fff88f"><font color="#c00000">考虑如下场景</font></span>：
- 某内核模块需要实现一个计数器(通常per-CPU的使用场景就是计数器)，需要统计某项操作或者事件的次数。
- 这个操作或者事件可能在多个CPU上同时发生。
那么考虑如下的实现：
1. 使用per-CPU变量，在每个CPU上独立实例化一个计数器。
2. 当每个CPU上发生该操作或事件时，计数器+1。
3. <font color="#c00000">确保每个事件的处理仅会涉及一个CPU</font>，不会被换出到其他CPU上。
4. 最终统计汇总计数器时使用其他的互斥操作实现。
这样就能极大的优化互斥管理。
总的来说，<font color="#c00000">per-CPU变量的使用场景为</font>：<span style="background:#fff88f"><font color="#c00000">高频局部修改，低频全局读写</font></span>(例如计数器、统计信息)。

那么per-CPU则有如下特性：
1. 每个CPU操作自身的副本，无需与其他CPU同步。该变量可以通过存储在每个CPU的私有内存区域中实现，或通过编译器或运行时机制隔离访问实现(例如在其访问时根据当前CPU ID计算偏移量，从而定位实例)
2. 读写操作时提供禁用抢占的操作方式。

#### 8.4.4.1 静态声明与定义

per-CPU变量的声明与定义：

```C
#include "linux/percpu-defs.h"

// 声明未初始化的变量
DECLARE_PER_CPU(int, my_counter);

// 声明并初始化
DEFINE_PER_CPU(int, my_counter) = 0;

// 启用缓存行对齐避免伪共享(本例中直接定义了数组)
DEFINE_PER_CPU(int[4], my_array) __cacheline_aligned = { 0 }; 
```

#### 8.4.4.2 动态创建与销毁

```C
#include "linux/percpu-defs.h"

int __percpu *dyn_counter = alloc_percpu(int);

// 操作per-CPU变量
*per_cpu_ptr(dyn_counter, smp_processor_id()) = 42;

free_percpu(dyn_counter);
```
#### 8.4.4.3 读写操作

<span style="background:#fff88f"><font color="#c00000">在读写per-CPU变量时需要禁用抢占</font></span>，<font color="#c00000">关闭抢占后当前任务不会被其他任务抢占</font>，<font color="#c00000">确保当前任务只会在同一个CPU上运行</font>，例如：

```C
int cpu = get_cpu();         // 获取当前CPU ID并禁用抢占
per_cpu(my_counter, cpu)++;  // 操作当前CPU的变量
put_cpu();                   // 启用抢占
```

或者直接用隐含启停抢占的形式：

```C
get_cpu_var(my_counter)++;   // 操作当前CPU变量(自动禁用抢占)
put_cpu_var(my_counter);     // 释放
```

上述接口的定义如下：

```C
#define get_cpu()		({ preempt_disable(); __smp_processor_id(); })
#define put_cpu()		preempt_enable()

/*
 * Must be an lvalue. Since @var must be a simple identifier,
 * we force a syntax error here if it isn't.
 */
#define get_cpu_var(var)						\
(*({									\
	preempt_disable();						\
	this_cpu_ptr(&var);						\
}))

/*
 * The weird & is necessary because sparse considers (void)(var) to be
 * a direct dereference of percpu variable (var).
 */
#define put_cpu_var(var)						\
do {									\
	(void)&(var);							\
	preempt_enable();						\
} while (0)
```

其主要依靠 `preempt_disable()` 和 `preempt_enable()` 进行管理CPU抢占。

#### 8.4.4.4 注意点

per-CPU变量需要注意如下的注意点：
1. 汇总时需要注意CPU热拔插问题。
2. 必须禁用抢占后才能读取CPU ID，不然可能错位。

# 9 高级字符设备驱动程序

## 9.1 ioctl

在第5章讲解了如何编写或实现用户对设备的读取或写入请求，但是在真实的设备中往往还有例如弹出设备、修改波特率等非普通读写操作。而这些方法往往使用ioctl作为操作接口。
在用户空间中， `ioctl` 的函数原型如下：

```C
int ioctl(int fd, unsigned long cmd, ...);
```

尽管在用户空间，该API的参数被定义为可变参数，但是在内核中并非如此。
查阅资料并分析可知，用户态的 `ioctl` 参数要求为：
- `ioctl` <span style="background:#fff88f"><font color="#c00000">至多支持3个参数</font></span>，因此可变参数的引用并没有引入更多的参数支持
- 但是 `ioctl` <font color="#c00000">支持2个参数的调用</font>，这也是使用可变参数的原因

在Linux 2.6.35及以前，内核的 `ioctl` 接口同时被定义为如下的接口：

```C
int (*ioctl)(struct inode *inode, struct file *filep, unsigned int cmd, unsigned long arg);
long (*unlocked_ioctl) (struct file *, unsigned int cmd, unsigned long arg);
long (*compat_ioctl) (struct file *, unsigned int cmd, unsigned long arg);
```

在Linux 2.6.36及之后，内核的ioctl<font color="#c00000">仅保留</font>了如下的接口：

```C
long (*unlocked_ioctl) (struct file *, unsigned int cmd, unsigned long arg);
long (*compat_ioctl) (struct file *, unsigned int cmd, unsigned long arg);
```

而在内核态，需要注意的是：
- 用户态的 `ioctl` <font color="#c00000">至多支持3个参数</font>，这样也和内核态的接口定义做到了匹配
- <span style="background:#fff88f"><font color="#c00000">但是用户态支持2个参数的调用</font></span>，<font color="#c00000">在2个参数的调用时</font>，<span style="background:#fff88f"><font color="#c00000">内核态收到的第三个参数是未定义的</font></span>。

虽然老的 `ioctl` 接口已不再使用，但是还是要先从老的版本开始讲起。

### 9.1.1 ioctl接口(Linux 2.6.35及以前)

如上文所述， `ioctl` 的接口定义如下：

```C
int (*ioctl)(struct inode *inode, struct file *filep, unsigned int cmd, unsigned long arg);
```

上述接口中的参数：
- `struct inode *` 和 `struct file *` 的定义与用法和[[Linux驱动开发笔记#5 8 open和release方法]]中的一致，内核负责将用户态的 `ioctl` 中指定的 `fd` 转化为这两个数据结构。
- `cmd` 则和用户态中传入的对应参数完全保持一致，而在用户态和内核态对该参数含义的约定也应当保持一致，通常用对应的头文件来实现。而内核态对 `cmd` 参数的处理通常可以使用 `switch` 方法。至于 `cmd` 参数的<span style="background:#fff88f"><font color="#c00000">命令编号原则</font></span>可见章节[[Linux驱动开发笔记#8.1.3 cmd命令编号]]。

而返回值也应当从 `<linux/errno.h>` 中选值返回，常用的值如下：
- `-ENOTTY` ：POSIX标准规定的指定的命令非法的返回值

<span style="background:#fff88f"><font color="#c00000">注意：老的ioctl会在获得大内核锁(BKL)的条件下运行，所以应当尽快处理并返回</font></span>。

ioctl是Linux 2.6.35及以前所使用的接口，但是其往往会遇到在不同位数下，`unsigned long` 数据大小不同的情况：
	![[Linux驱动开发笔记#2 2 1 1 不同架构处理器下的数据类型大小]]
对于32位Linux系统，其只能运行32位的驱动程序和32位的用户态程序，因此ioctl可以很好的工作。而对于64位系统，其上可以运行32为的用户态程序，此时32位程序传来的 `unsigned long` 就是4Byte的整数类型，此时再传递给内核态驱动程序就可能出现错误。

此外，<span style="background:#fff88f"><font color="#c00000">更大的问题</font></span>在于<font color="#c00000">老的ioctl方法是由内核的大内核锁(BKL)实现并发控制的</font>，驱动在ioctl中较长的占用处理器则会导致无关的进程会被该ioctl产生较长时间的系统调用延迟()。为了解决此问题([[The new way of ioctl()]])，Linux在2.6.11开始引入了 `unlocked_ioctl` 和 `compat_ioctl` ，并在Linux 2.6.36彻底删除了 `ioctl` 接口。

### 9.1.2 unlocked_ioctl和compat_ioctl(Linux 2.6.36及以后)

正如上文所述，在64位系统上运行32位的用户态程序会导致传输传递时字节大小不匹配的问题。因此无论在32位还是64位的系统上都需要分别实现这两个函数。其调用情况为：

| 用户和内核位数关系       | ioct实际调用接口       | 理应的内核实现                                                                      |
| --------------- | ---------------- | ---------------------------------------------------------------------------- |
| 32位用户态调用32位内核驱动 |                  | `int32_t (*unlocked_ioctl) (struct file *, unsigned int cmd, uint32_t arg);` |
| 64位用户态调用32位内核驱动 | 不存在此种情况          |                                                                              |
| 64位用户态调用64位内核驱动 | `unlocked_ioctl` | `int64_t (*unlocked_ioctl) (struct file *, unsigned int cmd, uint64_t arg);` |
| 32位用户态调用64位内核驱动 | `compat_ioctl`   | `int32_t (*compat_ioctl) (struct file *, unsigned int cmd, uint32_t arg);`   |

几个注意点：
1. <font color="#c00000">在32位系统上调用ioctl，对应的实现也是</font> `unlocked_ioctl` 只是位宽不一样。
2. 在这两个接口中：
	- `compat_ioctl` 意味"兼容性的ioctl"
	- `unlocked_ioctl` 意味"<font color="#c00000">解锁的ioctl</font>"，<font color="#c00000">此函数不会为内核施加大内核锁</font>，且此时需要驱动程序管理自己的互斥锁。

### 9.1.3 cmd命令编号

#### 9.1.3.1 cmd命令编号的基本原则

按照规则，ioctl的cmd并不能随意编号，<span style="background:#fff88f"><font color="#c00000">一个基本原则是命令号应当在整个系统范围内唯一</font></span>。该原则的设定主要有如下考虑：
- <font color="#c00000">避免用户态程序误操作其他设备</font>：若没有该原则，假设用户态同时打开了多个设备，其对设备A的某一cmd进行操作时误选中设备B进行操作，而设备B也有与cmd相对应的命令。则在这种情况下，对设备B的误操作并不会抛出 `-EINVAL` 错误，从而导致错误未被有效暴露。
- 更多考虑可见：[[ioctl-number.rst#^kt29rl]]

Linux的cmd命令编号原则应参考 `Documentation/userspace-api/ioctl/ioctl-number.rst` (翻译可见[[ioctl-number.rst]])。在定义cmd编号时，应当在头文件中参考上述规则使用 `_IO(type,nr)` 、 `_IOR(type,nr,size)` 、 `_IOWR(type,nr,size)` 等宏进行定义。

上述参数中：
- `type` 应当填写该设备所拥有的类型序号，可能多个设备共用一个 `type` ，并按照 `nr` 的范围划分，可见[[ioctl-number.rst]]
- `nr` 应当在该设备所拥有的 `type` 的 `nr` 子区间内顺序递增
- `size` <span style="background:#fff88f"><font color="#c00000">不应当填写具体的size值，直接填写类型即可</font></span>
(奇怪的命名)

使用示例如下(`cifs_ioctl.h`)：

```C
#define CIFS_IOCTL_MAGIC         0xCF  
#define CIFS_IOC_COPYCHUNK_FILE  _IOW(CIFS_IOCTL_MAGIC, 3, int)  
#define CIFS_IOC_SET_INTEGRITY   _IO(CIFS_IOCTL_MAGIC, 4)  
#define CIFS_IOC_GET_MNT_INFO    _IOR(CIFS_IOCTL_MAGIC, 5, struct smb_mnt_fs_info)  
#define CIFS_ENUMERATE_SNAPSHOTS _IOR(CIFS_IOCTL_MAGIC, 6, struct smb_snapshot_array)  
#define CIFS_QUERY_INFO          _IOWR(CIFS_IOCTL_MAGIC, 7, struct smb_query_info)  
#define CIFS_DUMP_KEY            _IOWR(CIFS_IOCTL_MAGIC, 8, struct smb3_key_debug_info) 
#define CIFS_IOC_NOTIFY          _IOW(CIFS_IOCTL_MAGIC, 9, struct smb3_notify)  
#define CIFS_DUMP_FULL_KEY       _IOWR(CIFS_IOCTL_MAGIC, 10, struct smb3_full_key_debug_info)  
#define CIFS_IOC_NOTIFY_INFO     _IOWR(CIFS_IOCTL_MAGIC, 11, struct smb3_notify_info)  
#define CIFS_IOC_GET_TCON_INFO   _IOR(CIFS_IOCTL_MAGIC, 12, struct smb_mnt_tcon_info)  
#define CIFS_IOC_SHUTDOWN        _IOR('X', 125, __u32)
```

而对于上述的"编码宏"，Linux也提供了对应的"解码宏"：
- `_IOC_DIR(nr)`
- `_IOC_TYPE(nr)`
- `_IOC_NR(nr)`
- `_IOC_SIZE(nr)`

#### 9.1.3.2 预定义命令

除了自己在ioctl的接受函数里预定义的命令以外，Linux还内置了一些通用的预定义命令。<span style="background:#fff88f"><font color="#c00000">这些命令会被Linux系统截断，并不会传递到内核驱动中</font></span>。且应当注意自己的cmd命令编号不应当与系统的预定义命令冲突或重复。
预定义命令主要可以分为如下三组：
- 可用于任何文件(包括普通文件、设备、FIFO和socket)的命令
- 只用于普通文件的命令
- 特定于文件系统的命令
通常来说，设备驱动的开发人员应当注意第一组预处理命令，这些命令的 `type` 都是 `T` 。这些命令主要有：
- `FIOCLEX` ：设备执行时关闭标志，<font color="#c00000">F</font>ile <font color="#c00000">io</font>ctl <font color="#c00000">cl</font>ose on <font color="#c00000">ex</font>ec。设置了这个标志后，<span style="background:#fff88f"><font color="#c00000">当进程退出</font></span>(即执行 `exec()` 系统调用)<span style="background:#fff88f"><font color="#c00000">时</font></span>，<span style="background:#fff88f"><font color="#c00000">自动关闭该文件</font></span>。
- `FIONCLEX` ：清除设备执行时关闭标志，主要用于撤销上述命令。
- `FIOASYNC` ：使能或关闭socket的异步模式。
- `FIOQSIZE` ：该命令在操作普通文件时会返回文件或目录的大小，但是用于操作设备时会返回 `-ENOTTY` 错误。
- `FIONBIO` ：允许或禁止一个文件(通常是Socket)的非阻塞模式。不过修改该标志位的方法通常是用 `fnctl` 使用 `F_SETFL` 命令完成。

### 9.1.4 ioctl传参

在ioctl传参时，应当注意传递的是实际参数还是指针。传递普通参数时正常实现即可，当传递指针时应当注意该用户空间的指针是否合法，其方法主要分为如下几类：
1. 传输大批量的内存数据时，使用 `copy_from_user` 或 `copy_to_user` 即可。
2. 传输小批量数据时，可以使用如下函数进行校验：

```C
int access_ok(int type, const void *addr, unsigned long size);
```

其中， `type` 可以选择 `VERIFY_READ` 或 `VERIFY_WRITE` ，参数 `addr` 指用户空间地址，参数 `size` 指要传输的字节数。注意， `VERIFY_WRITE` 是 `VERIFY_READ` 的超集。 `access_ok` 将返回0或1。
随后即可使用 `<asm/uaccess.h>` 中的<font color="#c00000">无需检查的</font>宏函数进行传输(预处理时展开)：
- `__put_user(x, ptr)` ： `x` 为内核态数据、 `ptr` 为用户指针
- `__get_user(x, ptr)` ： `x` 为内核态数据、 `ptr` 为用户指针
注意：
- `access_ok` <font color="#c00000">只负责检验该内存地址是否位于进程对应有权限访问的区域内</font>
- 在使用 `access_ok` 后可以使用Linux为常用的1、2、4、8字节类型提供的，尽管大部分代码并不需要使用 `access_ok` 进行访问。
3. 直接使用<font color="#c00000">含可访问检查</font>(已内置无需再次 `access_ok` )的宏函数(预处理时展开)：
	- `put_user(x, ptr)` ： `x` 为内核态数据、 `ptr` 为用户指针
	- `get_user(x, ptr)` ： `x` 为内核态数据、 `ptr` 为用户指针

<span style="background:#fff88f"><font color="#c00000">注意：2和3仅可用于sizeof为1、2、4、8字节大小的参数传递，其他类型无法使用</font></span>。
<span style="background:#fff88f"><font color="#c00000">宏函数内置的sizeof是对用户空间的指针所指对象大小进行计算</font></span>(即 `sizeof(*(ptr))` )

### 9.1.5 权限与操作

在驱动程序中，对设备的操作也应当分为不同的权限等级，例如读取硬盘、写入硬盘以及格式化硬盘本就不应当是同一组权限。而在Linux中也内置了一些权限，例如在 `<linux/capability.h>`
中预先定义了如下一些可能常用的权限：
- `CAP_DAC_OVERRIDE` ：
- `CAP_NET_ADMIN` ：执行网络管理任务的权限，例如配置网络接口
- `CAP_SYS_MODULE` ：载入或者卸载内核模块的权限
- `CAP_SYS_RAWIO` ：执行裸IO的权限，例如直接使用I2C或者USB通信
- `CAP_SYS_ADMIN` ：
- `CAP_SYS_TTY_CONFIG` ：执行tty配置任务的权限
在内核驱动中，可以使用 `<sys/sched.h>` 中的如下API检查是否有对应权限：

```C
int capable(int capability);
```

对于不满足权限的请求可以返回 `-EPREM` 。

## 9.2 非ioctl类设备控制

并非所有的设备都有必要使用ioctl这种控制方式，例如想要实现一个PWM控制的舵机驱动程序，大可不必使用ioctl实现这类控制，直接使用字符控制即可。例如若实现：

```Shell
echo "90" > /dev/servo0
```

则比使用 `ioctl` 外加特定的头文件定义 `ioctl` 的 `cmd` 要方便且可移植。类似的例子还有使用 `AT` 指令配置调制解调器等设备。

## 9.3 阻塞型IO

当设备无法立即完成某请求时，常用的做法之一是实现一个阻塞型IO。

阻塞和休眠通常都是由等待一个事件或资源引起的，因此其等待的时间通常具有不可预测的特性。在进入休眠时，务必注意下列注意事项：
1. <span style="background:#fff88f"><font color="#c00000">不可在原子上下文中进行休眠</font></span>。因为原子操作通常依靠自旋锁、顺序锁甚至是关闭中断来实现的。在这里进行休眠及其容易造成死锁或其他系统稳定性相关的问题。<font color="#c00000">在进入休眠时需检查如下事项</font>：
	1. 休眠时不可拥有(<font color="#c00000">因为下述机制本就是为避免休眠切约定不可休眠的互斥方法</font>)：
		- [ ] 自旋锁
		- [ ] 顺序锁
		- [ ] RCU锁
	2. 休眠时不可关闭中断
2. 休眠时允许拥有信号量，则务必关注可能会被该信号量影响的线程，且需要注意不要构成循环等待这种死锁情况。(该线程所持有的信号量所阻塞的线程拥有该线程所等待的资源)
3. 在进行休眠时，<font color="#c00000">务必确保有其他线程或进程会唤醒本进程</font>。

### 9.3.1 阻塞型IO的标准语义

关于阻塞IO和非阻塞IO的相关定义与基础知识可以详见：[[IO模型#3 IO模型]]。

#### 9.3.1.1 open语义

#TODO 

#### 9.3.1.2 read与write语义

由于无论是否IO为阻塞型IO，read、write的行为必须和poll的行为保持同步，因此此处不详细说明阻塞IO模型下的read与write语义。
阻塞型IO的read与write语义应详见：
- [[Linux驱动开发笔记#8 7 1 2 read函数的标准语义]]
- [[Linux驱动开发笔记#8 7 1 3 write函数的标准语义]]

## 9.4 简单休眠

在Linux中的头文件 `<linux/wait.h>` 中提供了阻塞与休眠相关的API，其较为重要的使用方法如下：
1. <font color="#c00000">休眠和唤醒</font>通常通过等待队列来实现，可以通过如下的方法静态或动态的定义一个等待队列：
```C
// 静态定义
DECLARE_WAIT_QUEUE_HEAD(name);

// 动态定义
wait_queue_head_t q_head;
init_waitqueue_head(&q_head);
```
2. 休眠指令，注意该休眠指令<font color="#c00000">实际上为宏函数</font>：
```C
// 休眠API(注意都是宏函数)

/**
 * @brief: 休眠直到condition为true
 * @note: 每次wq_head被唤醒都会被执行并判定condition
 */
wait_event(wq_head, condition)

/**
 * @brief: 休眠直到condition为true，支持系统被挂起期间冻结
 */
wait_event_freezable(wq_head, condition)

/**
 * @brief: 休眠直到condition为true，或者超时(以jiffy表示)时中断休眠。
 * @return:
 *     - 当超时后condition为true返回0
 *     - 当超时后condition为false返回1
 *     - 超时前condition为true则返回剩余jiffy数(大于等于1)
 */
wait_event_timeout(wq_head, condition, timeout)

/**
 * @brief: 休眠直到condition为true。在执行等待前和后，cmd1和cmd2会分别被执行
 * @return:
 *     - 当其被信号打断时返回值为非零
 */
wait_event_cmd(wq_head, condition, cmd1, cmd2)

/**
 * @brief: 休眠直到condition为true，或者被信号中断休眠。当其被信号打断时返回值为非零。
 * @return:
 *     - 当其被信号打断时返回值为非零
 */
wait_event_interruptible(wq_head, condition)
```
注：
- 上述 `condition` 是一个<font color="#c00000">不带副作用</font>的 `bool` 表达式，<span style="background:#fff88f"><font color="#c00000">该表达式可能会被多次求值</font></span>。
- `condition` 的另一注意点见下方[[Linux驱动开发笔记#^dcp6ey|关键注意点]]。
3. 唤醒指令。休眠和唤醒通常伴随出现。
```C
// wake_up会唤醒所有等在queue上的非独占休眠线程
wake_up(x)

// wake_up_interruptible只会唤醒可中断休眠的线程
wake_up_interruptible(x)
```

<span style="background:#fff88f"><font color="#c00000">关键注意点</font></span>： ^dcp6ey
1. 本章节所提及的简单休眠API，<font color="#c00000">当一个线程触发</font> `wake_up` <font color="#c00000">后</font>，<font color="#c00000">阻塞队列上的</font>(非独占等待节点之前的)<span style="background:#fff88f"><font color="#c00000">所有</font></span><font color="#c00000"><u>简单休眠</u>的线程</font><span style="background:#fff88f"><font color="#c00000">均会被唤醒并判定休眠条件</font></span> `condition` 。在简单休眠中，队列并没有实际的先后作用，队列的作用发生于[[Linux驱动开发笔记#独占等待]]中。
2. 由于一次 `wake_up` 可能会唤醒多个简单休眠对象，<font color="#c00000">因此</font> `condition` <font color="#c00000">的操作也必须是原子的</font>。
3. 简单休眠可能会被多次唤醒，并且时常会不满足判定条件。<font color="#c00000">不满足判定条件的线程会被再次休眠</font>。
4. 注意点1中所述的 "<font color="#c00000">阻塞队列上的非独占等待节点之前的所有简单线程均会被唤醒</font>" <font color="#c00000">的设计</font><span style="background:#fff88f"><font color="#c00000">在后续所学习的别的内核提供的功能上有大用</font></span>。例如：
	- IO多路复用模型中：
		- 一个使用select/poll/epoll监听多个文件事件的线程在不满足监听条件时会被阻塞，但是阻塞是由内核框架完成的，<font color="#c00000">被设置为可中断的</font><span style="background:#fff88f"><font color="#c00000">普通</font></span><font color="#c00000">休眠</font>。
		- 而让驱动或内核去把等待poll类函数的线程绑定到若干事件上的程序设计又太过复杂，因此索性设计为只要当可被监听的事件发生，均调用 `wake_up_interruptible()` 唤醒所有普通休眠的线程，自然就包括了被poll类函数阻塞的线程。

## 9.5 高级休眠

在上一章节的简单休眠中所使用的 `wait_queue_head_t` 的定义如下：

```C
struct wait_queue_head {
	spinlock_t		lock;
	struct list_head	head;
};
typedef struct wait_queue_head wait_queue_head_t;
```

其是由一个自旋锁和链表组成。

而线程的休眠与恢复会影响 `task_struct` 中的 `__state` 标志位，该标志位有如下几个状态：
- `TASK_RUNNING`
- `TASK_INTERRUPTIBLE`
- `TASK_UNINTERRUPTIBLE`
- `__TASK_STOPPED`
- `__TASK_TRACED`
这些状态被定义于 `linux/sched.h` ，从而影响任务的调度。

而以简单休眠章节中的最简单的休眠函数 `wait_event` 为例，来分析 `wait_event` (宏)函数的具体定义：

```C
/*
 * The below macro ___wait_event() has an explicit shadow of the __ret
 * variable when used from the wait_event_*() macros.
 *
 * This is so that both can use the ___wait_cond_timeout() construct
 * to wrap the condition.
 *
 * The type inconsistency of the wait_event_*() __ret variable is also
 * on purpose; we use long where we can return timeout values and int
 * otherwise.
 */

#define ___wait_event(wq_head, condition, state, exclusive, ret, cmd)		\
({										\
	__label__ __out;							\
	struct wait_queue_entry __wq_entry;					\
	long __ret = ret;	/* explicit shadow */				\
										\
	init_wait_entry(&__wq_entry, exclusive ? WQ_FLAG_EXCLUSIVE : 0);	\
	for (;;) {								\
		long __int = prepare_to_wait_event(&wq_head, &__wq_entry, state);\
										\
		if (condition)							\
			break;							\
										\
		if (___wait_is_interruptible(state) && __int) {			\
			__ret = __int;						\
			goto __out;						\
		}								\
										\
		cmd;								\
	}									\
	finish_wait(&wq_head, &__wq_entry);					\
__out:	__ret;									\
})

#define __wait_event(wq_head, condition)					\
	(void)___wait_event(wq_head, condition, TASK_UNINTERRUPTIBLE, 0, 0,	\
			    schedule())

/**
 * wait_event - sleep until a condition gets true
 * @wq_head: the waitqueue to wait on
 * @condition: a C expression for the event to wait for
 *
 * The process is put to sleep (TASK_UNINTERRUPTIBLE) until the
 * @condition evaluates to true. The @condition is checked each time
 * the waitqueue @wq_head is woken up.
 *
 * wake_up() has to be called after changing any variable that could
 * change the result of the wait condition.
 */
#define wait_event(wq_head, condition)						\
do {										\
	might_sleep();								\
	if (condition)								\
		break;								\
	__wait_event(wq_head, condition);					\
} while (0)
```

其定义和使用了三个宏，按照调用顺序依次为：
- `wait_event(wq_head, condition)` ：
	1. 该函数先调用 `might_sleep` 宏函数，<font color="#c00000">被设计为一个注解</font>，该函数会先后调用如下两个函数：
		1. `__might_sleep(__FILE__, __LINE__);` ，在源码中定义为空函数。
		2. `might_resched()` ，即 `int __cond_resched(void)` 函数。
	2. 判定是否满足唤醒条件，若不满足则调用 `__wait_event(wq_head, condition);` 。
- `__wait_event(wq_head, condition)` ：
	1. 直接调用 `___wait_event(wq_head, condition, TASK_UNINTERRUPTIBLE, 0, 0, schedule())` ，即：
		- 设置该休眠为不可中断
		- 非独占等待
		- 返回值为 `0`
		- 在不满足唤醒条件时休眠(即 `___wait_event` 定义中的 `cmd` 部分)
- `___wait_event(wq_head, condition, state, exclusive, ret, cmd)` ：
	1. 创建并初始化等待队列入口 `wait_queue_entry` 
	2. 使用 `prepare_to_wait_event` 将等待队列入口添加到等待队列中，同时设置现成的状态。
	3. 在 `cmd` 中调用 `shedule()` 选择下一个要运行的进程，并进行上下文切换。

### 9.5.1 独占等待

正如章节简单休眠中所述，线程请求简单休眠后，一次 `wake_up` 可能会唤醒多个简单休眠对象，每一个被唤醒的多个简单休眠对象又会重新竞争 `condition` 资源，竞争不到的休眠对象又会被 `schedule` 重新切换到别的进程上，在一定程度上浪费了资源。
因此linux设计了一种一次只会唤醒一个休眠对象的等待，称为独占等待。

独占等待的特性：
1. 被设置为独占等待的进程在休眠时会被<font color="#c00000">添加到等待队列</font><span style="background:#fff88f"><font color="#c00000">尾部</font></span>
2. 普通休眠的进程会被添加到等待队列<span style="background:#fff88f"><font color="#c00000">头部</font></span>
3. 当 `wake_up` 被调用时，其会一直唤醒<font color="#c00000">第一个独占休眠</font><span style="background:#fff88f"><font color="#c00000">以及之前的</font></span>队列上的<font color="#c00000">等待进程</font>。

独占等待的相关api为：

```C
/**
 * @brief: 独占等待直到condition为true。在执行等待前和后，cmd1和cmd2会分别被执行
 * @return:
 *     - 当其被信号打断时返回值为非零
 * @note:
 *     - 独占等待相关注意事项见上述段落
 */
wait_event_exclusive_cmd(wq_head, condition, cmd1, cmd2)
```

### 9.5.2 手工休眠

手工休眠主要工作是将内核提供的宏函数展开并按照需要的逻辑实现。
#TODO 

## 9.6 唤醒及其相关细节

```C
/**
 * @brief: 唤醒队列上的第一个独占等待的进程(如果存在)和所有非独占等待的进程
 * @return:
 * @note:
 */
wake_up(x)

/**
 * @brief: 唤醒队列上的nr个独占等待的进程(如果存在)和所有非独占等待的进程
 * @return:
 * @note:
 *     - 当nr为0时是唤醒所有独占等待的进程，而非0个
 */
wake_up_nr(x, nr)

/**
 * @brief: 唤醒队列上的所有进程
 * @return:
 * @note:
 *     - 本质上就是 wake_up_nr(x, 0)
 */
wake_up_all(x)

/**
 * @brief:
 * @return:
 * @note:
 */
wake_up_locked(x)
wake_up_all_locked(x)

/**
 * @brief: 
 *     - 唤醒队列上的第一个独占等待的进程(如果存在)和所有非独占等待的进程，
 *       并跳过所有不可中断休眠的进程
 * @return:
 * @note:
 */
wake_up_interruptible(x)

// 下面两个均为跳过所有不可中断休眠进程的版本。
wake_up_interruptible_nr(x, nr)
wake_up_interruptible_all(x)

/**
 * @brief: 
 *     - 同步版本的唤醒更倾向于在唤醒者进入休眠后，被唤醒者才会被执行；
 *       而非普通版本的立即执行。
 *     - 在并发上通常用于调度者不希望自己立即被调度处理器时使用。
 *     - 性能上的优势在于控制了被唤醒者的执行顺序，减少了上下文切换的次数。
 * @return: void
 */
wake_up_interruptible_sync(x)
```

## 9.7 非阻塞型IO

学习本章前，务必学习[[IO模型]]。

除了阻塞IO之外，Linux支持用户程序以非阻塞IO打开/操作设备。
选择是否为非阻塞IO需要<span style="background:#fff88f"><font color="#c00000">且仅能</font></span>在 `f_open` 阶段进行设置。

```C
// 只读、非阻塞
fd = open("path", O_RDONLY | O_NONBLOCK)
```

随后在内核模块中的后续操作时就应当根据是否定义了该非阻塞标志实现不同的行为。例如当应用程序请求的操作无法执行时，通常返回 `-EAGAIN` (try it again)。
只有 `read` 、 `write` 和 `open` 文件操作会收非阻塞标志的影响。

### 9.7.1 非阻塞型IO的标准语义

#### 9.7.1.1 poll函数的标准语义

Linux为[[IO模型#3 3 IO多路复用 IO Multiplexing|IO多路复用模型]]提供了 `select` 、 `poll` 、 `epoll` 三种操作接口。但是这三种操作接口本质都是调用 `file_operations` 结构体中的 `poll` 函数指针实现的。

设备驱动程序中的 `poll` 函数声明为：

```C
__poll_t poll(struct file *filep, struct poll_table_struct *wait);
```

尽管IO多路复用的实现机制较为复杂，但是在上述函数中只需要实现<font color="#c00000">如下的基本语义</font>：
0. 自己定义并管理一个等待队列  `wait_queue_head_t` 。
1. 不用管系统怎么使用poll，直接使用 `poll_wait` 将当前线程塞回上述等待队列。
2. 不用管用户具体等待的事件掩码是什么，直接返回当前可操作事件的事件掩码。
随后在驱动程序的潜在事件发生处(例如中断中)使用 `wake_up_interruptible()` <font color="#c00000">唤醒对应队列上的所有普通休眠进程</font>。

示例如下：

```C
struct mpipe_dev {
	// 读/写等待队列
	wait_queue_head_t read_queue;
	wait_queue_head_t write_queue;

	// 读/写环形缓冲区
	struct kfifo read_fifo;
	struct kfifo write_fifo;

	struct cdev cdev;
	spinlock_t lock;
	// ...
}

static int __init mpipe_init(void) { ... }
static void __exit mpipe_exit(void) { ... }

static __poll_t poll(struct file *filep, struct poll_table_struct *wait)
{
	__poll_t mask = 0;
	struct mpipe_dev *dev = file->private_data;

	// 1. 不需要管具体的系统实现，只需要将等待队列插入到
	poll_wait(filep, &dev->read_queue, wait);
	poll_wait(filep, &dev->write_queue, wait);

	// 2. 不用管用户具体在等待哪个，将设备是否可读、可写等全检查一遍并返回
	if(!kfifo_is_empty(&dev->read_fifo)) {
		// 读缓冲区非空, 可读
		mask |= POLLIN | POLLRDNORM;
	}
	if(!kfifo_is_full(&dev->read_fifo)) {
		// 写缓冲区非满, 可写
		mask |= POLLOUT | POLLWRNORM;
	}

	return mask;
}



static int mpipe_write(struct file *filep, const char __user *, size_t, loff_t *)
{
	struct mpipe_dev *dev = filep->private_data;
	// ...

	// 3. 当写入事件成功完成时, 如果缓冲区非空, 通知读队列开读。
    if (!kfifo_is_empty(&dev->read_fifo))
        wake_up_interruptible(&dev->read_queue);

	return ...;
}

static int mpipe_read(struct file *filep, char __user *, size_t, loff_t *)
{
	struct mpipe_dev *dev = filep->private_data;
	// ...
	
	// 3. 当读取事件成功完成时, 如果缓冲区非满, 通知写队列开写。
    if (!kfifo_is_full(&dev->write_fifo))
        wake_up_interruptible(&dev->write_queue);

	return ...;
}
```

至于具体的 `select` 、 `poll` 、 `epoll` 的底层原理可参见[[Linux驱动开发笔记#8 7 2 select、poll、epoll的底层原理和数据结构]]。
简单的机制总结可见：[[Linux内核原理及其开发/应试笔记与八股#^uhjg4c]]。

上述的poll函数，除了用于为 `select` 、 `poll` 、 `epoll` 三种操作接口提供后端外，还需要保证<font color="#c00000">在文件的不同状态时</font>与 `read` 、 `write` 函数<span style="background:#fff88f"><font color="#c00000">保持对应匹配的行为</font></span>(<font color="#c00000">即使当前文件被使用阻塞IO打开</font>)，因为对应用程序而言，<span style="background:#fff88f"><font color="#c00000">poll等函数(select、epoll，下同)的返回结果必须保证能够明确接下来的read和write函数是否会遭到阻塞</font></span>。
具体可见后续章节。

#### 9.7.1.2 read函数的标准语义

从设备读取数据时可以分为如下三种情况进行讨论：
1. <font color="#c00000">如果输入缓冲区有数据</font>：即可读数据大于等于1byte，则read函数应当立即返回，并读取至少一个字节。
2. <font color="#c00000">如果输入缓冲区没有数据</font>：则：
	1. <font color="#c00000">若未设置为非阻塞IO</font>：则read函数必须阻塞直到至少有一个字节到达。
	2. <font color="#c00000">若设置为非阻塞IO</font>：则：
		- read函数必须立即返回，返回值为 `-EAGAIN` 。
		- <font color="#c00000">poll函数必须报告设备不可读</font>。
3. <font color="#c00000">若到达文件末尾</font>：则：
	- read函数必须立即返回0。
	- <font color="#c00000">无论是否为非阻塞IO</font>，poll函数应当报告 `POLLHUP` 。

#### 9.7.1.3 write函数的标准语义

向设备写入数据时可以分为如下三种情况进行讨论：
1. <font color="#c00000">如果输出缓冲区有空间</font>：即可写数据大于等于1byte，则：
	- write函数必须立刻返回，并至少接收一个字节。
	- poll函数应当报告设备可写。
2. <font color="#c00000">如果输出缓冲区已满</font>：则：
	1. <font color="#c00000">若未设置为非阻塞IO</font>：则write函数必须阻塞直到至少有一个字节可写。
	2. <font color="#c00000">若设置为非阻塞IO</font>：则：
		- write函数必须立即返回，返回值为 `-EAGAIN` 。
		- <font color="#c00000">poll函数必须报告设备不可写</font>。
3. <font color="#c00000">若输出设备无剩余可写空间</font>：例如磁盘已满，则<font color="#c00000">write应当立即返回并报告</font> `-ENOSPC` (无剩余空间)，<font color="#c00000">无论设备是否为阻塞IO</font>。

此外，还需要注意：
1. <font color="#c00000">永远不能让write调用等待缓冲区中的数据写入设备</font>，无论是否为阻塞IO。正是由于<font color="#c00000">poll等函数可以用于保证接下来的write函数不会被阻塞</font>。而上述的poll与write之间的行为必须保证联动，<font color="#c00000">上述poll函数表示可写时，write必须不可被阻塞</font>，也不能等待缓冲区数据写入设备。
2. 如果需要保证数据完整性，则可以实现 `fsync` 方法，<span style="background:#fff88f"><font color="#c00000">fsync方法会阻塞直到缓冲区数据被写入设备</font></span>，<font color="#c00000">无论该IO是否被设置为阻塞IO</font>。
3. 可移除设备应当实现 `fsync` 方法。

#### 9.7.1.4 fsync函数的标准语义

`fsync` 函数的声明为：

```C
int fsync(struct file *filep, loff_t start, loff_t end, int datasync);
```

其中：
- `struct file *filep` 为指向文件的指针。
- `loff_t start` ：同步操作的起始位置，是一个64位的偏移量。
- `loff_t end` ：同步操作的结束位置，同样是一个64位的偏移量。
- `int datasync` ：用来指示同步操作的类型，如果 `datasync` 非零，则仅同步文件的数据部分，而不同步文件的元数据(如最后修改时间等)。如果为零，则同时同步数据和元数据。
该函数对操作的时间等没有具体的要求，正常实现即可。
在大多数情况下，该函数不会出现在字符设备中。但是在块设备中通常都会出现。

#### 9.7.1.5 open函数的标准语义

#TODO 


### 9.7.2 select、poll、epoll的底层原理和数据结构

详见[[IO多路复用接口(select、poll、epoll)]]。

<font color="#c00000">简单总结版本</font>：[[Linux内核原理及其开发/应试笔记与八股#^uhjg4c]]。

### 9.7.3 异步通知

本章节所讲述的IO模型为[[IO模型#3 4 信号驱动型IO Signal Driven IO|信号驱动型IO]]。

用户态APP启用异步通知的基本步骤为：
1. 使用 `sigaction` 或 `signal` 注册需要监听的信号及其回调函数。通常推荐使用前者。
2. 将文件的所有者设置为当前进程，随后的内核通知的目标进程就会被设置为该进程。
3. 启用异步通知。
4. 在回调函数中对IO进行处理。
示例如下：

```C
// 1. 注册监听信号及其回调函数
//    这里使用signal只是因为使用起来比较简单和简洁，实际使用中应使用sigaction。
signal(SIGIO, &callback);

// 2. 设置文件所有者为当前进程
fcntl(fd, F_SETOWN, getpid());

// 3. 启用异步通知
//    获取该文件原先的文件状态标签，添加异步通知功能，再设置回去
f_flags = fcntl(fd, F_GETFL, 0);
fcntl(fd, F_SETFL, flags | O_ASYNC);

// 4. 定义回调函数, 略
...
```

通常来说，用户应假设只有socket和terminal具有异步通知能力。

上述用户态操作对应的内核驱动程序的操作分别为：

| <center>用户态操作</center> | <center>内核操作</center>           | <center>驱动程序操作</center>                                                                                       |
| ---------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| 为文件设置回调函数              | 内核会将 `filep->f_owner` 设置为目标PID。 |                                                                                                               |
| 为文件设置所有者               |                                 |                                                                                                               |
| 启用异步通知                 |                                 | <span style="background:#fff88f"><font color="#c00000">只要当FASYNC标记被改变</font></span>，<br>驱动程序的 `fasync` 操作被调用。 |
| 调用 `close` 操作          |                                 | 调用驱动程序的 `fasync` ，将该 `struct file*` 移除通知队列                                                                    |

`fasync` 函数的声明为：

```C
int fasync(int fd, struct file *filp, int on);
```

内核中为了方便该函数的实现，提供了如下的辅助函数：
- `int fasync_helper(int fd, struct file * filp, int on, struct fasync_struct **fapp)` ：
	- 该函数帮助驱动程序向 `fasync_struct` 中<font color="#c00000">添加或移除节点</font>。当 `on == 0` 时移除， `on == 1` 时添加。
	- 在调用该函数时，前三个参数与 `fasync` 函数中传来的一致，第四个参数为驱动程序所管理的 `fasync_struct` 链表。
	- 其返回值：
		- 小于0时表示函数执行错误
		- 等于0时表示函数并为对链表进行更改
		- 大于0时表示成功添加或删除队列中的条目
- `void kill_fasync(struct fasync_struct **fp, int sig, int band)` ：
	- <font color="#c00000">该函数应当在设备可以访问时由驱动程序主动发出</font>，用于向监听的进程发出信号。
	- 其参数：
		- `struct fasync_struct **fp` ：驱动程序所管理的 `fasync_struct` 链表
		- `int sig` ：驱动程序要发出的信号
		- `int band` ：

## 9.8 文件操作的用户态和内核态标准语义汇总

### 9.8.1 open操作

#### 9.8.1.1 用户态语义


#### 9.8.1.2 系统调用操作(sys_open)

系统调用 `sys_open` 的内部处理详见：[[基础IO打开关闭(open.c)#^qyilk5]]。
- 该处理可以简述如下： ^dttvnu
	- 

#### 9.8.1.3 内核态语义


### 9.8.2 close函数

#### 9.8.2.1 用户态语义

POSIX的用户态 `close` 语义可见：[[IEEE Std 1003.1™-2017 学习笔记#^s5pcbs]]。



#### 9.8.2.2 系统调用操作(sys_close)

系统调用 `sys_close` 的内部处理详见：[[基础IO打开关闭(open.c)#^4b5xl4]]。
- 该处理可以简述如下： ^dqyd87
	1. 使用用户提供的整数类型的 `fd` 文件号，从 `fd table` 中找到对应的内核中的文件对象 `struct file` 。
	2. 调用




### 9.8.3 read函数

#### 9.8.3.1 用户态语义


#### 9.8.3.2 系统调用操作(sys_read)

系统调用 `sys_read` 的内部处理详见：[[基础IO读写(read_write.c)#^4c1l78]]。
- 该处理可以简述如下： ^rhxomn
	- 


#### 9.8.3.3 内核态语义(f_op->read)



## 9.9 高级字符设备驱动程序最终Demo ^qdfcky

该Demo为一个简易的IPC管道( `mpipe` )，其具备如下基本特性：
- 基本设备属性：
	- 该驱动程序为字符设备，挂载到文件系统的 `/dev/mpipe` 路径。
	- 该设备使用动态分配设备号。
	- 每个 `mpipe` 均有一个唯一的 `mpipe_id` 。
	- 在每个 `mpipe` 进行连接之前，所有的读写操作均不可正常进行。
- 连接操作：
	- 在 `mpipe` 连接时，双方必须知晓对方的 `mpipe_id` 。
	- 设置目标的 `mpipe_id` 的操作为非阻塞操作，只要 `mpipe_id` 合法即成功。
	- 在设置好目标 `mpipe_id` 后，应当使用 `ioctl` 轮询连接状态。
	- 当且仅当双方的目标 `mpipe_id` 均匹配，管道才会被成功连接。
- 断开操作：
	- 当一方申请断开，则双方完成当前mpipe读写指令后立即断开。
- IO操作：
	- 支持阻塞IO与非阻塞IO，且符合标准语义。
	- 支持的IO操作有：
		- `open`
		- `close`
		- `read`
		- `write`
		- `poll` 类操作
		- `signal` 、 `sigaction`

### 9.9.1 初步考虑数据结构

#### 9.9.1.1 管道基础信息结构体( `struct mpipe_info` )

在内核驱动程序设计中，通常会使用 `filep->private_data` 使得驱动程序可以存储与用户态 `fd` 相绑定的数据信息。
在本驱动程序设计中，主要用于存储与单端管道相关的数据结构。

#### 9.9.1.2 链表结构体( `struct mpipe_list` )




#### 9.9.1.3 考虑管道状态表示

| <center>状态</center> | <center>判定方式</center>                                     |
| ------------------- | --------------------------------------------------------- |
| 管道被禁用               | `mpipe_info.target_mpipe_id == MPIPE_STATUS_DISABLED`     |
| 管道等待连接              | `mpipe_info.target_mpipe_id == MPIPE_STATUS_DISCONNECTED` |
| 管道已连接               | `mpipe_info.partner_pipe != NULL`                         |




### 9.9.2 初步考虑互斥并发管理

#### 9.9.2.1 基础互斥并发管理

针对上述结构体的操作可以考虑如下两种并发管理：
1. <u>整个驱动程序共用一个锁</u>。Linux的ppdev即使用此方案( `/drivers/char/ppdev.c` )
2. <u>分别对链表整体结构和链表各节点进行加锁</u>。
从并发能力来讲，选项2更为优秀。
但是由于其实现较为繁琐，且需要考虑更多的互斥问题，因此本笔记除了本章节使用方案2以外，后续章节均使用方案1以简化实现方式。

#### 9.9.2.2 死锁预防

在操作系统的学习中我们知道了死锁产生的四个必要条件以及死锁预防的方式：

![[第二章 进程与线程#^p2qb7k]]
![[第二章 进程与线程#2 4 2 死锁的预防]]

而在上述的并发互斥管理中，需要在如下的情况下考虑死锁预防：
1. 必须避免链表锁( `list_spin` )和各节点锁( `mpipe_info.info_spin` )之间的循环等待。<font color="#c00000">即保证先对链表锁加锁，才能对各节点锁加锁</font>。
2. 必须避免多个节点锁( `mpipe_info.info_spin` )之间的循环等待。<font color="#c00000">即保证现对ID小的基础信息结构体加锁，再对ID大的基础信息结构体加锁</font>。

### 9.9.3 初步考虑连接建立

如上述管道的基本特性，两个管道之间要建立连接需要其目标 `mpipe_id` 均为对方的 `mpipe_id` 。则需要考虑如下的几个场景：
1. 若当前管道未设置目标 `mpipe_id` ，则设置该目标id，同时检测对方的目标id是否为当前管道。
	1. 如果不是当前管道则什么都不做。
	2. 如果是当前管道，则：
		1. 检查是不是自己与自己连接，如果是则需要避免重复加锁带来的死锁问题。
		2. 建立连接，并通知等待等待管道连接的队列执行唤醒。
2. 若当前管道设置了目标管道id：
	1. 若与原先id相同，则什么都不做。
	2. 若与原先id不同，则检测是否需要断开原连接，并设置新的目标id，随后检查对方的目标id是否为当前管道。
		1. 如果不是则..
		2. 如果是则..
3. 其他情况。

### 9.9.4 考虑文件关闭操作

#### 9.9.4.1 考虑如下场景

由于本子章节并不针对于上述假象设备 `mpipe` ，因此本子章节的设备名均命名为 `mdev` 。

##### 9.9.4.1.1 场景一：正在处理read的过程中，close被调用并执行完毕

在内核中的驱动正在响应用户的操作请求<font color="#c00000">的</font><span style="background:#fff88f"><font color="#c00000">过程中</font></span>， `f_op->release` 被调用，那么仍在处理的操作请求如何完成？
1. 明显地，直接在 `f_op->release` 中释放 `struct mdev_info` 将无法保证正在执行的操作会被顺利完成，例如下方代码中，在完成 `mdev_read` 中的 `do_operation1` 后被下处理器，并完成 `mdev_release` 函数，随后 `do_operation2` 就会触发错误：
```C
static ssize_t mdev_read(struct file *filep, char __user *buf, size_t count, loff_t *ppos)
{
	// 1. 获取info数据结构
	struct mdev_info *mdev_info_p = filep->private_data;

	// 2. 执行操作1
	do_operation1(mdev_info_p);

	// 3. 执行操作2
	do_operation2(mdev_info_p);

	return ...;
}

static int mdev_release(struct inode *node, struct file *filep)
{
	// [错误示范] 直接释放相关数据结构
	// 1. 获取info数据结构
	struct mdev_info *mdev_info_p = filep->private_data;

	// 2. 回收数据结构
	kfree(mdev_info_p);

	return 0;
}
```
2. 则此时可以考虑使用计数器的方式代替直接的 `free` 操作：
```C
struct mdev_info {
	// ...

    // ref counter for mdev_info, used to complete incomplete requests.
    atomic_t ref_counts;
};

/**
 * @brief: add references to mdev_info.
 */
static void mdev_info_get(struct mdev_info *info)
{
	atomic_inc(&info->ref_counts);
}

/**
 * @brief: remove the reference to mpipe_info, andelease the memory space
 *          when the last reference is released.
 */
static void mdev_info_put(struct mdev_info *info)
{
    if(atomic_dec_and_test(&info->ref_counts))
    {
        vfree(info);
    }
}

static int mdev_open(struct inode *node, struct file *filep)
{
	//...

	// success.
	// 增加对该结构体的引用计数
	mdev_info_get(mdev_info);

	return 0;
}

static ssize_t mdev_read(struct file *filep, char __user *buf, size_t count, loff_t *ppos)
{
	// 1. 获取info数据结构
	struct mdev_info *mdev_info_p = filep->private_data;

	// 2. 增加引用计数器
	mdev_info_get(mdev_info);

	// 3. 执行操作1
	do_operation1(mdev_info_p);

	// 4. 执行操作2
	do_operation2(mdev_info_p);

	// 5. 解除引用奇数
	mdev_info_put(mdev_info);

	return ...;
}

static int mdev_release(struct inode *node, struct file *filep)
{
	// [错误示范] 普通计数器
	// 1. 获取info数据结构
	struct mdev_info *mdev_info_p = filep->private_data;

	// 2. 解除驱动对该info的引用计数
	mdev_info_put(mdev_info_p);

	return 0;
}
```
3. 但是依旧有问题，例如：
	1. 用户发起read请求，并执行到 `mdev_read` 的 `struct mdev_info *mdev_info_p = filep->private_data;` 处被下处理器，<font color="#c00000">此时引用计数器并未增加</font>。
	2. 随后内核处理用户的文件关闭请求，并完成 `mdev_release` 的执行。<font color="#c00000">此时引用计数器被成功归0</font>， `struct mdev_info` <font color="#c00000">被成功释放</font>。
	3.  `mdev_read` <font color="#c00000">继续执行</font>，<span style="background:#fff88f"><font color="#c00000">此时计数器为-1</font></span>，<font color="#c00000">且需要访问的</font> `struct mdev_info` <span style="background:#fff88f"><font color="#c00000">已被清空</font></span>。错误发生。

针对这个问题，则可以考虑使用[[引用计数器refcount_t(refcount.h)|引用计数器]]管理 `mdev_info` 解决，详见相关API。

### 9.9.5 考虑断开连接操作




### 9.9.6 最终驱动程序和测试程序

则最终Demo程序如下：

```C

```

其用户态测试程序为：

```C

```

# 10 时间、延迟及延缓操作

## 10.1 度量时间差(以系统启动时间为基准)

### 10.1.1 jiffies计数器

#### 10.1.1.1 jiffies_64机制

内核中会定义一个硬件的时钟中断，该中断频率通常为1000hz<font color="#7f7f7f">(软件仿真器中是24hz)</font>，该值不为固定值，可以在编译内核时设置，因此进行内核开发时不应当指定固定值，而应当通过API来获取。且在修改内核中断频率后，必须重新编译并使用新的内核模块。
该值可在内核态代码中访问，其被定义在 `<linux/param.h>` 中的 `HZ` 中。

内核中的变量 `jiffies_64` 在系统启动时会被置0，并当上述时钟中断发生时计数器会+1。该计数器在32位和64位系统中均为64位。

<font color="#c00000">在实际开发中，应当使用</font> `jiffies` <font color="#c00000">变量</font>，其为 `unsigned long` 类型，其具体位数可见[[Linux驱动开发笔记#2 2 1 1 不同架构处理器下的数据类型大小|2.2.1.1 不同架构处理器下的数据类型大小]]。在64位处理器上这两个变量其实是同一个，对该变量的访问也是原子的。在32位处理器上，该值是 `jiffies_64` 的低32位，<font color="#c00000">且访问非原子</font>。因此：
- 访问 `jiffies_64` 应使用统一的接口:
```C
#include <linux/jiffies.h>
u64 get_jiffies_64(void);
```
- 访问 `jiffies` 时可以直接访问。

#### 10.1.1.2 32位CPU下的jiffies及其溢出问题

在32位平台下，1000hz中断时， `jiffies` 大约50天会溢出一次。但是内核态代码仍然应当谨慎处理该问题。
而想只用一个32位的计数器完全从根本上解决溢出问题是不现实的(例如32位的 `jiffies_a` 于数百天以前记录，此时和当前 `jiffies` 比较大小或者计算时间差)，因此其被如下设计：
1. 32位的 `jiffies` <font color="#c00000">应当至少可以满足</font>比较<span style="background:#fff88f"><font color="#c00000">至多数秒或数天</font></span>间隔的时间戳。
2. 当比较<span style="background:#fff88f"><font color="#c00000">可能接近或者大于溢出周期</font></span>的时间戳时应当考虑使用 `jiffies_64` 。
因此，当<font color="#c00000">比较或计算</font><span style="background:#fff88f"><font color="#c00000">远低于半个溢出周期</font></span><font color="#c00000">的时间戳时</font>可以考虑使用如下的函数：

```C
#include <linux/jiffies.h>

// 宏函数, 当a比b靠后时返回真, 表达式为((long)(b) - (long)(a) < 0))
int time_after(unsigned long a, unsigned long b);
// 宏函数, 当a比b靠前时返回真, 表达式为((long)(a) - (long)(b) < 0))
int time_before(unsigned long a, unsigned long b);
// 宏函数, 当a比b靠后或相等时返回真, 表达式为((long)(b) - (long)(a) <= 0))
int time_after_eq(unsigned long a, unsigned long b);
// 宏函数, 当a比b靠前或相等时返回真, 表达式为((long)(a) - (long)(b) <= 0))
int time_before_eq(unsigned long a, unsigned long b);
```

其原理为将 `a` 和 `b` 强制转换为 `signed long` 后进行比较，本质依赖[[CPP/应试笔记与八股#2 7 讲一讲负整数在计算机中是如何存储的 p7e9a4|负数补码原则]]，以char为例，其无符号和有符号之间的强制转换关系如下：

| `unsigned long` | `signed long` |
| :-------------: | :-----------: |
|        0        |       0       |
|        1        |       1       |
|        2        |       2       |
|        3        |       3       |
|       ...       |      ...      |
|       127       |      127      |
|       128       |     -128      |
|       129       |     -127      |
|       130       |     -126      |
|       ...       |      ...      |
|       254       |      -2       |
|       255       |      -1       |
|        0        |       0       |
|        1        |       1       |

例如：
- 当 `a = 254` ，随后计数器自增溢出到 `1` 时b取值，此时运算 `(char)(b) - (char)(a) = 1 - (-2) = 3` ，可以正常运算和判定先后。
- 但是当 `a` 、 `b` <span style="background:#fff88f"><font color="#c00000">时差超过半个计数周期并发生溢出时</font></span>，<font color="#c00000">运算就不再准确</font>：
	- `a = 254`
	- 随后130个计数后获取 `b = 128`
	- 此时 `(char)(b) - (char)(a) = -128 - (-2) = -126` 判定不再准确

#### 10.1.1.3 jiffies与用户态时间互转

```C
#include <linux/time.h>

unsigned long timespec_to_jiffies(struct timespec *value);
void jiffies_to_timespec(unsigned long jiffies, struct timespec *value);
unsigned long timeval_to_jiffies(struct timeval *value);
void jiffies_to_timeval(unsigned long jiffies, struct timeval *value);
```

### 10.1.2 平台特有高精度计时寄存器

#### 10.1.2.1 通用平台

linux内核为所有平台都提供了访问CPU时钟周期数的API，在支持的平台上会返回正确宽度的 `cycles_t` ，但是在不支持的平台上返回结果恒为0。

```C
#include <linux/timex.h>
cycles_t get_cycles(void);
```

#### 10.1.2.2 x86

在Pentium后的所有x86和x86_64的CPU上均会有一个TSC计数器(Timestamp counter)，该计数器会记录CPU的时钟周期数，可以通过如下方式访问：

```C
#include <asm/msr.h>

// 宏, 将64位的计数器原子地读取到两个32位的变量中
rdtsc(low32, high32);
// 宏, 只原子地读取低32位
rdtscl(low32);
// 宏, 将64位计数器原子地读取到一个64位变量中
rdtscll(var64);
```

## 10.2 获取当前时间(绝对时间)

在大多数情况下，内核只需要处理 `jiffies` 就可以满足需求，并且通常会将年月日时分秒的处理留给用户空间进行处理，但是内核依旧提供了一些绝对时间的处理方法。

### 10.2.1 年月日时分秒转jiffies

```C
#include <linux/time.h>
unsigned long mktime(unsigned int year, unsigned int mon,
						unsigned int day, unsigned int hour,
						unsigned int min, unsigned int sec);
```

### 10.2.2 获取UNIX时间戳(以1970年为起始)

```C
#include <linux/time.h>

// struct timeval可以记录微秒(ms)级别的时间
// 且在许多平台上该API也有微秒级别的精度
void do_gettimeofday(struct timeval *tv);
```

```C
#include <linux/time.h>

// struct timespec可以记录纳秒(ns)级别的时间
// 但是实际上也只有时钟滴答的精度(jiffies)
struct timespec current_kernel_time(void);
```

## 10.3 延迟执行

在考虑使用延迟执行时，需要根据延迟时间分别考虑使用的API：
- 当延迟时间大于时钟滴答( `jiffies` )，且<font color="#c00000">可以以一个时钟滴答为单位</font>(<font color="#c00000">通常为若干毫秒</font>)进行延迟时，此时应优先考虑使用 `jiffies` 等待。
- 当时间延迟小于等于一个时钟滴答，或不能以时钟滴答为单位进行等待时，此时应当使用普通等待。

### 10.3.1 jiffies等待

#### 10.3.1.1 忙等(不推荐)

直接使用：

```C
while(time_before(jiffies, target))
	cpu_relax();
```

即可，需要注意的是：
1. <span style="background:#fff88f"><font color="#c00000">在进入该循环之前不可禁止中断</font></span>，不然 `jiffies` 永远无法得到更新，直接陷入死机。
2. 在对应平台上 `cpu_relax()` 会做出不同的行为(例如在支持超线程的CPU上会让出处理器给其他线程)，但是行为具体做了什么不重要，因为不推荐使用此方式。

#### 10.3.1.2 让出处理器(不推荐)

```C
while(time_before(jiffies, target))
	shedule();
```

除了<font color="#c00000">不允许关闭中断</font>外通常不会有太多问题，但<font color="#c00000">依旧不是最好的解决方案</font>。当系统中有别的可运行进程时，该代码可以正常让出处理器；但是当系统中仅剩这一个可运行进程或低负荷情况下， `shedule()` 并不能有效地让出处理器，此时又变成忙等状态。

#### 10.3.1.3 超时(推荐)

直接使用休眠章节提到的 `wait_event_*timeout` 函数即可，API如下：

```C
#include <linux/wait.h>

wait_queue_head_t wait;

/**
 * @brief: 休眠直到condition为true，或者超时(以jiffy表示)时中断休眠。
 * @return:
 *     - 当超时后condition为true返回0
 *     - 当超时后condition为false返回1
 *     - 超时前condition为true则返回剩余jiffy数(大于等于1)
 */
wait_event_timeout(wq_head, condition, timeout)


/**
 * @brief: 休眠直到condition为true，或者被信号中断休眠，或者超时(以jiffy表示)时中断休眠。当其被信号打断时返回值为非零。
 * @return:
 *     - 当超时后condition为true返回0
 *     - 当超时后condition为false返回1
 *     - 超时前condition为true则返回剩余jiffy数(大于等于1)
 */
wait_event_interruptible_timeout(wq_head, condition, timeout)
```

在使用上述API进行等待时只需要把 `condition` 填写为 `0` 并等待超时即可。
本方法与上述让出处理器的方法的区别仅在于本方法的API还额外设置了任务状态( `TASK_INTERRUPTIBLE` / `TASK_UNINTERRUPTIBLE` )。

### 10.3.2 绝对时间等待

```C
#include <linux/delay.h>
void ndelay(unsigned long nsecs);
void udelay(unsigned long usecs);
void mdelay(unsigned long msecs);
```

上述函数的实际实现包含在 `<asm/delay.h>` 中，且<font color="#c00000">除了udelay以外的两个函数</font><span style="background:#fff88f"><font color="#c00000">可能并未被定义</font></span>。而 `udelay` <font color="#c00000">一定会被提供</font>并且其最终的延迟时间一定可以达到目标延迟时间或更长。
此外，内核还未 `udelay` 和 `ndelay` 中能接收的参数值添加了上限，当值过大时会提示 `__bad_udelay` 。
<font color="#c00000">注意</font>：<span style="background:#fff88f"><font color="#c00000">上述三个函数均为忙等待函数</font></span>，非忙等待函数为如下几个函数：

```C
#include <linux/delay.h>

// 可以被中断的休眠，当进程被提前唤醒时，其返回值为提前唤醒的毫秒数。
unsigned long msleep_interruptible(unsigned int millisecs);

// 非忙等，但是也不可中断休眠
void ssleep(unsigned int seconds);
```

## 10.4 内核定时器

内核定时器通常有如下的典型应用场景(实际上并不局限于此)：
1. 对于没有提供外部中断功能的硬件设备，可以使用内核定时器定时轮询。
2. 在完成 `fops->close` 等操作时，使用内核定时器异步完成。

<span style="background:#fff88f"><font color="#c00000">内核定时器是一种软件中断</font></span>，<font color="#c00000">这些代码位于中断上下文中而非进程上下文</font>，此时的注意事项可见[[Linux驱动开发笔记#^fw453g|中断上下文的注意事项]]：
![[Linux驱动开发笔记#13 1 2 中断上下文中的注意事项 fw453g]]

此外内核还提供了一些API可以用于查询当前上下文的状态，API及不同上下文的注意事项可见[[Linux驱动开发笔记#^h05ata|当前上下文状态与注意事项]]。

内核定时器的几个重要特性：
1. 允许任务将自己注册在稍后一些的时间上重新运行，因为每个 `timer_list` 结构都会在运行之前从活动定时器链表中移走。
2. <font color="#c00000">定时器函数</font><span style="background:#fff88f"><font color="#c00000">默认</font></span><font color="#c00000">会在注册自己的CPU上重新运行</font>，这样可以尽可能保持缓存的局域性。****
3. 即使在单处理器上，定时器也是竞态的潜在来源。

### 10.4.1 内核定时器数据结构定义

内核定时器的数据结构定义如下：

```C
struct timer_list {
	/*
	 * All fields that change during normal runtime grouped to the
	 * same cacheline
	 */
	struct hlist_node	entry;
	unsigned long		expires;
	void			(*function)(struct timer_list *);
	u32			flags;

#ifdef CONFIG_LOCKDEP
	struct lockdep_map	lockdep_map;
#endif
};
```

其中，上述结构体中：
- `struct hlist_node entry` ：
	- 功能含义：哈希链表节点，根据超时值(`expires`)进行hash
	- 维护方：内核自动维护，驱动不可访问或修改
- `unsigned long expires` ：
	- 功能含义：定时器超时时的 `jiffies` 值
	- 维护方：
		- <font color="#c00000">驱动在初始化之前必须配置</font>，<font color="#c00000">配置后不允许直接修改</font>
		- 内核可能会对临近超时的定时器进行一些优化和分组，但是驱动在此阶段只读
- `void (*function)(struct timer_list *)` ：
	- 功能含义：当系统时间 `jiffies >= expires` 时，内核<font color="#c00000">在中断上下文</font>调用的函数，参数为当前定时器的指针
	- 维护方：<font color="#c00000">驱动必须实现</font>
- `u32 flags` ：
	- 功能含义：存储定时器的状态标志位。这些标志位由内核和驱动共同使用，用于控制定时器的状态和行为。常用的标志有：
		- `TIMER_DEFERRABLE` ：表示可延迟的定时器，允许内核为节能等因素推迟该定时器
		- `TIMER_PINNED` ：将定时器绑定到当前CPU，即加载到当前CPU的定时器队列中
		- `TIMER_MIGRATING` ：内核内部使用，表示定时器正在CPU之间迁移
	- 维护方：驱动可通过 `timer_set_flags()` 设置
- `struct lockdep_map lockdep_map` ：
	- 功能含义：内核锁验证器成员，可用于检出锁依赖和死锁问题。
	- 维护方：在 `CONFIG_LOCKDEP` 开启时，内核会自动配置。

### 10.4.2 内核定时器相关API

#### 10.4.2.1 静态初始化

```C
#include <linux/timer.h>

#define __TIMER_INITIALIZER(_function, _flags) {		\
		.entry = { .next = TIMER_ENTRY_STATIC },	\
		.function = (_function),			\
		.flags = (_flags),				\
		__TIMER_LOCKDEP_MAP_INITIALIZER(FILE_LINE)	\
	}

#define DEFINE_TIMER(_name, _function)				\
	struct timer_list _name =				\
		__TIMER_INITIALIZER(_function, 0)
```

其中：
- 在调用时，使用 `DEFINE_TIMER` 定义定时器变量名并传入目标函数即可。
- 随后需要使用 `add_timer` 将该定时器加入到内核中。

#### 10.4.2.2 动态初始化

- 动态初始化(头文件 `timer.h` )：
```C
#include <linux/timer.h>

/**
 * timer_setup - prepare a timer for first use
 * @timer: the timer in question
 * @callback: the function to call when timer expires
 * @flags: any TIMER_* flags
 *
 * Regular timer initialization should use either DEFINE_TIMER() above,
 * or timer_setup(). For timers on the stack, timer_setup_on_stack() must
 * be used and must be balanced with a call to destroy_timer_on_stack().
 */
#define timer_setup(timer, callback, flags)			\
	__init_timer((timer), (callback), (flags))

#define timer_setup_on_stack(timer, callback, flags)		\
	__init_timer_on_stack((timer), (callback), (flags))
```

其中：
- 通常的定时器使用 `DEFINE_TIMER` 和 `timer_setup` 即可。
- 如需使用栈上定时器则需要使用 `timer_setup_on_stack` ，且有如下的注意事项：
	- 栈上定时器的生命周期受限于当前函数栈帧，必须在函数返回前删除并释放定时器，仅适用于短期定时操作。
	- 释放栈上定时器的操作为 `destroy_timer_on_stack` ，在某些内核配置模式下，未调用该释放操作可能会导致内存泄漏。
- 上述两个函数的返回值为 `void` 。
- 随后需要使用 `add_timer` 将该定时器加入到内核中。

#### 10.4.2.3 添加定时器

添加定时器到内核的定时器模块中：

```C
void add_timer(struct timer_list *timer);
void add_timer_on(struct timer_list *timer, int cpu);
```

其中：
- 在定时器对象初始化完成后即可使用 `add_timer*` 函数将定时器加入到内核中，其中：
	- `add_timer` 会将定时器加入到当前CPU中。
	- `add_timer_on` 会将定时器加入到指定CPU中，可以减少跨CPU的中断和上下文切换开销(例如实现NUMA架构下的局部性优化)。

#### 10.4.2.4 更新(修改)定时器到期时间

```C
int mod_timer(struct timer_list *timer, unsigned long expires);
int mod_timer_pending(struct timer_list *timer, unsigned long expires);
```

其通常用于延长定时器的到期时间。

#### 10.4.2.5 删除定时器

```C
int del_timer(struct timer_list *timer);
int del_timer_sync(struct timer_list *timer);
```

其中：
- `del_timer_sync` 可以确保该函数在返回时没有任何CPU在运行定时器的回调函数，在SMP系统上可以用于避免竞态等。

#### 10.4.2.6 查询定时器是否在等待调度(是否在挂起状态)

```C
int timer_pending(const struct timer_list * timer);
```

其返回值：
- `1 if the timer is pending, 0 if not.`

### 10.4.3 内核定时器的实现(了解)

#TODO 

## 10.5 tasklet(即将被移除) ^meiuw1

tasklet机制即小任务机制，其特性有：
1. <font color="#c00000">本质上基于软中断实现</font>，<span style="background:#fff88f"><font color="#c00000">始终在中断期间运行</font></span>，具体注意事项应见[[Linux驱动开发笔记#12 1 2 中断上下文中的注意事项 fw453g|中断上下文中的注意事项]]
2. <font color="#c00000">其通常在中断中被创建</font>，<span style="background:#fff88f"><font color="#c00000">用于处理中断下半部</font></span>，主要是为了：
	1. <font color="#c00000">快速让出硬中断</font>，<span style="background:#fff88f"><font color="#c00000">使硬件中断可以快速的接收下一个信号</font></span>
	2. <font color="#c00000">要求任务有极高的响应速度</font>(因此不能用工作队列)
3. 相较于定时器，开发者不能要求tasklet在给定的时间运行。
4. tasklet可以注册自己本身。
5. tasklet有高低优先级特性，高优先级的tasklet会被先执行。
6. <font color="#c00000">tasklet在系统负载不重时立刻执行，且始终不会晚于下一个定时器滴答</font>。
7. tasklet可以和别的tasklet并发执行，但<span style="background:#fff88f"><font color="#c00000">同一个tasklet自身</font></span><font color="#c00000">只能串行执行</font>(指的是自己注册自己的运行情况)，即同一个tasklet不会在多个处理器上同时运行。
8. tasklet<font color="#c00000">内部有一个禁用-启用次数计数器</font>，当且仅当计数器为0时会被调度。

tasklet其<font color="#c00000">最根本的功能是可以将部分或后续操作异步的进行处理</font>，其常用使用流程：
1. 定义 `tasklet_struct` 的变量。
2. 初始化tasklet，并填入回调函数，参数等。
3. 使用 `tasklet_schedule` 将回调函数中的操作放入异步处理。

因此 `tasklet` 要求开发者：
1. 遵守中断上下文中的注意事项
2. 快速执行、快速结束

经典例子：

```C
void my_tasklet_handler(unsigned long data) {
    // 在中断外完成中断处理的后半部分...
}

// 某中断处理函数
static irqreturn_t my_interrupt_handler(int irq, void *dev_id) {
    // 快速读取设备状态寄存器(关键操作)
    device_status = readl(DEVICE_STATUS_REG);
    printk(KERN_INFO "Interrupt handled on CPU %d: Device status = 0x%x\n",
           smp_processor_id(), device_status);

    // 调度 tasklet 处理非关键操作...
    tasklet_schedule(&my_tasklet);

    return IRQ_HANDLED;
}
```

### 10.5.1 数据结构定义


```C
#include <linux/interrupt.h>

/* Tasklets --- multithreaded analogue of BHs.

   This API is deprecated. Please consider using threaded IRQs instead:
   https://lore.kernel.org/lkml/20200716081538.2sivhkj4hcyrusem@linutronix.de

   Main feature differing them of generic softirqs: tasklet
   is running only on one CPU simultaneously.

   Main feature differing them of BHs: different tasklets
   may be run simultaneously on different CPUs.

   Properties:
   * If tasklet_schedule() is called, then tasklet is guaranteed
     to be executed on some cpu at least once after this.
   * If the tasklet is already scheduled, but its execution is still not
     started, it will be executed only once.
   * If this tasklet is already running on another CPU (or schedule is called
     from tasklet itself), it is rescheduled for later.
   * Tasklet is strictly serialized wrt itself, but not
     wrt another tasklets. If client needs some intertask synchronization,
     he makes it with spinlocks.
 */
struct tasklet_struct
{
	struct tasklet_struct *next;
	unsigned long state;
	atomic_t count;
	bool use_callback;
	union {
		void (*func)(unsigned long data);
		void (*callback)(struct tasklet_struct *t);
	};
	unsigned long data;
};
```

注意：
- `tasklet` 不需要也不能手动配置其成员，其应当使用对应API初始化。

### 10.5.2 tasklet相关API

#### 10.5.2.1 初始化tasklet

```C
void tasklet_init(struct tasklet_struct *t,
	void (*func)(unsigned long), unsigned long data);
```

本函数的功能是将回调函数、参数填入tasklet对象。

#### 10.5.2.2 手动调度tasklet

手动调度tasklet(异步，<font color="#c00000">调用后会立即返回</font>)：

```C
void tasklet_schedule(struct tasklet_struct *t);
```

#### 10.5.2.3 禁用tasklet

```C
void tasklet_disable(struct tasklet_struct *t);
void tasklet_disable_nosync(struct tasklet_struct *t);
```

禁用该tasklet，并在再次启用前该tasklet不会被调度。其中：
- `tasklet_disable` 在该tasklet被执行时调用会忙等直到tasklet退出。
- `tasklet_disable_nosync` 在该tasklet被执行时调用操作无效，并且不会忙等。

#### 10.5.2.4 启用tasklet

启用被禁用的tasklet：

```C
void tasklet_enable(struct tasklet_struct *t);
```

## 10.6 工作队列(workqueue) ^qihja2

workqueue和tasklet<font color="#c00000">都是</font>内核的一种<font color="#c00000">异步执行机制</font>，其区别如下表所示。

| <center>特性</center> | <center>workqueue</center>                                                                              | <center>tasklet</center>                            |
| ------------------- | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| 运行环境                | "内核线程"的上下文                                                                                              | 中断上下文                                               |
| 环境限制                | 无，<font color="#c00000">允许休眠</font>，可以不原子化。<br>但由于其在"内核线程"的上下文中，故<font color="#c00000">不可访问用户空间</font>。 | 要遵守中断限制，如禁止休眠等。                                     |
| 多次执行                | 可以多次执行，每次执行之前调用 `schedule_work()`                                                                       | 可以多次执行，每次执行之前调用 `tasklet_schedule`                  |
| 抢占                  | 执行时可以抢占，可以长时间占用                                                                                         | 不可抢占，尽快退出                                           |
| 并发性                 | 同一个工作实例不能在多个CPU上同时运行。<br>(但是同一个回调函数可以创建多个实例)                                                            | 同一个tasklet不会在多个CPU上同时执行<br>(但是同一个回调函数可以创建多个tasklet) |
| 延迟                  | 延迟高                                                                                                     | 延迟很低，实时性高                                           |
| 延迟控制                | 可以做到指定时间的延迟                                                                                             | 不可指定延迟                                              |

工作实例按照是否需要延迟分可为：
1. `struct work_struct` ：[[Linux驱动开发笔记#^2jgyju|不需要延迟的工作任务]]，需要尽快被调度
2. `struct delayed_work` ：[[Linux驱动开发笔记#^l81zqg|需要延迟的工作任务]]，需要在指定时间后被执行
而上述两个工作队列<font color="#c00000">都允许在</font><span style="background:#fff88f"><font color="#c00000"><B>被执行后</B></font></span><font color="#c00000">反复被添加到工作队列中</font>，这也是其标准用法

而如上文所述，workqueue是在"内核线程"中执行的，具体来说其可在如下两种工作队列中执行：
1. [[Linux驱动开发笔记#^oyzb5s|独有工作队列]]：每个workqueue<span style="background:#fff88f"><font color="#c00000">专用的</font></span><font color="#c00000">一个或多个</font>"内核线程"中
2. [[Linux驱动开发笔记#^g6drzs|共享工作队列]]：整个内核共享的workqueue的"内核线程"中

### 10.6.1 不需要延迟的工作任务(work_struct) ^2jgyju

可使用如下的方式进行初始化：

```C
#include <linux/workqueue.h>

// 静态定义
#define DECLARE_WORK(n, f)                                         \  
        struct work_struct n = __WORK_INITIALIZER(n, f)

// 动态定义
#define INIT_WORK(_work, _func)                                    \  
        __INIT_WORK((_work), (_func), 0)
```

其中：
- `DECLARE_WORK` 中：
	- `n` 为工作实例的变量名
	- `f` 为类型为 `void (*work_func_t)(struct work_struct *work)` 的回调函数
- `INIT_WORK` 中：
	- `_work` 为 `struct work_struct *` 类型的工作实例
	- `_func` 为 `void (*work_func_t)(struct work_struct *work)` 类型的回调函数

### 10.6.2 需要延迟的工作任务(delayed_work) ^l81zqg

静态定义：

```C
#include <linux/workqueue.h>

#define DECLARE_DELAYED_WORK(n, f)                                  \  
    struct delayed_work n = __DELAYED_WORK_INITIALIZER(n, f, 0)  
  
#define DECLARE_DEFERRABLE_WORK(n, f)                               \  
    struct delayed_work n = __DELAYED_WORK_INITIALIZER(n, f, TIMER_DEFERRABLE)
```

其中：
- `n` 为工作实例的变量名
- `f` 为类型为 `void (*work_func_t)(struct work_struct *work)` 的回调函数
- `DEFERRABLE` 表示可推迟的工作实例

动态定义：

```C
#define INIT_DELAYED_WORK(_work, _func)					\
	__INIT_DELAYED_WORK(_work, _func, 0)
```

其中：
- `_work` 为 `struct work_struct *` 类型的工作实例
- `_func` 为 `void (*work_func_t)(struct work_struct *work)` 类型的回调函数，需要注意：
	- 回调函数的<font color="#c00000">参数类型为</font> `struct work_struct*` <font color="#c00000">而非</font> `struct delayed_work*` ，其需要使用 `container_of` 来获取 `struct work_struct*` 的上层容器 `struct delayed_work*` 。

### 10.6.3 独有工作队列及相关API ^oyzb5s

#### 10.6.3.1 定义独有工作队列对象

独有工作队列在创建时，可以选择：
1. 为该workqueue在每个CPU上都创建一个专属的"内核线程"
2. 只为该workqueue创建一个"内核线程"，<font color="#c00000">在默认情况下该队列会被绑定到一个具体的CPU上</font>，<font color="#c00000">具体是哪个CPU取决于调度器</font>，但是通常是<font color="#c00000">提交时</font>( `queue_work` )使用的CPU。需要注意：
	1. 若原先的CPU被弹出或不可用，则会被转移到其他CPU上运行。
	2. 实际测试中，即使系统负载不高，<font color="#c00000">也可能会被切换到别的CPU上</font>(也就是不保证始终在同一个CPU上)。

```C
#include <linux/workqueue.h>

// 下方两个函数已被宏定义到alloc_workqueue。下方为宏替换后的函数原型，并非实际定义

// 为该队列在每个CPU上都创建一个专属的内核线程
struct workqueue_struct *create_workqueue(const char *name);
// 仅创建一个内核线程
struct workqueue_struct *create_singlethread_workqueue(const char *name);
```

#### 10.6.3.2 提交工作到独有工作队列

```C
// 
bool queue_work(struct workqueue_struct *wq,
	struct work_struct *work);

// 提交并指定延迟，延迟单位为jiffies
bool queue_delayed_work(struct workqueue_struct *wq,
	struct delayed_work *dwork,
	unsigned long delay);
```
其中：
- <span style="background:#fff88f"><font color="#c00000">返回值</font></span>：
	- 当任务成功加入队列时返回 `true`
	- 如果工作项已经在队列中(即重复提交时)返回 `false`
- 内存顺序保证：
	- 如果 `queue_work` 返回 `true`，则在 `queue_work` 调用之前的所有内存写操作( `stores` )对执行 `work` 的CPU是可见的。
	- 即在 `work` 执行时，可以安全地访问在 `queue_work` 之前写入的数据。

#### 10.6.3.3 提交任务



#### 10.6.3.4 取消任务


```C
bool cancel_delayed_work(struct delayed_work *dwork);
```

其中：
- 返回值：
	- 若任务在开始前被取消则返回 `true`
- 该函数可以确认任务是否开始。若需要确认任务是否完成，可以用下方的API。

#### 10.6.3.5 等待整个工作队列执行完毕(阻塞)

```C
flush_workqueue(wq);
```

#### 10.6.3.6 释放工作队列

```C
void destroy_workqueue(struct workqueue_struct *wq);
```

其中在该接口调用前必须保证队列中所有任务完成，例如：
- 使用 `flush_workqueue` 阻塞并等待队列中所有任务完成。
- 使用 `flush_work` 阻塞并等待某一个任务完成。

### 10.6.4 共享队列及其API ^g6drzs

并不是所有的内核模块都有独立管理一个等待队列的必要，因此内核提供了如下几种共享队列：
- `system_wq` ：普通优先级的工作队列(默认)。
- `system_highpri_wq` ：高优先级的工作队列。
- `system_long_wq` ：适用于执行时间较长的任务。

而对于共享队列来说，其有如下的特性：
1. <font color="#c00000">无需</font>使用 `create_workqueue` 或 `destroy_workqueue` <font color="#c00000">创建和销毁队列</font>。
2. 相较于独有工作队列，其资源消耗更小。
3. 由于要和其他内核代码共享队列，因此：
	1. 不能长期占用队列，例如长期休眠等。
	2. 不能长期占用队列(同上一条)，例如<font color="#c00000">频繁占用</font>或<font color="#c00000">占用过多时间</font>(超过 `10000us` 会被检测)

#### 10.6.4.1 提交工作到共享队列

```C
// 提交工作，返回值意义同上一章节
bool schedule_work(struct work_struct *work);

// 提交工作并指定运行的CPU
bool schedule_work_on(int cpu, struct work_struct *work);

// 提交工作并指定延迟，延迟单位为jiffies
bool schedule_delayed_work(struct delayed_work *dwork,
	unsigned long delay);

// 提交工作并指定延迟和所运行的CPU
bool schedule_delayed_work_on(int cpu, struct delayed_work *dwork,
	unsigned long delay)
```

#### 10.6.4.2 等待指定工作完成

等待指定工作完成的接口与上一章节相同：





# 11 内存分配

## 11.1 Linux内核内存管理概述

### 11.1.1 Linux内核内存分配的层次结构

Linux内核的内存分配存在如下的层次结构：
1. 伙伴系统：负责以page为单位对物理内存进行分割，支持 `alloc_pages` 接口。
2. slab分配器(SLUB、SLOB)：基于伙伴系统，将page拆分为固定大小的若干小块(8B、16B、...、8KB)。
3. kmalloc/kfree接口：为大多数开发者提供的接口，底层依赖slab分配器。

### 11.1.2 Linux内核的内存区段(了解)

Linux的内存区段划分取决于具体的硬件平台，可以使用如下命令查询：

```shell
cat /proc/buddyinfo
```

一个demo结果为：

```Shell
root@VM-4-7-ubuntu:/proc# cat buddyinfo
Node 0, zone      DMA      9     18     13      8     12      4      3      5      3      0      0
Node 0, zone    DMA32  10175   2398    642    372    107     27      4      2      0      5      1
```

注：wsl中通常没有该文件。

#### 11.1.2.1 x86架构(32位)

在x86上，Linux内存区段被划分为如下三个区段：
- `ZONE_DMA` ：物理地址 `0x00000000` 到 `0x00FFFFFF` (0~16 MB)，专供老式ISA设备使用。
- `ZONE_NORMAL` ：物理地址 `0x01000000` 到 `0x07FFFFFF` (16 MB ~ 896 MB)，内核可直接线性映射到虚拟地址空间的区域。
- `ZONE_HIGHMEM` ：物理地址 `0x08000000` 及以上(高于896 MB)，供用户空间程序使用，需动态映射到内核空间。

## 11.2 伙伴系统(buddy system)

如上述章节，伙伴系统负责以page为单位对物理内存进行分割，则当内核需要分配大块的内存时，直接使用伙伴系统是最优选择。其主要提供了如下的API(均位于 `linux/gfp.h` )：
- `alloc_pages(gfp_t gfp_mask, unsigned int order)` ：
	- 分配连续物理页帧，返回页描述符(`struct page*`)，可直接用于底层内存操作。
- `__get_free_pages(gfp_t gfp_mask, unsigned int order)` ：
	- 与 `alloc_pages` 类似，但返回物理内存的起始虚拟地址(内核逻辑地址)。
- `free_pages(unsigned long addr, unsigned int order)` ：
	- 释放通过上述接口分配的内存。
- `get_zeroed_page(gfp_t gfp_mask)` ：
	- 分配并用零填充的单页。
其中：
- `order` <font color="#c00000">为要申请或施放的页面数的</font> $\log_2$ <font color="#c00000">次幂</font>。
- `gfp_mask` 可见[[Linux驱动开发笔记#^74tb72|kmalloc接口开发调用]]。

## 11.3 后备高速缓存(slab) ^utt6c3

slab基于buddy system实现了如下的两种缓存：
1. 特定对象专用缓存：专为某个类型(如 `struct task_struct`)频繁分配设计（通过 `kmem_cache_create` 创建）。
2. 通用对象缓存：以固定大小(如8B、16B、32B、...、8KB)预创建的缓存池，`kmalloc` 通过它们实现内存分配。

正如上述所属的两种缓存，当：
1. 需要<font color="#c00000">高频且高效地</font>创建和销毁某些<font color="#c00000">小的内存对象</font>时；
2. 需要分配的<font color="#c00000">内存对象大小不是2的整数幂</font>，<font color="#c00000">且内核中需要分配众多该对象时</font>(例如 `inode` 对象)。
使用通用对象缓存的 `kmalloc` 分别可能造成如下问题：
- 高频高效创建小内存对象-> `kmalloc` 会比直接使用slab多造成一些花销
- <font color="#c00000">内存对象大小不是2的整数幂</font>-><span style="background:#fff88f"><font color="#c00000">造成内存碎片</font></span>，可见[[Linux驱动开发笔记#^yd7n15|kmalloc原理概述]]
此时应当使用特定对象专用缓存进行管理，这种内存池也被称作后备高速缓存。尽管后备高速缓存(lookaside cache)的名字中有"cache"，但是其实际存储位置仍然为内存区域。

在终端中输入如下命令即可查看slab的使用情况：

```Shell
cat /proc/slabinfo
```

一个输出demo：

```Shell
# name            <active_objs> <num_objs> <objsize> <objperslab> <pagesperslab> : tunables <limit> <batchcount> <sharedfactor> : slabdata <active_slabs> <num_slabs> <sharedavail>
nf_conntrack         197    264    320   12    1 : tunables    0    0    0 : slabdata     22     22      0
au_finfo               0      0    192   21    1 : tunables    0    0    0 : slabdata      0      0      0
```

### 11.3.1 开发调用

slab在开发中通常按照如下的方式进行调用：
1. 使用 `kmem_cache_create` 创建专用slab缓存，函数原型等价于(但不等于)：
	```C
// 旧版本
void* kmem_cache_create(const char* name, size_t size, slab_flags_t flag, void (*ctor)(void *));

// 新版本
void* kmem_cache_create(const char* name, size_t size, slab_flags_t flag);
	```
	上述函数实际使用宏函数实现，依赖于C11的 `_Generic()` 特性同时兼容新旧版本。
	其中：
	- `name` ：为缓存名称，用于 `/proc/slabinfo` 和调试信息中标识，命名应有唯一性。<font color="#c00000">该参数应当使用静态存储</font>，通常直接取字符串。
	- `size` ：每个slab对象的大小，应使用 `sizeof(obj)` 获取。
	- `flag` ：控制如何完成分配，可用值如下：
		- `SLAB_NO_REAP` ：禁止内核在内存不足时主动回收(Reap)该Slab缓存的空闲内存页，<font color="#c00000">通常不用</font>。在SLUB实现中已经弃用，是早期Linux的设计。
		- `SLAB_HWCACHE_ALIGN` ：对齐到硬件缓存行大小，保证单个CPU一次只能读取一个对象，减少跨核心的缓存行无效化。在实际开发中应当使用一些工具验证该标志位的真实收益，避免盲目使用导致的内存开销。
		- `SLAB_CACHE_DMA` ：要求从DMA内存区段分配。
	- `ctor` ：对象的构造函数，初始化用，可为 `NULL` 。
2. 使用 `kmem_cache_alloc` 从高速缓存中分配内存：
	```C
void* kmem_cache_alloc(struct kmem_cache *cachep, gfp_t flags);
	```
3. 使用 `kmem_cache_free` 回收内存：
	```C
void kmem_cache_free(struct kmem_cache *s, void *objp);
	```
4. 使用 `kmem_cache_destroy` 销毁slab缓存：
	```C
void kmem_cache_destroy(struct kmem_cache *s);
	```

### 11.3.2 slab的变种实现或改进

#### 11.3.2.1 SLUB

SLUB和SLOB均为slab的变种，现代内核默认使用SLUB。
#TODO 

#### 11.3.2.2 SLOB

#TODO 


## 11.4 kmalloc接口(最常用)

<span style="background:#fff88f"><font color="#c00000">特性</font></span>：
1. <span style="background:#fff88f"><font color="#c00000">分配得到的内存区域在物理地址上一定连续</font></span>，这是和vmalloc的重要区别，该特性的延申特性有：
	1. 由于物理地址连续，故可用于DMA。
	2. 可以避免切换页表所导致的开销。
2. 由于物理地址连续，因此其可分配的最大单块内存有限制，<font color="#c00000">通常为内存页面的2倍</font>。
3. <font color="#c00000">分配的内存默认不可被换出</font>。
4. <font color="#c00000">分配的内存不会被ZSWAP/ZRAM</font>。
5. 基于slab的通用对象缓存实现。
6. <font color="#c00000">内存实际占用会向上取整到2的整数幂</font>。因此有内存碎片。
7. 可以避免休眠。
8. 销毁 `kmalloc` 申请的内存需要使用 `kfree` 。

### 11.4.1 开发调用 ^74tb72

函数原型(但实际上并非如此)：

```C
#include <linux/slab.h>
void *kmalloc(size_t size, gfp_t gfp);
```

其中分配标志 `gfp` <font color="#c00000">主要分为"分配优先级"和"分配选项"两类</font>，<span style="background:#fff88f"><font color="#c00000">这两类之间可以使用或运算结合配置</font></span>。
分配优先级有：
- `GFP_NOWAIT` ：在<font color="#c00000">内核空间</font>中分配内存，<font color="#c00000">不会引起休眠</font>。
- `GFP_ATOMIC` ：原子地分配内存，<font color="#c00000">不会引起休眠</font>，<font color="#c00000">可能会使用紧急内存池</font>。通常在中断中使用。
- `GFP_KERNEL` ：在<font color="#c00000">内核空间</font>中分配内存，可能休眠。
- `GFP_USER` ：在内核中<font color="#c00000">为用户空间相关操作</font>分配内存(例如 `mmap` )，可能休眠，且该内存<font color="#c00000">用户可见</font>。
- `GFP_HIGHUSER` ：类似于 `GFP_USER` ，但是优先分配高端内存。
- `GFP_NOIO` ：类似于`GFP_KERNEL` ，但是禁止I/O代码初始化。
- `GFP_NOFS` ：类似于`GFP_KERNEL` ，但是禁止文件系统调用。
分配选项有：
- `__GFP_ZERO` ：分配并清空内存空间。
- `__GFP_DMA` ：分配可DMA区段中的内存。
- `__GFP_HIGHMEM` ：分配高端内存，且可能使用紧急内存池。
- `__GFP_COLD` ：从冷页面页表中进行内存分配，这部分内存所在页面没有被频繁访问，甚至已经被swap到硬盘。<font color="#c00000">可以用于分配不经常使用的内存</font>。在不使用该标志时，会优先分配热缓存页面。
- `__GFP_NOWARN` ：避免在kmalloc中使用printk。
- `__GFP_HIGH` ：表示高优先级请求，在紧急情况下使用，允许使用内核预留的内存页面。
- `__GFP_REPEAT` ：进行有限次数的重试。
- `__GFP_NOFAIL` ：无限重试直到分配成功。<font color="#c00000">慎重使用</font>。
- `__GFP_NORETRY` ：若请求的内存不可得则应当立即返回，使用该标志位可以<font color="#c00000">减少休眠</font>。

在终端中输入如下命令即可查询 `kmalloc` 的使用情况：

```Shell
cat /proc/slabinfo | grep kmalloc
```

### 11.4.2 原理概述 ^yd7n15

正如上文所述，`kmalloc` 是基于[[Linux驱动开发笔记#^utt6c3|slab]]实现的，所以其使用的头文件也是 `slab.h` 。

在内核启动时，内核通过 `kmalloc_caches` 数组预先创建一系列通用Slab缓存，该系列缓存大小为8B、16B、32B、...、8KB，这些缓存使用上一子章节末尾的查询命令输出的slab名分别为kmalloc-8、kmalloc-16、...、kmalloc-8k。

当发生 `kmalloc` 调用时，其会将 `kmalloc` 中的 `size` 参数<span style="background:#fff88f"><font color="#c00000">向上对齐到最小的缓存块</font></span>，<font color="#c00000">例如 200Byte -> 256Byte</font>。随后根据GFP标志为其分配对象。

## 11.5 vmalloc接口

特性：
1. 虚拟地址连续，<span style="background:#fff88f"><font color="#c00000">但是物理地址可能离散</font></span>，这是与kmalloc之间最重要的区别。
2. 分配得到的内存使用起来效率不高。
3. 可能会导致休眠。
4. 分配得到的内存位于内核的"动态映射区"。
5. 可以用于大块的，对物理连续性无要求的场景，例如文件系统缓存、网络协议栈的临时缓冲区。
6. 可以考虑使用伙伴系统代替该需求，直接与页面打交道。
7. 销毁 `vmalloc` 申请的内存需要使用 `vfree` 。
8. 使用vmalloc的代码可能会在合并到主线linux时受到冷遇。

### 11.5.1 vmalloc & kmalloc(slab)特性对比

| 特性       | slab-特定对象缓存 | slab-通用对象缓存(kmalloc) | vmalloc                                                                    |
| -------- | ----------- | -------------------- | -------------------------------------------------------------------------- |
| 虚拟地址连续性  | 连续          | 连续                   | 连续                                                                         |
| 物理地址连续性  | 一定连续        | 一定连续                 | <span style="background:#fff88f"><font color="#c00000">不一定连续</font></span> |
| 能否避免休眠   | 可以避免        | 可以避免                 | <span style="background:#fff88f"><font color="#c00000">不能</font></span>    |
| 所得内存使用效率 | 高           | 高                    | 一般                                                                         |

### 11.5.2 开发调用

```C
#include "linux/vmalloc.h"
// 注：下方并非实际定义，仅为原型参考
void *vmalloc(unsigned long size);
```

# 12 与硬件通信

## 12.1 硬件寄存器与常规内存

本子章节的学习需要先完成[[内存屏障]]的学习。

编译器及CPU对内存访问的常见优化方式有使用高速缓存、指令重排等。而对于硬件来说，上述两种方式均不可接受。其对应的解决方案为：
1. 将底层硬件配置为在访问IO区域时禁用硬件缓存
2. 使用内存屏障避免指令重排

Linux内核提供了如下的几种内存屏障的使用方式：

- 编译器内存屏障：
```C
#include <linux/kernel.h>
// 通知编译器插入一个内存屏障，但并不影响CPU层面的乱序执行
void barrier(void);
```
- 单核心内存屏障：
```C
#include <asm/system.h>
// 以下四种API均为在硬件层面插入内存屏障
// 在大多数架构中，下列四种API调用时均会隐含 barrier() 调用
// 读内存屏障，可以保证 rmb() 调用之前的所有读取操作均已完成
void rmb(void);
// 阻止部分读取操作的读内存屏障，除非明白与 rmb() 之间的差别，否则不建议调用
void read_barrier_depends(void);
// 写内存屏障，可以保证 wmb() 调用之前的所有写入操作均已完成
void wmb(void);
// 全内存屏障，可以保证 mb() 调用之前的所有读写操作均已完成
void mb(void);
```
- 多核心内存屏障：
	- 相比于单核心的内存屏障，多核心的内存屏障额外的增加了多核心之间的同步机制，例如[[CPU缓存一致性|MESI]]等。
```C
#include <asm/system.h>
void smp_rmb(void);
void smp_read_barrier_depends(void);
void smp_wmb(void);
void smp_mb(void);
```

一个经典的内存屏障的使用形式如下：

```C
// 写入寄存器进行硬件配置
writel(dev->regs.addr, xxx);
writel(dev->regs.size, xxx);
writel(dev->regs.ops, xxx);

// 插入写内存屏障，确保前面三哥寄存器操作均已完成
wmb();

// 执行硬件操作
writel(dev->regs.control, xxx);
```

## 12.2 使用IO端口

Linux系统的包含串口、PCI bus、DMA等IO端口的分配均在 `/proc/ioports` 中可见，并会列出IO的地址范围，例如：

```Shell
# cat /proc/ioports
0000-0cf7 : PCI Bus 0000:00
  0000-001f : dma1
  0020-0021 : pic1
  0040-0043 : timer0
  0050-0053 : timer1
  0060-0060 : keyboard
  0064-0064 : keyboard
  0070-0071 : rtc0
  0080-008f : dma page reg
  00a0-00a1 : pic2
  00c0-00df : dma2
  00f0-00ff : fpu
  0170-0177 : 0000:00:01.1
    0170-0177 : ata_piix
  01f0-01f7 : 0000:00:01.1
    01f0-01f7 : ata_piix
  0376-0376 : 0000:00:01.1
    0376-0376 : ata_piix
  03f2-03f2 : floppy
  03f4-03f5 : floppy
  03f6-03f6 : 0000:00:01.1
    03f6-03f6 : ata_piix
  03f7-03f7 : floppy
  03f8-03ff : serial
  0600-063f : 0000:00:01.3
    0600-0603 : ACPI PM1a_EVT_BLK
    0604-0605 : ACPI PM1a_CNT_BLK
    0608-060b : ACPI PM_TMR
  0700-070f : 0000:00:01.3
0cf8-0cff : PCI conf1
0d00-ffff : PCI Bus 0000:00
  afe0-afe3 : ACPI GPE0_BLK
  c000-cfff : PCI Bus 0000:02
  d000-dfff : PCI Bus 0000:01
  e000-e03f : 0000:00:06.0
  e040-e05f : 0000:00:01.2
    e040-e05f : uhci_hcd
  e060-e07f : 0000:00:05.0
  e080-e09f : 0000:00:07.0
  e0a0-e0af : 0000:00:01.1
    e0a0-e0af : ata_piix
```

<font color="#c00000">值得注意的是上述地址范围</font><span style="background:#fff88f"><font color="#c00000">并非内存地址范围</font></span>，<font color="#c00000">上述地址是独立编址的</font>，称作端口IO(Port IO)。

内核中为IO端口分配提供了如下的接口：
- 请求分配IO，可以通过返回值判定可用性(并非实际原型)：
```C
#include <linux/ioports.h>
struct resource *request_region(resource_size_t start, resource_size_t n, const char *name);
```
- 释放IO(并非实际原型)：
```C
#include <linux/ioports.h>
void release_region(resource_size_t start, resource_size_t n);
```
- 操作IO：
```C
#include <asm/io.h>

// 读写8位
u8 inb(unsigned long addr);
void outb(unsigned char x, unsigned long port);

// 读写16位
u16 inw(unsigned long addr);
void outw(unsigned short x, unsigned long port);

// 读写32位
u32 inl(unsigned long addr);
void outl(unsigned int x, unsigned long port);
```
- 串操作：
	- 一些架构上提供了一次传输一个数据序列的指令，因此内核还提供了对应的串操作。在支持串IO的架构上会使用对应的指令，在不支持的架构上会使用紧凑循环实现，比自行实现循环效率要高。
```C
#include <asm/io.h>

void insb(unsigned long port, void *dst, unsigned long count);
void outsb(unsigned long port, const void *src, unsigned long count);

void insw(unsigned long port, void *dst, unsigned long count);
void outsw(unsigned long port, const void *src, unsigned long count);

void insl(unsigned long port, void *dst, unsigned long count);
void outsl(unsigned long port, const void *src, unsigned long count);
```
- 暂停式IO：
	- 在一些老式总线上(比如ISA总线)可能会出现CPU速度比总线速度快的问题，因此若需要保持正确的时序的话就需要引入暂停式IO。
	- 此类IO比上述IO多了一个 `_p` 后缀。
	- 暂停式IO会使用一些延迟方法来等待这些低速设备的响应(通常是延迟1us)。<font color="#c00000">该IO在现代设备中很少使用</font>，在大多数平台上均已被重定向为普通IO(Power-PC仍有延迟)。

### 12.2.1 实际Demo

#TODO 

## 12.3 使用IO内存

CPU硬件或操作系统通常会把硬件的寄存器或内存映射到内存空间当中去。与上一章节的端口IO(Port IO)的区别点在于该内存地址位于内存空间中，称作内存映射IO(Memory-Mapped IO，MMIO)。根据计算机体系结构和目标IO的不同，IO内存<font color="#c00000">可能是</font>、<font color="#c00000">也可能不是经由页表进行的</font>，<font color="#c00000">但是在内核编程时使用的步骤是一致的</font>。

使用IO内存的基本步骤为：
1. [[Linux驱动开发笔记#^x2iaei|标注物理内存资源的所有权]]( `request_mem_region` )，进行互斥和资源管理
2. [[Linux驱动开发笔记#^p797kv|将物理内存区域映射到虚拟内存]]( `ioremap` )，方便进行权限管理
3. [[Linux驱动开发笔记#^1udrzm|操作内存区域]]，注意不要使用普通内存操作，普通内存操作不具备可移植性
4. [[Linux驱动开发笔记#^akiihr|取消内存映射]]( `iounmap` )
5. [[Linux驱动开发笔记#11 3 1 5 释放内存资源的所有权 release_mem_region 0ucvb2|释放内存资源的所有权]]( `release_mem_region` )

使用页表组织MMIO的优点有：
1. 为用户态提供虚拟内存地址，避免暴露物理地址
2. 方便统一使用虚拟内存机制管理内存，不需要为了管理用户态的访问增设额外的机制
3. 方便管理权限
4. 一些设备的内存可能在物理上不连续，例如PCI BAR空间等
5. 方便内核使用 `mmap` 将MMIO映射到用户空间
MMIO会被设置为不可换出、不可缓存(uncached)，不用担心页面置换问题。

在使用IO内存时，基本流程和使用普通内存一致，<font color="#c00000">均为申请-使用-释放的过程</font>，只是使用的API和成功/失败对应的意义不同。

### 12.3.1 相关API

#### 12.3.1.1 标注物理内存资源的所有权(request_mem_region) ^x2iaei

`request_mem_region` 的函数原型可参考(注意并非实际函数原型)：

```C
#include <linux/ioport.h>
struct resource * request_mem_region(resource_size_t start, resource_size_t n, const char* name);
```

需要注意：
1. 该函数并不像普通的 `*malloc` 那样分配内存
2. <span style="background:#fff88f"><font color="#c00000">该函数的目的是确保该物理区域不会被多个驱动冲突访问</font></span>，并不负责权限控制。从技术上来看，即使不使用 `request_mem_region` 进行标记，对应内存区域依旧可以被访问，但是不能确保安全，且无法使用该函数的 `name` 进行追踪。
3. 使用本函数标记所有权的内存区域需要使用[[Linux驱动开发笔记#^0ucvb2|release_mem_region]]函数释放物理内存的所有权。
#### 12.3.1.2 将物理内存区域映射到虚拟内存(ioremap) ^p797kv

```C
#include <asm/io.h>
void __iomem *ioremap(phys_addr_t offset, size_t size);
void __iomem *ioremap_prot(phys_addr_t phys_addr, size_t size, unsigned long prot)
```

需要注意：
1. 此类函数的作用为<span style="background:#fff88f"><font color="#c00000">将物理地址映射到内核虚拟地址，并设置访问权限和缓存策略</font></span>。
2. 该函数映射后的地址位于 `vmalloc` 区域中
3. 函数的默认虚拟内存配置为：
	1. 可读可写，不可执行
	2. 默认禁用缓存
	具体的配置需求可使用 `ioremap_prot` 手动配置。

#### 12.3.1.3 取消内存映射(iounmap) ^akiihr

```C
#include <asm/io.h>
void iounmap(volatile void __iomem *addr);
```

#### 12.3.1.4 操作内存区域 ^1udrzm

在部分平台上允许使用普通IO操作来访问这些内存，但是该方法不具备可移植性。应当使用如下的方法族：

```C
#include <asm/io.h>

// 读取单个
unsigned int ioread8(void *addr);
unsigned int ioread16(void *addr);
unsigned int ioread32(void *addr);

// 写入单个
void iowrite8(u8 value, void *addr);
void iowrite16(u16 value, void *addr);
void iowrite32(u32 value, void *addr);

// 读写序列
void ioread8_rep(void *addr, void *buf, unsigned long count);
void ioread16(void *addr, void *buf, unsigned long count);
void ioread32(void *addr, void *buf, unsigned long count);
void iowrite8(void *addr, const void *buf, unsigned long count);
void iowrite16(void *addr, const void *buf, unsigned long count);
void iowrite32(void *addr, const void *buf, unsigned long count);

// 内存操作
void memset_io(void *dst, int c, unsigned long count);
void memcpy_fromio(void *to, const void *from, unsigned long count);
void memcpy_toio(void *to, const void *from, unsigned long count);
```

#### 12.3.1.5 释放内存资源的所有权(release_mem_region) ^0ucvb2

该函数的参考原型如下(并非实际原型)：

```C
#include <linux/ioport.h>
void release_mem_region(resource_size_t start, resource_size_t n);
```

# 13 中断处理

## 13.1 当前上下文状态与注意事项 ^h05ata

### 13.1.1 查询当前是否在中断上下文中

```C
#include <asm/hardirq.h>
in_interrupt();
```

当当前上下文为软件或硬件中断时会返回非零值。

### 13.1.2 中断上下文中的注意事项 ^fw453g

在中断上下文中时需要注意：
1. <span style="background:#fff88f"><font color="#c00000">不允许访问用户空间</font></span>，因为不在进程上下文中。
2. <span style="background:#fff88f"><font color="#c00000">禁止访问用户空间</font></span>，用于指向当前进程的 `current` 指针也无效。
3. 不能执行休眠或调度，不可调用 `schedule` 或 `wait_event` 等。也不能调用可能引起休眠的函数或信号量，例如 `kmalloc(..., GFP_KERNEL)` 。
4. 但是可以使用忙等。

### 13.1.3 查询当前是否在原子上下文中

```C
#include <asm/hardirq.h>
in_atpmic();
```

在原子上下文中时需要注意：
1. <span style="background:#fff88f"><font color="#c00000">不允许访问用户空间</font></span>，因为可能引起调度。
2. `current` 指针可用，但是不能访问用户空间。

## 13.2 查看系统当前已注册中断

使用 `cat /proc/interrupts` 命令，有：

```Shell
          CPU0       CPU1       
 0:        170          0     IR-IO-APIC    2-edge      timer
 1:         10          0     IR-IO-APIC    1-edge      i8042
 8:          1          0     IR-IO-APIC    8-edge      rtc0
 9:        214          0     IR-IO-APIC    9-fasteoi   acpi
11:          0          0     IO-APIC  11-fasteoi   virtio2, uhci_hcd:usb1
12:        124          0     IR-IO-APIC   12-edge      i8042
16:       3589          0     IR-IO-APIC   16-fasteoi   ehci_hcd:usb1
24:          0        652     IR-PCI-MSI 32768-edge      xhci_hcd
...
```

^b47kyp

上述内容中：
- 第一列为中断号
- 各CPU列为在该CPU上触发中断的次数
- 最后一列为关联的硬件设备或中断类型，如果由逗号分隔的表示是[[Linux驱动开发笔记#^c8eb6k|共享中断]]。
- 中间几列为处理中断的可编程中断控制器

需要补充的是：
1. Linux 内核通常会在第一个 CPU 上处理中断，从而最大化缓存本地性。

此外，使用 `cat /proc/stat` 命令，在 `intr` 行也可以查看各中断的触发次数，例如：

```Shell
...
intr 2586828620 0 9 0 0 24 0 3 0 0 0 0 0 15 0 34688478 0 0 0 0 0 0 0 0 0 50 539037977 688394395 0 284284934 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
...
```

上述 `intr` 行中：
- 第一个数字为系统触发中断的总次数
- 后续若干个数字是各个 IRQ 信号线上触发中断的次数(即使没有安装中断处理程序也会计数)

## 13.3 中断的注册

### 13.3.1 注册中断(request_irq)

在Linux内核中，注册(安装)中断例程需要使用如下的API：

```C
#include <linux/interrupts.h>
int request_irq(unsigned int irq, irq_handler_t handler, unsigned long flags, const char *name, void *dev);
```

其中：

| <center>参数</center>     | <center>含义</center>                                                                                                                                                                                                                                   |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `unsigned int irq`      | 选用的中断号，选用原则见：[[Linux驱动开发笔记#^adyua2\|中断号选用原则]]                                                                                                                                                                                                         |
| `irq_handler_t handler` | 中断处理函数指针，原型为：`(*irq_handler_t)(int irq, void *dev)` <br>其中：<br>- `irq` 为中断号，同参数1<br>- `dev` 为指向私有数据区的指针，同参数5<br>返回值 `irq_handler_t` 可选：<br>- `IRQ_NONE` ：中断未由本设备触发<br>- `IRQ_HANDLED` ：中断已被处理<br>- `IRQ_WAKE_THREAD` ：需要唤醒线程化处理(结合 `IRQF_ONESHOT` 使用) |
| `unsigned long flags`   | 中断管理掩码                                                                                                                                                                                                                                                |
| `const char *name`      | 中断号拥有者，会在 `/proc/interrupts` 中显示                                                                                                                                                                                                                      |
| `void *dev`             | 可以用于指向私有数据区。<br>在非共享中断也可以设置为 `NULL` ，但不建议，<span style="background:#fff88f"><font color="#c00000">最好保持全内核唯一性</font></span>(所以一般指向 `dev` )。<br><font color="#c00000">因为该值在内核中断管理的数据结构中起到了类似Key值的作用</font>。<br>具体可见[[Linux驱动开发笔记#^rqxyj6\|关于dev参数的说明]]。  |

常用的中断管理掩码有：
1. 中断触发方式掩码：
	- `IRQF_TRIGGER_NONE` ：不指定触发方式，沿用硬件或固件的当前配置。
	- `IRQF_TRIGGER_RISING` ：上升沿触发
	- `IRQF_TRIGGER_FALLING` ：下降沿触发
	- `IRQF_TRIGGER_HIGH` ：高电平触发
	- `IRQF_TRIGGER_LOW` ：低电平触发
	- `IRQF_TRIGGER_PROBE` ：自动探测触发(慎用，需要二次判定触发条件是否正确，且整个内核原码中尚无使用)
2. 中断共享控制掩码：
	- `IRQF_SHARED` ：共享中断。新平台中很少使用。
		- <span style="background:#fff88f"><font color="#c00000">所有共享设备的中断触发方式必须一致</font></span>，否则报错。
		- 不允许和非共享设备共享中断。
	- `IRQF_PROBE_SHARED` ：共享中断，允许驱动在共享中断线时，<font color="#c00000">绕过触发方式的严格一致性检查</font>。
		- 可以用于共享设备中<span style="background:#fff88f"><font color="#c00000">触发方式</font></span><font color="#c00000">不一致</font>的情况。
		- 用于调试、探测或动态适配用途，<font color="#c00000">生产环境中禁用该标志位</font>。
	- `IRQF_COND_ONESHOT` ：表示该共享中断在执行完成后必须显式的重新启用。需要注意：
		- 该标志位必须配合 `IRQF_SHARED` 使用，否则无效。
		- 若某一共享设备已经启用该标志位，后来设备在注册中断时未设置标志位，则后来设备的注册操作会返回 `-EINVAL` 。
		- 可以与 `IRQF_ONESHOT` 重复设置，但没有必要。
3. 中断处理与调度控制：
	- `IRQF_TIMER` ：标记为定时器中断，优先处理以保障精度。
	- `IRQF_PERCPU` ：标记为per-CPU中断，每个CPU核心独立注册并处理该中断，通常用于ARM的每个CPU的本地计时器，或高性能网卡的每CPU中断。
	- `IRQF_NOBALANCING` ：禁止中断负载均衡，用于将中断绑定到一个特定的CPU上。
	- `IRQF_IRQPOLL` ：中断用于轮询模式优化，用于需要频繁轮询的中断。
	- `IRQF_ONESHOT` ：单次启动中断，表示中断在执行完成后必须显式的重新启用。
	- `IRQF_NO_THREAD` ：禁止线程化中断，强制使用原子上下文处理程序，用于极低延迟或不可睡眠的中断处理。
	- `IRQF_NO_AUTOEN` ：不自动启用中断，需手动调用 `enable_irq()` ，可以灵活控制中断启用时机，例如初始化阶段延迟启用。
4. 休眠与唤醒管理：
	- `IRQF_NO_SUSPEND` ：在系统挂起期间不关闭此中断，用于电源按钮、RTC等外部唤醒设备。
		- 该中断不保证中断能唤醒系统，需结合设备唤醒能力配置。
	- `IRQF_FORCE_RESUME` ：在系统唤醒后强制重新启用中断，修复某些休眠后中断未正确恢复的场景。
	- `IRQF_EARLY_RESUME` ：在系统唤醒早期阶段恢复中断
	- `IRQF_COND_SUSPEND` ：可以动态的决定是否可以被挂起。
		- 使用 `enable_irq_wake(irq)` 可以把该中断作为唤醒中断，从而在系统挂起期间不关闭此中断。
		- 使用 `disable_irq(irq)` 可以禁用该中断。

### 13.3.2 中断号选用原则 ^adyua2

Linux内核中，并非所有的中断都可以自由选择中断号：
- 部分中断的中断号是由硬件进行编码，一般在设备树文件中
- 现代的PCI、USB设备通常支持灵活的中断分配
以RK3588为例， `rk3588-base.dtsi` 中有如下片段

```dts
uart0: serial@fd890000 {  
    compatible = "rockchip,rk3588-uart", "snps,dw-apb-uart";  
    reg = <0x0 0xfd890000 0x0 0x100>;  
    interrupts = <GIC_SPI 331 IRQ_TYPE_LEVEL_HIGH 0>;  
    clocks = <&cru SCLK_UART0>, <&cru PCLK_UART0>;  
    clock-names = "baudclk", "apb_pclk";  
    dmas = <&dmac0 6>, <&dmac0 7>;  
    dma-names = "tx", "rx";  
    pinctrl-0 = <&uart0m1_xfer>;  
    pinctrl-names = "default";  
    reg-shift = <2>;  
    reg-io-width = <4>;  
    status = "disabled";  
};
```

该片段将 `uart0` 的中断定义到了共享外设中断( `GIC_SPI` )的331号中断中。
因此在进行驱动程序编写时，<span style="background:#fff88f"><font color="#c00000">需要使用如下的API进行中断号获取</font></span>：
- 对于通用设备，可以使用如下的API获取中断号：
```C
#include <linux/platform_device.h>
int platform_get_irq(struct platform_device *dev, unsigned int n);
```
- 对于PCI设备，可以使用如下的API获取中断向量：
```C
#include <linux/pci.h>
// 申请含有指定中断数量的中断向量
int pci_alloc_irq_vectors(struct pci_dev *dev, unsigned int min_vecs, unsigned int max_vecs, unsigned int flags);
// 获取中断向量中的第nr个中断号
int pci_irq_vector(struct pci_dev *dev, unsigned int nr);
```

### 13.3.3 中断的取消注册

中断取消应当使用如下的API：

```C
#include <linux/interrupt.h>
const void *free_irq(unsigned int irq, void *dev_id);
```

关于 `free_irq` 函数的说明：
1. 调用该函数时，内核会等待并保证当前正在运行的中断处理例程退出。
2. <font color="#c00000">调用该函数之前</font>，<font color="#c00000">必须保证设备已停止触发该中断</font>。
3. 保证该函数执行周期内，`dev_id` 指向的数据(如有)有效。

关于 `dev` 参数的说明： ^rqxyj6
1. 该 `dev_id` 参数必须和中断注册时的 `dev` 参数保持一致。
2. 该 `dev_id` 参数必须全内核中唯一，否则会冲突(因此通常取dev对象的指针)。
3. 该 `dev_id` 参数<span style="background:#fff88f"><font color="#c00000">用于在内核的中断管理数据结构</font></span>( `desc` )<span style="background:#fff88f"><font color="#c00000">中当作Key值</font></span>。

## 13.4 禁用和启用中断

### 13.4.1 禁用启用单个中断

```C
#include <linux/interrupts.h>

// 禁用并等待当前的中断例程完成，要避免死锁
void disable_irq(unsigned int irq);
// 禁用中断，但不等待例程完成，要注意竞态
void disable_irq_nosync(unsigned int irq);
bool disable_hardirq(unsigned int irq);
void disable_percpu_irq(unsigned int irq);

void enable_irq(unsigned int irq);
void enable_percpu_irq(unsigned int irq, unsigned int type);
```

在Linux内核内部维护了一个计数器，只有中断启用次数大于等于禁用次数时，中断才会被启动(当启用大于禁用时，会抛WARN日志)。而平台的中断启停实现则是修改可编程中断控制器指定中断的掩码，从而在所有的处理器上禁用或启用中断。

### 13.4.2 禁用启用当前处理器的全部中断

```C
#include <linux/irqflags.h>

// 注意下列函数为宏函数，下列原型并非实际原型
void local_irq_save(unsigned long flags);
void local_irq_disable(void);

void local_irq_restore(unsigned long flags);
void local_irq_enable(void);
```

与上一子章节不同的是，某个核心全部中断的开启和关闭并没有维护计数器。

## 13.5 顶半部和底半部

通常来说，可以把必须在中断内快速完成的工作和可以稍微延后到中断外的工作分为中断的顶半部和底半部，从而优化中断例程的运行时间，这部分讨论可见[[Linux驱动开发笔记#^meiuw1|tasklet机制]]章节。不过目前Linux已经不再推荐继续使用tasklet，因此可以考虑使用线程化中断技术：
- 将快速响应的部分留在中断例程中，从而保证中断响应的实时性
- 随后可以把耗时操作放入内核线程中，优化了中断例程的响应速度，同时可以支持休眠、调度等操作。
- 同步机制可以使用自旋锁、信号量等经典机制。
此外使用[[Linux驱动开发笔记#^qihja2|工作队列]]机制也可以完成同步功能。

## 13.6 中断共享 ^c8eb6k

如前文中断的注册章节所述，共享中断注册使用如下API时：

```C
#include <linux/interrupts.h>
int request_irq(unsigned int irq, irq_handler_t handler, unsigned long flags, const char *name, void *dev);
```

参数：
- `handle` ：必须可以识别属于自己的中断
- `flags` ：
	- 必须选择 `IRQF_SHARED` 等中断共享控制掩码
	- 中断触发方式的掩码必须一致
- `dev` ：
	- <font color="#c00000">必须唯一</font>，且不可为NULL。通常指向模块的地址空间。
	- 在释放中断注册时，
且成功注册的条件必须为如下之一：
1. 中断线空闲
2. 已经注册为共享的中断线，且触发方式一致

共享中断在 `cat /proc/interrupts` 中的体现如下方的中断号11，由 `virtio2` 和 `USB1` 共享：
![[Linux驱动开发笔记#^b47kyp]]

# 14 内核的数据类型

本章并无太多难点，更多的是使用规范类问题。
参考资料：
- [Linux kernel coding style — The Linux Kernel documentation](https://www.kernel.org/doc/html/latest/process/coding-style.html)

## 14.1 整型及位宽

关于 `u8` 、 `s8` 与 `uint8_t` 、`int8_t` ：

> Although it would only take a short amount of time for the eyes and brain to become accustomed to the standard types like `uint32_t`, some people object to their use anyway.
> 
> Therefore, the Linux-specific `u8/u16/u32/u64` types and their signed equivalents which are identical to standard types are permitted -- although they are not mandatory in new code of your own.
> 
> When editing existing code which already uses one or the other set of types, you should conform to the existing choices in that code.

即：
1. <font color="#c00000">在新代码中</font>推荐使用 `<linux/types.h>` 中的 `u8` 、 `s8` 等，但也允许使用 `<stdint.h>` 中的 `uint8_t` 和 `int8_t`
2. <span style="background:#fff88f"><font color="#c00000">在老代码中一定要和原代码中的风格保持一致</font></span>，不可混用。

## 14.2 基本数据结构

基本索引：
- [[基本数据结构(types.h部分)]]
	- [[链表(list.h)#^xl7wru|链表锚点]]

## 14.3 其他若干问题

直接参考[Linux 内核代码风格 — The Linux Kernel documentation](https://www.kernel.org/doc/html/latest/translations/zh_CN/process/coding-style.html)(中文版)即可。

# 15 PCI驱动程序

PCI的总线拓扑结构如下图所示：
	![[Pasted image 20250326165450.png]]


几个关键概念：
- PCI根复合体(Root Complex，RC)：是CPU和PCI设备的连接枢纽，其负责如下的功能：
	- 组织PCI拓扑结构，管理PCI根总线
	- 内存访问路由：确保 PCIe 设备的读写请求正确映射到系统内存地址空间。
- PCI根总线：是PCI拓扑的起点。在协议上并没有限制PCI根总线的数量。
- PCI桥(Bridge)：实现PCI总线之间相互桥接通信的设备。其往往不止可以桥接PCI与PCI，还可以连接不同的PCI协议(PCI、PCI-X、PCIe x.0等)。
- PCI交换机(Switch)：可以把PCI交换机看成若干逻辑PCI桥的集合：
	![[Pasted image 20250326172040.png]]

几个额外注意点：
1. 直接与PCI根复合体相连接的总线为PCI根总线。
2. PCI Root Complex能够直接通过内存控制器访问物理内存而不需要经过CPU的逐一处理。
3. 在早期计算机中，PCI根复合体往往集成在北桥中。而在现代计算机中，PCI根复合体会集成到每个物理CPU中。

回到Linux软件层面：







使用 `lspci` 指令













# 16 USB驱动程序


# 17 Linux设备模型 ^drcdil

## 17.1 kobject

在学习Linux设备模型之前，应当简单了解一些Linux内核如何管理"对象"，即 `kobject` 。
`kobject` 被定义于 `linux/kobject.h` 中，其定义如下：

```C
struct kobject {
	const char		*name;
	struct list_head	entry;
	struct kobject		*parent;
	struct kset		*kset;
	const struct kobj_type	*ktype;
	struct kernfs_node	*sd; /* sysfs directory entry */
	struct kref		kref;

	unsigned int state_initialized:1;
	unsigned int state_in_sysfs:1;
	unsigned int state_add_uevent_sent:1;
	unsigned int state_remove_uevent_sent:1;
	unsigned int uevent_suppress:1;

#ifdef CONFIG_DEBUG_KOBJECT_RELEASE
	struct delayed_work	release;
#endif
};
```

在C语言中并没有提供继承关系，因此其需要在其他的结构体中嵌入该结构体，例如字符设备的 `cdev` ：

```C
struct cdev {
	struct kobject kobj;
	struct module *owner;
	const struct file_operations *ops;
	struct list_head list;
	dev_t dev;
	unsigned int count;
} __randomize_layout;
```

通过"继承"该 `kobject` ，Linux内核可以完成统一的引用计数、sysfs表述、热拔插处理等特性。
与[[链表(list.h)#^xl7wru|链表锚点]]等数据结构相同的是，可以使用 `container_of` 宏查找 `kobject` 的host数据结构，详见下方子章节。

### 17.1.1 kobject相关API ^blb9e0

#### 17.1.1.1 kobject的初始化

```C
#include <linux/kobject.h>
void kobject_init(struct kobject *kobj, const struct kobj_type *ktype);
```

其中：
- `kobj_type` 是kobject中的一个复杂的结构体，可以完成众多标准化行为，其必不可少的属性为：
	- `kobj_type.release` ：当引用计数为0时会被调用。
	其他成员可暂时先不用了解
- <span style="background:#fff88f"><font color="#c00000">引用计数器会被设置为1</font></span>。

#### 17.1.1.2 kobject的引用计数

```C
// 增加引用计数
struct kobject *kobject_get(struct kobject *kobj);
struct kobject * __must_check kobject_get_unless_zero(struct kobject *kobj);
// 释放引用计数，如果释放后为0则调用上述的kobj_type.release
void kobject_put(struct kobject *kobj);
```

#### 17.1.1.3 kobject设置名字

```C
#include <linux/kobject.h>
int kobject_set_name(struct kobject *kobj, const char *name, ...);
```

该函数可能会设置失败，例如：
- 当可变参数与其 `fmt` 中预留类型不一致
- 无法成功分配内存时
- 名称不合法时

而 `kobject` 的名称会直接决定：
- 文件系统中，`/sys` <font color="#c00000">下的绝大多数路径及子路径名由kobject的name决定</font>，<font color="#c00000">递归关系与继承关系保持一致</font>。
	- 许多用户态工具(例如 `lsusb` `lspci` 等均依赖于此)
	- 而子路径下还通常会保留一些文件，这些文件可以是由驱动程序进行添加，也可以由设备模型的 `ktype` 提供默认属性自动创建。
- `kobject` 的名称在调试和日志追踪中也会被使用。

因此，`kobject` 的名称应当：
- 不能包含反斜杠
- 强烈拒绝使用空格

## 17.2 kobject层次结构、kset和子系统

### 17.2.1 kobject层次结构

在内核中，各个模块之间有层次结构关系。也正如前文所述，kobject可以提供统一的引用计数、sysfs表述、热拔插处理等特性。而在层次结构管理上，内核为kobject提供了两种<font color="#c00000">独立的</font>机制：
- parent指针：指向其父对象<u>的kobject节点</u>
- kset：往往(并不绝对，这也是所谓的 "独立")就是该object的父对象
其数据结构表示为：
	![[msedge_X79BSHCPBB.png]]
(注意有深浅两条线，深虚线指向父对象的 `kobject` 成员，浅虚线指向父对象)

### 17.2.2 kset

kset有如后续子章节所示的常用接口。

#### 17.2.2.1 kset的普通初始化和设置接口

```C
// 一次性完成 `kset` 的分配、初始化、添加到 sysfs：
struct kset *kset_create_and_add(const char *name,  
    const struct kset_uevent_ops *uevent_ops,  
    struct kobject *parent_kobj);
    
// 分步完成
void kset_init(struct kset *k);
int kset_register(struct kset *k);

// 引用计数
struct kset *kset_get(struct kset *k);
void kset_put(struct kset *k);
```

注：
- 由于 `kset` 内嵌了 `kobject` ，因此为 `kset` 设置名字的方法依旧使用 `kobject` 对应的方法。

#### 17.2.2.2 将kobject添加到内核模型中(sysfs和kset中)

函数原型：

```C
#include "linux/kobject.h"
int kobject_add(struct kobject *kobj, struct kobject *parent, const char *fmt, ...);
```

其中：
- `kobj` ：需要添加到内核模型中的 `kobject` 指针，<span style="background:#fff88f"><font color="#c00000">必须</font></span>：
	- <font color="#c00000">已通过</font> `kobject_init()` <font color="#c00000">初始化</font>
	- <font color="#c00000">设置好其</font> `ktype` 
	- <font color="#c00000">设置好其</font> `kset` 
- `parent` ：父 `kobject` 的指针，用于构建层次结构。若为 `NULL` 则会：
  - 使用 `kobj->parent` 中的值，若仍为 `NULL` 则视为根节点，创建于 `/sys` 下。
- `fmt` ：格式化字符串，用于生成 `kobj` 在sysfs中的目录名称(直接在/sys中创建新的文件目录<font color="#c00000">需三思</font>，详见子系统章节)。

本函数会：
1. 向 `kobj->set` 中添加本obj。
2. 在sysfs中的父obj对应目录下注册节点。
3. <font color="#c00000">增加对父对象的引用计数</font>。

例如基础例子：

```C
my_kobj = kzalloc(sizeof(*my_kobj), GFP_KERNEL); 
kobject_init(my_kobj, &my_ktype); // 定义 my_ktype 的 release 方法 
kobject_add(my_kobj, NULL, "my_custom_object"); // 在 sysfs 根目录下创建目录
```

稍微复杂一点的例子：

```C
// 创建 kset
my_kset = kset_create_and_add("my_kset", NULL, NULL);
if (!my_kset)
    return -ENOMEM;
// 创建并初始化 kobject
struct kobject *kobj = kzalloc(sizeof(*kobj), GFP_KERNEL);
if (!kobj) {
    kset_unregister(my_kset);
    return -ENOMEM;
}
kobject_init(kobj, &my_ktype);
kobj->kset = my_kset; // 关联到 kset(但此时并未实际添加)

// 添加到 sysfs、kset、parent中。
int ret = kobject_add(kobj, parent, "my_object");
if (ret) {
    kobject_put(kobj);
    kset_unregister(my_kset);
    return ret;
}
```

注：
- 执行本步骤<font color="#c00000">之前</font>，<font color="#c00000">需要手动配置</font> `kobject` <font color="#c00000">中的</font> `kset` <font color="#c00000">成员</font>，随后在本步骤中才会向kset所维护的循环链表中添加元素。

### 17.2.3 子系统

在Linux内核中，若干kset聚类后被封装为一个"子系统"，例如"块设备子系统"、"总线子系统"、"设备分类子系统"等。

Linux的子系统通常会显示在sysfs的顶层(但不绝对)，例如上述子系统：
- `/sys/block` ：块设备子系统
- `/sys/bus` ：总线子系统
- `/sys/class` ：设备分类子系统

在早期的Linux版本(Linux2.6以前)中，子系统有专门的数据结构 `struct subsystem` ，但是在新版本的Linux中完全依赖于 `kset` 和 `kobject` 进行实现。如下是普通 `kset` 和子系统之间的区别：

| <center>特征</center> | <center>子系统</center>             | <center>普通 `kset`</center> |
| ------------------- | -------------------------------- | -------------------------- |
| 注册位置                | 通常直接挂载到 `sysfs` 根目录下             | 挂载到其他 `kobject/kset` 的子目录  |
| 功能角色                | 管理一类核心硬件或内核功能(如总线、设备类)           | 用于组织局部对象(如一个设备驱动管理的子设备)    |
| 初始化时机               | 内核启动早期由核心模块初始化(如 `init/main.c` ) | 动态创建(如模块加载时)               |
| 父对象                 | 父 `kobject` 通常为 `NULL` 或内核根对象    | 父对象明确指向某个子系统或设备            |

因此现在的子系统更是一个逻辑概念。

## 17.3 kobj_type

上述的 `kobject` 和 `kset` 很好地处理了内核对象之间的层次关系。而 `kobject` 被设计用于嵌入各类具体的内核对象中，但上述设计并不负责实现各类内核对象的具体实现。
各类 `kobject` 内核对象的具体实现被交由 `kobj_type` 进行管理，其定义如下：

```C
struct kobj_type {
	// 释放资源函数
	void (*release)(struct kobject *kobj);
	// 仅服务默认属性组中的普通属性的文本编解码接口
	const struct sysfs_ops *sysfs_ops;
	// 默认属性组(替代 default_attrs)
	const struct attribute_group **default_groups;
	// 子对象命名空间类型
	const struct kobj_ns_type_operations *(*child_ns_type)(const struct kobject *kobj);
	// 命名空间回调
	const void *(*namespace)(const struct kobject *kobj);
	// 文件权限
	void (*get_ownership)(const struct kobject *kobj, kuid_t *uid, kgid_t *gid);
};
```

### 17.3.1 属性

正如前文章节所述，sysfs下绝大多数的文件夹是由kobject的层次结构决定(或者说文件夹反映了层次结构)。

而除了文件夹以外，sysfs下还有很多普通文件或链接文件。其中，大部分普通文件反映了 `kobject` 所暴露的属性，这些属性可以按照如下两种方式划分：
1. 按数据类型划分：
	1. [[Linux驱动开发笔记#^6qh3el|普通属性]]：人眼可阅读的属性，通过字符串进行编解码表述，可以承载各种可由文本编码的信息。
	2. [[Linux驱动开发笔记#^fo54b5|二进制属性]]：二进制属性。
2. 按属性功能划分：
	1. [[Linux驱动开发笔记#^dt7ny4|默认属性组]]：在kobject初始化时创建，不可动态增删
	2. [[Linux驱动开发笔记#16 3 2 动态属性 dvhzcw|动态属性]]：在kobject运行时创建，可以动态增删

#### 17.3.1.1 普通属性 ^6qh3el

<font color="#9bbb59">普通属性</font>：
- <font color="#9bbb59">普通属性</font>对应普通的字符串属性，可以使用文本编码非文本信息进行传输。不过内核并未强制或检查实际传输的数据是文本还是二进制。<font color="#c00000">具体编码和解码分别通过</font> `show` <font color="#c00000">和</font> `store` <font color="#c00000">函数实现</font>，<span style="background:#fff88f"><font color="#c00000">这两个函数存储于</font></span> `kobject.ktype.sysfs_ops` <span style="background:#fff88f"><font color="#c00000">中</font></span>。服务普通属性的成员有：
	- `is_visible`
	- `attrs`

需要注意：
1. 普通属性的数据结构中仅仅记录了 `name` 和 `umode` 两个成员，其通过上述 `kobject.ktype.sysfs_ops` 中记录的 `show` 和 `store` 函数进行文本编解码。其中上述成员的作用如下：
	- `name` ：属性名。
	- `umode` ：默认权限，<font color="#c00000">会被上述</font> `is_visible` <font color="#c00000">覆盖</font>。
		- 该设计并非冗余设计，在不需要动态权限或未提供 `is_visible` 时则可以直接使用静态权限。

##### 17.3.1.1.1 普通属性的文本编解码接口(sysfs_ops)

正如上一章节所述，`ktype.sysfs_ops` <font color="#c00000">仅服务于</font>普通属性。该数据结构的定义如下：

```C
struct sysfs_ops {
	ssize_t	(*show)(struct kobject *kobj, struct attribute *attr, char *buffer);
	ssize_t	(*store)(struct kobject *kobj, struct attribute *attr, const char *buffer, size_t size);
};
```

其中：
- `show` 函数用于将属性转换为人眼可阅读的值，并要求：
	- 返回值为实际字符串长度，<font color="#c00000">并要求长度小于一个</font> `PAGE_SIZE` <font color="#c00000">大小</font>。若超过此大小则需要拆分成多个属性。
- `store` 函数用于将缓冲区中的数据解码，并在 `size` 中传入了数据的长度(依旧小于 `PAGE_SIZE` )，并需注意：
	- 如果输入的数据与预期不符，则应当返回一个负的错误码。
- 其他若干注意点见后续章节。

#### 17.3.1.2 二进制属性 ^fo54b5

<font color="#9bbb59">二进制属性</font>：
- <font color="#9bbb59">二进制属性</font>对应二进制数据。二进制属性的成员有：
	- `is_bin_visible`
	- `bin_size` ：<font color="#c00000">二进制属性大小，若没有上限则设置为0</font>。
	- `bin_attrs`

需要注意：
1. 二进制属性的数据结构中记录了部分VFS的函数接口，用于向内核提供二进制实现。
2. 关于"为什么二进制属性的数据结构中记录了操作函数，而普通属性却没有"：
	1. 普通属性被设计用于轻量级的数据操作，其绕开了VFS的文件操作抽象层，例如：
		1. <font color="#c00000">不需要</font> `open` <font color="#c00000">/</font> `release` <font color="#c00000">的生命周期管理，直接操作缓冲区</font>
		2. <font color="#c00000">无须维护和操作</font><span style="background:#fff88f"><font color="#c00000">每个属性唯一的</font></span> `file_p` <font color="#c00000">句柄</font>
		3. <span style="background:#fff88f"><font color="#c00000">因此没必要每个属性单独使用一个服务函数</font></span>，可以将若干个属性共用一个。
	2. 二进制属性要完全经过VFS，依旧需要按照普通文件接口设计，故需要内置一些VFS的调用函数。
3. 每次调用能操作的最大数据量是一页。
4. 更多注意点见后续章节。

### 17.3.2 默认属性组 ^dt7ny4

默认属性的最大特性是<span style="background:#fff88f"><font color="#c00000">其只能在kobject初始化时创建，不可动态增删</font></span>。这些属性由 `kobj_type` 中的 `default_groups` 成员记录：

```C
/**
 * struct attribute_group - data structure used to declare an attribute group.
 * @name:	Optional: Attribute group name
 *		If specified, the attribute group will be created in a
 *		new subdirectory with this name. Additionally when a
 *		group is named, @is_visible and @is_bin_visible may
 *		return SYSFS_GROUP_INVISIBLE to control visibility of
 *		the directory itself.
 * @is_visible:	Optional: Function to return permissions associated with an
 *		attribute of the group. Will be called repeatedly for
 *		each non-binary attribute in the group. Only read/write
 *		permissions as well as SYSFS_PREALLOC are accepted. Must
 *		return 0 if an attribute is not visible. The returned
 *		value will replace static permissions defined in struct
 *		attribute. Use SYSFS_GROUP_VISIBLE() when assigning this
 *		callback to specify separate _group_visible() and
 *		_attr_visible() handlers.
 * @is_bin_visible:
 *		Optional: Function to return permissions associated with a
 *		binary attribute of the group. Will be called repeatedly
 *		for each binary attribute in the group. Only read/write
 *		permissions as well as SYSFS_PREALLOC (and the
 *		visibility flags for named groups) are accepted. Must
 *		return 0 if a binary attribute is not visible. The
 *		returned value will replace static permissions defined
 *		in struct bin_attribute. If @is_visible is not set, Use
 *		SYSFS_GROUP_VISIBLE() when assigning this callback to
 *		specify separate _group_visible() and _attr_visible()
 *		handlers.
 * @bin_size:
 *		Optional: Function to return the size of a binary attribute
 *		of the group. Will be called repeatedly for each binary
 *		attribute in the group. Overwrites the size field embedded
 *		inside the attribute itself.
 * @attrs:	Pointer to NULL terminated list of attributes.
 * @bin_attrs:	Pointer to NULL terminated list of binary attributes.
 *		Either attrs or bin_attrs or both must be provided.
 */
struct attribute_group {
	const char		*name;
	umode_t			(*is_visible)(struct kobject *,
					              struct attribute *, int);
	umode_t			(*is_bin_visible)(struct kobject *,
						              const struct bin_attribute *, int);
	size_t			(*bin_size)(struct kobject *,
					            const struct bin_attribute *,
					            int);
	union {
		struct bin_attribute		**bin_attrs;
		const struct bin_attribute	*const *bin_attrs_new;
	};
};
```

上述数据结构各成员含义如下：

| <center>成员</center> | <center>作用</center>                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------ |
| `name`              | 属性组的名称：<br>- 若指定name，属性组会创建一个同名的子目录，所有属性文件将位于此目录下<br>- 若不指定name，属性文件直接位于父 `kobject` 的目录下，无中间子目录。 |
| `is_visible`        | 动态控制<font color="#9bbb59">普通属性</font>的可见性和权限。返回 `0` 表示属性不可见，返回权限掩码(如 `0644`)确定可见性及权限。            |
| `is_bin_visible`    | 动态控制<font color="#9bbb59">二进制属性</font>的可见性和权限，逻辑同 `is_visible`。                                  |
| `bin_size`          | 动态设置<font color="#9bbb59">二进制属性</font>的大小，覆盖 `struct bin_attribute` 中静态定义的 `size` 字段。            |
| `attrs`             | 指向以 `NULL` 结尾的<font color="#9bbb59">普通属性</font>数组。每个属性对应一个 sysfs 文件。                             |
| `bin_attrs`         | 指向以 `NULL` 结尾的<font color="#9bbb59">二进制属性</font>数组。使用联合体是为了兼容新旧内核的 API 差异。                       |

注：
1. 关于"默认属性组"，该属性组寄生于 `kobject.ktype.default_groups` 中，<span style="background:#fff88f"><font color="#c00000">并<u>仅能</u>在</font></span> `kobject` <span style="background:#fff88f"><font color="#c00000">初始化时注册</font></span>。<font color="#c00000">运行时注册需要依赖</font>[[Linux驱动开发笔记#^dvhzcw|动态属性]]<font color="#c00000">接口</font>。

### 17.3.3 动态属性 ^dvhzcw

正如上述章节所述，<span style="background:#fff88f"><font color="#c00000">默认属性仅能在初始化时被注册</font></span>，<font color="#c00000">无法在运行时动态创建</font>，<span style="background:#fff88f"><font color="#c00000">且严禁在运行时删除</font></span>(不过可以隐藏)。而动态属性可以满足上述需求，具体见子章节。

#### 17.3.3.1 普通属性

```C
#include <linux/sysfs.h>
int __must_check sysfs_create_file(struct kobject *kobj,  
                                   const struct attribute *attr);

void sysfs_remove_file(struct kobject *kobj,  
                       const struct attribute *attr);
```

在上述接口中需注意：
1. 调用 `sysfs_remove_file` 后，sysfs中的入口会立即消失。<span style="background:#fff88f"><font color="#c00000">但是在这之前已经打开了该文件的程序依旧可以正常访问</font></span>，<span style="background:#fff88f"><font color="#c00000">因此在show和store函数中需要正确处理这种情况</font></span>。 ^rw06xj

#### 17.3.3.2 二进制属性

```C
#include <linux/sysfs.h>
int sysfs_create_bin_file(struct kobject *kobj,  
                          const struct bin_attribute *attr);

void sysfs_remove_bin_file(struct kobject *kobj,  
                           const struct bin_attribute *attr);
```

注意：
1. 同上一章节注意点1。

### 17.3.4 符号链接

sysfs被设计为一个树结构，但是树形结构并不能满足所有需求，例如：
	某个USB摄像头位于 `/sys/device` 目录下(例如 `/sys/device/.../usb1/1-1/1-1.2` 下)，但是处于设计便利性考虑，其依旧需要在 `/sys/class/video4linux/` 目录下暴露该摄像头从而方便用户态程序访问，而无须遍历复杂的目录结构。
上述需求就需要使用符号链接特性完成，但是注意<font color="#c00000">符号链接</font><span style="background:#fff88f"><font color="#c00000">只能用于创建一个指向某个kobject(即对应目录)的目录</font></span>，<span style="background:#fff88f"><font color="#c00000">无法对某个其他kobject的某个属性创建符号链接</font></span>。

```C
#include <linux/sysfs.h>
int sysfs_create_link(struct kobject *kobj,
				      struct kobject *target, const char *name);
```

## 17.4 热拔插

通常来说内核态程序(例如驱动、模块等)均可以调用 `kobject_event` 触发事件，但是在设计约束中需要遵循设备模型规范，避免破坏系统稳定性。

### 17.4.1 热拔插事件的触发

热拔插事件的触发使用 `kobject_uevent` 接口：

```C
#include <linux/kobject.h>
/**
 * kobject_uevent - notify userspace by sending an uevent
 *
 * @kobj: struct kobject that the action is happening to
 * @action: action that is happening
 *
 * Returns 0 if kobject_uevent() is completed with success or the
 * corresponding error when it fails.
 */
int kobject_uevent(struct kobject *kobj, enum kobject_action action);
```

该接口触发时需要指定事件类型，属于热拔插事件的有：
- `KOBJ_ADD`
- `KOBJ_REMOVE`
此外，该接口可以触发的其他事件还有：

```C
/*
 * The actions here must match the index to the string array
 * in lib/kobject_uevent.c
 *
 * Do not add new actions here without checking with the driver-core
 * maintainers. Action strings are not meant to express subsystem
 * or device specific properties. In most cases you want to send a
 * kobject_uevent_env(kobj, KOBJ_CHANGE, env) with additional event
 * specific variables added to the event environment.
 */
enum kobject_action {
	KOBJ_ADD,        // 设备首次注册到内核
	KOBJ_REMOVE,     // 设备从内核注销
	KOBJ_CHANGE,     // 设备属性或状态变化(如磁盘容量更新、电源状态变更)
	KOBJ_MOVE,       // 设备路径或名称变更(如设备重命名)
	KOBJ_ONLINE,     // 设备逻辑上线(如启用离线硬盘)
	KOBJ_OFFLINE,    // 设备逻辑下线(如禁用硬盘)
	KOBJ_BIND,       // 设备与驱动绑定(如手动绑定驱动)
	KOBJ_UNBIND,     // 设备与驱动解绑(如手动卸载驱动)
};
```

### 17.4.2 用户空间设备管理(udev、mdev)

#TODO

## 17.5 总线、设备和驱动程序 ^ygjg2l

在上述的Linux字符设备中，我们似乎已经能够通过实现简单的 `cdev` 来实现字符设备的驱动了，而对于块设备等也可以按照此种方式解决。但是不妨思考下面的情况：
- 某个设备需要依赖总线A，以及需要配置DMA、寄存器、引脚等信息。
- 该总线以及这些寄存器、引脚、DMA在不同的CPU平台上的配置信息甚至调用方法都不同。
- 而总线A下往往又不止挂载一个设备。
那么应当如何跨平台通用性呢？部分配置可以依靠加载模块时传入参数处理(如寄存器、DMA区段等)，但是：
- 当各个平台上的总线接口及操作方式不一致时。
- 需要协调总线上的不同设备时。
就难以处理了，必然会导致大量的逻辑冲突和重复代码。

因此Linux将总线、驱动程序以及设备单独抽象，来解决上述问题。

Linux的总线-设备-驱动程序模型是一个复杂的机制，本章节仅做基础概览，详细可见[[Linux设备模型]]。

基本概念：
- <font color="#9bbb59">总线</font>(bus)：总线是处理器与一个或多个设备之间的通道。其描述了设备如何连接到系统。
	- 在设备模型中，所有的设备都通过总线相连，且总线之间可以互相插入(例如一个USB控制器通常是一个PCI设备)。
	- 生命周期：静态的，在内核初始化时构造，不随硬件拔插变化。
	- 职责：
		- <font color="#c00000">负责设备与驱动匹配</font>：当设备或驱动注册时，总线尝试匹配并绑定二者。
		- 热拔插事件处理
	- sysfs中的位置： `/sys/bus/${bus}/`
- <font color="#9bbb59">设备</font>(device)：描述硬件实体，是硬件实体的抽象。
	- 生命周期：动态，随硬件或模块加载和卸载
	- 职责：
		- 描述硬件属性(地址、型号、状态等)
		- 通过 `struct device` 表示
	- sysfs中的位置： `/sys/devices/`
- <font color="#9bbb59">驱动</font>(driver)：描述如何控制硬件
	- 生命周期：动态，随模块加载和卸载
	- 职责：
		- 实现硬件的操作方法
		- 通过 `struct device_driver` 表示
	- sysfs中的位置： `/sys/bus/<bus>/drivers/`

Linux设备概览可见下图：
	![[Linux设备模型概览.drawio.svg]]

总线-设备-驱动程序是linux的设备模型，不过需要注意的是：
1. <font color="#c00000">并不是所有的字符设备都符合该模型</font>，<font color="#c00000">简单的字符设备并不符合该模型</font>。
2. 块设备符合该模型。

### 17.5.1 总线

总线的主要职责有：
- <font color="#c00000">负责设备与驱动匹配</font>：当设备或驱动注册时，总线尝试匹配并绑定二者。
- 热拔插事件处理：

#### 17.5.1.1 总线类型抽象(bus_type)

<font color="#c00000">总线</font><span style="background:#fff88f"><font color="#c00000">类型</font></span>的数据结构定义如下，不过总线的具体实现对大多数驱动程序开发者并不必要。

```C
#include <linux/device/bus.h>

/**
 * struct bus_type - The bus type of the device
 *
 * @name:	The name of the bus.
 * @dev_name:	Used for subsystems to enumerate devices like ("foo%u", dev->id).
 * @bus_groups:	Default attributes of the bus.
 * @dev_groups:	Default attributes of the devices on the bus.
 * @drv_groups: Default attributes of the device drivers on the bus.
 * @match:	Called, perhaps multiple times, whenever a new device or driver
 *		is added for this bus. It should return a positive value if the
 *		given device can be handled by the given driver and zero
 *		otherwise. It may also return error code if determining that
 *		the driver supports the device is not possible. In case of
 *		-EPROBE_DEFER it will queue the device for deferred probing.
 * @uevent:	Called when a device is added, removed, or a few other things
 *		that generate uevents to add the environment variables.
 * @probe:	Called when a new device or driver add to this bus, and callback
 *		the specific driver's probe to initial the matched device.
 * @sync_state:	Called to sync device state to software state after all the
 *		state tracking consumers linked to this device (present at
 *		the time of late_initcall) have successfully bound to a
 *		driver. If the device has no consumers, this function will
 *		be called at late_initcall_sync level. If the device has
 *		consumers that are never bound to a driver, this function
 *		will never get called until they do.
 * @remove:	Called when a device removed from this bus.
 * @shutdown:	Called at shut-down time to quiesce the device.
 *
 * @online:	Called to put the device back online (after offlining it).
 * @offline:	Called to put the device offline for hot-removal. May fail.
 *
 * @suspend:	Called when a device on this bus wants to go to sleep mode.
 * @resume:	Called to bring a device on this bus out of sleep mode.
 * @num_vf:	Called to find out how many virtual functions a device on this
 *		bus supports.
 * @dma_configure:	Called to setup DMA configuration on a device on
 *			this bus.
 * @dma_cleanup:	Called to cleanup DMA configuration on a device on
 *			this bus.
 * @pm:		Power management operations of this bus, callback the specific
 *		device driver's pm-ops.
 * @need_parent_lock:	When probing or removing a device on this bus, the
 *			device core should lock the device's parent.
 *
 * A bus is a channel between the processor and one or more devices. For the
 * purposes of the device model, all devices are connected via a bus, even if
 * it is an internal, virtual, "platform" bus. Buses can plug into each other.
 * A USB controller is usually a PCI device, for example. The device model
 * represents the actual connections between buses and the devices they control.
 * A bus is represented by the bus_type structure. It contains the name, the
 * default attributes, the bus' methods, PM operations, and the driver core's
 * private data.
 */
struct bus_type {
	const char		*name;
	const char		*dev_name;
	const struct attribute_group **bus_groups;
	const struct attribute_group **dev_groups;
	const struct attribute_group **drv_groups;

	int (*match)(struct device *dev, struct device_driver *drv);
	int (*uevent)(const struct device *dev, struct kobj_uevent_env *env);
	int (*probe)(struct device *dev);
	void (*sync_state)(struct device *dev);
	void (*remove)(struct device *dev);
	void (*shutdown)(struct device *dev);

	int (*online)(struct device *dev);
	int (*offline)(struct device *dev);

	int (*suspend)(struct device *dev, pm_message_t state);
	int (*resume)(struct device *dev);

	int (*num_vf)(struct device *dev);

	int (*dma_configure)(struct device *dev);
	void (*dma_cleanup)(struct device *dev);

	const struct dev_pm_ops *pm;

	bool need_parent_lock;
};
```

需要注意：
1. <font color="#c00000">该数据结构描述的是总线</font><span style="background:#fff88f"><font color="#c00000">类型</font></span>，在系统中无论该总线<span style="background:#fff88f"><font color="#c00000">是否有多个</font></span>，是否被热拔插，其<span style="background:#fff88f"><font color="#c00000">在内核初始化阶段</font></span><font color="#c00000">一定会被实例化一个</font>，<span style="background:#fff88f"><font color="#c00000">且只会被实例化一个</font></span>。该数据结构为总线类型(PCI、USB等)的抽象。
2. 该结构体将与总线实例无关的特性统一管理到一起，增加了可移植性(例如 `.match` 成员)

上述数据结构中，基本信息成员有：
- `name` ：总线类型的名称，在 `/sys/bus/` 下显示。
- `dev_name` ：总线下的子设备命名模板，<font color="#c00000">该成员并非强制</font>，<span style="background:#fff88f"><font color="#c00000">且通常用于定义常量设备名</font></span>，具体命名规则取决于总线代码实现，详见[[Linux驱动开发笔记#^4d2k0x|bus_type.drv_name]]。
- `bus_groups` ：总线自身的默认属性组，详见[[Linux驱动开发笔记#^xdmvsy|总线属性]]。
- `dev_groups` ：总线下所有设备的默认属性组，详见[[Linux驱动开发笔记#^xdmvsy|总线属性]]。
- `drv_groups` ：总线下所有驱动的默认属性组，详见[[Linux驱动开发笔记#^xdmvsy|总线属性]]。
核心回调函数成员有：
- `match` ：<span style="background:#fff88f"><font color="#c00000">设备和驱动匹配的函数逻辑</font></span>，详见：[[Linux驱动开发笔记#^d8ytfa|bus_type.match]]
- `uevent` ：处理热拔插事件
- `probe` ：<span style="background:#fff88f"><font color="#c00000">设备探测入口函数</font></span>，当 `match` 成功匹配到设备和驱动后，会调用驱动的 `probe` 函数<font color="#c00000">对设备进行初始化等</font>，详见：[[Linux驱动开发笔记#^y39y0v|bus_type.probe]]。
- `sync_state` ：同步设备状态，在所有依赖该设备的对象(例如驱动、软件或硬件实体)绑定完成后调用(如果驱动未加载或返回错误，则不会触发该函数)。
- `remove` ：设备移除时调用的函数
- `shutdown` ：系统关机时调用的函数，用于安全停止设备
电源管理成员有：
- `suspend` ：设备进入睡眠模式前的回调，可用于保存寄存器状态等。
- `resume` ：设备从睡眠模式唤醒后的回调，可用于恢复寄存器状态等。
- `pm` ：总线级别的电源管理操作集，例如 `suspend_late` 、 `resume_early` 等。
设备状态管理成员有：
- `online` ：将设备重新上线，例如热插入
- `offline` ：将设备下线，准备热移除，但可能因为设备占用无法移除。
高级功能：
- `num_vf` ：查询设备支持的虚拟函数数量
- `dma_configure` ：配置设备的DMA参数，例如IOMMU映射
- `dma_cleanup` ：清除设备的DMA配置
其他配置：
- `need_parent_lock` ：指定在探测或移除设备时，是否需要锁定父设备的互斥量。

##### 17.5.1.1.1 bus_type.drv_name ^4d2k0x

该成员并非强制的，例如PCI总线中就未从该成员导入模板，而是用 `dev_set_name` 为设备设置名称时，使用了常量字符串的模板：

```C
dev_set_name(&dev->dev, "%04x:%02x:%02x.%d", pci_domain_nr(bus),
	dev->bus->number, PCI_SLOT(devfn), PCI_FUNC(devfn));
```

其具体模板命名规则取决于总线代码实现，例如USB通常为：

```C
dev_set_name(&dev->dev, "usb%d", ...);
```

##### 17.5.1.1.2 bus_type.match ^d8ytfa

正如该成员的类型定义所示：

```C
int (*match)(struct device *dev, struct device_driver *drv);
```

该函数会接收一个 `struct device` 实例和一个 `struct device_driver` 实例，用于检测这两个实例是否匹配。那么明显地，当一个总线上的新设备或新驱动程序被添加时，内核会一次或多次调用该函数。

<span style="background:#fff88f"><font color="#c00000">该函数的返回值含义为</font></span>：
- 返回值为正数：表示设备与驱动匹配成功
- 返回值为零：表示设备与驱动不匹配
- 返回值为负数：表示匹配过程中发生错误

以PCI总线的 `match` 为例：

```C
/**
 * pci_bus_match - Tell if a PCI device structure has a matching PCI device id structure
 * @dev: the PCI device structure to match against
 * @drv: the device driver to search for matching PCI device id structures
 *
 * Used by a driver to check whether a PCI device present in the
 * system is in its list of supported devices. Returns the matching
 * pci_device_id structure or %NULL if there is no match.
 */
static int pci_bus_match(struct device *dev, struct device_driver *drv)
{
	struct pci_dev *pci_dev = to_pci_dev(dev);
	struct pci_driver *pci_drv;
	const struct pci_device_id *found_id;

	if (!pci_dev->match_driver)
		return 0;

	pci_drv = to_pci_driver(drv);
	found_id = pci_match_device(pci_drv, pci_dev);
	if (found_id)
		return 1;

	return 0;
}

/**
 * pci_match_device - See if a device matches a driver's list of IDs
 * @drv: the PCI driver to match against
 * @dev: the PCI device structure to match against
 *
 * Used by a driver to check whether a PCI device is in its list of
 * supported devices or in the dynids list, which may have been augmented
 * via the sysfs "new_id" file.  Returns the matching pci_device_id
 * structure or %NULL if there is no match.
 */
static const struct pci_device_id *pci_match_device(struct pci_driver *drv,
						    struct pci_dev *dev)
{
	struct pci_dynid *dynid;
	const struct pci_device_id *found_id = NULL, *ids;

	/* When driver_override is set, only bind to the matching driver */
	if (dev->driver_override && strcmp(dev->driver_override, drv->name))
		return NULL;

	/* Look at the dynamic ids first, before the static ones */
	spin_lock(&drv->dynids.lock);
	list_for_each_entry(dynid, &drv->dynids.list, node) {
		if (pci_match_one_device(&dynid->id, dev)) {
			found_id = &dynid->id;
			break;
		}
	}
	spin_unlock(&drv->dynids.lock);

	if (found_id)
		return found_id;

	for (ids = drv->id_table; (found_id = pci_match_id(ids, dev));
	     ids = found_id + 1) {
		/*
		 * The match table is split based on driver_override.
		 * In case override_only was set, enforce driver_override
		 * matching.
		 */
		if (found_id->override_only) {
			if (dev->driver_override)
				return found_id;
		} else {
			return found_id;
		}
	}

	/* driver_override will always match, send a dummy id */
	if (dev->driver_override)
		return &pci_device_id_any;
	return NULL;
}
```

其直接将设备的ID与驱动所支持的ID进行匹配，当匹配到时则返回非零值。

##### 17.5.1.1.3 bus_type.probe ^y39y0v

当上述 `match` 函数返回非零值时，内核会尝试调用总线的 `probe` 函数，在总线的 `probe` 函数中，会对设备进行总线层面的配置，并调用驱动对应的 `probe` 函数。<font color="#c00000">规定返回值为0时成功</font>，<font color="#c00000">负数时则失败</font>。

以PCI总线为例，其 `probe` 函数主要有如下流程：
1. 检查设备是否允许 `probe`
2. 为设备分配PCI中断号
3. 管理设备计数
4. 为设备和驱动执行 `probe` ：
	1. 检测驱动是否注册了 `probe` 方法
	2. 再次运行 `pci_match_device` 
	3. 按照调用栈间接调用驱动提供的 `probe` 方法：
		`pci_call_probe` -> `local_pci_probe` -> `pci_drv->probe(pci_dev, ddi->id);` 

```C
static int pci_device_probe(struct device *dev)
{
	int error;
	struct pci_dev *pci_dev = to_pci_dev(dev);
	struct pci_driver *drv = to_pci_driver(dev->driver);

	if (!pci_device_can_probe(pci_dev))
		return -ENODEV;

	pci_assign_irq(pci_dev);

	error = pcibios_alloc_irq(pci_dev);
	if (error < 0)
		return error;

	pci_dev_get(pci_dev);
	error = __pci_device_probe(drv, pci_dev);
	if (error) {
		pcibios_free_irq(pci_dev);
		pci_dev_put(pci_dev);
	}

	return error;
}
```

##### 17.5.1.1.4 总线属性 ^xdmvsy









##### 17.5.1.1.5 总线的驱动匹配与加载 ^nkmven

驱动匹配机制的核心实现位于 `dd.c` 中的 `__device_attach` 函数，其处理流程如下：
1. 检测当前设备是否正在处理中或已从系统中删除(通过 `dev->p->dead` )，在该状态下对该设备的任何异步事件都应退出且不采取任何行动。
2. 检测当前设备是否已经分配驱动：
	1. 若已分配驱动，则检测是否绑定驱动
		1. 若当前设备已绑定驱动，则返回 `1`
		2. 否则执行驱动绑定：
			1. 成功时返回 `1`
			2. 否则取消该设备分配
3. 若当前设备未分配驱动：
	1. 增加父设备的PM引用
	2. <font color="#c00000">遍历总线上所有驱动</font>并进行匹配(即遍历调用 `__device_attach_driver` 方法)：
		1. 执行 `ret = drv->bus->match` ，且若：
			1. 返回值(`ret`)为 ` 0 ` ，<font color="#c00000">表示不匹配</font>，向上返回 `0`
			2. 返回值 `ret == -EPROBE_DEFER`，<font color="#c00000">表示延迟探测</font>(通常是依赖的硬件未就绪)，则将该设备加入延迟探测队列，并向上返回 ` ret `
			3. 返回值为<font color="#c00000">其他负值</font>，<font color="#c00000">表示匹配发生错误</font>，则向上返回 `ret`
			4. 返回值大于0，<font color="#c00000">表示匹配成功</font>，继续后续操作
		2. 执行驱动的 `probe` 方法进行探测，<font color="#c00000">若成功则完成匹配成功并绑定驱动和设备</font>
	3. 若同时满足<font color="#c00000">下方三个条件</font>：
		- 所有驱动都无法完成匹配
		- 且允许异步探测(`allow_async`)
		- 且驱动有异步探测支持(`have_async`)
	    则：
		1. 打印调试信息
		2. 增加设备引用计数
		3. 标记 `async=true` 等待后续异步探测
	4. 否则(不同时满足上述三个条件)：
		1. 让设备进入空闲状态
		2. 对父设备减少引用计数

注：
1. <font color="#c00000">对于步骤2中的"已分配驱动但未绑定驱动"的情况</font>，其可能的原因有：
	- 手动绑定驱动
	- 在步骤3.2.1.2中被判定为需要延迟探测
	- 在步骤3.2.1.4中被判定为需要异步探测
2. `__device_attach` 函数的返回值：
	- 为0时表示未匹配或匹配失败，<font color="#c00000">后续会继续遍历下一个驱动</font>
	- 为1时表示匹配成功且完成设备-驱动绑定，<font color="#c00000">后续结束遍历</font>
	- 为负值时表示发生错误，<font color="#c00000">后续停止遍历并返回错误</font>。其中：
		- `-EPROBE_DEFER` 表示需要延迟探测

总结：
- <font color="#c00000">总线驱动的匹配与加载流程大致为</font>： ^ay1960
	1. 检测当前设备是否被强制绑定驱动、是否被标记为需要延迟探测、是否被标记为需要异步探测。若是，则尝试为设备绑定已经分配的驱动。
	2. 为设备尝试匹配并遍历总线上的驱动(执行总线的 `match` 函数)，检查当前设备是否被标记为需要延迟探测、需要异步探测。若需要则加入对应队列。
	3. 若成功匹配，则执行驱动的 `probe` 函数，完成设备-驱动绑定。若失败则尝试匹配下一个驱动。

#### 17.5.1.2 总线实例抽象()







### 17.5.2 设备

#### 17.5.2.1 设备对象的基本数据结构

设备的数据结构定义如下：

```C
/**
 * struct device - The basic device structure
 * @parent:	The device's "parent" device, the device to which it is attached.
 * 		In most cases, a parent device is some sort of bus or host
 * 		controller. If parent is NULL, the device, is a top-level device,
 * 		which is not usually what you want.
 * @p:		Holds the private data of the driver core portions of the device.
 * 		See the comment of the struct device_private for detail.
 * @kobj:	A top-level, abstract class from which other classes are derived.
 * @init_name:	Initial name of the device.
 * @type:	The type of device.
 * 		This identifies the device type and carries type-specific
 * 		information.
 * @mutex:	Mutex to synchronize calls to its driver.
 * @bus:	Type of bus device is on.
 * @driver:	Which driver has allocated this
 * @platform_data: Platform data specific to the device.
 * 		Example: For devices on custom boards, as typical of embedded
 * 		and SOC based hardware, Linux often uses platform_data to point
 * 		to board-specific structures describing devices and how they
 * 		are wired.  That can include what ports are available, chip
 * 		variants, which GPIO pins act in what additional roles, and so
 * 		on.  This shrinks the "Board Support Packages" (BSPs) and
 * 		minimizes board-specific #ifdefs in drivers.
 * @driver_data: Private pointer for driver specific info.
 * @links:	Links to suppliers and consumers of this device.
 * @power:	For device power management.
 *		See Documentation/driver-api/pm/devices.rst for details.
 * @pm_domain:	Provide callbacks that are executed during system suspend,
 * 		hibernation, system resume and during runtime PM transitions
 * 		along with subsystem-level and driver-level callbacks.
 * @em_pd:	device's energy model performance domain
 * @pins:	For device pin management.
 *		See Documentation/driver-api/pin-control.rst for details.
 * @msi:	MSI related data
 * @numa_node:	NUMA node this device is close to.
 * @dma_ops:    DMA mapping operations for this device.
 * @dma_mask:	Dma mask (if dma'ble device).
 * @coherent_dma_mask: Like dma_mask, but for alloc_coherent mapping as not all
 * 		hardware supports 64-bit addresses for consistent allocations
 * 		such descriptors.
 * @bus_dma_limit: Limit of an upstream bridge or bus which imposes a smaller
 *		DMA limit than the device itself supports.
 * @dma_range_map: map for DMA memory ranges relative to that of RAM
 * @dma_parms:	A low level driver may set these to teach IOMMU code about
 * 		segment limitations.
 * @dma_pools:	Dma pools (if dma'ble device).
 * @dma_mem:	Internal for coherent mem override.
 * @cma_area:	Contiguous memory area for dma allocations
 * @dma_io_tlb_mem: Software IO TLB allocator.  Not for driver use.
 * @dma_io_tlb_pools:	List of transient swiotlb memory pools.
 * @dma_io_tlb_lock:	Protects changes to the list of active pools.
 * @dma_uses_io_tlb: %true if device has used the software IO TLB.
 * @archdata:	For arch-specific additions.
 * @of_node:	Associated device tree node.
 * @fwnode:	Associated device node supplied by platform firmware.
 * @devt:	For creating the sysfs "dev".
 * @id:		device instance
 * @devres_lock: Spinlock to protect the resource of the device.
 * @devres_head: The resources list of the device.
 * @class:	The class of the device.
 * @groups:	Optional attribute groups.
 * @release:	Callback to free the device after all references have
 * 		gone away. This should be set by the allocator of the
 * 		device (i.e. the bus driver that discovered the device).
 * @iommu_group: IOMMU group the device belongs to.
 * @iommu:	Per device generic IOMMU runtime data
 * @physical_location: Describes physical location of the device connection
 *		point in the system housing.
 * @removable:  Whether the device can be removed from the system. This
 *              should be set by the subsystem / bus driver that discovered
 *              the device.
 *
 * @offline_disabled: If set, the device is permanently online.
 * @offline:	Set after successful invocation of bus type's .offline().
 * @of_node_reused: Set if the device-tree node is shared with an ancestor
 *              device.
 * @state_synced: The hardware state of this device has been synced to match
 *		  the software state of this device by calling the driver/bus
 *		  sync_state() callback.
 * @can_match:	The device has matched with a driver at least once or it is in
 *		a bus (like AMBA) which can't check for matching drivers until
 *		other devices probe successfully.
 * @dma_coherent: this particular device is dma coherent, even if the
 *		architecture supports non-coherent devices.
 * @dma_ops_bypass: If set to %true then the dma_ops are bypassed for the
 *		streaming DMA operations (->map_* / ->unmap_* / ->sync_*),
 *		and optionall (if the coherent mask is large enough) also
 *		for dma allocations.  This flag is managed by the dma ops
 *		instance from ->dma_supported.
 * @dma_skip_sync: DMA sync operations can be skipped for coherent buffers.
 * @dma_iommu: Device is using default IOMMU implementation for DMA and
 *		doesn't rely on dma_ops structure.
 *
 * At the lowest level, every device in a Linux system is represented by an
 * instance of struct device. The device structure contains the information
 * that the device model core needs to model the system. Most subsystems,
 * however, track additional information about the devices they host. As a
 * result, it is rare for devices to be represented by bare device structures;
 * instead, that structure, like kobject structures, is usually embedded within
 * a higher-level representation of the device.
 */
struct device {
	struct kobject kobj;
	struct device		*parent;

	struct device_private	*p;

	const char		*init_name; /* initial name of the device */
	const struct device_type *type;

	const struct bus_type	*bus;	/* type of bus device is on */
	struct device_driver *driver;	/* which driver has allocated this
					   device */
	void		*platform_data;	/* Platform specific data, device
					   core doesn't touch it */
	void		*driver_data;	/* Driver data, set and get with
					   dev_set_drvdata/dev_get_drvdata */
	struct mutex		mutex;	/* mutex to synchronize calls to
					 * its driver.
					 */

	struct dev_links_info	links;
	struct dev_pm_info	power;
	struct dev_pm_domain	*pm_domain;

#ifdef CONFIG_ENERGY_MODEL
	struct em_perf_domain	*em_pd;
#endif

#ifdef CONFIG_PINCTRL
	struct dev_pin_info	*pins;
#endif
	struct dev_msi_info	msi;
#ifdef CONFIG_ARCH_HAS_DMA_OPS
	const struct dma_map_ops *dma_ops;
#endif
	u64		*dma_mask;	/* dma mask (if dma'able device) */
	u64		coherent_dma_mask;/* Like dma_mask, but for
					     alloc_coherent mappings as
					     not all hardware supports
					     64 bit addresses for consistent
					     allocations such descriptors. */
	u64		bus_dma_limit;	/* upstream dma constraint */
	const struct bus_dma_region *dma_range_map;

	struct device_dma_parameters *dma_parms;

	struct list_head	dma_pools;	/* dma pools (if dma'ble) */

#ifdef CONFIG_DMA_DECLARE_COHERENT
	struct dma_coherent_mem	*dma_mem; /* internal for coherent mem
					     override */
#endif
#ifdef CONFIG_DMA_CMA
	struct cma *cma_area;		/* contiguous memory area for dma
					   allocations */
#endif
#ifdef CONFIG_SWIOTLB
	struct io_tlb_mem *dma_io_tlb_mem;
#endif
#ifdef CONFIG_SWIOTLB_DYNAMIC
	struct list_head dma_io_tlb_pools;
	spinlock_t dma_io_tlb_lock;
	bool dma_uses_io_tlb;
#endif
	/* arch specific additions */
	struct dev_archdata	archdata;

	struct device_node	*of_node; /* associated device tree node */
	struct fwnode_handle	*fwnode; /* firmware device node */

#ifdef CONFIG_NUMA
	int		numa_node;	/* NUMA node this device is close to */
#endif
	dev_t			devt;	/* dev_t, creates the sysfs "dev" */
	u32			id;	/* device instance */

	spinlock_t		devres_lock;
	struct list_head	devres_head;

	const struct class	*class;
	const struct attribute_group **groups;	/* optional groups */

	void	(*release)(struct device *dev);
	struct iommu_group	*iommu_group;
	struct dev_iommu	*iommu;

	struct device_physical_location *physical_location;

	enum device_removable	removable;

	bool			offline_disabled:1;
	bool			offline:1;
	bool			of_node_reused:1;
	bool			state_synced:1;
	bool			can_match:1;
#if defined(CONFIG_ARCH_HAS_SYNC_DMA_FOR_DEVICE) || \
    defined(CONFIG_ARCH_HAS_SYNC_DMA_FOR_CPU) || \
    defined(CONFIG_ARCH_HAS_SYNC_DMA_FOR_CPU_ALL)
	bool			dma_coherent:1;
#endif
#ifdef CONFIG_DMA_OPS_BYPASS
	bool			dma_ops_bypass:1;
#endif
#ifdef CONFIG_DMA_NEED_SYNC
	bool			dma_skip_sync:1;
#endif
#ifdef CONFIG_IOMMU_DMA
	bool			dma_iommu:1;
#endif
};
```

上述数据结构中，其成员：
- `struct kobject kobj` ：
	- 功能含义：内嵌的 `kobject` 提供sysfs表示、引用计数器等核心内核对象特性
	- 维护方：Linux设备模型自动维护，驱动不应直接操作
- `struct device *parent` ：
	- 功能含义：指向父设备(通常是总线/主机控制器)，构成设备树层次结构(例如将USB设备挂到USB控制器下)。
		- 该成员在部分总线下是自动生成的，在部分总线下是可以手动指定的。
		- 该成员与 `kobj->parent` 的区别点在于：
			 - `kobj->parent` 用于表示sysfs的层次结构
			 - 本 `parent` 成员用于描述设备的层次关系
		- <font color="#c00000">在事实上两者通常一致</font>，但是内核允许解耦和，例如：
			 1. <font color="#c00000">虚拟设备</font>(例如 `/dev/null` 或内存设备)<font color="#c00000">可能没有物理父设备</font>,其 `device.parent` 就为NULL。但是在sysfs里也不能直接挂到根目录中，因此其 `device.kobj.parent` 设置到该类别所属的kobj上，例如内存设备设置到了 `mem_class` 。
			 2. 有时sysfs规范和实际设备关系不符，例如网络设备需要放到 `/sys/class/net` ，但是其设备层次上的父设备是物理总线控制器。
			 3. 还有设备树的层级覆盖等问题。
	- 维护方：<font color="#c00000">驱动必须在注册前设置</font>
- `struct device_private *p` ：
	- 功能含义：驱动私有数据
	- 维护方：驱动可选设置和维护
- `const char *init_name` ：
	- 功能含义：设备的初始名称，总线和驱动可覆盖此名称
	- 维护方：驱动可选设置
- `const struct device_type *type` ：
	- 功能含义：设备的特定类型信息，例如PCI设备( `pci_dev_type` )、蓝牙主机( `bt_host` )等，通常在总线实现中定义与配置。
	- 维护方：
		- <font color="#c00000">标准总线设备通常由总线进行配置</font>(最常见，例如PCI、USB、Platfrom等)
		- 设备树或ACPI定义的硬件往往由设备树描述或固件配置
		- 特殊设备可在设备驱动程序的 `probe` 函数中配置
- `const struct bus_type *bus` ：
	- 功能含义：设备所属的总线类型，例如`&platform_bus_type`
	- 维护方：<font color="#c00000">驱动必须设置</font>
- `struct device_driver *driver` ：
	- 功能含义：当前设备绑定的驱动
	- 维护方：总线自动配置，驱动只读访问
- `void *platform_data` ：
	- 功能含义：<font color="#c00000">平台相关的私有数据</font>(即板级代码，即BSP的代码)，例如某一个具体平台的硬件相关数据，例如寄存器、中断号等...
	- 维护方：驱动可选设置
- `void *driver_data` ：
	- 功能含义：驱动私有数据
		- 可通过 `dev_get_drvdata` 接口访问
	- 维护方：驱动可选设置和维护
- `struct mutex mutex` ：
	- 功能含义：设备操作互斥锁
	- 维护方：驱动按需设置
- `struct dev_links_info links` 
- `struct dev_pm_info power` ：
	- 功能含义：电源管理状态
- `struct dev_pm_domain *pm_domain` ：
	- 
- `struct em_perf_domain *em_pd` ：
	- 功能含义：
- `struct dev_pin_info *pins` ：
- `struct dev_msi_info msi` ：
- `const struct dma_map_ops *dma_ops` ：
- `u64 *dma_mask` ：
	- 功能含义：DMA地址掩码，限制设备可访问的物理地址范围
- `u64 coherent_dma_mask` ：
- `u64 bus_dma_limit`
- `const struct bus_dma_region *dma_range_map` ：
- `struct device_dma_parameters *dma_parms` ：
	- 功能含义：DMA参数，用于优化DMA传输
- `struct list_head dma_pools`
- `struct dma_coherent_mem *dma_mem`
- `struct cma *cma_area`
- `struct io_tlb_mem *dma_io_tlb_mem`
- `struct list_head dma_io_tlb_pools`
- `spinlock_t dma_io_tlb_lock`
- `bool dma_uses_io_tlb`
- `struct dev_archdata archdata`
- `struct device_node *of_node` ：
	- 功能含义：关联的设备树节点
- `struct fwnode_handle *fwnode` ：
	- 功能含义：固件抽象节点，统一处理不同固件源的设备描述
- `int numa_node` ：
	- 功能含义：设备所属的NUMA节点，优化内存访问局部性
- `dev_t devt` ：
	- 功能含义：设备号
	- 维护方：<font color="#c00000">仅当需要暴露字符设备接口或块设备接口时才需要配置</font>。
- `u32 id` ：
	- 功能含义：设备的唯一标识符，不同设备类型的ID生成规则不一致，例如：
		- 平台设备：可以显式指定，或使用 `PLATFORM_DEVID_AUTO` 自动设置
		- PCI设备：由PCI位置(总线号、设备号、功能号)哈希生成唯一ID
		- 字符设备、块设备：由设备号转换而来。
		- ACPI设备：使用ACPI的 `_UID` 方法或固件提供的唯一标识符
		- 设备树设备：通过节点路径或 `reg` 属性生成
	- 维护方：
- `spinlock_t devres_lock`
- `struct list_head devres_head`
- `const struct class *class`
	- 功能含义：设备所属的类别，例如 `&input_class` ，用于分类管理
- `const struct attribute_group **groups`
- `void (*release)(struct device *dev)` ：
	- 功能含义：资源释放函数，<font color="#c00000"><u>当该设备的引用计数为0时</u></font>，内核会调用此方法
	- 维护方：<font color="#c00000">内核必须实现</font>
- `struct iommu_group *iommu_group`
- `struct dev_iommu *iommu`
- `struct device_physical_location *physical_location`
- `enum device_removable removable`
- `bool offline_disabled:1`
- `bool offline:1`
- `bool of_node_reused:1`
- `bool state_synced:1`
- `bool can_match:1`
- `bool dma_coherent:1`
- `bool dma_ops_bypass:1`
- `bool dma_skip_sync:1`
- `bool dma_iommu:1`

#### 17.5.2.2 设备对象的基础API

##### 17.5.2.2.1 注册设备


##### 17.5.2.2.2 删除设备


##### 17.5.2.2.3 


#### 17.5.2.3 高级设备与设备结构的嵌入

如上述数据结构所示， `struct device` 仅仅表示了一个基础的、通用的数据结构。和其他基础结构一样， `struct device` 也经常嵌入高级结构表示高级设备。例如块设备、PCI设备、USB设备中都要嵌入该设备结构：

```C
struct block_device {
	...
	struct device		bd_device;
} __randomize_layout;

struct pci_dev {
	...
	struct device	dev;			/* Generic device interface */
	...
}

struct usb_device {
	...
	struct device dev;
	...
}
```

而嵌入了 `struct device` 的设备对象往往都有其专属的API来代替默认接口，例如：
- 设备注册和释放接口(`device_register` 和 `device_unregister`)被替代为：
	- `pci_register_device` 和 `pci_unregister_device`
	- `usb_register_dev` 和 `usb_deregister_dev`
	- `i2c_new_device` 和 `i2c_unregister_device`
	- `platform_device_register` 和 `platform_device_unregister`
等。

在后续子章节中将<u>简单介绍</u>几个常用且重要的延伸高级设备，详细的讲解可见[[Linux设备模型]]。

##### 17.5.2.3.1 平台设备

<font color="#9bbb59">平台设备</font>(<font color="#9bbb59">platform device</font>)，重点在于嵌软层面的"platform"。与PCI、USB设备不同的是，<font color="#9bbb59">平台设备</font>指的是<font color="#c00000">不通过任何总线</font>，<font color="#c00000">直接连接到处理器的一种设备</font>。

平台设备的特性还有：
1. <font color="#c00000">通常不具备</font>传统总线的<font color="#c00000">自动枚举能力</font>，需要在内核中静态配置
2. <font color="#c00000">资源固定</font>，硬件所需要的资源(内存地址、寄存器、中断)在硬件设计时已确定
3. 在驱动开发时，其 `device.bus` 指向 `platform_bus_type`
4. <u>通常</u>依赖设备树进行配置

相关使用和API可见：[[平台总线]]

### 17.5.3 设备驱动程序

#### 17.5.3.1 设备驱动程序的基本数据结构

设备驱动程序的基本数据结构(`struct device_driver`)如章节[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/device/driver.h#^2dewi6|device_driver]]所示：
![[Linux内核原理及其开发/内核源码探析/内核源码分析/include/device/driver.h#device_driver 2dewi6]]

##### 17.5.3.1.1 device_driver.probe

probe函数表示对指定设备进行探测，其返回值定义如下：
- <font color="#c00000">成功时返回</font> `0`，设备成功初始化
- <font color="#c00000">失败时返回值负的错误码</font>，常用值有：
	- `-ENOMEM` ：内存不足
	- `-EINVAL` ：无效参数
	- `-ENODEV` ：设备不存在或不支持
	- `-EBUSY` ：请求的资源已被占用
	- `-EPROBE_DEFER` ：<font color="#c00000">表示请求延迟探测</font>

#### 17.5.3.2 设备模型层级与回调规定 ^4gz3xk

明显地，上述 `device_driver` 对象通常需要嵌入到更高级的对象当中去，例如 `platform_driver` 、 `spi_driver` 等。

而在Linux中一个常见的设计现象就是更高级设备模型通常会覆盖低级设备模型中的部分方法或属性，例如 `spi_driver` 的完整定义如下：

```C
struct spi_driver {
	const struct spi_device_id *id_table;
	int			(*probe)(struct spi_device *spi);
	void			(*remove)(struct spi_device *spi);
	void			(*shutdown)(struct spi_device *spi);
	struct device_driver	driver;
};
```

明显的，<font color="#c00000">其提供了部分基础驱动模型同名的方法</font>，<font color="#c00000">但又缺失了部分基础驱动模型的方法</font>(例如 `resume` 或 `pm.resume` )，那么针对这两个问题有如下的处理规则：
1. 对于同名方法，其规则为<span style="background:#fff88f"><font color="#c00000">优先使用更高级的同名方法</font></span>，其在内核中的处理路径基本如下：

```C
if (dev->bus && dev->bus->probe)
    return dev->bus->probe(dev);
else if (drv->probe)
    return drv->probe(dev);
```

2. 对于缺失的方法，则默认使用基础模型中提供的方法。

### 17.5.4 类







# 18 内存映射和DMA




# 19 块设备驱动程序





