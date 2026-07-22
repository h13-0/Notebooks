---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 

参考书籍：
- Cortex-M3 权威指南，Joseph Yiu著；宋岩译。
- ARM Cortex-M3与Cortex-M4权威指南(第3版)，Joseph Yiu著；吴常玉，曹孟娟，王丽红译。
- The Cortex-M3 Technical Reference Manual
- The ARMv7-M Architecture Application Level Reference Manual

# 1 目录

```toc
```

# 2 ARM Cortex-M处理器简介

Arm Cortex M3是Arm v7中M系列的一个分支，其是哈佛架构，有独立的指令总线和数据总线，指令和数据共享同一个存储器空间。

## 2.1 核心寄存器组

Cortex M3有如下16个寄存器：
	![[msedge_1MZIgPfib3.png]]
其中：
- R0-R12为32位通用寄存器，用于数据操作，其中：
	- 16位Thumb指令只能访问R0-R7，32位Thumb-2指令可以访问全部寄存器
- R13为堆栈指针寄存器，<font color="#c00000">其由主堆栈指针和进程堆栈指针两个寄存器组成</font>，<font color="#c00000">同一时刻内仅有一个可见</font>。
	- 堆栈指针最低两位恒定为0，即堆栈是四字节对齐的。
	- 使用哪个由[[ARM Cortex M3、M4学习笔记#^19zgcv|CONTROL 控制寄存器]]决定。
- R14为连接寄存器，<font color="#c00000">当调用一个子程序时由R14存储返回地址</font>。
- R15为程序计数寄存器(PC)，

## 2.2 特殊功能寄存器组

特殊寄存器包含如下五个寄存器：
	![[msedge_5GBhP6gh2m.png]]
其中：
- `xPSR` 为程序状态寄存器
- `PRIMASK` 为所有可屏蔽中断的屏蔽寄存器
- `FAULTMASL` 为所有fault的屏蔽寄存器
- `BASEPRI` 为屏蔽优先级低于某个具体数值的寄存器
- `CONTROL` 定义特权状态，并决定使用哪一个R13堆栈指针寄存器

### 2.2.1 xPSR 程序状态寄存器

状态字寄存器xPSR的结构如下：
	![[msedge_AkXI5N77wZ.png]]
其按照功能可以拆分为：
- 应用程序PSR(APSR)
- 中断号PSR(IPSR)
- 执行PSR(EPSR)




### 2.2.2 CONTROL 控制寄存器 ^19zgcv

常规CPU设计中，通常总是支持设置CPU权限级别，从而进行权限级别控制。Cortex M3中定义了如下的特权分级：
- 特权级：
	- 程序可以：
		- 访问在MPU允许的范围内的所有寄存器
		- 允许执行所有指令
		- 允许切换到非特权级(即修改 `CONTROL` 寄存器)
- 非特权级：
	- 程序可以：
		- 只能通过操作SVC指令，从而触发SVC异常才可重新回到特权

在Cortex M3中，CONTROL寄存器被用于<font color="#c00000">定义特权特权级别</font>和<font color="#c00000">选择当前使用的堆栈指针</font>，其基础区位为：
- `CONTROL[0]` ：<font color="#c00000">异常服务例程外</font>的特权级别选择(异常服务例程中永远为特权级)
	- `CONTROL[0]=0` 时为特权级
	- `CONTROL[0]=1` 时为用户级(非特权级)
- `CONTROL[1]` ：堆栈指针选择
	- `CONTROL[1]=0` 时为主堆栈指针MSP
	- `CONTROL[1]=1` 时为进程堆栈指针PSP
- `CONTROL[2:31]` ：保留

## 2.3 操作模式与特权模式

在[[ARM Cortex M3、M4学习笔记#^19zgcv|CONTROL 控制寄存器]]中已经讲了Cortex M3所支持的两种特权模式，其主要决定了对应模式下可执行的指令与访问的空间。

而Cortex M3还定义了如下两种不同的操作模式：
- `handler mode` ：异常服务例程代码的执行模式，在响应异常时自动进入。<font color="#c00000">该模式下的代码总是特权级</font>。
- `thread mode` ：普通应用程序代码的执行模式。该模式下的代码可以是特权级，也可以是非特权级。

不过与特权模式不同的是，操作模式并不由某个具体的寄存器反应或改变，其是一种CPU状态。当其在异常服务例程中时，CPU会自动变为handler mode和特权级，退出服务例程时会自动退出handler mode。

注：
- 在 `handler mode` <font color="#c00000">时</font><span style="background:#fff88f"><font color="#c00000">永远为特权级</font></span>，而无论 `CONTROL` 寄存器的状态。

## 2.4 嵌套向量中断控制器(NVIC)

嵌套向量中断控制器(Nested Vectored Interrupt Controller)提供了如下的功能：
- 可嵌套中断支持
- 中断向量支持
- 动态优先级调整支持
- 较低的中断响应时长
- 中断的可屏蔽特性

### 2.4.1 可嵌套中断支持

每一个中断都有其对应的优先级，代码当前的优先级被存储于 `xPSR` 寄存器中


### 2.4.2 中断向量支持


# 3 技术综述
# 4 嵌入式软件开发简介



# 5 架构


# 6 指令集


# 7 存储器系统


# 8 异常和中断

## 8.1 异常和中断简介

在ARM处理器中，任何会打断程序顺序执行的事件都被称作异常(exception)
## 8.2 异常类型


![[msedge_ymhoWlu9tC.png]]
![[msedge_UWkdSATg7U.png]]




## 8.3 向量表


## 8.4 中断输入与悬起行为


## 8.5 Fault类异常


### 8.5.1 总线Faults



### 8.5.2 存储器管理Faults

### 8.5.3 UsageFault ^h6lmyb




### 8.5.4 硬Faults


## 8.6 SVC和PendSV

基本概念：
- <font color="#9bbb59">SVC</font>：Supervisor Call，系统服务调用。
- <font color="#9bbb59">PendSV</font>：Pendable Service，可挂起系统调用
上述两个中断的区别就在于能否得到延缓执行。

### 8.6.1 SVC系统服务调用

SVC用于完成用户态的系统调用请求。其主要由如下几个部分组成：
- SVC指令：用于在用户态唤起内核提供的系统调用，在调用SVC指令时，必须附加目标系统调用对应的SVC服务编号参数。
- SVC中断：
	1. 当用户态调用SVC指令后，CPU会产生SVC中断。
	2. 在触发SVC中断前，CPU会自动保存现场(PC等)到当前活动堆栈中。
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

### 8.6.2 PendSV可挂起系统调用

#### 8.6.2.1 Why PendSV? ^6ao2rz

现在假设我们使用普通的定时器(例如Systick)来实现任务的分时调度，使用SVC来接收用户的系统调用。现在考虑如下几个场景：
1. 当在处理一个比Systick优先级低的中断时，触发了Systick的中断并发生调度，则会出现优先级反转问题："用户线程优先级看起来比中断优先级高了"，如下图。
	![[msedge_BfDyMgQBmP.png]]
2. 根据上一章节中的设计，SVC的优先级通常非常高。如果在SVC中就直接完成用户态的系统调用的话，是否过于耗时？是否有必要把用户的系统调用的后端实现放到SVC如此高的优先级？如何把系统调用的后端放到更低的优先级中处理？
当然，<span style="background:#fff88f"><font color="#c00000">解决上述问题只需要实现一个"延迟执行的机制"</font></span>。该机制可以直接依靠"ARM中断嵌套及其优先级"的机制进行解决，可见下一章节。

#### 8.6.2.2 PendSV规则及原理

上一章节的问题可以考虑实现一种延迟执行机制，将系统调用的后端实现及上下文切换丢到所有其他中断运行结束后自动运行即可。也正如上述章节所述，可以直接依靠ARM中断嵌套机制实现，配置一个优先级最低的专用中断，将SVC中断的后半、系统调用后端实现及延迟上下文切换等内容放入该专用中断中即可。当其他所有中断运行完毕后，该中断即会自动运行。PendSV即是基于此思路在硬件层面专门优化来的专用中断。

- 简化版本： ^5nd44b
	- PendSV是CPU专门为SVC中断的后半、系统调用的后端实现及延迟上下文切换特殊优化而来的一个专用中断。该中断的优先级通常配置为最低，以方便让上述操作在其他所有中断运行结束后自动运行。该特性基于中断嵌套机制。
	- 此外，PendSV通常用于任务切换，因此只要想切换任务，不经过SVC中断也可以手动触发

PendSV基本规则：
1. <span style="background:#fff88f"><font color="#c00000">PendSV的中断优先级需要配置为最低</font></span>。
2. 可以在Systick等中断中触发。






