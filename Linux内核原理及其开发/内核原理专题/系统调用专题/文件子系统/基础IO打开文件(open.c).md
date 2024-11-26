---
number headings: auto, first-level 2, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发 

## 1 目录

```toc
```

## 2 Readme

本笔记主要针对 `linux/fs/open.c` 中的系统调用进行分析。

## 3 系统调用及其分析

### 3.1 open ^qyilk5

`open` 系统调用的基本处理流程如下：
1. 检测大文件支持；对于内核架构：
	1. 32位的内核需要检测在编译时是否将 `off_t` 配置为32位：
		1. 如果被配置为32位，即 `CONFIG_ARCH_32BIT_OFF_T` 被启用，则 `off_t` 最多支持2GB的偏移量。<font color="#c00000">若用户态程序想要读取大文件</font>，<font color="#c00000">则用户态需要显式定义</font> `_FILE_OFFSET_BITS=64` 或使用 `O_LARGEFILE` 标志来启用64位的`off_t` 。
		2. <font color="#c00000">如果未被配置为32位</font>，即 `CONFIG_ARCH_32BIT_OFF_T` 未启用，则<font color="#c00000">默认开启大文件模式</font>。
	2. 64位的内核通常无须配置该项，原生支持64位的 `off_t` ，默认开启大文件模式。
2. 调用返回 `long do_sys_open(int dfd, const char __user *filename, int flags, umode_t mode)` ：
	1. 调用 `build_open_how` 将用户态的 `umode_t` 
	2. 调用返回 `static long do_sys_openat2(int dfd, const char __user *filename, struct open_how *how)` ：
		1. 调用 `build_open_flags` 将 `open_how` 转换为 `flags` ：


### 3.2 close

`close` 系统调用的基本处理流程如下：
1. 调用 `struct file *file_close_fd(unsigned int fd);` ，从 `fdt` 中寻找 `fd` 对应的 `file` 结构体指针。 
2. 调用 `filp_flush` 刷新文件缓冲区。
	1. 
	2. 当设置了 `f_op->flush` 时调用 `f_op->flush` 。
	3. 
3. 调用 `__fput_sync`
4. 检测特定错误
5. 返回 `filp_flush` 的返回值。

