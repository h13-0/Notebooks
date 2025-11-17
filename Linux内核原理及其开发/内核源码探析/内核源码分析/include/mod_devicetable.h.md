


# spi_device_id ^886i4y

版本：`6.10.0-rc1` <!--格式要求见注1-->
原代码范围：`515-518`    <!--方便章节排序-->
分析状态：✅ <!--✅表示已处理完毕、⌛表示未处理完毕-->

数据结构定义：

```C
struct spi_device_id {
	char name[SPI_NAME_SIZE];
	kernel_ulong_t driver_data;	/* Data private to the driver */
};
```

其成员：
- `char name[SPI_NAME_SIZE]` ：
	- 功能含义：
		- 设备的匹配名，与[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/spi/spi.h#^ga6pq3|spi_device.modalias]]对应
		- 由 `MODULE_DEVICE_TABLE(spi, ...)` 生成形如 `spi:<name>` 的模块别名，便于udev/modprobe自动加载
- `kernel_ulong_t driver_data` ：
	- 功能含义：驱动私有的常量数据
		- 常用来编码芯片变体或特性位，用于驱动程序的 `probe` 中的分支处理
		- 类型为指针宽度的无符号长整型，具体存储内容根据驱动程序而定
		- 在 `probe` 中可使用 `spi_get_device_id(spi)` 处理
