---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 #Linux驱动开发 #应试笔记与八股 

# 1 Readme

本文为[[Linux内核原理及其开发/minimal-linux-drivers/Readme|最小Linux驱动]]子板块的相关八股汇总。

# 2 minimal-linux-drivers




## 2.1 mm2m_device





## 2.2 mvideo_device

### 2.1.1 通用基础类

#### 2.1.1.1 vb2_queue中维护了几个队列，队列中的buffer是什么状态

1. `vb2_queue` 中维护了两个队列，分别是：
	1. 用户入队后驱动还没来得及出队的队列，队列中的buffer状态为 `QUEUED`
	2. 驱动入队后用户还没来得及出队的队列，队列中的buffer状态为 `DONE*`
2. 


### 2.1.2 机制类

#### 2.1.2.1 该驱动



## 2.3 vloop



