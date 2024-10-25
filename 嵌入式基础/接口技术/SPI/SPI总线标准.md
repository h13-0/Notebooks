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
- Quad SPI：四线制数据线，每一个方向都有4根并行传输的线路，可以一次传输4bit。
- Dual SPI：两线制数据线，每一个方向都有2根并行传输的线路，可以一次传输2bit。
- 3-wire SPI：三线SPI

初版SPI协议的规范定义于[M68HC11系列的Datasheet](https://www.nxp.com/docs/en/data-sheet/M68HC11E.pdf)的Chapter 8上(但是看这个没什么用)。

## 3 SPI总线特性

### 3.1 传输的若干基本环节及其时序

#### 3.1.1 时钟相位(CPHA)与时钟极性(CPOL)

时钟相位(CPHA)：在时钟脉冲(SCK)的第一个还是第二个边缘触发采样。
- `CHPA=0` ：在SCK脉冲的第一个边缘触发采样
- `CHPA=1` ：在SCK脉冲的第二个边缘触发采样

时钟极性(CPOL)：定义时钟信号<font color="#c00000">在信号就绪时</font>的电平为高还是为低。
- `CPOL=0` ：SCK空闲时为0，信号就绪时为1
- `CPOL=1` ：SCK空闲时为1，信号就绪时为0

![[SPI_CPOL_CPHA.jpeg]]


#### 3.1.2 时钟相位(CPHA)


### 3.2 总线特性汇总

SPI支持的特性如下：
- 全双工

SPI不支持的特性如下：
- 没有流控制
- 没有应答机制




