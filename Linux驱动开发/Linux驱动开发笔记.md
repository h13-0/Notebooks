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
