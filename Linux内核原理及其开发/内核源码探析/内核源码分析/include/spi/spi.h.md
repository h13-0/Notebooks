#操作系统 #Linux系统原理 

# 目录

```toc
```

# spi_device ^j2uocs

版本：`6.10.0-rc1` 
原代码范围：`130-244` 
分析状态：⌛

对象功能含义：
- 该对象是SPI从设备在内核中的对象实例，用于操作对象和通信

数据结构定义：

```C
/**
 * struct spi_device - Controller side proxy for an SPI slave device
 * @dev: Driver model representation of the device.
 * @controller: SPI controller used with the device.
 * @max_speed_hz: Maximum clock rate to be used with this chip
 *	(on this board); may be changed by the device's driver.
 *	The spi_transfer.speed_hz can override this for each transfer.
 * @chip_select: Array of physical chipselect, spi->chipselect[i] gives
 *	the corresponding physical CS for logical CS i.
 * @mode: The spi mode defines how data is clocked out and in.
 *	This may be changed by the device's driver.
 *	The "active low" default for chipselect mode can be overridden
 *	(by specifying SPI_CS_HIGH) as can the "MSB first" default for
 *	each word in a transfer (by specifying SPI_LSB_FIRST).
 * @bits_per_word: Data transfers involve one or more words; word sizes
 *	like eight or 12 bits are common.  In-memory wordsizes are
 *	powers of two bytes (e.g. 20 bit samples use 32 bits).
 *	This may be changed by the device's driver, or left at the
 *	default (0) indicating protocol words are eight bit bytes.
 *	The spi_transfer.bits_per_word can override this for each transfer.
 * @rt: Make the pump thread real time priority.
 * @irq: Negative, or the number passed to request_irq() to receive
 *	interrupts from this device.
 * @controller_state: Controller's runtime state
 * @controller_data: Board-specific definitions for controller, such as
 *	FIFO initialization parameters; from board_info.controller_data
 * @modalias: Name of the driver to use with this device, or an alias
 *	for that name.  This appears in the sysfs "modalias" attribute
 *	for driver coldplugging, and in uevents used for hotplugging
 * @driver_override: If the name of a driver is written to this attribute, then
 *	the device will bind to the named driver and only the named driver.
 *	Do not set directly, because core frees it; use driver_set_override() to
 *	set or clear it.
 * @cs_gpiod: Array of GPIO descriptors of the corresponding chipselect lines
 *	(optional, NULL when not using a GPIO line)
 * @word_delay: delay to be inserted between consecutive
 *	words of a transfer
 * @cs_setup: delay to be introduced by the controller after CS is asserted
 * @cs_hold: delay to be introduced by the controller before CS is deasserted
 * @cs_inactive: delay to be introduced by the controller after CS is
 *	deasserted. If @cs_change_delay is used from @spi_transfer, then the
 *	two delays will be added up.
 * @pcpu_statistics: statistics for the spi_device
 * @cs_index_mask: Bit mask of the active chipselect(s) in the chipselect array
 *
 * A @spi_device is used to interchange data between an SPI slave
 * (usually a discrete chip) and CPU memory.
 *
 * In @dev, the platform_data is used to hold information about this
 * device that's meaningful to the device's protocol driver, but not
 * to its controller.  One example might be an identifier for a chip
 * variant with slightly different functionality; another might be
 * information about how this particular board wires the chip's pins.
 */
struct spi_device {
	struct device		dev;
	struct spi_controller	*controller;
	u32			max_speed_hz;
	u8			chip_select[SPI_CS_CNT_MAX];
	u8			bits_per_word;
	bool			rt;
#define SPI_NO_TX		BIT(31)		/* No transmit wire */
#define SPI_NO_RX		BIT(30)		/* No receive wire */
	/*
	 * TPM specification defines flow control over SPI. Client device
	 * can insert a wait state on MISO when address is transmitted by
	 * controller on MOSI. Detecting the wait state in software is only
	 * possible for full duplex controllers. For controllers that support
	 * only half-duplex, the wait state detection needs to be implemented
	 * in hardware. TPM devices would set this flag when hardware flow
	 * control is expected from SPI controller.
	 */
#define SPI_TPM_HW_FLOW		BIT(29)		/* TPM HW flow control */
	/*
	 * All bits defined above should be covered by SPI_MODE_KERNEL_MASK.
	 * The SPI_MODE_KERNEL_MASK has the SPI_MODE_USER_MASK counterpart,
	 * which is defined in 'include/uapi/linux/spi/spi.h'.
	 * The bits defined here are from bit 31 downwards, while in
	 * SPI_MODE_USER_MASK are from 0 upwards.
	 * These bits must not overlap. A static assert check should make sure of that.
	 * If adding extra bits, make sure to decrease the bit index below as well.
	 */
#define SPI_MODE_KERNEL_MASK	(~(BIT(29) - 1))
	u32			mode;
	int			irq;
	void			*controller_state;
	void			*controller_data;
	char			modalias[SPI_NAME_SIZE];
	const char		*driver_override;
	struct gpio_desc	*cs_gpiod[SPI_CS_CNT_MAX];	/* Chip select gpio desc */
	struct spi_delay	word_delay; /* Inter-word delay */
	/* CS delays */
	struct spi_delay	cs_setup;
	struct spi_delay	cs_hold;
	struct spi_delay	cs_inactive;

	/* The statistics */
	struct spi_statistics __percpu	*pcpu_statistics;

	/* Bit mask of the chipselect(s) that the driver need to use from
	 * the chipselect array.When the controller is capable to handle
	 * multiple chip selects & memories are connected in parallel
	 * then more than one bit need to be set in cs_index_mask.
	 */
	u32			cs_index_mask : SPI_CS_CNT_MAX;

	/*
	 * Likely need more hooks for more protocol options affecting how
	 * the controller talks to each chip, like:
	 *  - memory packing (12 bit samples into low bits, others zeroed)
	 *  - priority
	 *  - chipselect delays
	 *  - ...
	 */
};
```

