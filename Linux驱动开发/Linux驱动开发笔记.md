---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式

# 目录

```toc
```

## 1 Linux设备驱动


## 2 驱动设计的硬件基础
### 2.1 设备的分类及特点

Linux将设备分为了如下三个大类：
- 字符设备：必须以串行顺序依次访问的设备，如触摸屏、磁带驱动器、鼠标
- 块设备：允许按照任意顺序进行访问，以块为单位进行操作，如硬盘、eMMC等
	- 块设备有两种访问方式：
		1. 使用类似于 `dd` 的命令操作设备的块
		2. 在块设备上建立 `FAT` 、 `EXT4` 等文件系统后，使用文件系统的方式进行访问。
- 网络设备：面向数据包的发送和接收设计，内核与网络设备之间的通信主要使用Socket
<font color="#c00000">除网络设备外</font>，字符设备和块设备会被会被映射到Linux文件系统的文件和目录上，使用 `open()` 、 `write()` 等方式进行访问。

### 2.2 处理器

#### 2.2.1 通用处理器(GPP)

当前的通用处理器主要采用了冯诺依曼架构和哈佛架构两种架构形式，其对应的常见的CPU系列有：
- 冯诺依曼架构：Intel、ARM7、MIPS
- 哈佛架构：AVR、ARM9-11、Arm Cortex A
具体区别可见[[常见CPU架构及其对比]]。

#### 2.2.2 数字信号处理器(DSP)


### 2.3 存储器

常用存储器分类可见[[常用存储器#常用存储器]]。


## 3 Linux内核及内核编程

### 3.1 Linux内核文件结构

#### 3.1.1 Linux 6

- arch：与体系结构相关的代码
- crypto：





## 4 Linux内核模块

### 4.1 Linux内核模块简介

Linux的组件可以选择编译进Linux内核或者编译为Linux内核模块，编译为Linux内核模块的好处有：
1. 在后续新增功能时，可以直接编译为模块而不需要重新替换内核
2. 方便随时删除功能

Linux内核模块的加载与卸载：
- Linux内核的加载使用 `insmod` 命令
- Linux内核的卸载使用 `rmmod` 命令

### 4.2 Linux内核模块程序结构

一个Linux内核模块应当具有且实现以下几个组成部分：
1. 模块加载函数<font color="#c00000">(必须)</font>
2. 模块卸载函数<font color="#c00000">(必须)</font>
3. 模块许可证声明<font color="#c00000">(必须)</font>
4. 模块参数(可选)
5. 模块导出符号(可选)
6. 模块作者信息(可选)

#### 4.2.1 模块加载函数

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

#### 4.2.2 模块卸载函数

```C
static void __exit exit_function(void)
{
	// ...模块卸载，释放资源
}
// 指定模块卸载函数
module_exit(exit_function);
```

#### 4.2.3 模块参数

模块在加载时可以传入一些命令行参数，其主要通过如下方式进行定义与加载：

```C
// 相当于缺省参数
static int port = 8080;
// module_param(参数名, 参数类型， 读/写权限)
module_param(port, int, S_IRUGO);
```

在加载时可以通过如下命令指定模块参数：

```Shell
insmod var=value #例如：insmod port=80
```

#### 4.2.4 模块导出符号

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

#### 4.2.5 模块常用信息

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

#### 4.2.6 其他常用特性

定义只在初始化阶段就需要的数据：

```C
static int var_name __initdata = 0;
```

#### 4.2.7 简单模块示例

在为内核编写模块时，<span style="background:#fff88f"><font color="#c00000">一定要选择与目标系统相匹配的内核源码</font></span>，否则生成的模块无法使用。

##### 4.2.7.1 拉取当前系统内核源码

###### 4.2.7.1.1 Ubuntu

Ubuntu可以使用 `apt` 和 `git` 两种方式获取源码。在获取源码之前，需要获取当前系统信息：

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
# 连接到git仓库
git remote add origin https://git.launchpad.net/~canonical-kernel/ubuntu/+source/linux-intel/+git/noble
# 只clone目标版本
git fetch --depth 1 origin 7fdb45c9bbbc95a3300b4d8de3f751f4c05c98e2
```

<font color="#c00000">只做内核驱动/模块开发建议使用后者</font>，完整clone速度过慢。
以上述命令为例，截止2024年05月30日：
- 完整clone共计10192670个object
- 只clone目标版本共计88631个object。

##### 4.2.7.2 普通模块示例

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
    printk("Hello module inited.");
    return 0;
}

static void __exit hello_module_exit(void)
{
    printk("Hello module exited.");
}

module_init(hello_module_init);
module_exit(hello_module_exit);
MODULE_LICENSE("GPL v2");
MODULE_AUTHOR("h13");
MODULE_DESCRIPTION("hello word module.");
MODULE_VERSION("V1.0");
```

并在  `lib/Makefile` 的末尾增加如下代码：

```Makefile
# Hello world module
obj-m += hello_module.o
```

回到linux代码根目录，执行：

```Shell
make -j8 #8线程
```

即可在 `lib` 路径下得到 `hello_module.ko` ，使用

使用 `modinfo hello_module.ko` 查看模块信息：

```Shell
# modinfo hello_module.ko
filename:       .../hello_module.ko
version:        V1.0
description:    hello word module.
author:         h13
license:        GPL v2
srcversion:     C6A36BCF3E2045DD1DE8E30
depends:
retpoline:      Y
intree:         Y
name:           hello_module
vermagic:       6.8.4+ SMP preempt mod_unload modversions
```


##### 4.2.7.3 字符驱动模块示例




## 5 Linux文件系统与设备文件

### 5.1 Linux基本文件操作

对于一个普通文件，其通常有打开、

### 5.2 Linux文件系统

#### 5.2.1 Linux文件系统目录结构

Linux文件系统的目录结构如下：
- `/bin` ：包含了基本命令，例如 `ls` 、 `cp` 、 `mkdir` 等。
- `/sbin` ：包含了系统命令，例如 `ifconfig` 、 `modprobe` 等。
- `/dev` ：设备文件的挂载目录。
- `/etc` ：配置文件的存放目录。
- `/lib` ：库文件目录。
- `/mnt` ：存储设备的挂载点。
- `/opt` ：可选应用软件的安装目录。
- `/proc` ：存放一些系统信息及进程信息。该目录并非实际位于文件系统中，<font color="#c00000">其位于内存中</font>。
- `/tmp` ：缓存目录。
- `/usr` ：用户目录
- `/var` ：用于存放经常变化的文件，例如日志等(位于 `/var/log` )。
- `/sys` ：

#### 5.2.2 Linux文件系统结构

正如大多数操作系统那样，应用程序和各文件系统(如Ext、FAT、NTFS)之间需要有一层虚拟文件系统(VFS)隔离。但是在Linux中许多设备也会被挂载为 `/dev` 目录下的一个文件，因此Linux的VFS还有调用转发设备驱动函数的功能，如下图所示。
	![[msedge_aH7KpZznqO.png]]
	![[msedge_tknHA5FLRe.png]]

在使用





















