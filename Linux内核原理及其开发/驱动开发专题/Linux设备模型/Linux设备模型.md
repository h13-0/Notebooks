---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 #Linux驱动开发 #操作系统 

# 1 Readme

学习本内容需要至少完成[[Linux内核原理及其开发/Linux驱动开发笔记#17 Linux设备模型 drcdil|Linux驱动开发笔记.Linux设备模型]]的学习。

# 2 目录

```toc
```

# 3 Linux设备模型

## 3.1 总线

在Linux中，与总线机制相关的代码位于：
- `drivers/base/bus.c`

中。





### 3.1.1 驱动匹配机制

#### 3.1.1.1 驱动匹配规则与优先级 ^9zo17a

驱动程序总的匹配规则由总线驱动程序的 `match` 函数决定，其匹配会发生在新的设备被注册或新的驱动程序被注册时，通常来说其匹配步骤为：
1. 遍历总线上的所有候选驱动或设备，并调用该总线的 `match` 回调函数
2. 如果 `match` 函数返回非0则表示该驱动可以匹配该设备。<font color="#c00000">如果有多个驱动都可以匹配该设备</font>，<span style="background:#fff88f"><font color="#c00000">则会按照驱动的遍历顺序调用其</font></span> `probe` <span style="background:#fff88f"><font color="#c00000">函数</font></span>，<span style="background:#fff88f"><font color="#c00000">其遍历顺序通常为驱动的注册顺序</font></span>，第一个成功 `probe` 的驱动会抢到该设备的驱动权。

#### 3.1.1.2 Linux设备的流程及生命周期









`probe` 之所以被命名为 `probe` 而非 `init` ，是因为其承担了远比初始化更复杂的任务。


### 3.1.2 compatible机制 ^1wbp4g

#### 3.1.2.1 compatible的基本匹配机制

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
    { /* Sentinel */ }                     // 必须以空节点结尾
};
```

则<span style="background:#fff88f"><font color="#c00000">当且仅当两个字符串完全一致时</font></span>，驱动得以成功匹配。

例如：
- 设备：`"deviceA"` ，驱动：`"deviceA"` -> 成功匹配
- 设备：`"deviceA"` ，驱动：`"manufactuerA,deviceA"` -> <font color="#c00000">无法匹配</font>
- 设备：`"manufactuerA,deviceA"` ，驱动：`"manufactuerA,deviceA"` -> 成功匹配
- 设备：`"manufactuerA, deviceA"` ，驱动：`"manufactuerA,deviceA"` -> <span style="background:#fff88f"><font color="#c00000">无法匹配</font></span>

而compatible属性的基本规定可见[[../../内核文档翻译/eLinux/Development Portals/Device Tree/Device Tree Reference#^740spc|compatible属性]]：![[../../内核文档翻译/eLinux/Development Portals/Device Tree/Device Tree Reference#2 2 2 compatible属性 740spc]]
#### 3.1.2.2 匹配的优先级原则







## 3.2 设备


## 3.3 电源管理


### 3.3.1 电源管理优先级 ^ce9oct

对于一般的高级驱动模型，其往往提供了如下的电源管理接口：
- 高级驱动模型： `struct xxx_driver`
	- 直接定义的老式电源管理接口，如 `struct xxx_driver.suspend` 等
	- 内嵌基础驱动模型的老式接口，如 `struct xxx_driver.driver.suspend` 等
	- 内嵌基础驱动模型的现代管理接口：`struct xxx_driver.driver.pm` 
其调用优先级如下：
1. 如果有现代接口，则调用现代接口