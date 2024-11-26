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

### 3.1 open

`open` 系统调用的基本处理流程如下：
1. 对于内核架构：
	1. 32位的内核需要检测在编译时是否开启了大文件支持( `CONFIG_ARCH_32BIT_OFF_T` )：
		1. 如果wei
	2. 判定32位的内核在编译时是否开启了大文件支持( `CONFIG_ARCH_32BIT_OFF_T` )，如果未开启，则 `off_t` 最多支持2GB的偏移量。
	3. 64位的内核无须配置该项，原生支持64位的 `off_t` 。
2. 调用返回 `do_sys_open` 
