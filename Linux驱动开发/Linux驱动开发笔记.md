---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 #Linux驱动开发 #操作系统

参考书籍：
- LINUX设备驱动程序（第三版），Jonathan Corbet，Alessandro Rubini，Greg Kroah-Hartman著；魏永明，耿岳，钟书毅译。
本笔记为入门学习笔记。

# 目录

```toc
```

## 1 Linux基础

### 1.1 Linux版本编号规则

Linux版本编号规则为：
```
VERSION.PATCHLEVEL.SUBLEVEL[-EXTRAVERSION]
```

其中：
- PATCHLEVEL有奇偶数之分，偶数是用于发行的稳定版本，奇数是开发过程中的快照版本
TODO


## 2 驱动设计的硬件基础
### 2.1 设备的分类及特点

Linux将设备分为了如下三个大类：
- 字符设备
- 块设备
- 网络设备

#### 2.1.1 字符设备

字符设备是指必须以<font color="#c00000">字节流顺序访问</font>的设备，如字符终端( `/dev/console` )、串口( `/dev/tty*` )、触摸屏、磁带驱动器、鼠标等。
- 其驱动程序至少需要实现 `open` 、 `close` 、 `read` 、 `write` 系统调用。
- 字符设备可以通过文件系统节点来访问(通常在 `/dev` 下)。
- 字符设备可以使用 `open()` 、 `read()` 、 `write()` 等方式进行访问。

#### 2.1.2 块设备

块设备允许按照任意顺序进行访问，以块为单位进行操作，如硬盘、eMMC等。
- 块设备有两种访问方式：
	1. 使用类似于 `dd` 的命令操作设备的块
	2. 在块设备上建立 `FAT` 、 `EXT4` 等文件系统后，使用文件系统的方式进行访问。
- 块设备也可以通过文件系统节点来访问(通常在 `/dev` 下)。
- 块设备可以使用 `open()` 、 `read()` 、 `write()` 等方式进行访问。

#### 2.1.3 网络设备

网络设备面向数据包的发送和接收设计，内核与网络设备之间的通信主要使用Socket。
- 一个纯软件实现的网络设备的例子为回环接口( `loopback` )。
- 网络设备并不是面向流的设备，因此通常不会被映射到Linux文件系统的文件和目录上，通常会被分配一个唯一的名字，如 `eth0` 。
- 网络设备会使用另外一套操作函数而不是 `read()` 、 `write()` 等。

### 2.2 处理器

#### 2.2.1 通用处理器(GPP)

当前的通用处理器主要采用了冯诺依曼架构和哈佛架构两种架构形式，其对应的常见的CPU系列有：
- 冯诺依曼架构：Intel、ARM7、MIPS
- 哈佛架构：AVR、ARM9-11、Arm Cortex A
具体区别可见[[常见CPU架构及其对比]]。

##### 2.2.1.1 不同架构处理器下的数据类型大小

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

#### 2.2.2 数字信号处理器(DSP)


### 2.3 存储器

