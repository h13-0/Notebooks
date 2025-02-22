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

STM32编译后的Sections主要有(按照地址从低到高排序)：

| Sections      | <center>作用</center>        |
| ------------- | -------------------------- |
| `.isr_vector` | 中断向量表，具体内容可见上述章节。          |
| `.text`       | 文本段(又叫代码段)                 |
| `.rodata`     | 只读数据段，存放常量字符串、`const` 变量等。 |
| `.ARM.extab`  | ARM平台的异常处理表                |
|               |                            |
|               |                            |
|               |                            |
|               |                            |


## 3 基本原理

基于上述STM32的启动过程，Bootloader可以按照如下的逻辑进行设计：
1. 




## 4 
