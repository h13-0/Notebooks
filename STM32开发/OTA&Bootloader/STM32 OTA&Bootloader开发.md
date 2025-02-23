---
number headings: auto, first-level 2, max 6, 1.1
---
#STM32开发 

## 1 目录

```toc
```

## 2 前置基础

### 2.1 STM32启动流程

![[STM32启动流程]]

### 2.2 固件布局(Sections)

STM32编译后的Sections主要有(按照地址从低到高排序)：

| <center>Sections</center> | <center>启动过程位置变化</center> | <center>作用</center>                                                                                 |
| ------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------- |
| `.isr_vector`             | 存放于flash中                 | 中断向量表，具体内容可见上述章节。                                                                                   |
| `.text`                   | 存放于flash中                 | 文本段(又叫代码段)                                                                                          |
| `.rodata`                 | 存放于flash中                 | 只读数据段，存放常量字符串、`const` 变量等。                                                                          |
| `.ARM.extab`              | 存放于flash中                 | ARM平台的异常处理表                                                                                         |
| `.ARM.exidx`              | 存放于flash中                 | 索引表，用于支持异常处理                                                                                        |
| `.preinit_array`          | 存放于flash中                 | 在 `.init` 段前执行，                                                                                     |
| `.init_array`             | 存放于flash中                 | 在 `.init` 段后执行，<font color="#c00000">存放全局构造函数或者初始化函数的指针</font>，会被在启动过程中的 `__libc_init_array` 函数中被调用 |
| `.fini_array`             | 存放于flash中                 | (裸机中极少使用)，<font color="#c00000">存放程序退出时的析构函数或资源释放函数的指针</font>，会在程序退出时被执行                            |
| `.data`                   | 存放于固件，启动后复制到内存            | 已初始化数据段，存放已初始化的全局变量和静态变量                                                                            |
| `.bss`                    | 固件中没有，启动时在内存中分配           | 存放未初始化的全局变量和静态变量                                                                                    |
| `._user_heap_stack`       | 固件中没有，启动时在内存中分配           | 用户堆栈                                                                                                |


## 3 实现

基于上述STM32的启动过程，Bootloader可以按照如下的逻辑进行设计。
需要说明的是，Bootloader和用户程序应当为两个独立的工程(或固件)。

### 3.1 Bootloader实现

在Bootloader工程中进行如下修改：
1. 修改 `*.ld` 文件的 `MEMORY` 定义的大小，<font color="#c00000">用于限制Bootloader固件的大小</font>：
	```C
MEMORY
{
  RAM    (xrw)    : ORIGIN = 0x20000000,   LENGTH = 20K
  FLASH    (rx)    : ORIGIN = 0x8000000,   LENGTH = 4K  /* 64K */
}
	```
1. 实现Bootloader基础功能
2. 补全业务逻辑，略。

#### 3.1.1 App程序实现

在APP中应当进行如下修改：
1. 修改Flash的起始位置、Flash大小，<font color="#c00000">需要注意的是K为1024而非1000</font>：
```C
MEMORY
{
  RAM    (xrw)    : ORIGIN = 0x20000000,   LENGTH = 20K
  /* FLASH    (rx)    : ORIGIN = 0x8000000,   LENGTH = 64K */
  FLASH    (rx)    : ORIGIN = 0x8002000,   LENGTH = 56K
}
```
- 补充：
	- 在本步骤中，<font color="#c00000">修改了FLASH的起始地址</font>，<span style="background:#fff88f"><font color="#c00000">也就顺带修改了该固件中所有函数调用时所指向的函数地址</font></span>(包括汇编指令、`.init` 段等函数地址调用)
1. 

## 4 
