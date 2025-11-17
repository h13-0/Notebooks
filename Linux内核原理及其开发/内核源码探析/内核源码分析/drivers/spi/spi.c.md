#操作系统 #Linux系统原理 

# 目录

```toc
```



版本：`${linux内核版本号}` % 格式要求见注1
原代码范围：`xxx-xxx`    % 方便章节排序
分析状态：✅/⌛ % ✅表示已处理完毕、⌛表示未处理完毕

函数签名： `${函数完整签名}`
- 功能简述： ^${anchor}
	- 
- 参数：
	- `${参数1签名}` ：${功能含义}
	- `${参数2签名}` ：${功能含义}
	- ...
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






