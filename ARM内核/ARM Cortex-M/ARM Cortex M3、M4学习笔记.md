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
- <font color="#9bbb59">PendSV</font>：Pendable Service，可挂起系统调用
上述两个中断的区别就在于能否得到延缓执行。

#### 8.6.1 SVC系统服务调用

SVC用于完成用户态的系统调用请求。其主要由如下几个部分组成：
- SVC指令：用于在用户态唤起内核提供的系统调用，在调用SVC指令时，必须附加目标系统调用对应的SVC服务编号参数。
- SVC中断：
	1. 当用户态调用SVC指令后，CPU会产生SVC中断。
	2. 在触发SVC中断前，
- SVC中断响应例程：
	1. 在进入操作系统的SVC中断响应例程后，响应例程会判断 `LR` 的第2个bit判断其使用的是主栈(MSP)还是进程栈(PSP)
	2. 从目标栈中提取 `PC` 对应地址的数据，该数据的第一个字节为SVC服务编号，第二个字节为SVC指令
	3. 在缺第该SVC服务编号后，操作系统会完成对应的系统调用。
	![[msedge_7IxSZn3kFG.png]]
	![[msedge_nMuZYtBq4X.png]]


需要注意的是，CM3内核在SVC中断产生时，会检测当前能否正常响应SVC中断：
1. 若SVC被屏蔽(例如 `PRIMASK=1`)，则无法响应SVC中断
2. 正在运行更高优先级的中断时无法响应SVC中断(此情况正常情况下不会发生，见[[ARM Cortex M3、M4学习笔记#^eoeevc|注2]])。
<font color="#c00000">即当前内核无法响应SVC中断时，内核会触发</font>[[ARM Cortex M3、M4学习笔记#^h6lmyb|UsageFault]]，且若未使能UsageFault，则会变成HardFault。即<span style="background:#fff88f"><font color="#c00000">SVC系统服务调用必须在可以得到响应时才能被调用，否则会触发异常</font></span>。<font color="#c00000">并且SVC需要占用高优先级中断</font>。

需要注意的是：
1. 在关键代码段关闭中断时，需要注意禁止关闭SVC中断。
2. <font color="#c00000">在比SVC优先级更高的中断中</font><span style="background:#fff88f"><font color="#c00000"><b>严禁</b></font></span><font color="#c00000">触发SVC中断</font>。<font color="#c00000">而在多核CPU中，<u>每个CPU都有自己独立的SVC中断</u></font>。因此：^eoeevc
	1. <font color="#c00000">所有用户可以访问的中断，其优先级均应小于SVC的优先级</font>。
	2. 当CPU在处理更高级中断时，用户不可能触发SVC调用；而内核代码只要做到上述原则，<font color="#c00000">就不会出现正在运行更高优先级的中断时无法响应SVC中断的问题</font>。
3. 因此SVC中断优先级应尽可能的高，这样可以提高SVC的响应速度，并且更容易的将需要访问SVC的中断放到比SVC低的优先级中。

#### 8.6.2 PendSV可挂起系统调用

##### 8.6.2.1 Why PendSV? ^6ao2rz

现在假设我们使用普通的定时器(例如Systick)来实现任务的分时调度，使用SVC来接收用户的系统调用。现在考虑如下几个场景：
1. 当在处理一个比Systick优先级低的中断时，触发了Systick的中断并发生调度，则会出现优先级反转问题："用户线程优先级看起来比中断优先级高了"，如下图。
	![[msedge_BfDyMgQBmP.png]]
2. 根据上述设计，SVC的优先级通常非常高。如果在SVC中就直接完成用户态的系统调用的话，是否过于耗时？是否有必要把用户的系统调用放到SVC如此高的优先级？如何把系统调用放到更低的优先级中实现？

##### 8.6.2.2 


针对上一章节


而PendSV不需要，可见下一章节。



