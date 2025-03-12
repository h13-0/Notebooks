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

#### 8.5.3 UsageFault ^h6lmyb




#### 8.5.4 硬Faults


### 8.6 SVC和PendSV

基本概念：
- <font color="#9bbb59">SVC</font>：Supervisor Call，系统服务调用。
- <font color="#9bbb59">PendSV</font>：可悬起系统调用
上述两个中断的区别就在于能否得到延缓执行。

#### 8.6.1 SVC系统服务调用

SVC用于完成用户态的系统调用请求。其主要由如下几个部分组成：
- SVC指令：用于在用户态唤起内核提供的系统调用，在调用SVC指令时，必须附加目标系统调用对应的SVC服务编号参数。
- SVC中断：当用户态调用SVC指令后，CPU会产生SVC中断。
- SVC中断响应例程：
	1. 在进入操作系统的SVC中断响应例程后，响应例程会判断 `LR` 的第2个bit判断其使用的是主栈(MSP)还是进程栈(PSP)
	2. 从目标栈中提取 `PC` 对应地址的数据，该数据的第一个字节为SVC服务编号，第二个字节为SVC指令
	3. 在缺第该SVC服务编号后，操作系统会完成对应的系统调用。
	![[msedge_7IxSZn3kFG.png]]
	![[msedge_nMuZYtBq4X.png]]


需要注意的是，CM3内核在SVC中断产生时，会检测当前能否正常响应SVC中断：
1. 若SVC被屏蔽(例如 `PRIMASK=1` )，则无法响应SVC中断
2. 正在运行更高优先级的中断时无法响应SVC中断
<font color="#c00000">即当前内核无法响应SVC中断时，内核会触发</font>[[ARM Cortex M3、M4学习笔记#^h6lmyb|UsageFault]]，且若未使能UsageFault，则会变成HardFault。即<span style="background:#fff88f"><font color="#c00000">SVC系统服务调用必须在可以得到响应时才能被调用，否则会触发异常</font></span>。<font color="#c00000">并且SVC需要占用高优先级中断</font>。

回到上述的SVC系统调用的响应链条上，分析SVC占用高优先级中断并且

考虑如下的情况：



需要注意的是：
1. 在关键代码段关闭中断时，需要注意禁止关闭SVC中断。


而PendSV不需要，可见下一章节。



