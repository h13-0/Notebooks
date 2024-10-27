---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 

本文主要基于I2C标准[UM10204](https://www.nxp.com/docs/en/user-guide/UM10204.pdf)进行编写。

# 目录

```toc
```

## 1 I2C总线标简介

I2C是指Inter-Integrated Circuit，由飞利浦公司制定，其协议标准为[UM10204](https://www.nxp.com/docs/en/user-guide/UM10204.pdf)。
除了基础的I2C总线传输外，还有<font color="#c00000">基于I2C总线协议的</font>SMB(System Management Bus)、PMBus(Power Management Bus)、IMPI(ntelligent Platform Management Interface)、DDC(Display Data Channel)和ATCA(Advanced Telecom Computing Architecture)<font color="#c00000">等拓展协议</font>。

此外，还有由MIPI联盟推出的向下兼容I2C的I3C协议，不过不在本文讨论范围内。

## 2 I2C总线特性

### 2.1 I2C总线的电气特性规定

<span style="background:#fff88f"><font color="#c00000">重要!!!</font></span>
I2C总线

### 2.2 传输的若干基本环节及其时序

本章节仅为传输的若干基本环节及其时序的讲解。不涉及总体的流程。总体流程见下一章节。

#### 2.2.1 SDA与SCL电平变化顺序的基本要求

在I2C协议中，SDA与SCL电平变化顺序主要有以下两种模式：
1. 在<font color="#c00000">传输普通数据</font>时，SCL会周期性的输出高电平脉冲，<font color="#c00000">并且在SCL保持为高电平时</font>，<span style="background:#fff88f"><font color="#c00000">SDA不可发生电平变化</font></span>。
	![[chrome_QPPGptJUqj.png]]
2. 在表示I2C控制信息时(即开始信号和结束信号)，<font color="#c00000">SCL会保持高电平</font>，<span style="background:#fff88f"><font color="#c00000">并且SDA发生电平变化</font></span>。
	1. 当发送开始信号时，SCL保持高电平，同时SDA由高变低。
	2. 当发送停止信号时，SCL保持高电平，同时SDA由低变高。

#### 2.2.2 开始信号及I2C空闲状态

在开始信号发生之前，<font color="#c00000">SDA和SCL均要保持在高电平</font>，<span style="background:#fff88f"><font color="#c00000">此时I2C为空闲状态</font></span>。

![[chrome_y7APMtSvm8.png]]

随后SCL保持高电平，SDA变低，发出开始信号。

#### 2.2.3 通用八位数据传输以及ACK/NACK

![[chrome_cV6snQc7tc.png]]
1. 在通用八位数据传输时，SDA先到达目标电平，随后SCL发送一个高电平脉冲。在此环节内，SDA高电平表示1，低电平表示0。
2. 重复8次完成一个Byte发送后，<font color="#c00000">数据发送方会释放数据总线</font>，<font color="#c00000">数据接收方会</font>在下一个SCL周期到来前将SDA的电平控制到ACK/NACK的目标电平。
3. 上述两步共计9个SCL脉冲完成了一个通用八位数据传输。ACK/NACK具体见下一同级章节。
<font color="#c00000">地址数据和普通八位数据均用此方法传输</font>。
<span style="background:#fff88f"><font color="#c00000">数据先发送高位再发送低位</font></span>。

#### 2.2.4 应答要求

应答信号的发送时机如上一章节所述，此处不再赘述。
应答信号一共两种：
1. ACK应答信号：此时数据接收方会将SDA控制为低电平，表示<span style="background:#fff88f">"<font color="#c00000">数据接收成功，并且期待接收下一字节</font>"</span>
2. NACK应答信号：此时数据接收方会将SDA控制为高电平，表示<span style="background:#fff88f">"<font color="#c00000">不再接收更多数据</font>"</span>。

### 2.3 I2C传输的总体流程

通常来说，嵌入式开发框架会同时提供普通的基本环节操作和封装好的数据传输操作，以分别应用于非标准的和标准的I2C硬件模型。

对于标准的I2C硬件模型，其从设备通常会有固定的I2C地址和若干可选的寄存器地址，对于这种标准模型，其读写流程是固定的，具体如下列章节所述。

#### 2.3.1 写入数据

对于8位地址的标准I2C通信模型，其写入数据的流程如下：
1. 发送开始信号
2. 发送8位的从设备I2C地址
3. 等待从机ACK
4. 发送要写入的寄存器地址
5. 等待从机ACK
6. 传送n byte(s)数据，并在：
	- 非末尾byte处等待从设备ACK
	- 末尾byte不等待从设备ACK，进入环节5
7. 发送结束信号
数据包结构如下：
	

#### 2.3.2 读取数据

对于8位地址的标准I2C通信模型，其读取数据的流程如下：
1. 发送开始信号
2. 发送8位的从设备I2C地址
3. 等待从设备ACK
4. 发送要读取的寄存器地址
5. 等待从设备ACK
6. 重新发送开始信号
7. 主设备接收I2C数据，并发送ACK直到数据传输完毕
8. 发送结束信号
