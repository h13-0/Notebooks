---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 

## 1 Readme

本文基于[Modbus官方文档](https://modbus.org/docs/Modbus_Application_Protocol_V1_1b.pdf)进行学习。

## 2 目录

```toc
```

## 3 Modbus概述

在众多学习资料中往往会提到：

> Modbus定义了Modbus ASCII、Modbus RTU、Modbus TCP/IP三种基本协议。

<span style="background:#fff88f"><font color="#c00000">但这种看法是不准确的、不本质的</font></span>。
Modbus确实在不同的物理层和链路层上的实现不同，<span style="background:#fff88f"><font color="#c00000">但是这三种情况在应用层的数据封装上完全一致</font></span>。其主要区别在于：
- Modbus RTU以逻辑二进制进行数据传输，直接传输Modbus对应的二进制数据包。
- Modbus TCP由于在TCP/IP网络上运行，<font color="#c00000">需要处理网络相关的问题</font>，<font color="#c00000">如会话的建立和维持</font>，这由MBAP头部分处理。
- Modbus ASCII<font color="#c00000">使用ASCII字符来编码二进制数据</font>，每个数据字节被分割为两个ASCII字符。例如使用ASCII字符 `'0'` 和 `'F'` 编码二进制 ``


Modbus有如下三种协议：
- Modbus ASCII
- Modbus RTU
- Modbus TCP
Modbus协议规定，使用Modbus的设备必须支持Modbus RTU，且默认为Modbus RTU，因此大多数设备使用的均为Modbus RTU。

此外，<font color="#c00000">协议规定Modbus协议是一种请求/应答协议</font>，<font color="#c00000">也就意味着无论是哪种Modbus</font>，<span style="background:#fff88f"><font color="#c00000">从站均不能主动向主站发送信息</font></span>。

Modbus当前支持的硬件协议：
- TCP/IP协议
- 异步串口协议：
	- RS-232
	- RS-442
	- RS-485
	- 光纤
	- 无线电
- [[第三章 数据链路层#3 4 3 HDLC协议|HDLC]](Modbus Plus)

Modbus官方缩写如下表所示。

| <center>缩写</center>   | <center>含义</center>             |
| ---- | ------------------------------- |
| ADU  | Application Data Unit           |
| HDLC | High level Data Link Control    |
| HMI  | Human Machine Interface         |
| IETF | Internet Engineering Task Force |
| I/O  | Input/Output                    |
| IP   | Internet Protocol               |
| MAC  | Medium Access Control           |
| MB   | MODBUS Protocol                 |
| MBAP | MODBUS Application Protocol     |
| PDU  | Protocol Data Unit              |
| PLC  | Programmable Logic Controller   |
| TCP  | Transport Control Protocol      |

Modbus提供了一种简单的，可以跨物理层/数据链路层/网络层的通信协议：
	![[chrome_Ylc5HPXvpA.png]]

Modbus在大多数总线下

![[chrome_1AsQ0QQGM7.png]]

### 3.1 Modbus RTU

#### 3.1.1 Modbus RTU基本规定

Modbus RTU的所有数据包均遵从如下基本格式：

|  地址域  |  功能码  |                   数据域                    | CRC差错校验 |
| :---: | :---: | :--------------------------------------: | :-----: |
| 1Byte | 1Byte | 长度不定，<font color="#c00000">也可能不存在</font> |  2Byte  |

在通信模型上：
- Modbus RTU可以分为主站和从站，<font color="#c00000">在一条链路上只能有1个主站</font>，<font color="#c00000">但是可以有多个从站</font>。
- 与I2C类似的是，Modbus中也有<font color="#9bbb59">从站地址</font>和<font color="#9bbb59">寄存器地址</font>的概念。其中，从站地址8位、<font color="#c00000">寄存器地址16位</font>。
- Modbus RTU在<font color="#c00000">任何情况下</font><span style="background:#fff88f"><font color="#c00000">子节点都不会主动发送数据</font></span>，仅当主站请求时，从站才可以发。
- Modbus RTU<font color="#c00000">有广播和单拨两种模式</font>：
	- <font color="#c00000">在广播模式下</font>，所有从站必须执行主站命令而<font color="#c00000">无需应答返回</font>。
	- 在单播模式下，<font color="#c00000">子节点必须做出应答</font>，<font color="#c00000">只有应答完成后主站才可以进行下一个事务处理</font>。
	- 和IP协议类似，<font color="#c00000">广播和单播模式通过地址进行区分</font>。

<span style="background:#fff88f"><font color="#c00000">在数据结构上</font></span>，Modbus中<font color="#c00000"><u>预先定义了一些数据结构</u></font>，比如：
- 线圈寄存器( `coils` )：1个bit的<font color="#c00000">读写</font>寄存器，通常表示 `TRUE/FALSE` 、 `ON/OFF` 等。
- 离散输入寄存器( `Discrete Inputs` )：1个bit的<span style="background:#fff88f"><font color="#c00000">只读</font></span>寄存器
- 保持寄存器：16个bit的<font color="#c00000">读写</font>寄存器
- 输入寄存器：16个bit的<span style="background:#fff88f"><font color="#c00000">只读</font></span>寄存器
为了方便叙述，将上述的16bit称之为 "字" ，即 "word" 。但是要注意并不是所有的CPU平台的 "word" 长度均为16bit。

#### 3.1.2 地址域

|  地址域  |  功能码  |                   数据域                    | CRC差错校验 |
| :---: | :---: | :--------------------------------------: | :-----: |
| 1Byte | 1Byte | 长度不定，<font color="#c00000">也可能不存在</font> |  2Byte  |

在上述的数据包基本格式中：
- 地址域共计1Byte，被划分为：
	- 地址 $0$ 被划分为广播地址
	- 地址 $[1, 247]$ 被划分为子节点单独地址
	- 地址 $[248, 255]$ 被用作保留地址
	因此：
	- 从机地址范围被定义在 $[1, 247]$ 
	- 保留区可以用于设置特定地址段的广播指令等

#### 3.1.3 功能码及其报文结构

|  地址域  |  功能码  |                   数据域                    | CRC差错校验 |
| :---: | :---: | :--------------------------------------: | :-----: |
| 1Byte | 1Byte | 长度不定，<font color="#c00000">也可能不存在</font> |  2Byte  |

在上述的数据包基本格式中：
- 功能码固定为1Byte，其中：
	- 功能码 $0$ 无效
	- 功能码 $[1, 127]$ 作为普通功能码使用
	- 功能码 $[128, 255]$ 用于异常响应
- `${功能码}${数据}` 部分被称作<font color="#9bbb59">PDU</font>(<font color="#9bbb59">协议数据单元</font>)。

Modbus RTU内置的功能码如下：

| <center>功能</center>                   |  功能码  | 操作类型 | <center>操作数量</center> |
| ------------------------------------- | :---: | :--: | --------------------- |
| <font color="#c00000">读线圈寄存器</font>   |  01   |  位   | 单个或多个                 |
| <font color="#c00000">读离散线圈寄存器</font> |  02   |  位   | 单个或多个                 |
| <font color="#c00000">读保持寄存器</font>   |  03   |  字   | 单个或多个                 |
| <font color="#c00000">读输入寄存器</font>   |  04   |  字   | 单个或多个                 |
| <font color="#c00000">写单个线圈寄存器</font> |  05   |  位   | 单个                    |
| <font color="#c00000">写单个保持寄存器</font> |  06   |  字   | 单个                    |
| 读异常状态                                 |  07   |      |                       |
| 诊断                                    |  08   |      |                       |
| 读通用事件计数器                              |  0B   |      |                       |
| 获取通用事件日志                              |  0C   |      |                       |
| <font color="#c00000">写多个线圈寄存器</font> |  0F   |  位   | 多个                    |
| <font color="#c00000">写多个保持寄存器</font> |  10   |  字   | 多个                    |
| 回报从站地址                                |  11   |      |                       |
| 读文件记录                                 |  14   |      |                       |
| 写文件记录                                 |  15   |      |                       |
| 使用AND/OR操作寄存器                         |  16   |      |                       |
| 读写多个寄存器                               |  17   |      |                       |
| 读FIFO队列                               |  18   |      |                       |
|                                       |  2B   |      |                       |
|                                       | 2B/0D |      |                       |
|                                       | 2B/0E |      |                       |

注：
- <font color="#c00000">上述表格中常用功能会被标红</font>

##### 3.1.3.1 01H 读线圈寄存器(bit)

###### 3.1.3.1.1 请求报文结构

正如基本规定中所述：
- Modbus RTU中设备地址占8位、寄存器地址占16位。
- 01H 读线圈寄存器可以读多个寄存器。
则有读线圈寄存器的数据包格式为：

|  格式：  | 地址域  | 功能码  | 起始地址<br>高字节 | 起始地址<br>低字节 | 读取数量<br>高字节 | 读取数量<br>低字节 | CRC校验 |
| :---: | :--: | :--: | :---------: | :---------: | :---------: | :---------: | :---: |
| Demo： | 0x01 | 0x01 |    0x02     |    0xC4     |    0x01     |    0x05     | 2Byte |

则上述Demo的含义为：
- 读取从站地址为 `0x01` 的设备上的 `0x02C4` 地址开始的连续 `0x0105` 个寄存器

###### 3.1.3.1.2 应答报文结构




##### 3.1.3.2 02H 读离散线圈寄存器(bit)



### 3.2 Modbus TCP

Modbus TCP默认端口为502端口。