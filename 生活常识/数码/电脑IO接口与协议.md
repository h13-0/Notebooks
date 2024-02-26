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

|  插槽型号   |   卡口引脚范围    | <center>标准长度</center>          | <center>支持协议</center>                                    |
| :-----: | :---------: | :----------------------------- | :------------------------------------------------------- |
|  A Key  |    8-15     | 1630、2230、3030                 | 两个PCIe x 1、USB 2.0、I2C、DP x4                             |
|  B Key  |    12-19    | 3042、2230、2242、2260、2280、22110 | SATA、PCIe x2、USB2.0、USB3.0、audio、UIM、HSIC、SSIC、I2C、SMBus |
|  E Key  |    24-31    | 1630、2230、3030                 | 两个PCIe x 1、USB 2.0、I2C、SDIO、UART、PCM、CNVi                |
|  M Key  |    59-66    | 2242、2260、2280、22110           | PCIe x4、SATA、SMBus                                       |
| A+E Key | 8-15、24-31  |                                | 两个PCIe x 1、USB 2.0、CNVi                                  |
| B+M Key | 12-19、59-66 |                                | PCIe x2、SATA、SMBus                                       |
|  F Key  |    28-35    |                                | 未来的内存接口(FMI, Future Memory Interface)                    |
|  G Key  |    39-46    |                                | 用户自定义协议，NGFF协议中未规定                                       |
|  C Key  |    16-23    |                                | Reserved                                                 |
|  D Key  |    20-27    |                                | Reserved                                                 |
|  H Key  |    43-50    |                                | Reserved                                                 |
|  J Key  |    47-54    |                                | Reserved                                                 |
|  K Key  |    51-58    |                                | Reserved                                                 |
|  L Key  |    55-62    |                                | Reserved                                                 |
注：
- 卡口引脚范围是指PCB和连接器上残缺的引脚位置，如下图所示(PCB的Pin20在背面)
	![[chrome_Oas0fwGQjX.png]]
- 如 `A+E Key` 、 `B+M Key` 的组合是拥有两个卡口区域的PCB，对于 `A+E Key` 的PCB，其可以同时使用 `A Key` 的连接器和 `E Key` 的连接器，示意图如下
	![[Pasted image 20240227005439.png]]

因此各个插槽型号对应的常用应用场景如下：

| 插槽型号  | <center>应用场景</center> |
| :---: | :-------------------- |
| A Key | 无线设备                  |
| B Key | WWAN+GNSS或SSD         |
| E Key | 无线设备                  |
| M Key | SSD                   |
