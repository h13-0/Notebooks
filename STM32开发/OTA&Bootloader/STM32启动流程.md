---
number headings: auto, first-level 2, max 6, 1.1
---
#STM32开发 

## 1 目录

```toc
```

## 2 Note

<font color="#c00000">下方内容默认均以STM32F103为例</font>，并可能地补上其他常用系列的不同点。

## 3 启动模式

STM32的启动模式主要有如下几种：
1. BOOT0=0：从主 Flash 启动(用户程序)。
2. BOOT0=1，BOOT1=0：从系统存储器启动(内置 Bootloader，用于串口/USB 下载程序)。
3. BOOT0=1，BOOT1=1：从内置SRAM启动(调试用途)。


## 4 启动流程



