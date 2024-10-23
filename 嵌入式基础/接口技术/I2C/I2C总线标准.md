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

### 2.1 SDA与SCL电平变化顺序

在I2C协议中，SDA与SCL电平变化顺序主要有以下两种模式：
1. 在传输普通数据时，SDA所传输的


### 2.2 基本时序

#### 2.2.1 开始信号及传输前电平信号要求

在开始信号发生之前，

![[chrome_y7APMtSvm8.png]]






## 3 I2C总线协议

### 3.1 标准模式、快速



