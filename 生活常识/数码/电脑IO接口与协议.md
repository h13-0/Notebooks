#生活常识 

## 目录
```toc

```

## 接口





## 协议


### PCIe

全称 `Peripheral Component Interconnect Express` ，官方简称 `PCIe` 。


## 外形规范 (接口的物理外形)

### M.2接口

M.2接口即NGFF接口，即 `Next Generation Form Factor` ，是一种外形尺寸规范



#### 接口分类及规格

|  插槽型号   |   卡口引脚范围    | <center>支持协议</center>                 |
| :-----: | :---------: | :------------------------------------ |
|  A Key  |    8-15     | PCIex2                                |
|  B Key  |    12-19    |                                       |
|  E Key  |    24-31    |                                       |
| A+E Key | 8-15、24-31  |                                       |
|  M Key  |    59-66    |                                       |
| B+M Key | 12-19、59-66 |                                       |
|  F Key  |    28-35    | 未来的内存接口(FMI, Future Memory Interface) |
|  G Key  |    39-46    |                                       |
|  C Key  |    16-23    | Reserved                              |
|  D Key  |    20-27    | Reserved                              |
|  H Key  |             | Reserved                              |
|  J Key  |             | Reserved                              |
|  K Key  |             | Reserved                              |
|  L Key  |             | Reserved                              |
注：
- 卡口引脚范围是指PCB和连接器上残缺的引脚位置，如下图所示(PCB的Pin20在背面)
	![[chrome_Oas0fwGQjX.png]]
- 如 `A+E Key` 、 `B+M Key` 的组合是拥有两个卡口区域的PCB，对于 `A+E Key` 的PCB，其可以同时使用 `A Key` 的连接器和 `E Key` 的连接器，示意图如下：
	![[Pasted image 20240227005439.png]]

