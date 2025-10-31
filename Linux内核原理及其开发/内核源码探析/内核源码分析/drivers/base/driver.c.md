#操作系统 #Linux系统原理 

# 目录

```toc
```

# driver_add_groups ^x7y7mj

版本：`6.10.0-rc1`
原代码范围：`202-206`
分析状态：✅

函数签名： `int driver_add_groups(struct device_driver *drv, const struct attribute_group **groups)` 
- 功能简述： ^rjmp0g
	- 将一组 `sysfs` 属性组(`attribute_group`)批量挂载到给定驱动 `drv` 的 `kobject` (`drv->p->kobj`)下，并创建对应目录/属性文件
	- 成功返回 0，失败返回负的错误码(如 `-ENOMEM`、`-EEXIST` 等)
- 参数：
	- `struct device_driver *drv` ：目标设备驱动实例
		- 要求其私有数据 `drv->p` 已初始化，且内部 `kobject` 已建立(通常在 `driver_register()/bus_add_driver()` 之后)
	- `const struct attribute_group **groups` ：以 `NULL` 结尾的属性组指针数组
		- 每个组可包含可选的目录名(`group->name`)与若干 `struct attribute*` (`group->attrs`)，用于在 sysfs 中生成目录与属性文件。
- 调用栈分析：
	1. 取得目标 `kobject`：`&drv->p->kobj`
	2. 调用 `sysfs_create_groups(&drv->p->kobj, groups)`，其功能简述：![[Linux内核原理及其开发/内核源码探析/内核源码分析/fs/sysfs/group.c#^8dcmqy]]
	3. 若任一组/属性创建失败，`sysfs_create_groups()` 返回负错并回滚已创建的组/文件，避免留下部分残留
	4. 将底层返回值原样向上传递；上层(如 `driver_register()` 路径中)通常在失败时调用 `bus_remove_driver()` 等清理

# driver_register ^fccqjf

版本：`6.10.0-rc1`
原代码范围：`214-258`
分析状态：⌛

函数签名：`int driver_register(struct device_driver *drv)` 
- 功能简述 ^9535px
	- 将一个内核通用设备驱动注册到其所属总线，建立对应的sysfs节点并触发用户空间事件，同时尝试与现有设备进行自动匹配与绑定
	- 失败时负责回滚已创建的内核对象与链表节点
- 参数：
	- `struct device_driver *drv` ：待注册的驱动描述结构
		- 要求已填写 `name` 与 `bus` 等关键字段，常用成员包括 `owner`、`probe`、`remove`、`shutdown`、`of_match_table`、`acpi_match_table`、`groups` 等
- 调用栈分析：
	1. 基本合法性假设检查与内部私有数据准备，<font color="#7f7f7f">包含检查总线是否成功注册、参数检查等</font>
	2. <font color="#c00000">调用</font>[[Linux内核原理及其开发/内核源码探析/内核源码分析/drivers/base/bus.c#^18vykf|bus_add_driver]]<font color="#c00000">添加总线驱动</font>，功能简述：![[Linux内核原理及其开发/内核源码探析/内核源码分析/drivers/base/bus.c#^4owd6m]]
	3. 调用[[Linux内核原理及其开发/内核源码探析/内核源码分析/drivers/base/driver.c#driver_add_groups x7y7mj|driver_add_groups]]为驱动添加属性组，功能简述：![[Linux内核原理及其开发/内核源码探析/内核源码分析/drivers/base/driver.c#^rjmp0g]]
	4. 调用 `kobject_uevent` 向用户空间发送热拔插事件
	5. 调用 `deferred_probe_extend_timeout` 使用内核延迟探测机制，适当延长延迟探测的超时时间
	6. 返回 `ret`

