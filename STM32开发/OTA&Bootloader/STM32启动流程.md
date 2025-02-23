---
number headings: auto, first-level 2, max 6, 1.1
---
#STM32开发 

## 1 目录

```toc
```

## 2 Note

<font color="#c00000">下方内容默认均以STM32F103为例</font>，并可能地补上其他常用系列的不同点。

## 3 前置基础

### 3.1 内存地址划分

[[STM32内存模型#^z95v2x]]：
![[STM32内存模型#2 1 STM32F10x的硬件内存地址划分 z95v2x]]

### 3.2 STM32固件结构 ^ekk2l7

STM32编译所得固件的Sections主要有(按照地址从低到高排序)：

| <center>Sections</center> | <center>启动过程位置变化</center> | <center>作用</center>                                                                                 |
| ------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------- |
| `.isr_vector`             | 存放于flash中                 | 中断向量表，具体内容可见上述章节。                                                                                   |
| `.text`                   | 存放于flash中                 | 文本段(又叫代码段)                                                                                          |
| `.rodata`                 | 存放于flash中                 | 只读数据段，存放常量字符串、`const` 变量等。                                                                          |
| `.ARM.extab`              | 存放于flash中                 | ARM平台的异常处理表                                                                                         |
| `.ARM.exidx`              | 存放于flash中                 | 索引表，用于支持异常处理                                                                                        |
| `.preinit_array`          | 存放于flash中                 | 在 `.init` 段前执行，                                                                                     |
| `.init_array`             | 存放于flash中                 | 在 `.init` 段后执行，<font color="#c00000">存放全局构造函数或者初始化函数的指针</font>，会被在启动过程中的 `__libc_init_array` 函数中被调用 |
| `.fini_array`             | 存放于flash中                 | (裸机中极少使用)，<font color="#c00000">存放程序退出时的析构函数或资源释放函数的指针</font>，会在程序退出时被执行                            |
| `.data`                   | 存放于固件，启动后复制到内存            | 已初始化数据段，存放已初始化的全局变量和静态变量                                                                            |
| `.bss`                    | 固件中没有，启动时在内存中分配           | 存放未初始化的全局变量和静态变量                                                                                    |
| `._user_heap_stack`       | 固件中没有，启动时在内存中分配           | 用户堆栈                                                                                                |

其中STM32的中断向量表如下：

| 地址偏移   | <center>存储内容</center>     | <center>长度</center> | <center>作用</center> |
| ------ | ------------------------- | ------------------- | ------------------- |
| 0x0000 | 初始栈顶指针(MSP初始值)            | 4字节                 |                     |
| 0x0004 | `Reset_Handler` 的函数地址     | 4字节                 |                     |
| 0x0008 | `NMI_Handler` 的函数地址       | 4字节                 |                     |
| 0x000C | `HardFault_Handler` 的函数地址 | 4字节                 |                     |
| ...    | ...(具体可见 `startup*.s` )   | ...                 |                     |

## 4 启动模式

STM32的启动模式主要有如下几种：

| <center>BOOT引脚配置</center> | <center>启动模式</center>                              | <center>内存映射</center>                                                                                                           |
| ------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| BOOT0=0                   | 从内置Flash启动                                         | 主闪存存储器被映射到启动空间(`0x0000 0000`)，<br>但仍然能够在它原有的地址(`0x0800 0000`)访问它，<br>即闪存存储器的内容可以在两个地址区域访问，<br>即 `0x0000 0000` 或 `0x0800 0000` 。 |
| BOOT0=1，BOOT1=0           | 从系统存储器启动<br>(内置Bootloader，又称自举程序，<br>用于串口/USB下载程序) | 系统存储器被映射到启动空间( `0x0000 0000` )，<br>但仍然能够在它原有的地址(互联型产品原有地址<br>为 `0x1FFF B000` ，其它产品原有地址为<br>`0x1FFF F000`)访问它。                   |
| BOOT0=1，BOOT1=1           | 从内置SRAM启动<br>(调试用途)                                | 只能在 `0x2000 0000` 开始的地址区访问SRAM。                                                                                                 |

注：
- STM32F10x：
	- 不支持从外部Flash启动。
	- 在系统复位后，SYSCLK的第4个上升沿，BOOT引脚的值将被锁存。用户可以通过设置BOOT1和BOOT0引脚的状态，来选择在复位后的启动模式。

## 5 从内置Flash启动的启动流程

从内置Flash启动的启动流程为：
1. 芯片上电或触发复位。
2. SYSCLK的第4个上升沿，BOOT引脚的值将被锁存，此时被配置为从内置Flash启动，`0x0000 0000` 的地址会被映射到 `0x0800 0000` ，并开始执行代码。
3. 读取固件头的中断向量表(可详见[[STM32启动流程#^ekk2l7|STM32固件结构]])，并执行：
	1. 将初始化栈顶指针读取到SP寄存器
	2. 执行 `Reset_Handler` 函数，详见[[STM32启动流程#^1xjvks]]：![[STM32启动流程#5 1 Reset_Handler函数 ^1xjvks]]

### 5.1 Reset_Handler函数 ^1xjvks


`Reset_Handler` 函数的参考代码如下：

```C
Reset_Handler:

/* Call the clock system initialization function.*/
    bl  SystemInit

/* Copy the data segment initializers from flash to SRAM */
  ldr r0, =_sdata
  ldr r1, =_edata
  ldr r2, =_sidata
  movs r3, #0
  b LoopCopyDataInit
```

其主要流程为：
1. 调用 `SystemInit` 函数，主要初始化系统时钟源、PLL锁等。
2. 初始化 `.data` 段。
3. 跳转 `LoopCopyDataInit` 函数：
   1. 清零 `.bss` 段。
   2. 调用 `__libc_init_array` 函数初始化C库。
   3. 调用 `main` 函数。
