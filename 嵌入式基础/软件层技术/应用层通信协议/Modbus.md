---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 

## 1 Readme

本文基于[Modbus官方文档](https://modbus.org/docs/Modbus_Application_Protocol_V1_1b.pdf)进行学习。

## 2 目录

```toc
```

## 3 Modbus

在众多学习资料中往往会提到：

> Modbus定义了Modbus ASCII、Modbus RTU、Modbus TCP/IP三种基本协议。

<span style="background:#fff88f"><font color="#c00000">但这种看法是不准确的、不本质的</font></span>。
Modbus确实在不同的物理层和链路层上的实现不同，<span style="background:#fff88f"><font color="#c00000">但是这三种情况在应用层的数据封装上完全一致</font></span>。其主要区别在于：
- Modbus RTU以逻辑二进制进行数据传输，直接传输Modbus对应的二进制数据包。<font color="#c00000">其主要在串行通信中使用</font>。
- Modbus TCP由于在TCP/IP网络上运行，<font color="#c00000">需要处理网络相关的问题</font>，<font color="#c00000">如会话的建立和维持</font>，这由MBAP头部分处理。
- Modbus ASCII<font color="#c00000">使用ASCII字符来编码二进制数据</font>，每个数据字节被分割为两个ASCII字符。例如使用ASCII字符 `'0'` 和 `'F'` 编码二进制 `0x0F` 。

此外，<font color="#c00000">协议规定Modbus协议是一种请求/应答协议</font>，<font color="#c00000">也就意味着无论是哪种Modbus</font>，<span style="background:#fff88f"><font color="#c00000">从站均不能主动向主站发送信息</font></span>。

此外，主站也可以被叫作Server，从站被叫作Client。

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

| <center>缩写</center> | <center>含义</center>             |
| ------------------- | ------------------------------- |
| ADU                 | Application Data Unit           |
| HDLC                | High level Data Link Control    |
| HMI                 | Human Machine Interface         |
| IETF                | Internet Engineering Task Force |
| I/O                 | Input/Output                    |
| IP                  | Internet Protocol               |
| MAC                 | Medium Access Control           |
| MB                  | MODBUS Protocol                 |
| MBAP                | MODBUS Application Protocol     |
| PDU                 | Protocol Data Unit              |
| PLC                 | Programmable Logic Controller   |
| TCP                 | Transport Control Protocol      |

Modbus提供了一种简单的，可以跨物理层/数据链路层/网络层的通信协议：
	![[chrome_Ylc5HPXvpA.png]]

### 3.1 Modbus基本报文结构

Modbus的数据包均遵从如下基本格式：

![[chrome_1AsQ0QQGM7.png]]

即：

|  地址域  |  功能码  |                   数据域                    | CRC差错校验 |
| :---: | :---: | :--------------------------------------: | :-----: |
| 1Byte | 1Byte | 长度不定，<font color="#c00000">也可能不存在</font> |  2Byte  |

在上图/上表中：
- `${地址域}${功能码}${数据}${差错校验}` 部分被称作<font color="#9bbb59">ADU</font>(<font color="#9bbb59">应用数据单元</font>)。
- `${功能码}${数据}` 部分被称作<font color="#9bbb59">PDU</font>(<font color="#9bbb59">协议数据单元</font>)。

在通信模型上：
- Modbus可以分为主站和从站，<font color="#c00000">在一条链路上只能有1个主站</font>，<font color="#c00000">但是可以有多个从站</font>。
- 与I2C类似的是，Modbus中也有<font color="#9bbb59">从站地址</font>和<font color="#9bbb59">寄存器地址</font>的概念。其中，从站地址8位、<font color="#c00000">寄存器地址16位</font>。
- 与C/S模型类似的是，Modbus在<font color="#c00000">任何情况下</font><span style="background:#fff88f"><font color="#c00000">从站都不会主动发送数据</font></span>，仅当主站请求时，从站才可以发。
- Modbus<font color="#c00000">有广播和单拨两种模式</font>：
	- <font color="#c00000">在广播模式下</font>，所有从站必须执行主站命令而<font color="#c00000">无需应答返回</font>。
	- 在单播模式下，<font color="#c00000">子节点必须做出应答</font>，<font color="#c00000">只有应答完成后主站才可以进行下一个事务处理</font>。
	- 和IP协议类似，<font color="#c00000">广播和单播模式通过地址进行区分</font>。

<span style="background:#fff88f"><font color="#c00000">在数据结构上</font></span>，Modbus定义了如下四种基础的数据结构：

| <center>数据结构</center> | 数据类型    | 读写类型 | <center>附注</center>            |
| --------------------- | ------- | ---- | ------------------------------ |
| 离散输入                  | 单bit数据  | 只读   | 通常表示 `TRUE/FALSE` 、 `ON/OFF` 等 |
| 线圈                    | 单bit数据  | 可读可写 |                                |
| 输入寄存器                 | 16bit的字 | 只读   |                                |
| 保持寄存器                 | 16bit的字 | 可读可写 |                                |

为了方便叙述，将上述的16bit称之为 "字" ，即 "word" 。但是要注意并不是所有的CPU平台的 "word" 长度均为16bit。

在报文长度上，<font color="#c00000">由于第一版Modbus的实现限制了ADU和PDU的长度</font>(该版本限制ADU最长256字节)，因此：
- RS232、RS485的Modbus中：
	- <font color="#c00000">PDU最长为253字节</font>
	- ADU最长为256字节：
		- Addr=1Byte
		- PDU=253Byte
		- CRC=2Byte
- TCP中的Modbus中：
	- <font color="#c00000">PDU最长为253字节</font>
	- ADU最长为260字节：
		- MBAP=7Byte
		- Addr=1Byte
		- PDU=253Byte
		- CRC=2Byte
该设计<font color="#c00000">保证了在任何链路中的数据协议单元长度均为253字节</font>，从而实现了跨物理层/数据链路层/网络层的通信协议。

<span style="background:#fff88f"><font color="#c00000">Modbus在数据编码时采用大端模式</font></span>。

#### 3.1.1 地址域

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

#### 3.1.2 功能码及其对应报文结构

在Modbus中的通信过程中：
- 如果从站的响应<font color="#c00000">没有错误</font>，则从站<font color="#c00000">返回报文的功能码与主站的请求报文中一致</font>。
- 如果从站的响应<font color="#c00000">发生错误</font>，则从站<font color="#c00000">返回报文的功能码为异常功能码</font>(<font color="#c00000">定义为</font> `请求功能码+0x80` )，具体可见异常响应章节。

|  地址域  |  功能码  |                   数据域                    | CRC差错校验 |
| :---: | :---: | :--------------------------------------: | :-----: |
| 1Byte | 1Byte | 长度不定，<font color="#c00000">也可能不存在</font> |  2Byte  |

在上述的数据包基本格式中：
- 功能码固定为1Byte，其中：
	- 功能码 $0$ 无效
	- 功能码 $[1, 127]$ 作为普通功能码使用
	- 功能码 $[128, 255]$ 用于异常响应

Modbus内置的功能码如下：

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

##### 3.1.2.1 01H 读线圈寄存器(bit)

###### 3.1.2.1.1 请求报文结构

正如基本规定中所述：
- Modbus中设备地址占8位、寄存器地址占16位。
- 01H 读线圈寄存器可以读多个寄存器。
则有读线圈寄存器的数据包格式为：

|  格式：  | 地址域  | 功能码  | 起始地址<br>高字节 | 起始地址<br>低字节 | 读取数量<br>高字节 | 读取数量<br>低字节 | CRC校验 |
| :---: | :--: | :--: | :---------: | :---------: | :---------: | :---------: | :---: |
| Demo： | 0x01 | 0x01 |    0x02     |    0xC4     |    0x01     |    0x05     | 2Byte |

则上述Demo的含义为：
- 读取从站地址为 `0x01` 的设备上的 `0x02C4` 地址开始的连续 `0x0105` 个寄存器

###### 3.1.2.1.2 应答报文结构




##### 3.1.2.2 02H 读离散线圈寄存器(bit)

### 3.2 异常响应


### 3.3 Modbus On TCP

Modbus TCP默认端口为502端口。



