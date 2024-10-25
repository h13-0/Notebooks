---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 

## 1 目录

```toc
```

## 2 SPI总线简介

SPI，即Serial Peripheral interface，即串行外围设备接口。其最早由摩托罗拉公司在其MC68HC11系列处理器上定义，但是后续并没有一个专门的委员会或标准化组织来定义和管理这个协议，因此尽管各制造商的SPI基本上完全兼容，但是仍有一些细节上的区别。

标准的SPI有且仅有如下四根电气线路：
- MOSI：Master Output Slave Input，主设备向从设备发送数据的线路
- MISO：Master Input Slave Output，从设备向主设备发送数据的线路
- SCK(CLK)：时钟信号
- $\overline{\text{SS}}$(CS)：片选信号，<font color="#c00000">注意低电平为使能</font>。
在此之上，为了适应不同的需求和场景，SPI还衍生出了如下的变体：
- 3-wire SPI：<font color="#c00000">将MISO和MOSI合并成一根电气线路</font>(称作SDA)，<span style="background:#fff88f"><font color="#c00000">为半双工通信</font></span>。
- Dual SPI：在3-wire SPI的基础上，又增加了一个MISO和MOSI共用的电路，并称为IO0和IO1，<span style="background:#fff88f"><font color="#c00000">为半双工通信</font></span>。
- Quad SPI：在3-wire SPI的基础上，使用4根MISO和MOSI复用的电气线路，<span style="background:#fff88f"><font color="#c00000">为半双工通信</font></span>。

初版SPI协议的规范定义于[M68HC11系列的Datasheet](https://www.nxp.com/docs/en/data-sheet/M68HC11E.pdf)的Chapter 8上(但是看这个没什么用)。

## 3 SPI总线特性

### 3.1 传输的若干基本环节及其时序

#### 3.1.1 SCK的时钟相位(CPHA)与时钟极性(CPOL)

时钟相位(CPHA)：在时钟脉冲(SCK)的第一个还是第二个边缘触发采样。
- `CHPA=0` ：在SCK脉冲的第一个边缘触发采样
- `CHPA=1` ：在SCK脉冲的第二个边缘触发采样

时钟极性(CPOL)：定义时钟信号<font color="#c00000">在信号就绪时</font>的电平为高还是为低。
- `CPOL=0` ：SCK空闲时为0，信号就绪时为1
- `CPOL=1` ：SCK空闲时为1，信号就绪时为0

上述两个配置项共可以组合出4种SPI配置。

#### 3.1.2 数据传输

在上述两个配置项后，其数据传输大致流程为：
1. MISO或MOSI抵达对应电平，使数据线电平就绪
2. 控制SCK电平到达采样电平，并在第一个或者第二个边缘触发接收方采样信号。
3. SCK恢复到空闲电平，并回到步骤1，直到完成8个或者16个时钟周期，完成一个数据单位的传输。
时序图如下(参考STM32开发手册)：
	![[SPI_CPOL_CPHA.jpeg]]

### 3.2 SPI拓展与变种

#### 3.2.1 缺线SPI

缺线SPI是指只使用MOSI或MISO的SPI，其通常是缺少MISO，用于单向通信的设备模型(例如显示屏等)。这也是最常用的SPI变种。

#### 3.2.2 3-wire SPI

由于SPI所处的工作逻辑限制，<font color="#c00000">尽管标准SPI是全双工电路</font>，<span style="background:#fff88f"><font color="#c00000">但是往往读写交替运行</font></span>。3-wire SPI是指只使用一根电气线路分时复用给MOSI和MISO的一种方式，在保证基本不影响性能的情况下节约了电气连接。其可以使用标准四线SPI配合一些外围电路修改而成。程序中需要注意分时复用。

#### 3.2.3 Dual SPI

Dual SPI基于3-wire SPI进行改进，又增加了一个MISO和MOSI复用的电气线路，称为IO0和IO1，一次可以传输2bit数据。<font color="#c00000">为半双工通信协议</font>。

#### 3.2.4 Quad SPI

Quad SPI通常简称QSPI，基于3-wire SPI进行改进，使用四个MISO和MOSI复用的电气线路，称为IO0、IO1、IO2、IO3，一次可以传输4bit数据。<font color="#c00000">为半双工通信协议</font>。

### 3.3 总线特性汇总

SPI支持的特性如下：
- <font color="#c00000">标准SPI是全双工</font>(但是往往交替传输信号)，<font color="#c00000">变种的三种SPI是半双工</font>。

SPI不支持的特性如下：
- 没有流控制
- 没有应答机制
- <font color="#c00000">不支持从机主动发送数据，需要外部IO通知主机查询</font>。




