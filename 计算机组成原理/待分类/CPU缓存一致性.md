---
number headings: auto, first-level 2, max 6, 1.1
---
#计算机组成原理 

## 1 目录

```toc
```

## 2 对称多处理器(SMP)CPU的基本内存缓存架构

SMP处理器的基本内存缓存架构如下图所示：
	![[Pasted image 20250221133107.png]]
其多个CPU之间的L1、L2 Cache每个CPU独立使用，L3和RAM是共享使用。
当CPU需要操作数据时，其会按照L1、L2、L3、RAM的顺序进行查询。而因为
