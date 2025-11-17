#操作系统 #Linux系统原理 

# 目录

```toc
```

# spi_match_device

版本：`6.10.0-rc1` 
原代码范围：`374-395` 
分析状态：✅/⌛ 

函数签名： `static int spi_match_device(struct device *dev, struct device_driver *drv)`
- 功能简述： ^6sulsd 
	- 判定一个SPI设备与SPI驱动是否匹配，按优先级依次考虑：
		1. 用户覆盖
		2. 设备树OF匹配
		3. ACPI匹配
		4. 驱动id_table表匹配
		5. 名称匹配
- 参数：
	- `struct device *dev` ：${功能含义}
	- `struct device_driver *drv` ：${功能含义}
- 调用栈分析：
	1. ${函数内部步骤1}
	2. ${函数内部步骤2}
	3. ...
	4. 调用\${其他linux内核函数}，功能简述：\${引用对应函数调用的obsidian_anchor}
	5. ...

```C
static int spi_match_device(struct device *dev, struct device_driver *drv)
{
	const struct spi_device	*spi = to_spi_device(dev);
	const struct spi_driver	*sdrv = to_spi_driver(drv);

	/* Check override first, and if set, only use the named driver */
	if (spi->driver_override)
		return strcmp(spi->driver_override, drv->name) == 0;

	/* Attempt an OF style match */
	if (of_driver_match_device(dev, drv))
		return 1;

	/* Then try ACPI */
	if (acpi_driver_match_device(dev, drv))
		return 1;

	if (sdrv->id_table)
		return !!spi_match_id(sdrv->id_table, spi->modalias);

	return strcmp(spi->modalias, drv->name) == 0;
}
```






