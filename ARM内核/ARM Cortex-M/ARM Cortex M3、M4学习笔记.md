---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 

参考书籍：
- Cortex-M3 权威指南，Joseph Yiu著；宋岩译。
- ARM Cortex-M3与Cortex-M4权威指南(第3版)，Joseph Yiu著；吴常玉，曹孟娟，王丽红译。

## 1 目录

```toc
```

## 2 ARM Cortex-M处理器简介

## 3 技术综述
## 4 嵌入式软件开发简介



## 5 架构


## 6 指令集


## 7 存储器系统


## 8 异常和中断

### 8.1 异常和中断简介


### 8.2 异常类型


![[msedge_ymhoWlu9tC.png]]
![[msedge_UWkdSATg7U.png]]




### 8.3 向量表


### 8.4 中断输入与悬起行为


### 8.5 Fault类异常


#### 8.5.1 总线Faults



#### 8.5.2 存储器管理Faults

#### 8.5.3 用法Faults

#### 8.5.4 硬Faults


### 8.6 SVC和PendSV

基本概念：
- <font color="#9bbb59">SVC</font>：系统服务调用
- <font color="#9bbb59">PendSV</font>：可悬起系统调用

SVC用于产生系统函数的调用请求，当用户发起系统调用请求时，会产生SVC异常，然后操作系统提供的SVC异常服务例程会得到执行，它再调用相关的操作系统函数，后者完成用户程序请求的服务。

![[msedge_KRuwi11Lur.png]]