常用存储器分类可见[[常用存储器#常用存储器]]。


## 3 Linux内核及内核编程

### 3.1 Linux内核文件结构

#### 3.1.1 Linux 6

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

### 3.2 Linux项目组织与编译系统

#### 3.2.1 Linux编译系统



#### 3.2.2 Kconfig基础语法

可见[[Kconfig基础语法]]。

## 4 Linux内核模块

### 4.1 Linux内核模块简介

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

### 4.2 Linux内核的额外注意事项

相比于普通的应用程序开发，Linux内核的开发需要额外注意以下几点：
1. <font color="#c00000">所有资源必须在模块卸载函数中手动释放</font>，操作系统不会帮内核模块管理资源。
2. 模块加载函数需要尽量快速的执行。
3. Linux内核模块代码必须是可重入的，因为他可能会被多个程序调用，会被同时在多个上下文中执行。
4. 内核所拥有的栈非常小，模块要和内核共用这些空间。
5. 内核模块中<font color="#c00000">不建议</font>(<font color="#c00000">且大多数情况下不允许</font>)使用浮点运算，如果需要开启浮点支持，则在某些架构上进入和退出内核空间时需要保存和恢复浮点处理器状态。

### 4.3 Linux内核模块程序结构

一个Linux内核模块应当具有且实现以下几个组成部分：
1. 模块加载函数<font color="#c00000">(必须)</font>
2. 模块卸载函数<font color="#c00000">(必须)</font>
3. 模块许可证声明<font color="#c00000">(必须)</font>
4. 模块参数(可选)
5. 模块导出符号(可选)
6. 模块作者信息(可选)

#### 4.3.1 模块加载函数

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

#### 4.3.2 模块卸载函数

```C
static void __exit exit_function(void)
{
	// ...模块卸载，释放资源
}
// 指定模块卸载函数
module_exit(exit_function);
```

<font color="#c00000">如果未定义模块卸载函数，则内核不允许卸载该模块。</font>

#### 4.3.3 模块参数

模块在加载时可以传入一些命令行参数，其主要通过如下方式进行定义与加载：

```C
// 相当于缺省参数
static int port = 8080;
// module_param(name, type, perm)
module_param(port, int, S_IRUGO);
```

在 `module_param` 函数中：
- `perm` 为访问许可配置：
	- `S_IRUGO` 表示任何人都可以读取该参数
	- `S_IRUGO|S_IWUSR` 表示root用户可以修改该参数。<font color="#c00000">但是当参数发生修改时</font>，<font color="#c00000">内核不会通知内核模块参数被修改</font>，因此<font color="#c00000">通常</font>不使用。

在加载时可以通过如下命令指定模块参数：

```Shell
insmod var=value #例如：insmod port=80
```

内核模块支持的加载参数列表如下：
- `bool`
- `invbool` ：<font color="#c00000">关联int型</font>，反转bool值，输入为 `true` 则传入为 `false` 。
- `charp` ：<font color="#c00000">关联char*</font>，<font color="#c00000">内核会为用户提供的字符串分配内存并设置指针</font>。
- `int`
- `long`
- `short`
- `uint` ：关联unsigned int，u表示无符号。
- `ulong`
- `ushort`
- <font color="#c00000">及上述类型对应的数组形式</font>，使用 `module_param_array` 进行参数接收。

#### 4.3.4 模块导出符号

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

注意：使用 `EXPORT_SYMBOL_GPL` 导出的符号不可以被非GPL模块引用。

#### 4.3.5 模块常用信息

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

#### 4.3.6 其他常用特性

1. 定义只在初始化阶段就需要的数据：

```C
static int var_name __initdata = 0;
```

上述 `__initdata` 和模块加载函数的 `__init` 都标识<font color="#c00000">在内核被加载完毕后</font>，<font color="#c00000">其所定义的变量或函数会被从内存中扔掉</font>。
2. 与上一条相似的是，内核中也有 `__exitdata` 与 `__exit` 。上述四个特性均会被放置到特殊ELF端。

#### 4.3.7 简单模块示例

在为内核编写模块时，<span style="background:#fff88f"><font color="#c00000">一定要选择与目标系统相匹配的内核源码</font></span>，否则生成的模块无法使用。

##### 4.3.7.1 拉取当前系统内核源码

###### 4.3.7.1.1 Ubuntu

Ubuntu可以使用 `apt` 和 `git` 两种方式获取源码。

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

##### 4.3.7.2 普通模块示例

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

###### 4.3.7.2.1 尝试修改vermagic(不推荐)

在上述结果中可以明显地发现<font color="#c00000"><font color="#c00000">即使在下载时内核源码版本匹配</font></font>，<font color="#c00000">但是编译出来的模块的vermagic仍不匹配</font>。
因此应当直接修改所下载的内核源码中 `include/linux/vermagic.h` 文件的 `vermagic` 定义。首先使用 `lsmod` 列出当前内核已加载的模块，并随便选取一个已加载的模块使用 `modinfo` 查看其模块信息：

```Shell
vermagic:       6.8.0-31-generic SMP preempt mod_unload modversions
```

然后查看 `include/linux/vermagic.h` 中的相关定义。

```C
/* Simply sanity version stamp for modules. */
#ifdef CONFIG_SMP
#define MODULE_VERMAGIC_SMP "SMP "
#else
#define MODULE_VERMAGIC_SMP ""
#endif
#ifdef CONFIG_PREEMPT_BUILD
#define MODULE_VERMAGIC_PREEMPT "preempt "
#elif defined(CONFIG_PREEMPT_RT)
#define MODULE_VERMAGIC_PREEMPT "preempt_rt "
#else
#define MODULE_VERMAGIC_PREEMPT ""
#endif
#ifdef CONFIG_MODULE_UNLOAD
#define MODULE_VERMAGIC_MODULE_UNLOAD "mod_unload "
#else
#define MODULE_VERMAGIC_MODULE_UNLOAD ""
#endif
#ifdef CONFIG_MODVERSIONS
#define MODULE_VERMAGIC_MODVERSIONS "modversions "
#else
#define MODULE_VERMAGIC_MODVERSIONS ""
#endif
#ifdef RANDSTRUCT
#include <generated/randstruct_hash.h>
#define MODULE_RANDSTRUCT "RANDSTRUCT_" RANDSTRUCT_HASHED_SEED
#else
#define MODULE_RANDSTRUCT
#endif

#define VERMAGIC_STRING                                                 \
        UTS_RELEASE " "                                                 \
        MODULE_VERMAGIC_SMP MODULE_VERMAGIC_PREEMPT                     \
        MODULE_VERMAGIC_MODULE_UNLOAD MODULE_VERMAGIC_MODVERSIONS       \
        MODULE_ARCH_VERMAGIC                                            \
        MODULE_RANDSTRUCT
```

发现是 `UTS_RELEASE` 字段不匹配，其定义与 `generated/utsrelease.h` 中，是自动生成的头文件。
回到linux内核源代码根目录的 `Makefile` 文件，定位到两段关键代码：

```Makefile
VERSION = 6
PATCHLEVEL = 8
SUBLEVEL = 1
EXTRAVERSION =
NAME = Hurr durr I'ma ninja sloth
```

```Makefile
# Read KERNELRELEASE from include/config/kernel.release (if it exists)
KERNELRELEASE = $(call read-file, include/config/kernel.release)
KERNELVERSION = $(VERSION)$(if $(PATCHLEVEL),.$(PATCHLEVEL)$(if $(SUBLEVEL),.$(SUBLEVEL)))$(EXTRAVERSION)
```

可发现将修改第一段的内核版本号即可，修改后如下。

```Makefile
VERSION = 6
PATCHLEVEL = 8
SUBLEVEL = 0
EXTRAVERSION = -31-generic
NAME = Hurr durr I'ma ninja sloth
```

最后的 `+` 号出现条件为：
- 上次tag之后，<font color="#c00000">代码有所改动</font>
- <font color="#c00000">并且</font>未定义 `LOCALVERSION` 
因此直接定义 `LOCALVERSION` 为空即可。

```Bash
make LOCALVERSION= include/config/kernel.release
```

综上，当官方提供的内核源代码版本与实际内核不符时，应当：
1. 修改根目录的 `Makefile` 中的版本号。
2. 定义 `LOCALVERSION` 为空，<font color="#c00000">或删除</font> `scripts/setlocalversion` <font color="#c00000">中的加号</font>(<font color="#c00000">建议</font>)。
修改后的vermagic信息为：

```Shell
vermagic:       6.8.0-31-generic SMP preempt mod_unload modversions
```

与系统中已加载的模块信息一致，但是此时加载仍然报错则证明内核源代码不匹，应当考虑编译安装当前有源代码的内核。


###### 4.3.7.2.2 自行编译并安装内核(推荐)

通常建议在学习开发Linux内核模块/驱动时使用自己的内核，除了方便版本匹配以外，还有更多的原因：
	![[Linux驱动开发笔记#^daooag]]
直接在内核源代码目录下执行：

```Shell
make modules
make modules-install
make install
```

随后重启，通常不建议卸载原内核，当内核配置出错无法启动后，可以在引导处切换内核。

###### 4.3.7.2.3 测试内核模块

<span style="background:#fff88f"><font color="#c00000">开启一个新的终端</font></span>监视 `printk` 信息：

```Shell
cat /proc/kmsg
```

在原终端加载模块：

```Shell
insmod hello_module.ko
```

无报错，且监视终端会输出日志：

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

再次使用 `lsmod | grep hellod` 则无结果。

若抓取日志，会发现一个警告，是由于没有签名造成的：

```Shell
dmesg | grep hello
[   85.531743] hello_module: module verification failed: signature and/or required key missing - tainting kernel
```

可以选择在 `Makefile` 文件中添加如下配置，关闭强制签名。

```Makefile
CONFIG_MODULE_SIG=n
```

##### 4.3.7.3 字符驱动模块示例

见章节：[[Linux驱动开发笔记#5 7 字符设备的分配、注册与回收]]

### 4.4 内核模块补充

#### 4.4.1 多文件编程

当内核模块 `test_module.ko` 由多个源文件 `file1.c` 、 `file2.c` 、 `...`  构成时，Makefile中可以如下编写：

```Makefile
obj-m += test_module.o
module-objs += file1.o file2.o ...
```

#### 4.4.2 内核态驱动与用户态驱动

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

## 5 简易的字符设备驱动程序

本章节的字符设备驱动程序将以一个简易的进程间管道通信为例。
基本设定：
1. 仅支持2个进程访问，超过2个时拒绝打开pipe文件。
2. 为了简化代码，无需其他鉴权等复杂操作。

### 5.1 主设备号和次设备号

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

### 5.2 设备编号的内部表达

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

### 5.3 分配和释放设备编号

分配设备号主要有两种方式，分别为静态分配和动态分配。

#### 5.3.1 静态分配设备号

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

#### 5.3.2 动态分配设备号(推荐)

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

#### 5.3.3 释放设备编号

对于上述的所有分配设备编号的方法，均可以使用如下的函数进行释放： 

```C
void unregister_chrdev_region(dev_t from, unsigned count)
```

### 5.4 绑定文件操作(file_operations 数据结构)

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
| `iopoll`            | 可为空                              |                     | NIO多路复用模型的后端实现。用于查询请求某个事件/操作是否会被阻塞。<br>为NULL时则意味告诉内核请求该设备任何事件/操作都不会发生阻塞。                                                                                                                                                                                                                                                                   |
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

### 5.5 file 数据结构

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

### 5.6 inode 数据结构

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

### 5.7 字符设备的分配、注册与回收

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

### 5.8 open和release方法

open应当完成如下任务：
1. 首次open时应当初始化硬件
2. 检查硬件错误
3. 在必要时更新 `file_operations` 中的指针
4. 在必要时向 `filep` 中填写应当存放在 `private_data` 中的数据

对应地，release应当完成如下任务：
1. 清除在 `filep` 中寄存的数据
2. 关闭设备

### 5.9 read和write方法

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

#### 5.9.1 read方法返回值

read方法的返回值应符合如下几种情况：
1. 当返回值大于0时，其含义为从字符设备读取到的字节数，该值不能大于 `count` 。
	1. 当返回值等于 `count` 时表示读取成功。
	2. 当返回值小于 `count` 时，<span style="background:#fff88f"><font color="#c00000">在部分情况下程序可能会重复执行read</font></span>直到凑够 `count` ，例如使用标准库的 `fread` 读取设备文件就会<font color="#c00000">自动执行此流程</font>。
2. 当返回值为0时，表示读取到文件末尾。
3. 当返回值小于0时，其用于表示错误。错误值定义于 `<linux/errno.h>`
此外，read方法也可以实现阻塞读取方式。

#### 5.9.2 write方法返回值

write和read方法的返回值及其注意事项相似。

### 5.10 readv和writev方法

在Linux中已对用户态提供了readv和writev两个批量读写的api。内核驱动可以自行选择是否实现批量版本的读写方法。若内核驱动不实现该方法，则readv和writev会自动<span style="background:#fff88f"><font color="#c00000">在用户态多次调用</font></span>对应的read和write方法进行实现。<font color="#c00000">随之带来的问题就是执行一次readv或writev会多次切换CPU状态</font>。
而对于用户而言，使用readv、writev而不是read、write的主要原因是前者可以<font color="#c00000">批量复制位于不连续内存空间</font>上的数据。

在Linux 2.6.18的 `struct file_operations` 中还保留有 `readv` 和 `writev` 的定义：

```C
ssize_t (*readv) (struct file *, const struct iovec *, unsigned long, loff_t *);
ssize_t (*writev) (struct file *, const struct iovec *, unsigned long, loff_t *);
```

<font color="#c00000">上述支持在Linux 2.6.19中已经删除</font>。

## 6 内核调试技术

### 6.1 内核的调试技术支持

内核中集成了很多可选的调试技术支持。这些调试技术或多或少的都会对内核的运行速度有所影响，因此<font color="#c00000">通常发行版的Linux一般不会开启这些支持</font>，这也是推荐使用自行编译的内核而非发行版内核的一个原因。 ^daooag

内核中的调试选项都在 `menuconfig` 下的 `Kernel hacking` 中，可选的调试选项如下：
TODO，用到再说


### 6.2 printk调试技术

















## 7 并发和竞态

Linux内核驱动的多个函数在实际运行中均非独占运行，一个 `open` 或 `read` 函数均可能会被多个线程的多个不同的上下文同时调用，因此要做好并发环境下的临界区管理。
在内核程序中通常也会依靠信号量或互斥锁进行临界区访问管理，但是需要注意的是，<span style="background:#fff88f"><font color="#c00000">内核态程序也会随时被切换为休眠状态，即使此时还处于内核的临界区内</font></span>。在执行一些操作时被切换为休眠状态是一个非常危险的事情。而Linux内核也给出了允许进入休眠态的互斥锁和不允许进入休眠态的互斥锁。
~~内核程序是这样的，用户态的程序临界区管理只需要上互斥锁就可以，而内核程序需要考虑的就很多了，内核程序在占用互斥锁后退出临界区之前会不会随时被切换为休眠状态、在使用禁止休眠的锁机制的临界区内被调用的其他内核组件会不会被切换为休眠状态等，都是需要考虑的事情。~~

### 7.1 Linux内核信号量与互斥锁的实现

Linux内核所使用的信号量和互斥锁应当使用头文件 `<asm/semaphore.h>` ，其相关用法见如下几个子章节所述。

#### 7.1.1 普通信号量的初始化

普通信号量的动态初始化可以用如下的函数进行：

```C
void sema_init(struct semaphore *sem, int val);
```

该函数中的 `val` 为该信号量的初始值。

#### 7.1.2 互斥锁的静态初始化

互斥锁可以按照如下的方式使用静态<font color="#c00000">定义</font>：

```C
#include <asm/semaphore.h>

// 定义初始值为1的互斥量，即mutex
DECLARE_MUTEX(name);
// 定义初始值为0的互斥量，在获取该互斥量之前必须先显式的解锁
DECLARE_MUTEX_LOCK(name);
```

由于该宏的实际用途为定义，但命名却使用了 `DECLARE` ，因此在Linux 2.6.36之后就删除了该接口。

#### 7.1.3 互斥锁的动态初始化

同样的，Linux也提供了互斥锁动态初始化的方法：

```C
void init_MUTEX(struct semaphore *sem);
void init_MUTEX_LOCKED(struct semaphore *sem);
```

不过这两个函数也在之后的版本被移除。

#### 7.1.4 互斥锁的操作

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

#### 7.1.5 读写锁

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

#### 7.1.6 completion事件

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

### 7.2 自旋锁

这里将自旋锁与普通的互斥锁分开讨论的主要原因是由于自旋锁和互斥锁的特性(<font color="#c00000">不可休眠</font>)、实现、应用场景及约定均有所不同，因此在后续的讨论中会将轮询实现的自旋锁和信号量分开讨论。

#### 7.2.1 自旋锁

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

#### 7.2.2 自旋读写锁

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

### 7.3 并发管理的常见问题

并发管理向来不是一个轻松的任务，并发及互斥锁的常见问题有如下几个章节：

#### 7.3.1 递归调用问题(可重入锁)

在编写代码时，很容易会写出一个已经持有互斥锁的函数去调用另外一个需要持有互斥锁才能运行的函数，这种通常称为递归调用。而在上述给出的并发管理工具中并未给出类似于POSIX中的递归锁或可重入锁，因此在内核编程中应更加着重注意此类问题。<font color="#c00000">通常的做法是在所有暴露给内核的API中做互斥管理，然后在这些API中所调用的内部实现均假设该互斥资源已被占有</font>。

#### 7.3.2 互斥资源的获取顺序问题

一个API需要同时获取多个互斥资源是一个很常见的事情，且<font color="#c00000">非常容易触发操作系统中的类似于哲学家吃饭问题的死锁问题</font>，通常的处理方式是一个内核程序统一按照一个有序的方式申请资源(即资源的有序分配法)。
并且，需要注意的是，在<font color="#c00000">同时应当获得一个信号量和一个自旋锁时</font>，<font color="#c00000"><b>必须</b>优先获取信号量</font>，<font color="#c00000">随后再去申请自旋锁</font>。<font color="#c00000">因为持有自旋锁的进程被信号量阻塞是一件<b>严重错误且非常危险</b>的事情</font>。
当然，最好的处理此类需要获取多个互斥资源的方法就是尽量避免这种现象。

#### 7.3.3 互斥锁的粒度管理问题

关于互斥资源管理的粒度问题，可以直接以Linux对SMP的支持进行举例。
在第一个支持多处理器的Linux2.0，整个内核有且仅有一个巨大的临界区(<font color="#c00000">BKL</font>，Big Kernel Lock)。当需要操作内核临界区时都需要申请该互斥锁。而在后来的Linux2.2中，互斥锁管理的粒度逐渐细化，例如I/O子系统共用一个互斥锁，网络系统共用一个互斥锁等。到了现在的版本，Linux内核中已经拥有了上千个互斥锁。
互斥资源管理粒度的细化无疑会提升CPU资源的利用率，但是在实际的工程中，<font color="#c00000">不应当过早的细化互斥资源的管理</font>，<font color="#c00000">因为项目最终的性能瓶颈往往不会出现在互斥资源的管理上</font>。<font color="#c00000">而混乱的互斥资源管理反而会导致更多严重问题的出现</font>。

### 7.4 并发管理的优化

#### 7.4.1 使用原子变量或非锁方法

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

#### 7.4.2 顺序锁(seqlock)

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

#### 7.4.3 RCU方法(读取-复制-更新方法)

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

## 8 高级字符设备驱动程序

### 8.1 ioctl

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

#### 8.1.1 ioctl接口(Linux 2.6.35及以前)

如上文所述， `ioctl` 的接口定义如下：

```C
int (*ioctl)(struct inode *inode, struct file *filep, unsigned int cmd, unsigned long arg);
```

上述接口中的参数：
- `struct inode *` 和 `struct file *` 的定义与用法和[[Linux驱动开发笔记#5 8 open和release方法]]中的一致，内核负责将用户态的 `ioctl` 中指定的 `fd` 转化为这两个数据结构。
- `cmd` 则和用户态中传入的对应参数完全保持一致，而在用户态和内核态对该参数含义的约定也应当保持一致，通常用对应的头文件来实现。而内核态对 `cmd` 参数的处理通常可以使用 `switch` 方法。至于 `cmd` 参数的<span style="background:#fff88f"><font color="#c00000">命令编号原则</font></span>可见章节[[Linux驱动开发笔记#8 1 3 cmd命令编号原则]]。

而返回值也应当从 `<linux/errno.h>` 中选值返回，常用的值如下：
- `-ENOTTY` ：POSIX标准规定的指定的命令非法的返回值

<span style="background:#fff88f"><font color="#c00000">注意：老的ioctl会在获得大内核锁(BKL)的条件下运行，所以应当尽快处理并返回</font></span>。

ioctl是Linux 2.6.35及以前所使用的接口，但是其往往会遇到在不同位数下，`unsigned long` 数据大小不同的情况：
	![[Linux驱动开发笔记#2 2 1 1 不同架构处理器下的数据类型大小]]
对于32位Linux系统，其只能运行32位的驱动程序和32位的用户态程序，因此ioctl可以很好的工作。而对于64位系统，其上可以运行32为的用户态程序，此时32位程序传来的 `unsigned long` 就是4Byte的整数类型，此时再传递给内核态驱动程序就可能出现错误。

此外，<span style="background:#fff88f"><font color="#c00000">更大的问题</font></span>在于<font color="#c00000">老的ioctl方法是由内核的大内核锁(BKL)实现并发控制的</font>，驱动在ioctl中较长的占用处理器则会导致无关的进程会被该ioctl产生较长时间的系统调用延迟()。为了解决此问题([[The new way of ioctl()]])，Linux在2.6.11开始引入了 `unlocked_ioctl` 和 `compat_ioctl` ，并在Linux 2.6.36彻底删除了 `ioctl` 接口。

#### 8.1.2 unlocked_ioctl和compat_ioctl(Linux 2.6.36及以后)

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

#### 8.1.3 cmd命令编号

##### 8.1.3.1 cmd命令编号的基本原则

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

##### 8.1.3.2 预定义命令

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

#### 8.1.4 ioctl传参

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

#### 8.1.5 权限与操作

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

### 8.2 非ioctl类设备控制

并非所有的设备都有必要使用ioctl这种控制方式，例如想要实现一个PWM控制的舵机驱动程序，大可不必使用ioctl实现这类控制，直接使用字符控制即可。例如若实现：

```Shell
echo "90" > /dev/servo0
```

则比使用 `ioctl` 外加特定的头文件定义 `ioctl` 的 `cmd` 要方便且可移植。类似的例子还有使用 `AT` 指令配置调制解调器等设备。

### 8.3 阻塞型IO

当设备无法立即完成某请求时，常用的做法之一是实现一个阻塞型IO。

#### 8.3.1 阻塞的若干注意事项

阻塞和休眠通常都是由等待一个事件或资源引起的，因此其等待的时间通常具有不可预测的特性。在进入休眠时，务必注意下列注意事项：
1. <span style="background:#fff88f"><font color="#c00000">不可在原子上下文中进行休眠</font></span>。因为原子操作通常依靠自旋锁、顺序锁甚至是关闭中断来实现的。在这里进行休眠及其容易造成死锁或其他系统稳定性相关的问题。<font color="#c00000">在进入休眠时需检查如下事项</font>：
	1. 休眠时不可拥有(<font color="#c00000">因为下述机制本就是为避免休眠切约定不可休眠的互斥方法</font>)：
		- [ ] 自旋锁
		- [ ] 顺序锁
		- [ ] RCU锁
	2. 休眠时不可关闭中断
2. 休眠时允许拥有信号量，则务必关注可能会被该信号量影响的线程，且需要注意不要构成循环等待这种死锁情况。(该线程所持有的信号量所阻塞的线程拥有该线程所等待的资源)
3. 在进行休眠时，<font color="#c00000">务必确保有其他线程或进程会唤醒本进程</font>。

#### 8.3.2 阻塞与休眠

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
3. 唤醒指令。休眠和唤醒通常伴随出现。
```C
// wake_up会唤醒所有等在queue上的线程
wake_up(x)

// wake_up_interruptible只会唤醒可中断休眠的线程
wake_up_interruptible(x)
```

### 8.4 非阻塞IO

除了阻塞IO之外，Linux支持用户程序以非阻塞IO打开/操作设备。
选择是否为非阻塞IO需要<span style="background:#fff88f"><font color="#c00000">且仅能</font></span>在 `f_open` 阶段进行设置。

```C
// 只读、非阻塞
fd = open("path"，O_RDONLY | O_NONBLOCK)
```

随后在内核模块中的后续操作时就应当根据是否定义了该非阻塞标志实现不同的行为。例如当应用程序请求的操作无法执行时，通常返回 `-EAGAIN` (try it again)。
只有 `read` 、 `write` 和 `open` 文件操作会收非阻塞标志的影响。

### 8.5 高级休眠

章节[[Linux驱动开发笔记#8 3 2 阻塞与休眠]]中所使用的 `wait_queue_head_t` 的定义如下：

```C
struct wait_queue_head {  
        spinlock_t            lock;  
        struct list_head       head;  
};  
typedef struct wait_queue_head wait_queue_head_t;
```

其是由一个自旋锁和链表组成。


## 9 时间、延迟及延缓操作


## 10 内存分配




