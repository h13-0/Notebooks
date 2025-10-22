---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 #Linux驱动开发 #操作系统

# 1 目录

```toc
```

# 2 U-Boot及其功能

U-Boot全称为Universal Bootloader，<font color="#c00000">是一个裸机程序</font>。其目的是为了解决不同硬件上的内核启动需求。
此外，U-Boot支持ARM、RISC-V、x86等架构，因此在工程上较为复杂。

## 2.1 U-Boot基本需求 ^cv97lr

考虑如下几个要点：
- 在单片机上，其RAM、Flash通常和CPU直接组合在一起，且其Flash通常也可以直接映射到内存空间从而实现程序的直接运行，这种设备也被称为<font color="#9bbb59">XIP设备</font>。
	- <font color="#9bbb59">XIP</font>：Execute in place，原地执行。
	- <font color="#9bbb59">XIP设备</font>：CPU可以直接在存储器中执行代码的设备。
- 而在嵌入式Linux硬件上，其：
	- RAM、Flash通常都独立于CPU之外，SoC通常只有内存控制器和Flash控制器，这些都不具备<font color="#9bbb59">XIP</font>功能。
	- RAM和Flash的型号、容量、类型多种多样，其无法做到像单片机一样直接完全由CPU硬件完成系统的启动。
因此嵌入式Linux硬件需要一个额外的Bootloader来实现内核的启动与更新等功能。

## 2.2 U-Boot基本职责

在此需求之上，U-Boot主要负责：
1. 初始化必要硬件，例如：
	1. DDR
	2. 时钟
	3. Flash
2. 将内核拷贝到内存中
3. 启动内核

## 2.3 U-Boot与设备树

在<font color="#c00000">上述硬件需求中</font>，例如CPU、时钟、内存等<font color="#c00000">需要设备树技术的介入</font>。而<font color="#c00000">设备树的介入也将</font>同一种芯片的不同电路设计、驱动选择所组成的<font color="#c00000">成千上万种的板级配置拆分到U-Boot和内核源代码之外</font>，<font color="#c00000">设备树也将被独立编译为一个单独的</font> `.dtb` <font color="#c00000">文件</font>，<font color="#c00000">以供U-Boot加载和读取</font>。

# 3 U-Boot的加载流程 ^ro5d63

对于大多数嵌入式Linux系统：
- 其SoC只拥有Flash控制器，而不拥有内置的Flash。
- 而U-Boot通常存放于外置Flash中。
- 而对于外置的Flash，其通常均不是XIP设备，需要额外一段(或多段)程序来完成U-Boot的加载，这些程序(或者启动阶段)分别为：
	- <font color="#9bbb59">BootROM</font>：一个可以直接被CPU读取和执行的存储区域(即XIP设备)，其通常在出厂时被刷写。<font color="#c00000">其使命是通过Flash控制器将Bootloader拷贝到内存中并执行</font>。
	- <font color="#9bbb59">SPL</font>：若SoC的SRAM容量不足以放下完整U-Boot时，BootROM会将精简版的U-Boot拷贝到SRAM，然后初始化DDR，从而继续拉起U-Boot。这个精简版的U-Boot就是SPL(Secondary Program Loader)。

也就是说对于嵌入式Linux，其： ^c45lgx
- 若Flash为非XIP设备(<font color="#c00000">大多数为此情况</font>)
	- 若SRAM可以存下U-Boot，其启动顺序为 `BootROM -> U-Boot -> kernel -> FS` 
	- 若SRAM无法存下U-Boot，其启动顺序为 `BootROM -> SPL -> U-Boot -> kernel -> FS`
- 若Flash为XIP设备，直接加载U-Boot