其成员：
- `struct device dev` ：
	- 功能含义：标准设备模型成员
- `struct spi_controller *controller` ：
	- 功能含义：指向设备所属的SPI控制器
- `u8 chip_select[SPI_CS_CNT_MAX]` ：
	- 功能含义：配合 `cs_index_mask` 成员实现多CS片选机制
	- 版本演化历史：
		- 在老内核中只有单个片选号，而新内核中的设计支持了多片选号/并联Flash的支持
- `u8 bits_per_word` ：
	- 功能含义：一个 `word` 有多少位
		- 其常见值有：
			- `0` ：默认8位
			- `8、16、32` ：对应位数
- `bool rt` ：
	- 功能含义：
- `char modalias[SPI_NAME_SIZE]` ： ^ga6pq3
	- 功能含义：
- 
- `u32 cs_index_mask : SPI_CS_CNT_MAX;`


# spi_driver

版本：`6.10.0-rc1` <!--格式要求见注1-->
原代码范围：`321-532` <!--方便章节排序-->
分析状态：⌛ <!--✅表示已处理完毕、⌛表示未处理完毕-->

数据结构定义：

```C
/**
 * struct spi_driver - Host side "protocol" driver
 * @id_table: List of SPI devices supported by this driver
 * @probe: Binds this driver to the SPI device.  Drivers can verify
 *	that the device is actually present, and may need to configure
 *	characteristics (such as bits_per_word) which weren't needed for
 *	the initial configuration done during system setup.
 * @remove: Unbinds this driver from the SPI device
 * @shutdown: Standard shutdown callback used during system state
 *	transitions such as powerdown/halt and kexec
 * @driver: SPI device drivers should initialize the name and owner
 *	field of this structure.
 *
 * This represents the kind of device driver that uses SPI messages to
 * interact with the hardware at the other end of a SPI link.  It's called
 * a "protocol" driver because it works through messages rather than talking
 * directly to SPI hardware (which is what the underlying SPI controller
 * driver does to pass those messages).  These protocols are defined in the
 * specification for the device(s) supported by the driver.
 *
 * As a rule, those device protocols represent the lowest level interface
 * supported by a driver, and it will support upper level interfaces too.
 * Examples of such upper levels include frameworks like MTD, networking,
 * MMC, RTC, filesystem character device nodes, and hardware monitoring.
 */
struct spi_driver {
	const struct spi_device_id *id_table;
	int			(*probe)(struct spi_device *spi);
	void			(*remove)(struct spi_device *spi);
	void			(*shutdown)(struct spi_device *spi);
	struct device_driver	driver;
};
```

