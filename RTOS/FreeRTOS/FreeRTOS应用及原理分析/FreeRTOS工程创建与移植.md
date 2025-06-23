---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 #FreeRTOS

## 1 目录

```toc
```

## 2 FreeRTOS工程创建

在一些不严谨的地方也可以称作 "FreeRTOS移植"，与下一章节的[[FreeRTOS工程创建与移植#4 FreeRTOS移植|FreeRTOS移植]]不同的地方在于 "工程创建" 指的是使用FreeRTOS支持的CPU完成工程创建，而移植则包含FreeRTOS暂未支持的CPU的底层实现。
而在


<font color="#c00000">这里以STM32F103系列单片机为例</font>。

### 2.1 基础工程的创建

#### 2.1.1 准备FreeRTOS源码

在官网[freertos.org](https://freertos.org/)中提供了普通版本和LTS版本的源码，
	![[chrome_cIeEB446qa.png]]
其区别主要有：
1. 版本定位不同，LTS为长支持版本。在未来FreeRTOS官方会逐渐全部转向为LTS版本。
2. 普通版本包含更多的示例代码，而LTS暂时没有
3. 文件结构不同

#### 2.1.2 提取FreeRTOS的源文件、头文件以及portable文件

##### 2.1.2.1 LTS版本


##### 2.1.2.2 普通版本

主要步骤如下：
1. 将 `FreeRTOS/Source/*.c` 复制到 `freertos/src` 下。
2. 将 `FreeRTOS/Source/include/*.h` 复制到 `freertos/inc` 下。
3. 在 `FreeRTOS/Source/portable/MemMang` 下选择一种内存管理方式，通常选择 `heap_4.c` 并复制到 `freertos/src` 下。
5. 在 `FreeRTOS/Source/include/portable` 下进入对应编译器所在目录，并在该目录中找到对应CPU结构体系所在的文件夹，复制 `port.c` 到 `freertos/src` ，复制 `portmacro.h` 到 `freertos/inc` 。
6. 进入 `FreeRTOS/Demo` ，根据平台和编译器选择文件夹，复制 `FreeRTOSConfig.h` 到 `freertos/inc` 。
即可完成文件提取。

简单来说，文件提取需要提取：
1. FreeRTOS通用源文件
2. FreeRTOS通用头文件
3. 选择FreeRTOS内存管理实现
4. 复制对应平台的 `port.c` 和 `portmacro.h` 
5. 复制对应平台的 `FreeRTOSConfig.h` 

#### 2.1.3 中断服务配置

FreeRTOS需要将如下的三个中断服务<span style="background:#fff88f"><font color="#c00000">直接映射到</font></span>对应的接口上：
- `PendSV_Handler`
- `SVC_Handler`
- `SysTick_Handler`
<font color="#c00000">这三个函数必须直接映射</font>，<span style="background:#fff88f"><font color="#c00000">不可在里面进行二次转发</font></span>(否则会出现函数调用栈，并触发HardFault异常)。可选的方式有：
1. 直接在 `FreeRTOSConfig.h` 中定义如下的宏，重命名中断handler名，<font color="#c00000">并删除原中断函数实现</font>(<font color="#c00000">若使用CubeMx则需要取消生成对应的中断函数</font>)
```C
#define xPortPendSVHandler      PendSV_Handler
#define vPortSVCHandler         SVC_Handler
#define xPortSysTickHandler     SysTick_Handler
```
2. 修改汇编启动文件，在启动阶段直接修改中断向量到 `xPortPendSVHandler` 等handler。

#### 2.1.4 启动和测试FreeRTOS

启动FreeRTOS只需要使用 `vTaskStartScheduler();` 启动调度器即可，随后在主函数中加入死循环并捕获FreeRTOS的退出。

## 3 FreeRTOS启动过程





## 4 FreeRTOS的移植


