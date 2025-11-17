#操作系统 #Linux系统原理 

# 目录

```toc
```




# device_driver ^2dewi6

版本：`6.10.0-rc0` <!--格式要求见注1-->
原代码范围：`51-122` <!--方便章节排序-->
分析状态：⌛ <!--✅表示已处理完毕、⌛表示未处理完毕-->

数据结构定义：

```C
/**
 * struct device_driver - The basic device driver structure
 * @name:	Name of the device driver.
 * @bus:	The bus which the device of this driver belongs to.
 * @owner:	The module owner.
 * @mod_name:	Used for built-in modules.
 * @suppress_bind_attrs: Disables bind/unbind via sysfs.
 * @probe_type:	Type of the probe (synchronous or asynchronous) to use.
 * @of_match_table: The open firmware table.
 * @acpi_match_table: The ACPI match table.
 * @probe:	Called to query the existence of a specific device,
 *		whether this driver can work with it, and bind the driver
 *		to a specific device.
 * @sync_state:	Called to sync device state to software state after all the
 *		state tracking consumers linked to this device (present at
 *		the time of late_initcall) have successfully bound to a
 *		driver. If the device has no consumers, this function will
 *		be called at late_initcall_sync level. If the device has
 *		consumers that are never bound to a driver, this function
 *		will never get called until they do.
 * @remove:	Called when the device is removed from the system to
 *		unbind a device from this driver.
 * @shutdown:	Called at shut-down time to quiesce the device.
 * @suspend:	Called to put the device to sleep mode. Usually to a
 *		low power state.
 * @resume:	Called to bring a device from sleep mode.
 * @groups:	Default attributes that get created by the driver core
 *		automatically.
 * @dev_groups:	Additional attributes attached to device instance once
 *		it is bound to the driver.
 * @pm:		Power management operations of the device which matched
 *		this driver.
 * @coredump:	Called when sysfs entry is written to. The device driver
 *		is expected to call the dev_coredump API resulting in a
 *		uevent.
 * @p:		Driver core's private data, no one other than the driver
 *		core can touch this.
 *
 * The device driver-model tracks all of the drivers known to the system.
 * The main reason for this tracking is to enable the driver core to match
 * up drivers with new devices. Once drivers are known objects within the
 * system, however, a number of other things become possible. Device drivers
 * can export information and configuration variables that are independent
 * of any specific device.
 */
struct device_driver {
	const char		*name;
	const struct bus_type	*bus;

	struct module		*owner;
	const char		*mod_name;	/* used for built-in modules */

	bool suppress_bind_attrs;	/* disables bind/unbind via sysfs */
	enum probe_type probe_type;

	const struct of_device_id	*of_match_table;
	const struct acpi_device_id	*acpi_match_table;

	int (*probe) (struct device *dev);
	void (*sync_state)(struct device *dev);
	int (*remove) (struct device *dev);
	void (*shutdown) (struct device *dev);
	int (*suspend) (struct device *dev, pm_message_t state);
	int (*resume) (struct device *dev);
	const struct attribute_group **groups;
	const struct attribute_group **dev_groups;

	const struct dev_pm_ops *pm;
	void (*coredump) (struct device *dev);

	struct driver_private *p;
};
```

其成员：
- `name` ：驱动的名称，会在sysfs( `/sys/bus/.../drivers/` )中进行显示。其与 `device_driver.kobj.name` 必须保持一致(但是无须手动为 `kobj.name` 赋值，注册驱动时内核自动完成)。
- `bus` ：指向驱动所属的总线类型，例如 `&platform_bus_type` 、 `&i2c_bus_type` 。在注册后会挂载到总线的驱动列表中。
- `owner` ：通常指向 `THIS_MODULE` 
- `mod_name` ：
- `suppress_bind_attrs` ：是否允许通过sysfs进行绑定/解绑。但该成员<font color="#c00000">仅限制用户通过sysfs进行热拔插操作</font>。
	- 注：
		1. Linux的设备支持通过 `sysfs` 进行绑定/解绑，例如：
			- `echo ${device_id} > /sys/bus/.../drivers/${driver}/bind`
			- `echo ${device_id} > /sys/bus/.../drivers/${driver}/unbind`
		2. 设备热拔插功能需要满足如下条件：
			1. 硬件支持热拔插
			2. 总线实现了热拔插事件通知
			3. 驱动提供了正确的 `probe` 和 `remove` 方法
		3. 除了sysfs进行热拔插以外，Linux中还有如下的常见热拔插机制：
			1. 直接拔，拔完之后总线通知驱动(例如USB)。
			2. 通过专用接口/方法进行弹出设备，例如：
				- `nvme ns-rescan /dev/nvme0`
				- `usbip unbind -b 1-2.3`
			3. 直接重启需要拔出的设备，例如网卡的 `ip link set dev eth0 down`
- `of_match_table` ：设备树匹配表(数组)，用于声明驱动支持的设备树节点。
	- 注：
		- 数组的最后一个成员的所有key值均为 `0x00` 用于标记结尾。
		- 数组成员的键值如下：
			- `char name[32]` ：设备名称，用于早期内核中通过设备树节点的 `name` 进行匹配的方式。现逐渐被弃用。
				- 例如 `.name = "uart0"` 匹配dts中的节点 `uart0`
			- `char type[32]` ：设备类型，通过设备树节点中的 `device_type` 键值进行匹配。<font color="#c00000">极少使用</font>，通常只用于定义CPU或内存节点。
				- 例如 `.type = "cpu"`
			- `char compatible[128]` ：<span style="background:#fff88f"><font color="#c00000">设备兼容性字符串</font></span>，现在最为常用的方式。支持设备和驱动同时选择多个志愿进行匹配。规则和例子详见[[Linux设备模型#^1wbp4g|compatible机制]]。
			- `const void *data` ：私有数据指针。
- `acpi_match_table` ：ACPI匹配表，用于ACPI固件设备的匹配(与设备树类似)
- `probe` ：当总线匹配到设备时调用，<font color="#c00000">负责初始化设备、分配资源、注册操作接口等</font>
- `remove` ：设备移除或驱动卸载时调用，释放资源、注销设备。
- `shutdown` ：系统关闭回调，是老版本电源管理的接口，新版本在 `device_driver.pm` 中由同名成员。优先调用 `device_driver.pm` 中同名对象。
- `suspend` ：设备休眠回调，是老版本电源管理的接口，同上。
- `resume` ：设备唤醒回调，是老版本电源管理的接口，同上。
- `sync_state` ：在所有设备状态跟踪组件绑定完成后调用，用于同步硬件与软件状态
- `groups` ：驱动在sysfs中暴露的属性组。
- `dev_groups` ：设备的属性组，每个设备独立维护。
- `pm` ：新的电源管理机制的电源管理操作集，其内部记录了众多电源管理函数，例如 `prepare` 、`suspend` 、`resume` 等。
- `coredump` ：用于在设备发生严重故障或需要调试时生成设备相关的核心转储(coredump)信息，在系统崩溃或主动触发调试时，收集设备特定的状态数据，以便后续分析故障原因。
- `p` ：私有数据。

注：
- 建议补充阅读章节：
	- [[Linux内核原理及其开发/Linux驱动开发笔记#17 5 3 2 设备模型层级与回调规定 4gz3xk|设备模型层级与回调规定]]
