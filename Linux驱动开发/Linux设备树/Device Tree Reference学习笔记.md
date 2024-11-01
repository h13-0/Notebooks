---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 #Linux驱动开发 #操作系统 

# Note

本笔记学习时的参考资料为[Device Tree Reference](https://elinux.org/Device_Tree_Reference?Overlay_Source_Format)，且笔记尽可能保持该资料原有的层次结构。

# 目录

```toc
```

# 学习笔记 

## 1 简介

### 1.1 什么是设备树

Linux中设备树的主要目的是<font color="#c00000">提供一种描述不可发现硬件的方法</font>。此信息以前在源代码中使用硬编码实现。



## 2 设备树的使用

### 2.1 基本数据格式

如下是一个简单的设备树示例：

```dts
/dts-v1/;

/ {
    node1 {
        a-string-property = "A string";
        a-string-list-property = "first string", "second string";
        // hex is implied in byte arrays. no '0x' prefix is required
        a-byte-data-property = [01 23 34 56];
        child-node1 {
            first-child-property;
            second-child-property = <1>;
            a-string-property = "Hello, world";
        };
        child-node2 {
        };
    };
    node2 {
        an-empty-property;
        a-cell-property = <1 2 3 4>; /* each number (cell) is a uint32 */
        child-node1 {
        };
    };
};
```

上述的设备树中：
- `/` 表示根节点，其后的花括号内定义了两个子节点 `node1` 和 `node2` 。
	- `node1` 节点中提供了若干 `key-value` 式的键值对：
		- `a-string-property` ：一个字符串类型的键值对，值为 `A string` 。
		- `a-string-list-property` ：一个由字符串组成的数组。
		- `a-byte-data-property` ：一个由二进制构成的数组，值为 `{ 0x01, 0x23, 0x34, 0x56}` 。
		- 子节点 `child-node1` ，子元素为：
			- 
	- `node2` 节点

而在设备树中支持的数据类型有：

| <center>数据类型</center> | <center>表示方式</center> | <center>Demo</center>                                               | <center>Value</center>      |
| --------------------- | --------------------- | ------------------------------------------------------------------- | --------------------------- |
| 文本字符串                 | 双引号包围                 | `a-string-property = "A string";`                                   | `A string`                  |
| 文本字符串构成的数组            | 逗号分割                  | `a-string-list-property = "first string", "second string";`         | 略                           |
| `uint32_t` 构成的数组      | 使用 `<>` 包围，空格分割       | `second-child-property = <1 0xbeef>;`                               | `{ 1, 48879 }`              |
| 二进制构成的数组              | 使用 `[]` 包围，空格分割       | `a-byte-data-property = [01 23 34 56];`                             | `{ 0x01, 0x23, 0x34, 0x56}` |
| 混合数据                  | 逗号分割                  | `mixed-property = "a string", [0x01 0x23 0x45 0x67], <0x12345678>;` |                             |

### 2.2 基本概念

#### 2.2.1 示例机及设备树编写

假设给定的机器有如下属性：
- 由 "Acme" 制造，命名为 "Coyote's Revenge"。
- 双核 Cortex-A9 CPU
- 映射到内存上的外设有：
	- 两个串口(serial)，基地址分别为：
		- `0x101F1000`
		- `0x101F2000`
	- GPIO控制器，基地址为 `0x101F3000` 
	- SPI总线控制器，基地址为 `0x10170000` ，并且外挂有如下设备：
		- 带有SS引脚的MMC插槽，SS引脚为 `GPIO#1`
	- 外部总线桥，并附带如下设备：
		- SMC SMC91111以太网设备，基地址为 `0x10100000`
		- I2C控制器，基地址为 `0x10160000` ，并外挂如下设备：
			- DS1338 RTC时钟，I2C地址为 `0x58`
		- 64MB NOR Flash，基地址为 `0x30000000`
- 256MB的SDRAM，基地址为 `0` 

则可以按照如下字章节的步骤进行编写设备树。

##### 2.2.1.1 指定系统的名称

在根节点上添加子节点 `compatible` ，<font color="#c00000">要求格式为</font> `<manufacturer>,<model>` ：

```dts
/dts-v1/;

/ {
    compatible = "acme,coyotes-revenge";
};
```

<span style="background:#fff88f"><font color="#c00000">该属性名务必正确填写</font></span>，因为操作系统会用该值决定如何在计算机上运行。

##### 2.2.1.2 CPUs


```dts
/dts-v1/;

/ {
    compatible = "acme,coyotes-revenge";

    cpus {
        cpu@0 {
            compatible = "arm,cortex-a9";
        };
        cpu@1 {
            compatible = "arm,cortex-a9";
        };
    };
};
```

CPU的 `compatible` 填写格式也必须为 `<manufacturer>,<model>` ，该值会指向正确的CPU架构。

上述示例中出现了 `cpu@0` ，其命名规则为 `<name>[@<unit-address>]` ，具体规则如下：
1. `<name>` 为一个简单字符串，长度最大为31字符。<font color="#c00000">通常节点是根据它所代表的设备类型来命名的</font>。
2. 当节点使用地址描述设备时，则应当包括 `unit-address` 。通常单元地址是用于访问设备的主地址，并列在节点 `reg` 的属性中。`reg` 属性可见后文。
3. 同级节点必须有唯一的( `<name>[@<unit-address>]` 格式的)名称，地址不同的节点名称不同。
4. 具体规则可见ePAPR规范的第2.2.1节。

##### 2.2.1.3 添加设备

针对上述假设，可以初步编写如下的设备树框架：

```dts
/dts-v1/;

/ {
    compatible = "acme,coyotes-revenge";

    cpus {
        cpu@0 {
            compatible = "arm,cortex-a9";
        };
        cpu@1 {
            compatible = "arm,cortex-a9";
        };
    };

    serial@101F0000 {
        compatible = "arm,pl011";
    };

    serial@101F2000 {
        compatible = "arm,pl011";
    };

    gpio@101F3000 {
        compatible = "arm,pl061";
    };

    interrupt-controller@10140000 {
        compatible = "arm,pl190";
    };

    spi@10115000 {
        compatible = "arm,pl022";
    };

    external-bus {
        ethernet@0,0 {
            compatible = "smc,smc91c111";
        };

        i2c@1,0 {
            compatible = "acme,a1234-i2c-bus";
            rtc@58 {
                compatible = "maxim,ds1338";
            };
        };

        flash@2,0 {
            compatible = "samsung,k8f1315ebm", "cfi-flash";
        };
    };
};
```

注：
1. 此时该设备树依旧是无效的设备树，其还缺少一些设备之间的连接信息
2. 每个节点都有 `compatible` 属性
3. flash节点中 `compatible` 属性有两个字符串
4. 节点的名称应当反应设备的类型，而非具体的型号。ePAPR 2.2.2章节中已定义通用节点名称的列表。

#### 2.2.2 compatible属性

树中每个节点都应当指定compatible属性，