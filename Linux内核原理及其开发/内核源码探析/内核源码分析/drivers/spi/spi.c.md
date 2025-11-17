#操作系统 #Linux系统原理 

# 目录

```toc
```

# spi_match_device ^6sulsd

版本：`6.10.0-rc1` 
原代码范围：`374-395` 
分析状态：✅/⌛ 

函数签名： `static int spi_match_device(struct device *dev, struct device_driver *drv)`
- 功能简述： ^4jla92
	- 判定一个SPI设备与SPI驱动是否匹配，按如下优先级进行判定：
		1. 用户覆盖
		2. 设备树OF匹配
		3. ACPI匹配
		4. 驱动id_table表匹配
		5. 名称匹配
	- 返回1表示匹配成功、返回0表示匹配失败
- 参数：
	- `struct device *dev` ：待匹配的设备对象
	- `struct device_driver *drv` ：待匹配的驱动对象
- 调用栈分析：
	1. 先将输入的设备及驱动转换为spi子系统的设备及驱动
	2. <font color="#c00000">检查用户覆盖</font>，判定依据为比较设备的 `driver_override` 和驱动的 `name`
	3. 尝试比较设备树的OF匹配
	4. 尝试ACPI匹配
	5. 尝试驱动id表匹配
	6. 进行名称匹配

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






