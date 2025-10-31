#操作系统 #Linux系统原理 

# 目录

```toc
```

# bus_add_driver ^18vykf

版本：`6.10.0-rc1` 
原代码范围：`638-718`
分析状态：⌛

函数签名：`int bus_add_driver(struct device_driver *drv)` 
- 功能简述： ^4owd6m
	- 将通用设备驱动挂接到对应总线的内部数据结构上，建立驱动的kobject与sysfs目录，按需对已存在设备执行自动探测与绑定
	- 在sysfs下补充模块链接、uevent属性、总线级属性组与bind/unbind控制项
	- 任一步失败时执行有序回滚，释放引用与对象，保持总线与驱动子系统一致性
- 参数：
	- `struct device_driver *drv` ：待加入总线的驱动对象
		- 要求其 `bus` 字段有效，`name` 非空，可选控制项包括 `owner`、`groups`、`suppress_bind_attrs` 等
- 调用栈分析：
	1. 获取并校验总线私有体  
	   - 调用 `bus_to_subsys(drv->bus)` 获取 `struct subsys_private *sp`  
	   - 失败返回 `-EINVAL`  
	   - 该获取会提升 `sp` 引用计数，后续用 `subsys_put` 匹配释放
	2. 分配并初始化驱动私有体  
	   - 调用 `kzalloc(sizeof(*priv), GFP_KERNEL)` 分配 `struct driver_private *priv`  
	   - 初始化 `priv->klist_devices`，建立 `priv->driver = drv` 与 `drv->p = priv` 关联  
	   - 设置 `priv->kobj.kset = sp->drivers_kset`
	3. 初始化并注册kobject  
	   - 调用 `kobject_init_and_add(&priv->kobj, &driver_ktype, NULL, "%s", drv->name)`  
	   - 在 `/sys/bus/<bus>/drivers/<name>` 创建驱动目录，类型由 `driver_ktype` 定义  
	   - 失败跳转回收路径
	4. 将驱动挂入总线驱动链表  
	   - 调用 `klist_add_tail(&priv->knode_bus, &sp->klist_drivers)` 完成挂接
	5. 自动探测已存在设备（若开启）  
	   - 若 `sp->drivers_autoprobe` 为真，调用 `driver_attach(drv)`  
	   - 遍历总线设备尝试匹配并触发 `probe`  
	   - 失败则从链表移除并回滚
	6. 建立模块与驱动的sysfs链接  
	   - 调用 `module_add_driver(drv->owner, drv)`  
	   - 在 `/sys/module/<owner>/drivers/` 下创建与该驱动的链接  
	   - 失败则调用 `driver_detach(drv)` 撤销已完成的设备绑定并回滚
	7. 创建uevent属性文件  
	   - 调用 `driver_create_file(drv, &driver_attr_uevent)` 在驱动目录下创建 `uevent` 属性  
	   - 失败仅告警，不致命
	8. 添加总线级属性组  
	   - 调用 `driver_add_groups(drv, sp->bus->drv_groups)` 为驱动附加总线定义的属性组  
	   - 失败仅告警（此处代码注释表明难以优雅回滚，选择放弃回退）
	9. 添加bind/unbind控制项（可抑制）  
	   - 若未设置 `drv->suppress_bind_attrs`，调用 `add_bind_files(drv)` 创建 `bind` 与 `unbind` 文件  
	   - 失败仅告警
	10. 成功返回0
	11. 失败回滚路径  
	    - `out_detach`：调用 `driver_detach(drv)` 解除已建立的设备绑定  
	    - `out_del_list`：`klist_del(&priv->knode_bus)` 将驱动从总线链表移除  
	    - `out_unregister`：`kobject_put(&priv->kobj)` 释放kobject，`drv->p = NULL`  
	    - `out_put_bus`：`subsys_put(sp)` 降低总线私有体引用计数并返回错误码


