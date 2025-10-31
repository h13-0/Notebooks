
# 目录

```toc
```

# \_\_platform_device_register ^nahva9

版本：`6.10.0-rc1` 
分析状态：✅

函数签名：`int __platform_driver_register(struct platform_driver *drv, struct module *owner)` 
- 参数：
	- `struct platform_driver *drv` ：要注册的平台驱动
	- `struct module *owner` ：提供平台驱动的模块
- 调用栈分析：
	1. 设置 `drv->driver` 的 `owner` 和总线类型
	2. <font color="#c00000">调用并返回</font> [[Linux内核原理及其开发/内核源码探析/内核源码分析/drivers/base/driver.c#^fccqjf|driver_register]] ：![[Linux内核原理及其开发/内核源码探析/内核源码分析/drivers/base/driver.c#driver_register fccqjf]]



