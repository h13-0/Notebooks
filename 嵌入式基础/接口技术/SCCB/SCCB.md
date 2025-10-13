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
	- `SCCB_E` ：<span style="background:#fff88f"><font color="#c00000">线路的传输/空闲引脚</font></span>，类似于I2C的Start/Stop时序，虽然规范中叫他片选引脚( `Serial Chip Select Output` )
		- 高电平时表示总线空闲
		- 低电平时表示总线传输或挂起
	- `SIC_C` ：时钟线路，类似于I2C的SCL，
		- 当总线处于非空闲模式时，主机驱动该引脚发送时钟信号，且 `SIO_D` 只在  `SIO_C` 低电平时发生变化
		- 当总线处于空闲模式时，保持高电平
	- `SIO_D` ：数据线路，类似于I2C的SDA，
		- 总线空闲时保持浮动，状态不固定
		- 在挂起模式时保持低电平
不过通常为了节省管脚(<font color="#7f7f7f">规避专利</font>)，其通常省略 `SCCB_E` 