---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 #Linux驱动开发 

# 1 Readme

本章节前置内容：
- [[../../../../嵌入式基础/接口技术/SPI/SPI总线标准|SPI总线标准]]
- [[../../Linux设备模型/SPI总线/SPI总线模型|SPI总线模型]]

# 2 目录

```toc
```

# 3 内核设备模型、设备树配置

内核模型、设备树配置等内容可见笔记[[../../Linux设备模型/SPI总线/SPI总线模型|SPI总线模型]]。
# 4 软件接口

本章节软件接口均是基于[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/spi/spi.h#^j2uocs|spi设备对象]]进行操作。

## 4.1 写入若干字节(spi_write)

可见章节[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/spi/spi.h#^mrzeek|spi_write]]：
![[Linux内核原理及其开发/内核源码探析/内核源码分析/include/spi/spi.h#spi_write mrzeek]]

## 4.2 读取若干字节(spi_read)

[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/spi/spi.h#^4zl7vy]]

## 4.3 写入8字节随后读取8字节(spi_w8r8)

该方法通常用于寄存器读取。

[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/spi/spi.h#^yvj6l7]]
