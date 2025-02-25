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
1. ESP32系列的GPIO系统由如下两个模块组成：
	1. `IO_MUX` ：<font color="#c00000">性能更高</font>、延迟更低、资源占用更少，但是可选的IO有限
	2. `GPIO matrix` ：<font color="#c00000">性能略低</font>，<font color="#c00000">有额外的延迟</font>，但是允许信号路由到任意GPIO。<font color="#c00000">部分高速外设的速率会因此因此受限</font>，<font color="#c00000">且部分功能必须使用</font> `IO_MUX` 。
2. 从CPU来的外设信号到物理引脚有如下的两种方式：
	1. 通过 `IO_MUX` 进行直接连接到对应的若干引脚
	2. 先通过 `IO_MUX` 再使用 `GPIO matrix` 路由到任意IO
3. 在分配GPIO时，若电气线路允许，则应当按照如下的规则进行分配：
	1. 优先分配 `GPIO matrix` 无法p
	2. 使用可以由 `IO_MUX` 直接连接的引脚，
