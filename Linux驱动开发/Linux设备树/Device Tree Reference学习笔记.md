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

#### 2.2.1 示例机及设备树框架搭建

##### 2.2.1.1 基本假设

假设给定的机器有如下属性：
- 由 "Acme" 制造，命名为 "Coyote's Revenge"。
- 双核 Cortex-A9 CPU
- 映射到内存上的外设有：
	- 两个串口(serial)：
		- 串口1基地址分别为 `0x101F1000` ，占用内存大小为 `0x1000`
		- 串口2基地址分别为 `0x101F2000` ，占用内存大小为 `0x1000`
	- GPIO控制器，基地址为 `0x101F3000` ，占用内存大小为 `0x1010` 。其中：
		- 区域1为 `0x101F3000 ~ 0x101F3FFF`
		- 区域2为 `0x101F4000 ~ 0x101F401F`
	- SPI总线控制器，基地址为 `0x10170000` ，占用内存大小为 `0x1000` ，并且外挂有如下设备：
		- 带有SS引脚的MMC插槽，SS引脚为 `GPIO#1`
	- 外部总线桥，假设为片选方式控制这个外部总线桥。该外部总线桥附带如下设备： ^c5o9gk
		- 片选0的偏移0：SMC SMC91111以太网设备，目标映射到的物理地址为 `0x10100000` 并占用大小 `0x10000` 的内存片。
		- 片选1的偏移0：I2C控制器，目标映射到的物理地址为 `0x10160000` 并占用大小 `0x10000` 的内存片，并外挂如下设备：
			- DS1338 RTC时钟，I2C地址为 `0x58`
		- 片选2的偏移0：64MB NOR Flash，目标映射到的物理地址为 `0x30000000` 并占用大小 `0x1000000` 的内存片。
- 256MB的SDRAM，基地址为 `0` 

##### 2.2.1.2 指定系统的名称

在根节点上添加子节点 `compatible` ，<font color="#c00000">要求格式为</font> `<manufacturer>,<model>` ：

```dts
/dts-v1/;

/ {
    compatible = "acme,coyotes-revenge";
};
```

