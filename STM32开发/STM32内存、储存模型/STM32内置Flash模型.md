---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 #STM32开发 

## 1 目录

```toc
```

## 2 STM32 F10x系列Flash组织结构

STM32 F10x系列按照存储容量可以进行如下划分：
- 小容量产品：容量为 `32KB` 及以下，标识符段为 `F103*6` 及以下的。
	![[msedge_EMBmFmDIL5.png]]
- 中容量产品：容量为 `48KB` ~ `128KB` ，标识符段为 `F103*7` ~ `F103*B` 。
	![[msedge_2N4A2QEz9X.png]]
- 大容量产品：容量为 `192KB` ~ `512KB` ，标识符段为 `F103*Z` ~ `F103*D` 。
	![[msedge_RWSicTexx5.png]]
- 超大容量产品：容量为 `512KB` ~ `1024KB` 的，标识符段为 `F103*D` ~ `F103*E` 。
	- ![[msedge_lNBTjFOTWK.png]]
	- <span style="background:#fff88f"><font color="#c00000">注意该系列产品为双BANK架构</font></span>。
- 互联型产品：标识符段为 `F105` 或 `F107` 的。
	![[msedge_LFuPxUpbdZ.png]]
注：
- 信息块主要包含：系统存储器(即内置Bootloader)、以及选项字节(例如内存容量等信息)，其存储与ROM中，不可修改。
- <span style="background:#fff88f"><font color="#c00000">信息快不占用STM32标称的Flash存储空间</font></span>。例如STM32F103C8，其用户可读写的空间仍为标称的64Kbyte。
- 命名规则参考：[[查阅性基础#^imvzdn|STM32命名规则]]。

## 3 Flash操作

见：[[STM32内置Flash读写]]。
