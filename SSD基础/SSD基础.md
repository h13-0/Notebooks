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

NAND Flash：
- 页面：最小读写单位，通常为4~16KB
- 块：最小擦除单位，通常为128~512页

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
- 页映射：以内存页为映射粒度，<span style="background:#fff88f"><font color="#c00000">是SSD常用的映射方式</font></span>
- 混合映射：一个逻辑块可以映射到任何一个物理块，块内页面采用页面映射。

![[Resources/Pasted image 20260917161253.png]]


上述表格中的优缺点，<span style="background:#fff88f"><font color="#c00000">其主要区别在于随机写入性能</font></span>。
具体而言，写入一小块(例如一页)数据，其区别为：
- 块映射：
	1. 申请一个空闲块
	2. <font color="#c00000">旧块中数据读出</font>
	3. 替换页面数据
	4. <font color="#c00000">写入新块</font>
	5. 更改块表映射
	6. 后续GC回收
- 页映射：
	1. <font color="#c00000">申请一个空闲页</font>
	2. <font color="#c00000">将新数据写入新页</font>
	3. 更新页表映射
	4. <font color="#c00000">将原页面标记为失效</font>
	5. 后续GC回收



