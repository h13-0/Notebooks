---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 #Linux驱动开发 #操作系统 
## 1 Readme

学习本内容需要至少完成[[Linux驱动开发笔记#^drcdil|Linux驱动开发笔记.Linux设备模型]]的学习。

## 2 目录

```toc
```

## 3 Linux设备模型

### 3.1 总线

在Linux中，与总线机制相关的代码位于：
- `drivers/base/bus.c`

中。





#### 3.1.1 驱动匹配机制

##### 3.1.1.1 Linux设备的流程及生命周期









`probe` 之所以被命名为 `probe` 而非 `init` ，是因为其承担了远比初始化更复杂的任务。


#### 3.1.2 compatible机制 ^1wbp4g

##### 3.1.2.1 compatible的基本匹配机制

在设备树中，可以通过向节点添加 `compatible` 属性来给出设备支持的驱动列表，例如：

```dts
uart0: serial@10000000 {
    compatible = "vendor,uart-2000", "generic-uart";
    reg = <0x10000000 0x1000>;
};
```

而驱动中需要定义 `device_driver.of_match_table[i].compatible` 字段，例如：

```C
static const struct of_device_id uart_driver_ids[] = {
    { .compatible = "vendor,uart-2000" },  // 高优先级匹配
    { .compatible = "generic-uart" },      // 低优先级匹配
    { /* Sentinel */ }
};
```

则<span style="background:#fff88f"><font color="#c00000">当且仅当两个字符串完全一致时</font></span>，驱动得以成功匹配。

例如：
- 设备：`"deviceA"` ，驱动：`"deviceA"` -> 成功匹配
- 设备：`"deviceA"` ，驱动：`"manufactuerA,deviceA"` -> <font color="#c00000">无法匹配</font>
- 设备：`"manufactuerA,deviceA"` ，驱动：`"manufactuerA,deviceA"` -> 成功匹配
- 设备：`"manufactuerA, deviceA"` ，驱动：`"manufactuerA,deviceA"` -> <span style="background:#fff88f"><font color="#c00000">无法匹配</font></span>

而compatible属性的基本规定可见[[Device Tree Reference学习笔记#^740spc|compatible属性]]：![[Device Tree Reference学习笔记#2 2 2 compatible属性 740spc]]
##### 3.1.2.2 匹配的优先级原则




## 4 总线



## 5 设备

### 5.1 平台设备 ^wahyvw

#### 5.1.1 平台设备的数据结构

```C
struct platform_device {
	const char	*name;
	int		id;
	bool		id_auto;
	struct device	dev;
	u64		platform_dma_mask;
	struct device_dma_parameters dma_parms;
	u32		num_resources;
	struct resource	*resource;

	const struct platform_device_id	*id_entry;
	/*
	 * Driver name to force a match.  Do not set directly, because core
	 * frees it.  Use driver_set_override() to set or clear it.
	 */
	const char *driver_override;

	/* MFD cell pointer */
	struct mfd_cell *mfd_cell;

	/* arch specific additions */
	struct pdev_archdata	archdata;
};
```


#### 5.1.2 平台设备的注册

```C
/**
 * platform_device_register - add a platform-level device
 * @pdev: platform device we're adding
 *
 * NOTE: _Never_ directly free @pdev after calling this function, even if it
 * returned an error! Always use platform_device_put() to give up the
 * reference initialised in this function instead.
 */
int platform_device_register(struct platform_device *pdev);
```

#### 5.1.3 平台设备的驱动匹配机制 ^76yg8m

驱动匹配时机：
- 当有新设备或新驱动被注册时，平台总线遍历已注册的设备，寻找匹配项。

驱动匹配条件：
1. 名称匹配方式：
	- 该方式要求设备对象会在 `platform_device.name` 和驱动对象在 `platform_driver.driver.name` 中声明一致的字符串。
2. 

