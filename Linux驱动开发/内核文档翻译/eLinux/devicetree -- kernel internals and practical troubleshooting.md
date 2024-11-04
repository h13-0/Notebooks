---
number headings: auto, first-level 2, max 6, 1.1
---
#Linux驱动开发 #操作系统 

原标题：`devicetree: kernel internals and practical troubleshooting` 。
原文档地址：[devicetree: Kernel Internals and Practical Troubleshooting](https://elinux.org/images/0/0c/Rowand--devicetree_kernel_internals.pdf)。

## 1 目录

```toc
```

## 2 序言

目前已经有了很多关于设备树是什么样子以及如何创建设备树的示例，而本文将探讨Linux内核如何使用设备树。本文的主题包括内核设备树框架、设备创建、资源分配、驱动程序绑定和连接对象等内容。故障排除将考虑初始化、分配和绑定排序、内核配置和驱动程序问题。

注意：本文所讲述内容指定的内核版本为 `3.15rc-1` 到 `3.16-rc7` 。涉及到CPU架构的代码将查看 `arch/arm/` 。

## 3 章节1 - 设备树

### 3.1 什么是设备树

> 设备树是具有描述系统中设备的节点的树数据结构。每个节点都有描述所表示设备特征的属性/值对。每个节点只有一个父节点，只有根节点没有父节点。 —— ePAPR v1.1

<span style="background:#fff88f"><font color="#c00000">设备树描述了无法通过探测定位的硬件</font></span>，<font color="#c00000">即描述了不可被主动发现的设备</font>。

### 3.2 设备树生命周期及其概念

设备树的生命周期如下图所示：
    ![[Pasted image 20241102223502.png]] ^qfilmj

其生命周期为：
1. dts源文件被dtc编译为dtb。
2. dtb被存储到启动镜像中(通常与内核镜像一起存储，在启动时被一起加载)。
3. bootloader从启动镜像中加载dtb，在经过可选的修改后被存入内存。
4. 在加载内核时，DTB在内存中的地址会被传递给kernel(通常以启动参数方式传递)。
5. 内核使用FDT初始化硬件，并生成扩展设备树，该拓展设备树在启动后可以被更改。
在上图中的若干对象及其表述可见各字章节。

#### 3.2.1 dts - device tree source file

dts，device tree source file，设备树源文件，具体可见[[Device Tree Reference学习笔记#2 设备树的使用]]，示例如下：
```
/ {   /* incomplete .dts example */              // <--- root node
    model = "Qualcomm APQ8074 Dragonboard";      // <--- property
    compatible = "qcom,apq8074-dragonboard";     // <--- property
    interrupt-parent = <&intc>;                  // <--- property, phandle
    soc: soc {                                   // <--- node
    ranges;                                      // <--- property
    compatible = "simple-bus";                   // <--- property
    intc: interrupt-controller@f9000000 {        // <--- node, phandle
        compatible = "qcom,msm-qgic2";           // <--- property
        interrupt-controller;                    // <--- property
        reg = <0xf9000000 0x1000>,               // <--- property
              <0xf9002000 0x1000>;
    console: serial@f991e000 {                   // <--- node
        compatible = "qcom,msm-uartdm-v1.4", "qcom,msm-uartdm";
        reg = <0xf991e000 0x1000>;               // <--- property
        interrupts = <0 108 0x0>;                // <--- property
    };
    // ...
}
```

#### 3.2.2 Binary Blob format

Binary Blob format，二进制块格式。是一个扁平结构，可以通过顺序扫描和偏移进行访问。其基本数据结构如下图所示：

![[Pasted image 20241102214441.png]]

#### 3.2.3 Flattened Device Tree(FDT)

FDT是平铺的结构，可以使用 `fdt_*` 族函数进行顺序扫描或偏移量进行访问。

#### 3.2.4 Expanded DT

Expanded DT有如下特性：
- <u>是一个树状的数据结构</u>(其中包含 `parent` 、 `child` 、 `sibling` 、`next` 、 `allnext` 等节点)。具体如下：
	- ![[chrome_8fAskRWQz2.png]]
	- 可以使用 `of_find_node_by_path()` 等方式进行树数据结构方式的访问。
	- `allnext` 链表<span style="background:#fff88f"><font color="#c00000">在被修改过之前</font></span><font color="#c00000">使用深度优先顺序</font>，<font color="#c00000">但是修改后无法保证该特性</font>，因此在开发时应视为随机顺序。
- 可以进行访问<span style="background:#fff88f"><font color="#c00000">和修改</font></span>(使用 `of_*` 族函数)。
- 通过链表访问其所有节点。
- 在启动阶段被创建。
- <span style="background:#fff88f"><font color="#c00000">节点和属性可以在引导后添加或删除</font></span>。
其参考结构定义如下：

```C
struct device_node {
   const char *name;
   const char *type;
   phandle phandle;
   const char *full_name;
   struct  property *properties;
   struct  property *deadprops;
   struct  device_node *parent;
   struct  device_node *child;
   struct  device_node *sibling;
   struct  device_node *next;
   struct  device_node *allnext;
   struct  kobject kobj;
   unsigned long _flags;
   void    *data;
#if defined(CONFIG_SPARC)
   ...
#endif
};
```

### 3.3 设备树节点的内部使用

暂时不做内核开发，仅列出可用API：

```C
of_find_node_by_name (*from, ...)  
of_find_node_by_type (*from, ...)  

// handle is unique, so *from not needed.
of_find_node_by_phandle (handle)  

// traverse allnext and properties.
of_find_node_with_property (*from, ...)
```

## 4 章节2 - 根据启动选项匹配和调整设备树

### 4.1 machine_desc结构体

machine_desc结构体用于为一个特定的设备树描述启动选项，该结构体可以用于多个不同的设备树。

machine_desc结构体定义如下(Linux 6.10.0-rc)：

```C
struct machine_desc {
    unsigned int		nr;             /* architecture number    */
    const char		    *name;          /* architecture name	  */
    unsigned long		atag_offset;    /* tagged list (relative) */
    const char *const 	*dt_compat;	    /* array of device tree
                                         * 'compatible' strings   */

    unsigned int        nr_irqs;        /* number of IRQs         */

#ifdef CONFIG_ZONE_DMA
    phys_addr_t         dma_zone_size;  /* size of DMA-able area  */
#endif

    unsigned int		video_start;	/* start of video RAM	 */
    unsigned int		video_end;	    /* end of video RAM	     */

	unsigned char       reserve_lp0 :1; /* never has lp0         */
    unsigned char       reserve_lp1 :1; /* never has lp1         */
    unsigned char       reserve_lp2 :1; /* never has lp2         */
    enum reboot_mode    reboot_mode;    /* default restart mode  */
    unsigned        l2c_aux_val;        /* L2 cache aux value    */
    unsigned        l2c_aux_mask;       /* L2 cache aux mask     */
    void            (*l2c_write_sec)(unsigned long, unsigned);
    const struct smp_operations    *smp; /* SMP operations       */
    bool            (*smp_init)(void);
    void            (*fixup)(struct tag *, char **);
    void            (*dt_fixup)(void);
    long long       (*pv_fixup)(void);
    void            (*reserve)(void);    /* reserve mem blocks   */
    void            (*map_io)(void);     /* IO mapping function  */
    void            (*init_early)(void);
    void            (*init_irq)(void);
    void            (*init_time)(void);
    void            (*init_machine)(void);
    void            (*init_late)(void);
    void            (*restart)(enum reboot_mode, const char *);
};
```

其中：
- `.nr` ：机器编号，通常对应于具体的硬件平台。
- `.name` ：平台名称，用于内核启动时输出日志。
- L2 Cache
	- `l2c_aux_val`
	- `l2c_aux_mask`
- boot hooks：
	- `smp_init`
	- `fixup`
	- `dt_fixup`
	- `pv_fixup`
	- `reserve`
	- `map_io`
	- `init_early` ：非常早的回调函数，会在 `setup_arch()` 中调用
	- `init_irq`
	- `init_time`
	- `init_machine`
	- `init_late`

- runtime hooks：
	- `l2c_write_sec`
	- `restart`

该结构体在代码中<font color="#c00000">使用静态创建</font>，<font color="#c00000">在支持多平台的Linux系统镜像上有多个该结构体</font>。
选择是否支持多平台会在编译Linux内核时交互时配置参数即可：
1. 使用 `make ARCH=arm menuconfig` 进入Arm-Linux的menuconfig配置
2. 随后弹出：
```shell
Require kernel to be portable to multiple machines (ARCH_MULTIPLATFORM) [Y/n/?] (NEW)
```
3. 按需配置即可，该配置项会影响宏 `CONFIG_ARCH_MULTIPLATFORM` 的结果，并影响编译。

关于该项，[kernelconfig.io](https://www.kernelconfig.io/config_arch_multiplatform)的解释如下：
> In general, all Arm machines can be supported in a single kernel image, covering either Armv4/v5 or Armv6/v7.  
> 
> However, some configuration options require hardcoding machine specific physical addresses or enable errata workarounds that  may break other machines.  
> 
> Selecting N here allows using those options, including DEBUG_UNCOMPRESS, XIP_KERNEL and ZBOOT_ROM. If unsure, say Y.

该结构体可以按照如下的方式定义：

```C
static const char * const qcom_dt_match[] __initconst = {
   "qcom,apq8074-dragonboard",
   "qcom,apq8084",
   "qcom,msm8660-surf",
   NULL
};

DT_MACHINE_START(QCOM_DT, "Qualcomm (Flattened Device Tree)")
   .dt_compat = qcom_dt_match,
MACHINE_END
```

上述的使用了两个宏，其定义如下：

```C
/*
 * Set of macros to define architecture features.  This is built into
 * a table by the linker.
 */
#define MACHINE_START(_type,_name)			            \
static const struct machine_desc __mach_desc_##_type    \
 __used                                                 \
 __section(".arch.info.init") = {                       \
    .nr        = MACH_TYPE_##_type,                     \
    .name        = _name,

#define MACHINE_END                                     \
};
```

该宏会：
1. 生成名为 `__mach_desc_${type}_type` 的结构体。
2. 将 `machine_desc` 结构体存放到 `vmlinux.lds` 中的 `.arch.info.init` 段。
3. 使用 `__used` 告诉编译器这段代码有用，组织对该变量的优化和警告。

### 4.2 简化的Linux内核启动过程

简化的内核启动过程的伪代码如下：

```
start_kernel()
    pr_notice("%s", linux_banner)
    setup_arch()
        mdesc = setup_machine_fdt(__atags_pointer)
        
            // 迭代机器匹配表，找到FDT中与机器兼容的字符串的最佳匹配
            mdesc = of_flat_dt_match_machine()
            
            /* sometimes firmware provides buggy data */
            // 某些版本的uboot在内存节点中可能会传递垃圾条目
                mdesc->dt_fixup()
        
        early_paging_init()
                mdesc->init_meminfo()
        
        arm_memblock_init()
                mdesc->reserve()
        
        paging_init()
            devicemaps_init()
                    mdesc->map_io()
        
        ...
            arm_pm_restart = mdesc->restart
        unflatten_device_tree()   <===============
            if (mdesc->smp_init())
        ...
            handle_arch_irq = mdesc->handle_irq
        ...
            mdesc->init_early()
    pr_notice("Kernel command line: %s\n", ...)
    init_IRQ()
            machine_desc->init_irq()
        outer_cache.write_sec = machine_desc->l2c_write_sec
    time_init()
        machine_desc->init_time()
    rest_init()
        kernel_thread(kernel_init, ...)
            kernel_init()
                        do_initcalls()
                            customize_machine()
                                machine_desc->init_machine()
                        // device probing, driver binding
                        init_machine_late()
                                machine_desc->init_late()
```

在上述代码中：
- 单缩进表示控制 `if` 、 `while` 等控制语句
- 双缩进表示函数的内部调用

### 4.3 选择设备树最匹配的machine_desc

匹配原则：
- 匹配时设备树的和结构体中的compatible字符串必须完全相同
- 设备树提供多个compatible选项时，<font color="#c00000">优先匹配最左的选项</font>

例如：
- 假设现在的设备树有如下的compatible属性：
```dts
/ {
	model = "TI Zoom3";
	compatible = "ti,omap3-zoom3", "ti,omap36xx", "ti,omap3";
};
```
- 并且Linux内核中有如下的 `machine_desc` 结构体：
```C
DT_MACHINE_START(OMAP3_DT, "Generic OMAP3 (Flattened Device Tree)")
    .init_early     = omap3430_init_early,
    .dt_compat      = omap3_boards_compat,
MACHINE_END

DT_MACHINE_START(OMAP36XX_DT, "Generic OMAP36xx (Flattened Device Tree)")
    .init_early     = omap3630_init_early,
    .dt_compat      = omap36xx_boards_compat,
MACHINE_END

static const char *omap3_boards_compat[] __initconst = {
    "ti,omap3430",
    "ti,omap3",
    NULL,
};

static const char *omap36xx_boards_compat[] __initconst = {
        "ti,omap36xx",
        NULL,
};
```
- 则：
	- 找不到 `"ti,omap3-zoom3"` 对应的结构体
	- 找到 `"ti,omap36xx"` 和 `"ti,omap3"` ：
		- 优先匹配左侧

### 4.4 L2 cache检查

在 `machine_desc` 结构体中，L2 Cache有如下两个配置项。

```C
    unsigned        l2c_aux_val;        /* L2 cache aux value    */
    unsigned        l2c_aux_val;       /* L2 cache aux mask     */
```

其中， `l2c_aux_mask` 用于配置是否需要开启L2兼容性检查：
- `(l2c_aux_mask || l2c_aux_val) != 0` 时，


TODO

### 4.5 总结与注意

1. 内核会选择与设备树最匹配的 `machine_desc` 结构体。
2. `machine_desc` 结构体中的值会改变启动过程。
3. 尽可能不用machine_desc hooks。

## 5 章节3 - 更多的内核启动细节

### 5.1 创建设备

#### 5.1.1 初始化回调




### 5.2 匹配设备和驱动程序



