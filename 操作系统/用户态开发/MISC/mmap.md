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
		- `PROT_READ`
		- `PROT_WRITE`
		- `PROT_EXEC` ，如映射JIT编译生成的机器码
		- `PROT_NONE` ，禁止访问，访问时会触发 `SIGSEGV`
	- `flags` ：
		- 核心标志，选一个使用：
			- `MAP_SHARED` ：映射可被多进程共享，对fd的修改
			- `MAP_PRIVATE` ：
		- 可选标志，可组合使用：
			- `MAP_ANONYMOUS` ：映射匿名内存(不需要文件)，此时 `fd` 应设为 `-1`，`offset` 为 `0`。
			- `MAP_FIXED` ：强制使用指定的 `addr` ，可能覆盖已有映射。
			- `MAP_LOCKED` ：锁定页面在内存中(避免换出到交换分区，需权限)
			- `MAP_POPULATE` ：提前预加载映射的物理内存，跳过按需缺页。
			- `MAP_NORESERVE` ：不预留交换空间，可能导致内存耗尽时触发 `OOM` 。
	- `fd` ：需要操作的文件描述符，需要注意：
		- 当 `flags` 包含 `MAP_ANONYMOUS` 时，此时 `fd` 应设为 `-1` 。
		- 即使有 `fd` ，<font color="#c00000">映射的生命周期与文件描述符无关</font>，<span style="background:#fff88f"><font color="#c00000">关闭fd不影响已映射的内存</font></span>。
	- `offset` ：从fd的 `offset` 处开始映射
- 返回值：
	- 成功时返回映射区域的起始地址，<span style="background:#fff88f"><font color="#c00000">地址可能不等于</font></span> `addr` ，<font color="#c00000">除非明确使用</font> `MAP_FIXED` 。成功后可使用 `*(addr + offset)` 操作内存。
	- 失败时返回 `MAP_FAILED` ，并设置 `errno` 。




