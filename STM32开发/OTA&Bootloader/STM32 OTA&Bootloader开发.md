---
number headings: auto, first-level 2, max 6, 1.1
---
#STM32开发 

## 1 目录

```toc
```

## 2 前置基础

### 2.1 STM32启动流程

![[STM32启动流程]]

### 2.2 固件布局(Sections)

[[STM32启动流程#^ekk2l7|STM32固件结构]]：
![[STM32启动流程#3 2 STM32固件结构 ekk2l7]]

## 3 实现

基于上述STM32的启动过程，Bootloader可以按照如下的逻辑进行设计。
需要说明的是，Bootloader和用户程序应当为两个独立的工程(或固件)。

### 3.1 Bootloader实现

在Bootloader工程中进行如下修改：
1. 修改 `*.ld` 文件的 `MEMORY` 定义的大小，<font color="#c00000">用于限制Bootloader固件的大小</font>：
```C
MEMORY
{
  RAM    (xrw)    : ORIGIN = 0x20000000,   LENGTH = 20K
  FLASH    (rx)    : ORIGIN = 0x8000000,   LENGTH = 20K  /* 64K */
}
```
1. 实现Bootloader基础功能，主要包含：
	1. [[STM32 OTA&Bootloader开发#^8pv5ar|Flash烧写功能]]
	2. [[STM32 OTA&Bootloader开发#^fsnwb3|跳转功能]]，需要完成：
		1. 关闭并重置Bootloader程序所用到的所有外设。
		2. 如果使用了RTOS，则还可能需要切换为特权模式。
		3. 设置主堆栈指针MSP。
		4. <font color="#c00000">找到并执行App程序中的复位中断的入口函数</font>( `Reset_Handler` )，<span style="background:#fff88f"><font color="#c00000">需要注意该函数仅仅包含了部分初始化功能</font></span>，<span style="background:#fff88f"><font color="#c00000">并不能重新初始化MCU!!!</font></span>
			- 详见：[[STM32启动流程#^yd4zac|Reset_handler注意点]]。
2. 补全业务逻辑，略。

#### 3.1.1 Flash烧写功能 ^8pv5ar





#### 3.1.2 跳转功能 ^fsnwb3

```C
/**
 * @brief: boot from flash.
 * @param: firmware address.
 * @note:
 * 		This function will disable necessary bootloader peripherals such as
 * 		interrupts, Systick, and RCC. Other extended peripherals need to be
 * 		manually disabled before executing this function.
 */
void boot(uint32_t addr)
{
	void (*app)(void) = (void *)(*(__IO uint32_t*)(addr + 4));

	// Gradually shut down the hardware resources used by the bootloader.
	// 1. Close global interrupt and prepare to shut down hardware.
	__disable_irq();

	// 2. Close systick and reset counter.
	SysTick->CTRL = 0; // For Cortex-m3/m4, simply press Ctrl at position 0 to close it.
	SysTick->LOAD = 0; // Clear the reload value register.
	SysTick->VAL  = 0; // Clear current count.

	// 3. Reset RCC.
	HAL_RCC_DeInit();

	// 4. Close all interrupt enable bits and clear interrupt suspension.
	for(int i = 0; i < 8; i++)
	{
		NVIC->ICER[i] = 0xFFFFFFFF;
		NVIC->ICPR[i] = 0xFFFFFFFF;
	}

	// 5. Switch the current CPU to privileged mode.
	__set_CONTROL(0);

	// 6. Set main stack pointer.
	__set_MSP(addr);

	// 7. Enable global interrupt.
	__enable_irq();

	// 8. Jump.
	app();
}
```

注意：
- `app` 指针<span style="background:#fff88f"><font color="#c00000">并非指向</font></span> `addr + 4` ，<span style="background:#fff88f"><font color="#c00000">而是指向</font></span> `addr + 4` <span style="background:#fff88f"><font color="#c00000">中存储的32位地址</font></span>。

### 3.2 App程序实现

在APP中应当进行如下修改：
1. 修改Flash的起始位置、Flash大小，<font color="#c00000">需要注意的是K为1024而非1000</font>：
```C
MEMORY
{
  RAM    (xrw)    : ORIGIN = 0x20000000,   LENGTH = 20K
  /* FLASH    (rx)    : ORIGIN = 0x8000000,   LENGTH = 64K */
  FLASH    (rx)    : ORIGIN = 0x8005000,   LENGTH = 46K
}
```
- 补充：
	- 在本步骤中，<font color="#c00000">修改了FLASH的起始地址</font>，<span style="background:#fff88f"><font color="#c00000">也就顺带修改了该固件中所有函数调用时所指向的函数地址</font></span>(包括汇编指令、`.init` 段等函数地址调用)，<font color="#c00000">也就是只要把固件拷贝到正确的内存地址后，即可保证启动后APP的正常运行</font>。
	- 而在整个生命周期中，仅有[[STM32启动流程|STM32启动过程中]]还未保证地址的正确偏移，此时则需要进行第二步处理。
2. 修改APP中的中断向量表偏移，全局搜索 `VECT_TAB_OFFSET` 宏，并完成修改即可。该宏位于 `system_stm32*xx.c` 中，<font color="#c00000">CubeMX不会重新生成该文件</font>，<font color="#c00000">正常使用宏定义即可</font>：
```C
#define USER_VECT_TAB_ADDRESS
#define VECT_TAB_OFFSET 0x00005000U // 具体偏移是Bootloader预留的空间大小
```
- 补充：
	- 在整个启动流程中，仅 `startup_*.s` 中的操作不受链接器的影响。
	- 本质上修改了 `SCB->VTOR` 所指向的地址。
