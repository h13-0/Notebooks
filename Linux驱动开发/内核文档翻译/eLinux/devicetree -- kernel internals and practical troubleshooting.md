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

### 3.2 设备树生命周期

设备树的声明周期如下图所示：
	![[Pasted image 20241102223502.png]]
其生命周期为：
1. dts源文件被dtc编译为dtb
2. dtb被存储到启动镜像中(通常与内核镜像一起存储，在启动时被一起加载)
3. bootloader从启动镜像中加载dtb，在经过可选的修改后被存入内存
4. 在加载内核时，DTB在内存中的地址会被传递给kernel(通常以启动参数方式传递)
5. 内核使用FDT初始化硬件，并生成扩展设备树
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



