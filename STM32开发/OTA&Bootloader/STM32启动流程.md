---
number headings: auto, first-level 2, max 6, 1.1
---
#STM32开发 

## 1 目录

```toc
```

## 2 Note

<font color="#c00000">下方内容默认均以STM32F103为例</font>，并可能地补上其他常用系列的不同点。

## 3 前置基础




## 4 启动模式

STM32的启动模式主要有如下几种：

| <center>BOOT引脚配置</center> | <center>启动模式</center>               | 内存映射    |
| ------------------------- | ----------------------------------- | ------- |
| BOOT0=0                   | 从内置Flash启动                          | 将Flash的 |
| BOOT0=1，BOOT1=0           | 从系统存储器启动(内置Bootloader，用于串口/USB下载程序) |         |
| BOOT0=1，BOOT1=1           | 从内置SRAM启动(调试用途)                     |         |

STM32F103不支持从外部Flash启动。

## 5 从内置Flash启动的启动流程

从内置Flash启动的启动流程为：
1. 芯片上电或触发复位。
2. 硬件

