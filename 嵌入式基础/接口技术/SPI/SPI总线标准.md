---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 

## 1 目录

```toc
```

## 2 SPI总线简介

SPI，即Serial Peripheral interface，即串行外围设备接口。其最早由摩托罗拉公司定义。


标准的SPI有且仅有如下四根电气线路：
- MOSI：Master Output Slave Input，主设备向从设备发送数据的线路
- MISO：Master Input Slave Output，从设备向主设备发送数据的线路
- SCK(CLK)：时钟信号
- CS(SS)：片选信号
在此之上，为了适应不同的需求和场景，SPI还衍生出了如下的变体：
- Quad SPI：四线制数据线，每一个方向都有4根并行传输的线路，可以一次传输4bit。
- Dual SPI：两线制数据线，每一个方向都有2根并行传输的线路，可以一次传输2bit。
- 3-wire SPI：三线SPI

## 3 SPI总线特性

### 3.1 传输的若干基本环节及其时序



### 3.2 总线特性汇总

SPI支持的特性如下：
- 全双工

SPI不支持的特性如下：
- 没有流控制
- 没有应答机制




