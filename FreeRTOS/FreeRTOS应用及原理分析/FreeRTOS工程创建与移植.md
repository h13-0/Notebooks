---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 #FreeRTOS

## 1 目录

```toc
```

## 2 FreeRTOS工程创建

在一些不严谨的地方也可以称作 "FreeRTOS移植"，与下一章节的[[FreeRTOS工程创建与移植#3 FreeRTOS移植|FreeRTOS移植]]不同的地方在于 "工程创建" 指的是使用FreeRTOS支持的CPU完成工程创建，而移植则包含FreeRTOS暂未支持的CPU的底层实现。

### 2.1 准备FreeRTOS源码

在官网[freertos.org](https://freertos.org/)中提供了普通版本和LTS版本的源码，
	![[chrome_cIeEB446qa.png]]
其区别主要有：
1. 版本定位不同，LTS为长支持版本
2. 普通版本包含更多的示例代码，而LTS暂时没有
3. 文件结构不同

### 2.2 提取FreeRTOS的源文件、头文件以及portable文件








## 3 FreeRTOS移植