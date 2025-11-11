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
	[${label}: ]node-name[@${unit-address}] {
		// 从设备属性
	}
}
```

而<font color="#c00000">SPI从设备必须作为SPI控制器节点的子节点存在</font>，其节点结构中：
- `node-name` ：
	- 功能含义：设备的通用名，用于形成设备树路径(`/proc/device-tree`)，<font color="#c00000">不参与驱动匹配</font>
- `unit-address` ：
	- 功能含义：
		- 片选号(`CS index`)，与控制器的CS数组的index一致
		- <font color="#c00000">其为书写形式要求</font>，<font color="#c00000">不决定节点属性</font>，但是必须与 `reg` 属性保持一致
- `label` ：别名，略
其必选属性有：
- `compatible` ：
	- 功能含义：描述兼容性属性，用于驱动匹配
- `reg` ：
	- 功能含义：片选号(`CS index`)，与 `unit-address` 必须匹配，不匹配则dtc警告
其可选属性有：
- `spi-cpol` ：
	- 功能含义：SPI的反向时钟特性([[嵌入式基础/接口技术/SPI/SPI总线标准#^341ed0|CPOL]])
- `spi-cpha` ：
	- 功能含义：SPI的移相时钟特性([[嵌入式基础/接口技术/SPI/SPI总线标准#^341ed0|CPHA]])
- `spi-cs-high` ：
	- 功能含义：片选为高电平
- `spi-3wire` ：
	- 功能含义：3线SPI模式(半双工)
- `spi-lsb-first` ：
	- 功能含义：SPI的地位优先特性(LSB)
- `spi-max-frequency` ：
	- 功能含义：该外设可接受的最大SPI时钟
更精细的片选和传输属性：
- `spi-cs-setup-delay-ns` 、`spi-cs-hold-delay-ns` 、`spi-cs-inactive-delay-ns` ：
	- 功能含义：CS时序与空闲要求
- `spi-rx-delay-us` 、`spi-tx-delay-us` 、`rx-sample-delay-ns` ：
	- 功能含义：收发的采样偏移
- `spi-rx-bus-width` 、`spi-tx-bus-width` ：
	- 功能含义：数据线宽属性，可选1/2/4/8，用于 dual/quad/octal 等[[嵌入式基础/接口技术/SPI/SPI总线标准#^b6tpvl|变种SPI]]


# 5 软件接口
