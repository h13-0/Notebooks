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
	- `SCCB_E` ：<span style="background:#fff88f"><font color="#c00000">线路的enable/disable引脚</font></span>，类似于I2C的Start/Stop时序，虽然规范中叫他片选引脚( `Serial Chip Select Output` )。<span style="background:#fff88f"><font color="#c00000">低电平有效</font></span>。
		- <font color="#c00000">逻辑</font>高电平时表示总线空闲
		- <font color="#c00000">逻辑</font>低电平时表示总线传输或挂起
	- `SIC_C` ：时钟线路，类似于I2C的SCL，高电平有效
		- 当总线处于空闲模式时，保持逻辑高电平
		- 当总线处于传输模式时，主机驱动该引脚发送时钟信号
		- 当总线处于挂起模式时，保持逻辑低电平
	- `SIO_D` ：数据线路，类似于I2C的SDA，高电平有效
		- 总线空闲时保持浮动，状态不固定
		- 在挂起模式时保持逻辑低电平
		- `SIO_D` 只能在 `SIO_C` 为0时发生变化
不过通常为了节省管脚(<font color="#7f7f7f">规避专利</font>)，其通常省略 `SCCB_E` ，此时电平时钟为高电平