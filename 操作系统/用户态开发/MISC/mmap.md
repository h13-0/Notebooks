---
number headings: auto, first-level 2, max 6, 1.1
---
#Linux用户态开发 

## 1 目录

```toc
```

## 2 函数原型及用户态调用

mmap即内存映射技术，<font color="#c00000">其可以将</font><span style="background:#fff88f"><font color="#c00000">文件</font></span><font color="#c00000">映射到程序的</font><span style="background:#fff88f"><font color="#c00000">内存空间</font></span>中。而在Linux中，<span style="background:#fff88f"><font color="#c00000">万物皆文件</font></span>。因此mmap实际上并不只是一个内存映射函数，而是可以将任何在[[Linux驱动开发笔记#^u7i5mc|file_operations结构体]]中提供了 `mmap` 实现的fd映射到用户空间中。

用户态 `mmap` 常用的fd来源(或 `mmap` 能提供的功能)有：
- 常规文件
- 设备文件
- 共享内存
- 匿名映射

至于 `file_operations` 中的 `mmap` 实现，其有如下原理概述：
- fd的 `mmap` 本质是将内核管理的一片内存区域映射到用户空间。
- 无论用户操作的fd是常规文件、字符设备、块设备、匿名映射、共享内存还是虚拟设备，其内核提供的 `mmap` 后端实现一定是将<span style="background:#fff88f"><font color="#c00000">内核管理的一片内存</font></span><font color="#c00000">映射到用户空间中</font>，而无法不使用内核管理的内存。

`mmap`的函数原型为：

```C
#include <sys/mman.h>

void *mmap(void addr[.length], size_t length, int prot, int flags,
    int fd, off_t offset);

int munmap(void addr[.length], size_t length);
```

上述参数中：
- 参数：
	- `addr` ：允许用户指定一片内存，若用户不指定则该函数会分配并返回一个地址。
	- `length` ：用户指定的内存区域大小
	- `prot` ：用户想要获取的内存权限，包含：
		- 
- 返回值：




