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

目前已经有了很多关于设备树是什么样子以及如何创建设备树的示例，而本文将探讨Linux内核如何使用设备树。

主题包括内核设备树框架、设备创建、资源分配、驱动程序绑定和连接对象。故障排除将考虑初始化、分配和绑定排序、内核配置和驱动程序问题。

注意：本文所讲述内容指定的内核版本为 

