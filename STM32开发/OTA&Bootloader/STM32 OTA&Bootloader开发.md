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

[[STM32启动流程#^ekk2l7|STM32固件结构]]：
![[STM32启动流程#3 2 STM32固件结构 ekk2l7]]

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
	- 在本步骤中，<font color="#c00000">修改了FLASH的起始地址</font>，<span style="background:#fff88f"><font color="#c00000">也就顺带修改了该固件中所有函数调用时所指向的函数地址</font></span>(包括汇编指令、`.init` 段等函数地址调用)，<font color="#c00000">也就是只要把固件拷贝到正确的内存地址后，即可保证启动后APP的正常运行</font>。
	- 而在整个生命周期中，仅有[[STM32启动流程|STM32启动过程中]]还未保证地址的正确偏移，此时则需要进行第二步处理。
1. 修改APP中的中断向量表偏移：
```C

```
- 


## 4 
