---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 #FreeRTOS

## 1 目录

```toc
```

## 2 FreeRTOS工程创建

在一些不严谨的地方也可以称作 "FreeRTOS移植"，与下一章节的[[FreeRTOS工程创建与移植#3 FreeRTOS移植|FreeRTOS移植]]不同的地方在于 "工程创建" 指的是使用FreeRTOS支持的CPU完成工程创建，而移植则包含FreeRTOS暂未支持的CPU的底层实现。

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
6. 对于ARM处理器，进入 `FreeRTOS/Source/include/portable` 




## 3 FreeRTOS移植