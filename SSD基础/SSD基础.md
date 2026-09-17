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
- Host-Based：使用主机(计算机)的CPU资源进行
- Device-Based：使用SSD自己的控制器进行



## 3.2 




