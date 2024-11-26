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
1. 对于内核架构：
	1. 32位的内核需要检测在编译时是否将 `off_t` 配置为32位：
		1. 如果被配置为32位，即 `CONFIG_ARCH_32BIT_OFF_T` 被启用，则 `off_t` 最多支持2GB的偏移量。<font color="#c00000">若用户态程序想要读取大文件</font>，<font color="#c00000">则用户态需要显式定义</font> `_FILE_OFFSET_BITS=64` 或使用 `O_LARGEFILE` 标志来启用64位的`off_t` 。
		2. <font color="#c00000">如果未被配置为32位</font>，即 `CONFIG_ARCH_32BIT_OFF_T` 未启用，则<font color="#c00000">默认开启大文件模式</font>。
	2. 64位的内核通常无须配置该项，原生支持64位的 `off_t` ，默认开启大文件模式。
2. 调用返回 `long do_sys_open(int dfd, const char __user *filename, int flags, umode_t mode)` ：
	1. 调用 `build_open_how`
	2. 调用 `build_open_flags` 将 `open_how` 转换为 `flags` ：
		1. 
	3. 