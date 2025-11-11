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

# 3 设备树配置

## 3.1 主机设备树配置

## 3.2 从设备设备树配置

在上一章节中已经完成了主机spi设备树节点的配置，其基本结构为

```dts
/ {   // 根节点
	spix {
	}
}

&spix {
	status = "okay";
	
	// 子设备节点
	spi_device: 
}


```






# 4 软件接口