<span style="background:#fff88f"><font color="#c00000">该属性名务必正确填写</font></span>，具体可详见章节[[Device Tree Reference学习笔记#2 2 2 compatible属性|compatible属性]]。

##### 2.2.1.3 CPUs


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

##### 2.2.1.4 添加设备

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
2. 每个节点都有 `compatible` 属性，具体可详见章节[[Device Tree Reference学习笔记#2 2 2 compatible属性|compatible属性]]
3. flash节点中 `compatible` 属性有两个字符串
4. 节点的名称应当反应设备的类型，而非具体的型号。ePAPR 2.2.2章节中已定义通用节点名称的列表。

#### 2.2.2 compatible属性

compatible属性是操作系统选择设备驱动时使用的key值，因此其基本要求为：
1. 树中每个节点都应当指定compatible属性。
2. compatible是一个字符串列表。
3. 列表中的<font color="#c00000">第一个字符串</font>格式应遵守 `<manufacturer>,<model>` 格式。
4. 后续的字符串表示兼容的其他设备，例如对于 `compatible = "fsl,mpc8349-uart", "ns16550"` ：
	- 其 `fsl,mpc8349-uart` 指向确切的器件
	- `ns16550` 说明该器件与 `ns16550` 完全兼容。
		- 注：理论上 `ns16550` 也应当遵守 `<manufacturer>,<model>` 格式，但是由于历史原因没有保留制造商前缀。
	- 该做法允许将现有设备驱动程序绑定到较新的设备，同时仍唯一标识确切的硬件。
	- 注：
		- <span style="background:#fff88f"><font color="#c00000">请勿使用通配兼容型号来实现设备树</font></span>，例如 `"fsl,mpc8349-uart"` 不可写为 `"fsl,mpc83xx-uart"` 。因为即使现在mpc83xx的所有型号都互相兼容，<font color="#c00000">但是不能保证该制造商<u>未来的</u>所有mpc83xx型号依旧会兼容该驱动程序</font>(通常来说，编写设备树的不一定是设备制造商自己。甚至设备制造商自己也无法做到向前兼容，例如如果遇到重大设计问题导致不得不改版等)。

### 2.3 寻址的工作原理

在操作系统原理中，将各种可寻址外设统一映射到一片固定的物理内存上是一个常见的设计。例如上述章节中将串口1映射到了 `0x101F1000` 上。
不过同样的，也存在无法映射到内存上的设备，比如上述的I2C总线上外挂的rtc设备等。

但是这些设备的寻找通常都需要指定一个地址，例如上述rtc也需要在I2C总线上指定一个从设备地址。(当然也有例外，例如CPU不需要寻址)

而设计统一的寻址方式需要解决如下的问题：
1. 不同位数或不同体系的CPU地址长度不同；不同总线协议约定的地址长度不同。
2. 不同外设映射到的内存大小不同。
因此Linux给出了可以在设备树中定义设备地址的特性。其有如下特性：
1. 使用 `#address-cells = <n>` <font color="#c00000">指定该节点</font><span style="background:#fff88f"><font color="#c00000">的子节点</font></span><font color="#c00000">的地址所占用的大小</font>，单位32Bit。例如 `#address-cells = <2>` 表示每个地址使用2个32位字<span style="background:#fff88f">(因为尖括号内是32位变量，因此单位就是32Bit)</span>。
2. 使用 `#size-cells = <n>` <font color="#c00000">指定该节点</font><span style="background:#fff88f"><font color="#c00000">的子节点</font></span><font color="#c00000">所占用内存大小<u>的宽度</u></font>，单位32Bit。例如 `#size-cells = <1>` <font color="#c00000">表示需要使用1个32位字定义内存大小变量</font>，即 `uint32_t size` 。<font color="#c00000">而具体占用的大小需要在下一条中定义</font>。
3. 在使用上述两个参数定义了一个设备及其子设备的<font color="#c00000">内存地址位数</font>和<font color="#c00000">内存大小位数</font>后，应当使用：
	- `reg = < ${region1}[ ${region2} ...] >` 
	定义若干个内存区域。其中：
	- 一个 `reg` <font color="#c00000">可以同时写一个或多个内存区域</font>。
	- `${regionx}` 的格式如下：
		- `[address_high ]address_low[ size_high size_low]`
	格式给出对应设备的参数，其中：
	1. 当address-cells为1时，address high<font color="#c00000">必须省略</font>。
	2. 当size-cells为0时，size high,size low<span style="background:#fff88f"><font color="#c00000">都</font></span><font color="#c00000">必须省略</font>。
	3. 当size-cells为1时，size high<font color="#c00000">必须省略</font>。
	(<span style="background:#fff88f"><font color="#c00000">其本质是先写address后写size，用了几个32位就写几个，没用就不写</font></span>，只是目前没有128位机)
具体示例如各子章节。

#### 2.3.1 CPU寻址示例

通常来说，CPU不需要寻址，因此该值通常用于指定 `CPU_ID` 。
则明显地：
- 内存地址位数(这里是 `CPU_ID` 位数)为1位，即 `#address-cells = <1>;`
- 内存大小位数(这里无实际意义)为0位，即 `#size-cells = <0>;`
则此时 `address high` 、 `size high` 、 `size low` <font color="#c00000">均可省略</font>，有：
- `reg = <0>;`

```dts
    cpus {
        #address-cells = <1>;
        #size-cells = <0>;
        cpu@0 {
            compatible = "arm,cortex-a9";
            reg = <0>;
        };
        cpu@1 {
            compatible = "arm,cortex-a9";
            reg = <1>;
        };
    };
```

#### 2.3.2 普通内存映射设备

在内存映射设备中，由于设备都被映射到内存中了，而上述内存宽度的两个配置都是<font color="#c00000">针对子节点</font><span style="background:#fff88f"><font color="#c00000">才</font></span><font color="#c00000">开始生效</font>。因此在根节点中定义内存宽度即可。

例如上述的32位Cortex A9中，则有平台内存映射设备的：
- `#address-cells = <1>`
- `#size-cells = <1>`
则根据基本假设：
![[Device Tree Reference学习笔记#2 2 1 1 基本假设]]
可继续编写如下的设备树：

```dts
/ {
    #address-cells = <1>;
    #size-cells = <1>;

    compatible = "acme,coyotes-revenge";

    cpus {
        #address-cells = <1>;
        #size-cells = <0>;
        cpu@0 {
            compatible = "arm,cortex-a9";
            reg = <0>;
        };
        cpu@1 {
            compatible = "arm,cortex-a9";
            reg = <1>;
        };
    };

    serial@101f0000 {
        compatible = "arm,pl011";
        reg = <0x101f0000 0x1000 >;
    };

    serial@101f2000 {
        compatible = "arm,pl011";
        reg = <0x101f2000 0x1000 >;
    };

    gpio@101f3000 {
        compatible = "arm,pl061";
        reg = <0x101f3000 0x1000
               0x101f4000 0x0010>;
    };

    interrupt-controller@10140000 {
        compatible = "arm,pl190";
        reg = <0x10140000 0x1000 >;
    };

    spi@10115000 {
        compatible = "arm,pl022";
        reg = <0x10115000 0x1000 >;
    };
    
    external-bus {
	    // 由于外部总线下的节点是非根节点
	    // (也就是不直接与CPU相连的，位于特定总线或设备下的节点)
	    // 因此其不能直接使用上述方法直接使用CPU地址域配置。
	    // 详细的方法见 "地址转换章节" 。
    };
};
```

其中：
- gpio的内存被分为了两个区域，并填写到了一个 `reg` 中。

#### 2.3.3 非内存映射设备

有些设备不能被映射到内存，其可能是没有地址范围，也可能是其内存不能被CPU访问而需要父设备代为访问。这种不能映射到内存的设备被称为非内存映射设备。

例如上述假设中，被挂在I2C总线下的DS1338 RTC时钟就属于非内存映射设备。其可以如下编写设备树：

```dts
        i2c@1,0 {
            compatible = "acme,a1234-i2c-bus";
            #address-cells = <1>;
            #size-cells = <0>;
            reg = <1 0 0x1000>;
            rtc@58 {
                compatible = "maxim,ds1338";
                reg = <58>;
            };
        };
```

其中：
- 这里i2c使用的地址为偏选1，偏移0。具体可见下一章节。

#### 2.3.4 地址转换(ranges属性)

CPU需要连接的总线种类繁多，其驱动设计要求也有所不同，有的不需要完成地址转换，有的需要完成地址转换但对具体映射的地址没有要求，有的时候需要将总线上的地址原封不动的映射到CPU地址上。例如：
- PCI总线上有一个完全独立的地址空间，但是需要把详细信息向操作相同公开。
- I2C总线上的设备没有被映射到CPU地址区域。

因此ranges属性被设计用于完成子地址和父地址之间的转换，其格式为：
- `ranges = <[${addr_pairs1} ${addr_pairs2} ...]>`
其中：
- `${addr_pairsx}` 的格式为：
	- `${slave_addr} ${master_addr}[${size}]` 。
需要注意的是：
- ranges属性可以为空(此时写作 `ranges;` )，<u>此时含义为将总线上的地址原封不动的映射到CPU地址上</u>。
- 不配置ranges属性(即不写该项)，则<font color="#c00000">该子节点上的所有设备不能由其父设备以外的任何设备直接访问</font>(例如I2C总线)。

例如，按照假设设备的外部总线桥：
![[Device Tree Reference学习笔记#^c5o9gk]]
其从设备的地址可以设计为：
- `<${片选ID} ${偏移量}>` 的两个32位字
- 32位CPU中地址占用1个32位字
- 长度占用1个32位字
则可以编写如下的 `ranges` 属性：

```dts
ranges = <0 0  0x10100000   0x10000       // Chipselect 1, Ethernet
	        1 0  0x10160000   0x10000     // Chipselect 2, i2c controller
	        2 0  0x30000000   0x1000000>; // Chipselect 3, NOR Flash
```

随后<font color="#c00000">从总线上挂的设备的reg使用从总线地址即可</font>，即：

```dts
    external-bus {
        #address-cells = <2>;
        #size-cells = <1>;
        ranges = <0 0  0x10100000   0x10000     // Chipselect 1, Ethernet
                  1 0  0x10160000   0x10000     // Chipselect 2, i2c controller
                  2 0  0x30000000   0x1000000>; // Chipselect 3, NOR Flash

        ethernet@0,0 {
            compatible = "smc,smc91c111";
            reg = <0 0 0x1000>;
        };

        i2c@1,0 {
            compatible = "acme,a1234-i2c-bus";
            #address-cells = <1>;
            #size-cells = <0>;
            reg = <1 0 0x1000>;
            rtc@58 {
                compatible = "maxim,ds1338";
                reg = <58>;
            };
        };

        flash@2,0 {
            compatible = "samsung,k8f1315ebm", "cfi-flash";
            reg = <2 0 0x4000000>;
        };
    };
```

### 2.4 中断的工作原理


























