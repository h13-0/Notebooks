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

| <center>Sections</center> | <center>启动过程位置变化</center> | <center>作用</center>                                 |
| ------------------------- | ------------------------- | --------------------------------------------------- |
| `.isr_vector`             | 存放于flash中                 | 中断向量表，具体内容可见上述章节。                                   |
| `.text`                   | 存放于flash中                 | 文本段(又叫代码段)                                          |
| `.rodata`                 | 存放于flash中                 | 只读数据段，存放常量字符串、`const` 变量等。                          |
| `.ARM.extab`              | 存放于flash中                 | ARM平台的异常处理表                                         |
| `.ARM.exidx`              | 存放于flash中                 | 索引表，用于支持异常处理                                        |
| `.preinit_array`          | 存放于flash中                 | 在 `.init` 段前执行                                      |
| `.init_array`             | 存放于flash中                 | 在 `.init` 段后执行，会被在启动过程中的 `__libc_init_array` 函数中被调用 |
| `.fini_array`             | 存放于flash中                 |                                                     |
| `.data`                   | 存放于固件，启动后复制到内存            | 已初始化数据段，存放已初始化的全局变量和静态变量                            |
| `.bss`                    | 固件中没有，启动时在内存中分配           | 存放未初始化的全局变量和静态变量                                    |
| `._user_heap_stack`       | 固件中没有，启动时在内存中分配           | 用户堆栈                                                |


## 3 基本原理

基于上述STM32的启动过程，Bootloader可以按照如下的逻辑进行设计：
1. 




## 4 