其成员：
- `const struct spi_device_id *id_table` ：
	- 功能含义：该驱动支持的设备名列表，成员定义可见[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/mod_devicetable.h#^886i4y|spi_device_id]]。
- `int (*probe)(struct spi_device *spi)` ：
	- 功能含义：驱动 `probe` 回调
- `void (*remove)(struct spi_device *spi)` ：
	- 功能含义：驱动解绑回调，<font color="#c00000">需要对称注销</font> `probe` <font color="#c00000">中的资源</font>
- `void (*shutdown)(struct spi_device *spi)` ：
	- 功能含义：关机阶段回调
		- 用于系统关机、重启等场景<font color="#c00000">下让器件回到安全状态</font>，<font color="#c00000">而不是资源回收</font>
- `struct device_driver driver` ：
	- 功能含义：通用驱动程序对象

# spi_write ^mrzeek

版本：`6.10.0-rc1` <!--格式要求见注1-->
原代码范围：`1422-443` <!--方便章节排序-->
分析状态：✅ <!--✅表示已处理完毕、⌛表示未处理完毕-->

函数签名： `int spi_write(struct spi_device *spi, const void *buf, size_t len)`
- 功能简述： ^43qc8t
	- 向spi设备中写入指定长度的数据
- 参数：
	- `struct spi_device *spi` ：目标SPI从设备指针
	- `const void *buf` ：数据所在缓冲区
	- `size_t len` ：要写入的<font color="#c00000">字节数</font>(而非word数)
- 调用栈分析：
	1. 实例化要传输的数据对象(`struct spi_transfer`)
	2. 调用并返回 `spi_sync_transfer`
- 注意事项：
	- <span style="background:#fff88f"><font color="#c00000">该函数可能会休眠</font></span>，因此中断上下文中禁用

# spi_board_info ^877sjn

版本：`6.10.0-rc1` 
原代码范围：`1563-1636` 
分析状态：⌛

数据结构定义：

```C
/**
 * struct spi_board_info - board-specific template for a SPI device
 * @modalias: Initializes spi_device.modalias; identifies the driver.
 * @platform_data: Initializes spi_device.platform_data; the particular
 *	data stored there is driver-specific.
 * @swnode: Software node for the device.
 * @controller_data: Initializes spi_device.controller_data; some
 *	controllers need hints about hardware setup, e.g. for DMA.
 * @irq: Initializes spi_device.irq; depends on how the board is wired.
 * @max_speed_hz: Initializes spi_device.max_speed_hz; based on limits
 *	from the chip datasheet and board-specific signal quality issues.
 * @bus_num: Identifies which spi_controller parents the spi_device; unused
 *	by spi_new_device(), and otherwise depends on board wiring.
 * @chip_select: Initializes spi_device.chip_select; depends on how
 *	the board is wired.
 * @mode: Initializes spi_device.mode; based on the chip datasheet, board
 *	wiring (some devices support both 3WIRE and standard modes), and
 *	possibly presence of an inverter in the chipselect path.
 *
 * When adding new SPI devices to the device tree, these structures serve
 * as a partial device template.  They hold information which can't always
 * be determined by drivers.  Information that probe() can establish (such
 * as the default transfer wordsize) is not included here.
 *
 * These structures are used in two places.  Their primary role is to
 * be stored in tables of board-specific device descriptors, which are
 * declared early in board initialization and then used (much later) to
 * populate a controller's device tree after the that controller's driver
 * initializes.  A secondary (and atypical) role is as a parameter to
 * spi_new_device() call, which happens after those controller drivers
 * are active in some dynamic board configuration models.
 */
struct spi_board_info {
	/*
	 * The device name and module name are coupled, like platform_bus;
	 * "modalias" is normally the driver name.
	 *
	 * platform_data goes to spi_device.dev.platform_data,
	 * controller_data goes to spi_device.controller_data,
	 * IRQ is copied too.
	 */
	char		modalias[SPI_NAME_SIZE];
	const void	*platform_data;
	const struct software_node *swnode;
	void		*controller_data;
	int		irq;

	/* Slower signaling on noisy or low voltage boards */
	u32		max_speed_hz;


	/*
	 * bus_num is board specific and matches the bus_num of some
	 * spi_controller that will probably be registered later.
	 *
	 * chip_select reflects how this chip is wired to that master;
	 * it's less than num_chipselect.
	 */
	u16		bus_num;
	u16		chip_select;

	/*
	 * mode becomes spi_device.mode, and is essential for chips
	 * where the default of SPI_CS_HIGH = 0 is wrong.
	 */
	u32		mode;

	/*
	 * ... may need additional spi_device chip config data here.
	 * avoid stuff protocol drivers can set; but include stuff
	 * needed to behave without being bound to a driver:
	 *  - quirks like clock rate mattering when not selected
	 */
};
```

其成员：
- `char modalias[SPI_NAME_SIZE]` ：
	- 功能含义：
		- 设备的匹配名，用于驱动匹配或模块的自动加载
		- 应与驱动的 `drv->name` 一致
		- 在DT/ACPI模式下由固件节点派生，不需要手动配置
- `const void *platform_data` ：
	- 功能含义：
		- 传统的传递给驱动的私有数据方法(`spi_device.dev.platform_data`)
	- 维护方：在DT/ACPI场景下通常使用设备属性而非本节点
- `const struct software_node *swnode` ：
	- 功能含义
- `void *controller_data`
- `int irq` :
	- 功能含义：从设备的中断号，取决于设备连接
	- 维护方：在DT/ACPI下由固件解析得到
- `u32 max_speed_hz` ：
	- 功能含义：设备允许的最高SCLK频率
	- 维护方：在DT/ACPI下由固件解析得到
- `u16 bus_num` ：
	- 功能含义：设备对应的 `spi_controller` 总线号
- `u16 chip_select` ：
	- 功能含义：设备对应的CS引脚号
	- 维护方：在DT/ACPI下由固件解析得到
- `u32 mode` ： ^znds47
	- 功能含义：设备的SPI配置掩码，通常包含 `SPI_CPHA` 、 `SPI_CPOL` 等标志位
	- 维护方：在DT/ACPI下由固件解析得到


