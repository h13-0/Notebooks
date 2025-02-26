---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 #STM32开发 

## 1 目录

```toc
```

## 2 STM32 F10x系列Flash组织结构

STM32 F10x系列按照存储容量可以进行如下划分：
- 小容量产品：32Kbyte及以下，标识符段为 `F103*6` 及以下的。
	![[msedge_EMBmFmDIL5.png]]
- 中容量产品：128Kbyte及以下，标识符段为 `F103*B` 及以下的。
	![[msedge_2N4A2QEz9X.png]]
- 大容量产品：256Kbyte及以上，最大512Kbyte，标识符段为 `F103*Z` 及以上的。
	![[msedge_RWSicTexx5.png]]
- 互联型产品：标识符段为 `F105` 或 `F107` 的。
	![[msedge_LFuPxUpbdZ.png]]
注：
- 信息块主要包含：系统存储器(即内置Bootloader)、以及选项字节(例如内存容量等信息)，其存储与ROM中，不可修改。
- <span style="background:#fff88f"><font color="#c00000">信息快不占用STM32标称的Flash存储空间</font></span>。例如STM32F103C8，其用户可读写的空间仍为标称的64Kbyte。
- 命名规则参考：[[查阅性基础#^imvzdn|STM32命名规则]]。
