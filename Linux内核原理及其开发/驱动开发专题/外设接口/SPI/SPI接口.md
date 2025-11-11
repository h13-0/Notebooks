---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 #Linux驱动开发 

# 1 Readme

本章节前置内容：
- [[../../../../嵌入式基础/接口技术/SPI/SPI总线标准|SPI总线标准]]

# 2 目录

```toc
```

# 3 内核设备模型及数据结构



## 3.1 


# 4 设备树配置

## 4.1 控制器设备树配置

## 4.2 从设备设备树配置

在上一章节中已经完成了主机spi设备树节点的配置，其基本结构为

```dts
/ {   // 根节点
	spix {
	}
}

&spix {
	status = "okay";
	// 从设备节点
	spi_device@xx {
	}
}
```

而<font color="#c00000">SPI从设备必须作为SPI控制器节点的子节点存在</font>，其必选属性有：
- `compatible` ：描述
- `reg` ：片选号，与控制器的

其可选属性有：
- `spi-cpol` ：SPI的反向时钟特性(CPOL)
- `spi-cpha` ：SPI的移相时钟特性(CPHA)
- `spi-cs-high` ：片选为高电平
- `spi-3wire` ：3线SPI模式(半双工)
- `spi-lsb-first` ：SPI的地位优先特性(LSB)
- `spi-max-frequency` ：该外设可接受的最大SPI时钟

[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/spi/spi.h#^j2uocs|spi_device]]

# 5 软件接口
