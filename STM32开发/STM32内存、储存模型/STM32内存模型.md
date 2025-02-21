---
number headings: auto, first-level 2, max 6, 1.1
---
#STM32开发 

## 1 目录

```toc
```

## 2 STM32F10x

### 2.1 STM32F10x的硬件内存地址划分 ^z95v2x

STM32F10x将Flash、SRAM、寄存器以及外设均映射到了统一的内存空间：
- `0x0000 0000` - `0x1FFF FFFF` ：代码存储区，映射到内部Flash或系统存储器(取决BOOT引脚)。其中：
	- `0x000 0000` 会在启动时，根据BOOT引脚选定的启动模式，将Flash 或 SRAM 或 系统存储器映射到该位置。
	- `0x800 0000` <font color="#c00000">始终被映射到Flash</font>。
	- `0x1FFF F000` <font color="#c00000">始终被映射到系统存储器</font>。
- `0x2000 0000` - `0x3FFF FFFF` ：SRAM存储区，存储执行时的变量、堆栈等动态数据(SRAM)。
- `0x4000 0000` - `0x5FFF FFFF` ：外设寄存器，排布GPIO、USART、SPI、TIM等外设控制寄存器。
- `0xE000 0000` - `0xE00F FFFF` ：Cortex-M内核私有外设，排布SysTick、NVIC、SCB等内核寄存器。

