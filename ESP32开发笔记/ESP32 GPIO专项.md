---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 #ESP32开发 

## 1 目录

```toc
```

## 2 ESP32系列GPIO硬件架构

ESP32系列的GPIO架构如下图所示(下图为ESP32)：
	![[chrome_AWDTtlXSXc.png]]
	![[chrome_JKccr4VVc3.png]]
可以得到：
1. 从CPU来的外设信号到物理引脚有如下的两种方式：
	1. 通过 `IO_MUX` 进行直接连接到对应的若干引脚
	2. 
