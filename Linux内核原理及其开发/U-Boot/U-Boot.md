---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 #Linux驱动开发 #操作系统

# 1 目录

```toc
```

# 2 U-Boot及其功能

U-Boot全称为Universal Bootloader，<font color="#c00000">是一个裸机程序</font>。其目的是为了解决不同硬件上的内核启动需求。

## 2.1 U-Boot基本需求

考虑如下几个要点：
- 在单片机上，其RAM、Flash通常和CPU直接组合在一起，且其Flash通常也可以直接映射到内存空间从而实现程序的直接运行。
- 而在嵌入式Linux硬件上，其RAM、Flash通常都独立于CPU之外，且RAM和Flash的型号、容量、类型多种多样，其无法做到像单片机一样直接完全由CPU硬件完成系统的启动。因此其需要一个额外的Bootloader来实现内核的启动与更新等功能。

## 2.2 U-Boot基本职责

在此需求之上，U-Boot主要负责：
1. 初始化必要硬件，例如：
	1. DDR
	2. 时钟
	3. Flash
2. 将内核拷贝到内存中
3. 启动内核

## U-Boot与设备树

在<font color="#c00000">上述硬件需求中</font>，例如CPU、时钟、内存等<font color="#c00000">需要设备树技术的介入</font>。而<font color="#c00000">设备树的介入也将</font>同一种芯片的不同电路设计、驱动选择所组成的<font color="#c00000">成千上万种的板级配置拆分到U-Boot和内核源代码之外</font>。


此外，U-Boot支持ARM、RISC-V、x86等架构，因此在工程上较为复杂。

