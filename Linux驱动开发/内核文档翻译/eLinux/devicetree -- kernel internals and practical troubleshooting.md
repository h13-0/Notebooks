---
number headings: auto, first-level 2, max 6, 1.1
---
#Linux驱动开发 #操作系统 

原标题：`devicetree: kernel internals and practical troubleshooting` 。
原文档地址：[devicetree: Kernel Internals and Practical Troubleshooting](https://elinux.org/images/0/0c/Rowand--devicetree_kernel_internals.pdf)。

## 1 目录

```toc
```

## 2 序言

目前已经有了很多关于设备树是什么样子以及如何创建设备树的示例，而本文将探讨Linux内核如何使用设备树。本文的主题包括内核设备树框架、设备创建、资源分配、驱动程序绑定和连接对象等内容。故障排除将考虑初始化、分配和绑定排序、内核配置和驱动程序问题。

注意：本文所讲述内容指定的内核版本为 `3.15rc-1` 到 `3.16-rc7` 。涉及到CPU架构的代码将查看 `arch/arm/` 。

## 3 章节1 - 设备树

### 3.1 什么是设备树

> 设备树是具有描述系统中设备的节点的树数据结构。每个节点都有描述所表示设备特征的属性/值对。每个节点只有一个父节点，只有根节点没有父节点。 —— ePAPR v1.1

<span style="background:#fff88f"><font color="#c00000">设备树描述了无法通过探测定位的硬件</font></span>，<font color="#c00000">即描述了不可被主动发现的设备</font>。

### 3.2 设备树生命周期

设备树的声明周期如下图所示：

