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

## 3.1 SPI设备模型

在内核中，SPI总线被定义如下：

```C
const struct bus_type spi_bus_type = {
	.name		= "spi",
	.dev_groups	= spi_dev_groups,
	.match		= spi_match_device,
	.uevent		= spi_uevent,
	.probe		= spi_probe,
	.remove		= spi_remove,
	.shutdown	= spi_shutdown,
};
EXPORT_SYMBOL_GPL(spi_bus_type);
```

### 3.1.1 设备匹配(match)

[[Linux内核原理及其开发/内核源码探析/内核源码分析/drivers/spi/spi.c#spi_match_device 6sulsd|设备匹配函数]]功能简述如下：
![[Linux内核原理及其开发/内核源码探析/内核源码分析/drivers/spi/spi.c#^4jla92]]


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
	- 数据类型： `string-list`
- `reg` ：
	- 功能含义：片选号(`CS index`)，与 `unit-address` 必须匹配，不匹配则dtc警告
	- 数据类型： `uint32_t`，值域 $[0, 256]$
其可选属性有(<font color="#c00000">会配置到</font>[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/spi/spi.h#^877sjn|spi_board_info]]的[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/spi/spi.h#^znds47|mode成员]]中)：
- `spi-cpol` ：
	- 功能含义：SPI的反向时钟特性([[嵌入式基础/接口技术/SPI/SPI总线标准#^341ed0|CPOL]])
	- 数据类型： `flag`
- `spi-cpha` ：
	- 功能含义：SPI的移相时钟特性([[嵌入式基础/接口技术/SPI/SPI总线标准#^341ed0|CPHA]])
		- 设置该flag时 `CPHA=2Edge`
		- 不设置时 `CPHA=1Edge` 
	- 数据类型： `flag` 
- `spi-cs-high` ：
	- 功能含义：片选为高电平
	- 数据类型： `flag`
- `spi-3wire` ：
	- 功能含义：3线SPI模式(半双工)
	- 数据类型： `flag`
- `spi-lsb-first` ：
	- 功能含义：SPI的地位优先特性(LSB)
	- 数据类型： `flag`
- `spi-max-frequency` ：
	- 功能含义：该外设可接受的最大SPI时钟
	- 数据类型： `uint32_t`
更精细的片选和传输属性：
- `spi-cs-setup-delay-ns` 、`spi-cs-hold-delay-ns` 、`spi-cs-inactive-delay-ns` ：
	- 功能含义：CS时序与空闲要求
	- 数据类型： `uint32_t`
- `spi-rx-delay-us` 、`spi-tx-delay-us` 、`rx-sample-delay-ns` ：
	- 功能含义：收发的采样偏移
	- 数据类型： `uint32_t`
- `spi-rx-bus-width` 、`spi-tx-bus-width` ：
	- 功能含义：数据线宽属性，可选1/2/4/8，用于 dual/quad/octal 等[[嵌入式基础/接口技术/SPI/SPI总线标准#^b6tpvl|变种SPI]]
	- 数据类型： `uint32_t`

当修改完成后，即可使用如下方法检测从设备是否生效：
- 进入 `/proc/device-tree/spi@${address}` ，检查从设备是否出现。

# 5 软件接口




