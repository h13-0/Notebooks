---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 

## 1 目录

```toc
```

## 2 Modbus概述

Modbus有如下三种协议：
- Modbus ASCII
- [Modbus RTU](https://modbus.org/docs/Modbus_Application_Protocol_V1_1b.pdf)
- Modbus TCP
Modbus协议规定，使用Modbus的设备必须支持Modbus RTU，且默认为Modbus RTU，因此大多数设备使用的均为Modbus RTU。

此外，<font color="#c00000">协议规定Modbus协议是一种请求/应答协议</font>，<font color="#c00000">也就意味着无论是哪种Modbus</font>，<span style="background:#fff88f"><font color="#c00000">从站均不能主动向主站发送信息</font></span>。

### 2.1 Modbus RTU

#### 2.1.1 Modbus RTU基本规定

Modbus RTU的所有数据包均遵从如下基本格式：

|  地址域  |  功能码  | 数据域  | CRC差错校验 |
| :---: | :---: | :--: | :-----: |
| 1Byte | 1Byte | 长度不定 |  2Byte  |

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

#### 2.1.2 地址域

|  地址域  |  功能码  | 数据域  | CRC差错校验 |
| :---: | :---: | :--: | :-----: |
| 1Byte | 1Byte | 长度不定 |  2Byte  |

在上述的数据包基本格式中：
- 地址域共计1Byte，被划分为：
	- 地址 $0$ 被划分为广播地址
	- 地址 $[1, 247]$ 被划分为子节点单独地址
	- 地址 $[248, 255]$ 被用作保留地址
	因此：
	- 从机地址范围被定义在 $[1, 247]$ 
	- 保留区可以用于设置特定地址段的广播指令等

#### 2.1.3 功能码及其报文结构

|  地址域  |  功能码  | 数据域  | CRC差错校验 |
| :---: | :---: | :--: | :-----: |
| 1Byte | 1Byte | 长度不定 |  2Byte  |

在上述的数据包基本格式中：
- 功能码固定为1Byte
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

##### 2.1.3.1 01H 读线圈寄存器(bit)

###### 2.1.3.1.1 请求报文结构

正如基本规定中所述：
- Modbus RTU中设备地址占8位、寄存器地址占16位。
- 01H 读线圈寄存器可以读多个寄存器。
则有读线圈寄存器的数据包格式为：

|  格式：  | 地址域  | 功能码  | 起始地址<br>高字节 | 起始地址<br>低字节 | 读取数量<br>高字节 | 读取数量<br>低字节 | CRC校验 |
| :---: | :--: | :--: | :---------: | :---------: | :---------: | :---------: | :---: |
| Demo： | 0x01 | 0x01 |    0x02     |    0xC4     |    0x01     |    0x05     | 2Byte |

则上述Demo的含义为：
- 读取从站地址为 `0x01` 的设备上的 `0x02C4` 地址开始的连续 `0x0105` 个寄存器

###### 2.1.3.1.2 应答报文结构




##### 2.1.3.2 02H 读离散线圈寄存器(bit)



### 2.2 Modbus TCP

Modbus TCP默认端口为502端口。