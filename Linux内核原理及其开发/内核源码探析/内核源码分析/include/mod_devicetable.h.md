


# spi_device_id

版本：`6.10.0-rc1` <!--格式要求见注1-->
原代码范围：`515-518`    <!--方便章节排序-->
分析状态：✅/⌛ <!--✅表示已处理完毕、⌛表示未处理完毕-->

数据结构定义：

```C
struct spi_device_id {
	char name[SPI_NAME_SIZE];
	kernel_ulong_t driver_data;	/* Data private to the driver */
};
```

其成员：
- `char name[SPI_NAME_SIZE]` ：
	- 功能含义：设备的匹配名，与[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/spi/spi.h#^ga6pq3|spi_device.modalias]]对应
- `kernel_ulong_t driver_data` ：

