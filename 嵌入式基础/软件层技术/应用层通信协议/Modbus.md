---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 

## 1 目录

```toc
```

## 2 Modbus概述

Modbus有如下三种协议：
- Modbus ASCII
- Modbus RTU
- Modbus TCP
Modbus协议规定，使用Modbus的设备必须支持Modbus RTU，且默认为Modbus RTU，因此大多数设备使用的均为Modbus RTU。

### 2.1 Modbus RTU

#### 2.1.1 Modbus RTU基本规定

Modbus RTU的所有数据包均遵从如下基本格式：

| 地址域   | 功能码   | 数据域  | CRC差错校验 |
| ----- | ----- | ---- | ------- |
| 1Byte | 1Byte | 长度不定 | 2Byte   |

在通信模型上：
- Modbus RTU可以分为主站和从站，<font color="#c00000">在一条链路上只能有1个主站</font>，<font color="#c00000">但是可以有多个从站</font>。
- Modbus RTU在<font color="#c00000">任何情况下</font><span style="background:#fff88f"><font color="#c00000">子节点都不会主动发送数据</font></span>，仅当主站请求时，从站才可以发。
- Modbus RTU<font color="#c00000">有广播和单拨两种模式</font>：
	- <font color="#c00000">在广播模式下</font>，所有从站必须执行主站命令而<font color="#c00000">无需应答返回</font>。
	- 在单播模式下，<font color="#c00000">子节点必须做出应答</font>，<font color="#c00000">只有应答完成后主站才可以进行下一个事务处理</font>。
	- 和IP协议类似，<font color="#c00000">广播和单播模式通过地址进行区分</font>。

在数据结构上，Modbus中<u>预先定义了一些数据结构</u>，比如：
- 线圈寄存器( `coils` )：1个bit的<font color="#c00000">读写</font>寄存器，通常表示 `TRUE/FALSE` 、 `ON/OFF` 等。
- 离散输入寄存器( `Discrete Inputs` )：1个bit的<span style="background:#fff88f"><font color="#c00000">只读</font></span>寄存器
- 保持寄存器：16个bit的<font color="#c00000">读写</font>寄存器
- 输入寄存器：16个bit的<span style="background:#fff88f"><font color="#c00000">只读</font></span>寄存器
为了方便叙述，将上述的16bit称之为 "字" ，即 "word" 。但是要注意并不是所有的CPU平台的 "word" 长度均为16bit。

#### 2.1.2 地址域

| 地址域   | 功能码   | 数据域  | CRC差错校验 |
| ----- | ----- | ---- | ------- |
| 1Byte | 1Byte | 长度不定 | 2Byte   |

而在上述的数据包基本格式中：
- 地址域共计1Byte，被划分为：
	- 地址 $0$ 被划分为广播地址
	- 地址 $[1, 247]$ 被划分为子节点单独地址
	- 地址 $[248, 255]$ 被用作保留地址
	因此：
	- 从机地址范围被定义在 $[1, 247]$ 
	- 保留区可以用于设置特定地址段的广播指令等


#### 2.1.3 PDU协议数据单元

PDU协议数据单元可以分为长度为1Byte的功能码，以及长度不定的数据域。

##### 2.1.3.1 功能码

Modbus功能码用于指定主设备请求从设备执行的特定操作。每个功能码定义了一种操作类型，例如读取数据、写入数据、诊断等。因此接下来将分功能归类讲解Modbus功能码。

###### 2.1.3.1.1 数据读写功能码



相对应的读写功能码列表如下：

| 功能       | 功能码 | 操作类型 | 操作数量  |
| -------- | --- | ---- | ----- |
| 读线圈寄存器   | 01  | 位    | 单个或多个 |
| 读离散线圈寄存器 | 02  | 位    | 单个或多个 |
| 读保持寄存器   | 03  | 字    | 单个或多个 |
| 读输入寄存器   | 04  | 字    | 单个或多个 |
| 写单个线圈寄存器 | 05  | 位    | 单个    |
| 写单个保持寄存器 | 06  | 字    | 单个    |
|          |     |      |       |
| 写多个线圈寄存器 | 0F  | 位    | 多个    |
| 写多个保持寄存器 | 10  | 字    | 多个    |



##### 2.1.3.2 数据域

