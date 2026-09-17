---
number headings: auto, first-level 1, max 6, 1.1
---
#SSD基础 

参考书籍：
- 深入浅出SSD 第2版

# 1 目录

```toc
```

# 2 基础概述


NAND特性：
- 闪存块必须先擦除才能写入，不可覆盖写入

# 3 FTL技术

## 3.1 FTL概述

FTL为内存转换层(Flash Translation Layer)，用于完成主机逻辑地址空间到闪存物理空间的转换。

其承担的特性有：
- <font color="#9bbb59">空间映射</font>：逻辑地址到物理地址之间的映射和转换
- <font color="#9bbb59">数据的擦除和写入</font>：NAND必须先擦除再写入
- <font color="#9bbb59">垃圾回收</font>：
- <font color="#9bbb59">磨损均衡</font>：每个闪存块的写入次数是有限的，<font color="#c00000">写入次数过多闪存块寿命可能耗尽</font>
- <font color="#9bbb59">读干扰问题</font>：每个闪存块的可读取次数也是有限的，<font color="#c00000">读取次数过多时可能会丢失数据</font>
- <font color="#9bbb59">数据保持问题</font>：由于电荷流失，在SSD上电时，定期扫描闪存并刷新数据
- <font color="#9bbb59">虚拟SLC</font>：可以把TLC或QLC配置成SLC，当作缓存，增加读写速度和可靠性
- <font color="#9bbb59">坏块管理</font>：屏蔽不可使用的坏块
- <font color="#9bbb59">异常掉电处理</font>

FTL根据执行方的不同，可以分为：
- Host-Based：使用主机(计算机)的CPU资源进行，例如：
	- SPI NAND
- Device-Based：使用SSD自己的控制器进行，<span style="background:#fff88f"><font color="#c00000">是主流的实现方式</font></span>，例如：
	- UFS、TF卡、eMMC、SSD等

## 3.2 映射管理

### 3.2.1 映射的种类

根据映射粒度的不同，FTL可以分为：
- 块映射：以内存块为映射粒度，一个用户逻辑块可以映射为任意一个闪存物理块
	- 优点：映射表空间小、连续大尺寸数据写入性能良好
	- 缺点：<font color="#c00000">小数据块写入性能差</font>，当写入小尺寸数据时，即使只更新一个逻辑页，也需要把整个物理块读取出来，改变数据，写入整块
- 页映射：以内存页为映射粒度，<span style="background:#fff88f"><font color="#c00000">是SSD常用的映射方式</font></span>
	- 有
- 混合映射：




 