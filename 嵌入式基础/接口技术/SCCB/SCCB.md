---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 

# 1 目录

```toc
```

# 2 SCCB总线简介

SCCB全称为 `Serial Camera Control Bus` ，是豪威公司设计的一款<font color="#c00000">类似于I2C的</font><span style="background:#fff88f"><font color="#c00000">摄像头控制总线</font></span>。

# 3 SCCB总线电气特性

SCCB其具有如下的三根线路：
	![[../../../Resources/chrome_XN4IR4xqvk.png]]
- 其各线路作用为：
	- `SCCB_E` ：<font color="#c00000">线路的启动/空闲引脚</font>，类似于I2C的Start/Stop时序，而非片选
不过通常为了节省管脚(<font color="#7f7f7f">规避专利</font>)，其通常省略 `SCCB_E` 