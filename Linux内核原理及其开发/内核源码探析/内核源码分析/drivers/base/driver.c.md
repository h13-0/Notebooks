
# 目录

```toc
```

# driver_register ^fccqjf

版本：`6.10.0-rc1`

函数签名：`int driver_register(struct device_driver *drv)`
- 参数：
	- `struct device_driver *drv` ：要注册的驱动
- 调用栈分析：
	1. 执行前检查，<font color="#7f7f7f">包含检查总线是否成功注册、参数检查等</font>
	2. <font color="#c00000">调用</font> `bus_add_driver` <font color="#c00000">添加总线驱动</font>，其作用包含：
		1. 在sysfs中注册节点
		2. 将

