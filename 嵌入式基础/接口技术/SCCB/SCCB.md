---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 

# 1 目录

```toc
```

# 2 SCCB总线简介

SCCB全称为 `Serial Camera Control Bus` ，是豪威公司设计的一款<font color="#c00000">类似于I2C的</font><span style="background:#fff88f"><font color="#c00000">摄像头控制总线</font></span>。

## 2.1 SCCB总线电气特性

SCCB其具有如下的三根线路：
	![[../../../Resources/chrome_XN4IR4xqvk.png]]
- 其各线路作用为：
	- `SCCB_E` ：<span style="background:#fff88f"><font color="#c00000">线路的enable/disable引脚</font></span>，类似于I2C的Start/Stop时序，虽然规范中叫他片选引脚( `Serial Chip Select Output` )。<span style="background:#fff88f"><font color="#c00000">低电平有效</font></span>。
		- <font color="#c00000">逻辑</font>高电平时表示总线空闲
		- <font color="#c00000">逻辑</font>低电平时表示总线传输或挂起
	- `SIC_C` ：时钟线路，类似于I2C的SCL，<font color="#c00000">高电平有效</font>
		- 当总线处于空闲模式时，保持逻辑高电平
		- 当总线处于传输模式时，主机驱动该引脚发送时钟信号
		- 当总线处于挂起模式时，保持逻辑低电平
	- `SIO_D` ：数据线路，类似于I2C的SDA，<font color="#c00000">高电平有效</font>
		- 总线空闲时保持浮动，状态不固定
		- 在挂起模式时保持逻辑低电平
		- `SIO_D` 只能在 `SIO_C` 为0时发生变化
不过通常为了节省管脚(<font color="#7f7f7f">规避专利</font>)，其通常省略 `SCCB_E` ，此时电平始终为高电平(即逻辑低，表传输)，此时电气连接如下：
	![[../../../Resources/chrome_q2Wp4PQNbf.png]]

## 2.2 SCCB基本时序

SCCB的基本时序如下图所示：
	![[../../../Resources/chrome_gUhCeX0ycJ.png]]
其中需要注意：
1. 在不考虑 `SCCB_E` 时，<font color="#c00000">其数据和时钟线在起始/终止传输信号的电平与I2C的数据和时钟线保持一致</font>。
2. 



# 3 与I2C的异同

|   特性    | <center>SCCB</center>                                                                                     | <center>I2C</center>                                                                |
| :-----: | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
|  电气引脚   | <font color="#c00000">SCCB可选地比I2C多一个使能(片选)引脚</font><br>SCCB还有一个时钟线和数据线                                    | I2C只有一个时钟线和一个数据线                                                                    |
|  电气特性   | SCCB的使能(片选)引脚使用推挽<br>SCCB的时钟和数据总线与I2C保持一致                                                                 | I2C数据和时钟总线均使用开漏+上拉模式                                                                |
|  C/S特性  | SCCB<font color="#c00000">仅支持单主机</font>，<font color="#c00000">无仲裁设计</font>                                | I2C支持多主机，有仲裁优先级                                                                     |
|  时钟控制   | <font color="#c00000">SCCB从机一般不拉时钟，无时钟延伸特性</font>                                                         | <font color="#c00000">I2C支持从机拉伸时钟</font>，可见[[嵌入式基础/应试笔记与八股#^ax59kk\|I2C的SCL脉冲由谁控制]] |
| 启动/终止信号 | <font color="#c00000">SCCB可用使能(片选)引脚控制启动和停止</font><br>不使用该引脚时和I2C保持一致                                     | 启动：SCL为高电平时，SDA从高变低<br>停止：SCL为高电平时，SDA从低变高                                          |
|  空闲电平   | 空闲时：<br>1. `SCCB_E` 为<font color="#c00000">逻辑</font>高电平<br>2. 时钟总线高电平、<font color="#c00000">数据总线浮动</font> | 空闲时时钟总线高电平、<font color="#c00000">数据总线高电平</font>                                     |
|  ACK语义  | <font color="#c00000">接收方不关心ACK语义</font>                                                                  | 接收方必须检查ACK/NACK                                                                     |
|   寻址    | 使用8bit设备ID                                                                                                | 7或10bit+R/W位                                                                        |

注：
1. 上表中差异点被标注为<font color="#c00000">红色</font>；
2. <font color="#c00000">完全可以使用I2C总线驱动SCCB总线</font>
