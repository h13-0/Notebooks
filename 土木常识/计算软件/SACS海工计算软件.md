#土木常识 

## 目录
```toc

```

## 一、SACS的一般建模流程

0. 设置模型单位及坐标原点
1. 建立点、线、面几何模型
2. 设置单元及板的Group、Section属性
3. 各单元及板偏移设置
4. 修正各杆件有效长度
5. 施加设备及附属构件荷载
6. 荷载工况组合
7. 强度分析选项设定
8. 校核重量重心，校对模型

### 1.0 设置模型单位及坐标原点

![[Pasted image 20230415211359.png]]
本处设置的是软件全局的单位，通常只用设置一次即可。
对于非第一次使用本软件，直接从步骤1开始即可。

### 1.1 建立点、线、面几何模型

对于复杂结构，如：
- 导管架基础
- 吸力筒导管架基础
推荐采用建模器中导向功能进行建模

对于简单结构，如：
- 单桩基础
- 高桩承台基础
- 三脚架基础
可以自行创建点，由点连线，由线构面的方式创建模型

#### 1.1.1 创建模型

在创建之前最好手动切换到工作目录下：
![[Pasted image 20230415224737.png]]
手动切换到工作目录即可。

创建模型：
![[Pasted image 20230415220610.png]]
另外两个选项就是字面意思。

然后会出现是手动设置模型(第一个)还是由向导设置(第二个)。
![[Pasted image 20230415212234.png]]

#### 1.1.2 设置导管架基础的各项高程
这里以向导设置为例，第一个label是设置高程的界面：
![[Pasted image 20230415212714.png]]

从上到下分别为：

| 参数          | 含义                                    |
| ------------- | -------------------------------------- |
| Working poing | 桩顶高程，通常对桩顶处理后和上部结构进行连接 |
| Pile connecting | 为桩和主腿连接的标高，工艺流程通常为先打桩，然后通过灌浆将桩和主腿相连接 |
| Water depth | 静水面水深，为水面到泥面线之间的距离。在SACS中，Z轴坐标原点是以平均海平面为基准 |
| Mudline | 泥面线高程，通常为负的水深 |
| Other Elevation | 其他水平平面标高，可以为塔身各个分段的关键标高 |

#### 1.1.3 导管架基础主腿设置

首先先再 `Number of` 中设置主腿数量：
![[Pasted image 20230415214907.png]]

对于四角腿：

可以选则是以 `Workpoint` 和四条主腿的斜度来定义主腿
`Row Labels` 中可以设定主腿的行列编号(参考右图)
![[Pasted image 20230415215100.png]]

`Leg type` 中可设置主腿和桩之间的连接方式，为灌浆和非灌浆：
![[Pasted image 20230415215349.png]]

点击 `Leg Spacing at Working Point` 定义四腿之间的间距(以顶端为准)：
![[Pasted image 20230415215820.png]]

此时得到的坐标为此平面的几何中心：
![[Pasted image 20230415215837.png]]

定义四条主腿斜度：
$$
\begin{aligned}斜度=\frac{1}{tan(\theta)}\end{aligned}
$$

对于三角腿：



此时点击 `OK` 即可进入模型界面。

如果此时需要修改引导中的参数，可以点击左上角
![[Pasted image 20230416095810.png]]
再次进入引导即可。

#### 1.1.4 界面控件

##### 1.1.4.1 基础功能区

![[Pasted image 20230415221410.png]]
![[Pasted image 20230415221349.png]]
从左至右依次为：

![[Pasted image 20230415221818.png]]
`新建文件` | `打开模型` `保存` `另存为` `复制选定区域到剪切板` `打印`

![[Pasted image 20230415221844.png]]
`重新绘制界面` `用鼠标滚轮放大缩小` `平移` `持续旋转` `旋转` `选区放大`

![[Pasted image 20230415221917.png]]
`缩放至填充视图` `切换为实体图` `全选视图内所有元素` | `生成报告` | `撤销` `重做` `关闭所有对话框(比如前面的报告)`

关于 `切换至实体图` 按钮效果：
![[Pasted image 20230416121342.png]]
![[Pasted image 20230416121334.png]] ^bm8l64



##### 1.1.4.2 视角操作区
![[Pasted image 20230415223329.png]]

![[Pasted image 20230415222223.png]]
`几个视图按钮` | `切换为等轴视图(通常用于立面切换为立体图)`


##### 1.1.4.3 标签显示
![[Pasted image 20230415223533.png]]

![[Pasted image 20230415222556.png]]
`显示点线面ID的按钮x3` `开关局部坐标系` | | `字号设置`

##### 1.1.4.4 构件设置
![[Pasted image 20230415223602.png]]

![[Pasted image 20230415222702.png]]
`显示点线面`

##### 1.1.4.5 选取器
![[Pasted image 20230415223615.png]]
![[Pasted image 20230415222731.png]]
`点拾取器` `线拾取器` `选择面` `选择任意构件`

#### 1.1.5 保存模型

点击 `保存` 或 `另存为` 按钮，注意选择：
![[Pasted image 20230415223913.png]]
只保存模型、只保存海况、我全都要。

#### 1.1.6 绘制立面(Face)结构

立面为直立面，一般用于绘制X撑、K撑等。
先选定立面：
`Display` -> `Face`
![[Pasted image 20230415225153.png]]

比如这里选择 `ROW A` 立面：
![[Pasted image 20230415225416.png]]

##### 1.1.6.1 绘制X撑
选择：
	`Member` -> `X Brace`
![[Pasted image 20230415225527.png]]

![[Pasted image 20230415225619.png]]

| 参数 | 含义 |
| --- | --- |
| Center joint | X撑中心点名称 |
| End joint of thru member | 未被打断杆件的起始点**(可在UI中单击选定点)** |
| Other end of thru member | 未被打断杆件的终止点 |
| End ... of non-thru ... | 被打断杆件的起始点 |
| Other ... of non-thru ... | 被打断杆件的终止点 |
| Group of thru member | 未被打断杆件的组(用于定义材料等) |
| ... of non-thru ... | 被打断杆件的组 |


例如我们要建下图：
![[Pasted image 20230415230141.png]]

未被打断杆件为右上到左下
被打断杆件为左上到右下

则如下选择：
![[Pasted image 20230415230642.png]]

建模结果如下：
![[Pasted image 20230415230731.png]]

点击 `Display Active/Isometric` 按钮即可回立体图
![[Pasted image 20230415231041.png]]

#### 1.1.6 绘制水平撑(Plan)结构

`Display` -> `Plan`
![[Pasted image 20230415231305.png]]

选择指定高程平面(比如这里选定的是-79.5m的泥面线)
![[Pasted image 20230415231422.png]]

例如以建立下图为例
![[Pasted image 20230415231730.png]]

手动添加杆件：
`Member` -> `Add`
![[Pasted image 20230415232058.png]]

![[Pasted image 20230416094623.png]]
其中 `Add immediately` 勾选后不用每次点击 `Apply` 了

建框、分组(略)：
![[Pasted image 20230415232255.png]]

然后要取断点：
`Member` -> `Divide`
![[Pasted image 20230415232425.png]]
从上到下依次为：

| 按钮 | 含义 |
| --- | --- |
| Ratio | 按比例分段 |
| Length | 按长度分段 |
|Z/Y/X Coordinate | 按坐标打断 |
| Equal Parts | 选择分成几份 |
| Perpendicular | 选择一点一线，做垂线打断 |
| Intersection | 交叉打断 |
| Existing Joint | 在存在的点的位置打断 |

Equal Parts：
![[Pasted image 20230416093827.png]]
上面两个框为选择两个点，在点中均分打断。
也可以直接选择直线进行打断

Length：
![[Pasted image 20230416094135.png]]
以某方向，一定长度打断单元

Perpendicular：
![[Pasted image 20230416094427.png]]
选择点和线即可做垂线打断

#### 1.1.7 上部组块建模

![[Pasted image 20230416111357.png]]
点击 `Add/Edit Deck Girder Data` 选择高程
![[Pasted image 20230416111545.png]]
下面的 `Add DKG` 等是是否需要生成图中所示结构。
剩下的细节设置同[[#1.1.6 绘制水平撑(Plan)结构]]，如果想要只显示上部组块，可以点击：
`Display` -> `Volumes` 设置显示区域：
![[Pasted image 20230416192020.png]]

![[Pasted image 20230416192056.png]]
在这里限制Z显示区域的最低值为上部组块的最低值即可：
![[Pasted image 20230416192123.png]]

### 1.2 添加板单元

`Plate` -> `Add`
![[Pasted image 20230416193914.png]]

![[Pasted image 20230416193954.png]]
类型中配置是三角形还是四边形，然后选择顶点配置Group即可。
效果：
![[Pasted image 20230416194056.png]]

### 1.3 设置单元及板的Group、Section属性

在前面章节中，已经对各个杆件设置了Group，接下来统一设置每个Group的弹性模量、密度、壁厚等属性即可。

#### 1.3.1 设置杆件属性
`Property` -> `Member Group`
![[Pasted image 20230416113320.png]]

![[Pasted image 20230416113536.png]]
`Undefined Groups` 中为未定义的组，选中后点击 `Add` 即可。

![[Pasted image 20230416114440.png]]

`Group type` 中
![[Pasted image 20230416114628.png]]

| 选项 | 含义 |
| --- | --- |
| General | 标准型材 |
| Tubular(OD&WT) | 圆管，通过外直径和壁厚定义 |
| Tubular()

##### 1.3.1.1 型钢库
单击小三角：
![[Pasted image 20230416192505.png]]

进入型材库：
![[Pasted image 20230416192531.png]]

可以筛选型钢类型：
![[Pasted image 20230416192604.png]]

| 类型 | 含义 |
| --- | --- |
| Tubular | 圆管 |
| Wide Flange | |
| Compact Wide Flange | 工字钢 |

![[Pasted image 20230416192823.png]]
选中后可以看到工字钢的参数是否正确，也可以选定后在 `Edit` 中具体配置截面：
![[Pasted image 20230416192916.png]]

也可以在这个中间更改截面类型：
![[Pasted image 20230416193353.png]]


##### 1.3.1.2 配置圆管
这里先选择 `Tubular(OD&WT)` ：
![[Pasted image 20230416115314.png]]

| 基本参数(需要注意单位和量纲) | 含义 |
| ------ | --- |
| E | 弹性模量 |
| G | 剪切模量 |
| Fy | 屈服强度 |
| Density | 密度 |
| Segment lenght | 分段长度，一般填写加厚段长度 |
| Flooded member | 是否受到水流冲击 |

如果圆管需要分段(如需要分为加厚段+普通段)，则需要从杆件的Joint A依次增加分段以确定分段顺序。一般需要多个定义了 `Segment length` 的段+一个未定义的段即可完全定义一根杆件。

在该窗口的 `Segment` 的 group box 中即可选定和查看各段信息。
![[Pasted image 20230416121036.png]]

设置完成后，点击 `切换至实体图` 按钮即可预览效果
![[SACS海工计算软件#^bm8l64]]

若想修改现存构件的Group，点击 `Member` -> `Member Properties` 然后选中编辑即可
![[Pasted image 20230416185640.png]]

按需设计即可得图纸：
![[Pasted image 20230416193536.png]]

#### 1.3.2 设置板件

`Property` -> `Plate Group`
![[Pasted image 20230416194225.png]]

然后在对话框中直接设置即可：
![[Pasted image 20230416194415.png]]
![[Pasted image 20230416194359.png]]

在这一步完成后，该模型可以称作为未修正的几何模型，通常还需要在其上进行偏移、关节点有效长度(由于压杆稳定等)设置等。

### 1.4 各单元及板偏移设置

比如规范中规定的安装间距，以及实际安装方法等。

#### 1.4.1 偏移各杆件
`Joint` -> `Automatic Design`
![[Pasted image 20230416204814.png]]

![[Pasted image 20230416204852.png]]

`Part of structure to include` 为需要做offset的节点的范围
![[Pasted image 20230417111022.png]]
`Active` 为当前所显示的节点
`All` 为全部节点
`Include select joints` 、 `Exclude selected joints` 字面意思

`Offset braces to outside of chord` 为将撑杆偏移到竹竿外侧，一般勾选

此时会有三个选项：
![[Pasted image 20230417112751.png]]

| 选项 | 含义 |
| --- | --- |
| None | 不作操作 |
| Move brace | 移动撑杆以满足间距要求 |
| Increase chord | 增加主杆直径以满足要求 |

![[Pasted image 20230417113027.png]]

一般选择移动撑杆。
![[Pasted image 20230417113425.png]]
`Gap` 按规范设定即可。

![[Pasted image 20230417113509.png]]
Tab `Can/Chord` 主要对加厚段长度进行设置
`Update segmented groups can lengths` 更新各分段加厚段长度，勾选
`Increase joint can lengths only` 为只增加不减少加厚段长度，勾选

设置完 `Apply` 即可
![[Pasted image 20230417114011.png]]
![[Pasted image 20230417114030.png]]

此时再点击对应杆件的加厚段长度，会发现已经被更改且不是整数
![[Pasted image 20230417114337.png]]
在实际工程中向上取整即可。

#### 1.4.2 偏移工字钢

软件自动生成的工字钢，其设计高程是和其中心重合的。
但是实际工程中通常是将翼缘高程安装到设计高程。
所以需要将上翼缘偏移到设计高程。
![[Pasted image 20230417114848.png]]

先 `Display` -> `Plan` 选择要操作的层

添加Offset：
`Member` -> `Offsets`
![[Pasted image 20230417154012.png]]

点击 `Screen` 即可选中屏幕中所有构件，按住 `Ctrl` 可以选中或取消选中。
在 `Offset type` 中可以选定偏移类型：
![[Pasted image 20230417154547.png]]

| 选项 | 含义 |
| --- | --- |
| Global | 整体坐标系 |
| Local | 杆件局部坐标系 |
| Top of steel | 钢材顶点 |

一般选定钢材定点和设计高度对齐，选中 `Top of steel` 然后 `Apply` 即可。
此时即可对齐：
![[Pasted image 20230417154835.png]]

#### 1.4.3 梁柱节点偏移设置

在经过上一章节的设置之后，上翼缘已经和设计平面重合。
但是此时型钢仍然是插在管件中的，如图所示：
![[Pasted image 20230417155333.png]]

`Member` -> `Offsets` 选中要操作的杆件，此时可以看到我们杆件两端是有 `Z Offset` 的，是上一步的上翼缘偏移的结果。
![[Pasted image 20230417155506.png]]

此时若点击 `Joint A` 的文本框使其激活，则会发现右侧 `Joint A` 处多了一个小红圈
![[Pasted image 20230417155613.png]]
然后手动偏移圆管半径即可。
![[Pasted image 20230417155843.png]]

#### 1.4.4 板单元偏移设置

例如防沉板实际上应该是在主结构下部，但是软件设计时是设计到最下层的管轴线上的。
`Plate` -> `Offsets`
按住 `Ctrl` 多选，然后 `Offset type` 选择 `Global`
由于是三角板，故需要同时设置三个节点的偏移：
![[Pasted image 20230417160825.png]]

`Apply` 即可
![[Pasted image 20230417160904.png]]

也可以在 `Plate` -> `Plate Properties` 中对Group集体设置偏移量
![[Pasted image 20230417160951.png]]

#### 1.4.5 斜拉筋节点偏移设置

`Member` -> `Offsets` 里面直接按需求设置


### 1.5 修正各杆件的有效长度

在SACS中，每个杆件都有其局部坐标系，其 `x轴` 指向杆件末端， `z轴` 为垂直于 `x轴` 的平面中与整体坐标系的 `z轴` 最为接近的方向(也就是尽可能的朝上，和整体系的 `z轴` 平行)，然后由右手螺旋法则确定 `y轴` 。
此时杆件可能会沿 `y轴` 和 `z轴` 弯曲失稳，故需要做两个方向的有效长度修正

可以点击该按钮开关局部坐标系显示：
![[Pasted image 20230417172221.png]]

#### 1.5.1 操作步骤

在进行本操作之前需要先设置各个杆件的 `Offset`
`Property` -> `K Factor` 中可以进行有效长度的修正
![[Pasted image 20230417172349.png]]

然后分别点击 `Ky` 、 `Kz` 进行修正。
![[Pasted image 20230417172507.png]]
`Frist joint` 和 `Second joint` 中选定两个点来选取杆件的两个端点(不知道是干什么的)
然后点击选取杆件。
然后在 `Kz` 中指定系数。
然后在 `Member` -> `Member Properties` 中就可以查看设置好的系数
![[Pasted image 20230417172929.png]]

到此为止，可以称当前模型为已修正的几何模型。

### 1.6 施加载荷

在实际工程中，比如电气设备等的载荷在软件中模拟较为麻烦，直接改为载荷即可。

在 `SACS` 中，荷载可以分为：
1. Surface Weight
2. Footprint Weight
3. Member Weight
4. Joint Weight
上述荷载均为非结构荷载，即排除自重的额外荷载。

#### 1.6.1 Surface荷载

##### 1.6.1.1 定义Surface
施加荷载必须先定义 `Surface` ,
`Weight` -> `Surface Definition`
![[Pasted image 20230418194152.png]]
然后赋 `Surface ID` ，选三个点，注意：
`1st Joint` 为 `Surface` 局部坐标系的原点
`2nd Joint` 为 `Surface` 局部坐标系的 `x轴` 方向
`3rd Joint` 为 `Surface` 局部坐标系的 `y轴` 方向

`Tolerance` 为容许误差，不知道是干什么的反正尽量填大一点
`Load distribution` 为荷载分布沿单元的方向，没看懂，应该是分布在沿 `x轴` 还是 `y轴` 方向的单元上？
`Boundary joints` 为 `Surface` 的边界，边界内均有荷载，一般选外边界，按 `Ctrl` 多选即可。

##### 1.6.1.2 Surface上定义荷载

`Weight` -> `Surface Weight`
![[Pasted image 20230418195733.png]]
然后填写 `Weight group` 、 `Weight ID` 、 `Pressure` 、 `Density` 等，将左侧 `Defined Surface IDs` 中的组添加到右侧 `Included Surface IDs` ， `Apply` 即可。

**若要分别定义多组Surface，<font color = 'red'><b>在 `Apply` 后取消选中设置好的 `Surface` 后</b></font>，再走一遍流程就行**

建议将同一个平面的多种不同荷载多次分别定义，如恒荷载和活荷载要分开定义。

#### 1.6.2 Footprint荷载

`Weight` -> `Footprint Weight`
![[Pasted image 20230418201100.png]]
注意 `Footprint Center` 是以 `SACS` 坐标系为准的坐标<font color = 'red'>(么?视频里原点是该截面的四条主腿的几何中心啊?)</font>。
`Weight Loaction` 为 `Footprint Weight` 的重心，例如对于方块型设备，其重心高度上通常为其本身高度的一般，故 `Footprint Weight` -> `Z` 填写二分之一高度即可。

![[Pasted image 20230418202244.png]]
`Footprint type` 为荷载受力施加于结构的类型，

| 选项 | 含义 |
| --- | --- |
| Skid | 分布到梁交叉节点上 |
| Area | 为分布到面内所有的梁上 |

通常选 `Skid` 。

然后 `Footprint Size` 为荷载施加的长和宽
![[Pasted image 20230418202308.png]]

然后设置分布数量，填2和2即可：
![[Pasted image 20230418202659.png]]

然后弹出 `Sum` 窗口，检查后 `Keep` 即可。
![[Pasted image 20230418202638.png]]

#### 1.6.3 添加线载荷

比如人行走道，栏杆等可以以线载荷的方式施加。

`Weight` -> `Member Weight`
![[Pasted image 20230418205031.png]]
然后按住 `Ctrl` 多选即可，然后赋 `Weight group` 和 `Weight ID` ，然后在 `Weight category` 中选择是分布于整个杆件上还是集中于杆件一点(通常为分布型)

##### 1.6.3.1 分布型
![[Pasted image 20230418205229.png]]

然后在起点和重点设置线载荷大小：
![[Pasted image 20230418205326.png]]

`Apply` -> `Keep` 即可。
![[Pasted image 20230418205409.png]]

##### 1.6.3.2 集中型

![[Pasted image 20230418210325.png]]

| 参数 | 含义 |
| --- | --- |
| `Concentrated weight` | 集中力大小 |
| `Distance to concentrated weight` | 集中点距杆件起始点的距离 |
| `Include buoyancy and wave load` | 是否考虑浮力和波浪载荷，要看波浪是否可以冲击到 |
| `Density` | 在考虑浮力时，填入密度，通过荷载反推体积来算浮力 |

其中，有些结构需要平放运输，直立安装后再安装设备，故通常设备等载荷不勾选 `Include buoyancy and wave load` ， 但是吊点(pad eye)等需要勾选。

`Distance to concentrated weight` 为 `0m` 时
![[Pasted image 20230418210314.png]]

`Distance to concentrated weight` 为 `1.5m` 时(此时杆件长为3m)
![[Pasted image 20230418210200.png]]


#### 1.6.4 添加点载荷

比如吊机、吊点(pad eye)等可以以点载荷方式施加。
`Weight` -> `Joint Weight`
![[Pasted image 20230418205734.png]]

选点，赋 `Group` 、 `ID` ，赋值， `Apply` -> `Keep` 即可。
![[Pasted image 20230418205700.png]]

#### 1.6.5 阳极块(Anode)载荷配置

`Weight` -> `Anode Weight`
![[Pasted image 20230418211611.png]]

| 参数 | 含义 |
| --- | --- |
| Anode weight | 单个阳极块重量 |
| anodes per | 每个杆件上有几个阳极块 |
| Include buoyancy and wave load | 是否考虑阳极块浮力和波浪载荷 |
| Density | 同1.6.4 |

然后多选单元， `Apply`
![[Pasted image 20230418212027.png]]

### 1.7 将Weight转为Load

章节1.6中只是定义了Weight，在计算时需要将Weight转化为Load

先在 `Weight` -> `Center of roll` 中定义一个旋转中心，一般定义为坐标原点(相当于SACS是以考虑整体运动来计算运动和静止两种情况下的荷载，下面加速度只在z轴设置了一个1.0G就是只考虑静止时的荷载)
![[Pasted image 20230418213841.png]]

然后去 `Environment` -> `Weight` 中，勾选 `Include Weight group` 和 `Acceleration` 。

在 `Acceleration` 中的Z中填写 `1.0` 即可，不要忘记填写 `Center ID` 。
![[Pasted image 20230418214321.png]]
`Do NOT include sturctural weight for this acceleration` 为只考虑额外荷载而不考虑结构本身，一般勾选。

然后在 `Include Weight group` 中勾选所需要包含的Group
![[Pasted image 20230418214553.png]]
`Apply`

然后在

### 1.8 环境荷载

比如风浪流、海生物吸附等。

#### 1.8.1 定义Cd、Cm
`Environment` -> `Drag/Mass Coefficient` 配置 `Cd` 、 `Cm` 系数
![[Pasted image 20230419114929.png]]
`Table type` 选用户自定义( `User defined` )
Label `Clean` 为光滑结构， `Fouled` 为海生物附着后的粗糙结构，
取消勾选 `Use clean values for fouled members` 即可设置粗糙结构

#### 1.8.2 定义海生物

##### 1.8.2.1 统一定义
`Environment` -> `Marine Growth`
![[Pasted image 20230419115821.png]]
`Mudline elevation override` 可以重定义泥面高度，一般填写泥面高度即可
列 `Bottom` 、 `Top` 定义范围，高程从泥面开始计算， `Thickness` 为海生物厚度

示例如下：
![[Pasted image 20230419120234.png]]

##### 1.8.2.2 单独修正单一杆件的海生物荷载
比如可以单独修正某一条主腿的海生物荷载
`Environment` -> `Member Group` -> `Global`
![[Pasted image 20230419144632.png]]
多选左侧 `Groups With No Overrides` ，然后在 `Coefficients` 输入Cd Cm即可
![[Pasted image 20230419144912.png]]


### 1.9 风浪流载荷

`Environment` -> `Seastate`
![[Pasted image 20230419145712.png]]
注意是 `Loading` 里面的 `Seastate`
![[Pasted image 20230419145806.png]]
赋名荷载条件 `Load condition`

需要定义哪几种载荷就要勾选哪几个
![[Pasted image 20230419145837.png]]

#### 1.9.1 定义波浪载荷(Wave)

勾选 `Wave`
![[Pasted image 20230419145927.png]]
在Tab `Wave I` 中的 `Wave type` 中有如下图所示类型的波浪(主要是选择波浪理论)
![[Pasted image 20230419150017.png]]

| 选项 | 含义 |
| --- | --- |
| Airy | 艾里波 |
| Stokes | 斯托克斯波 |
| Steam | 流函数 |
| Cnoidal | 椭圆余弦波 |
~~后面的我也看不懂了..~~

然后输入波浪要素即可。

Tab `Wave II` 中设置多少个相位角计算一次载荷，因为每个相位角对结构的力是不一样的。
在 `Critical position` 中选择最大基地剪应力 `Max base shear` 为指标
然后选择是否需要覆盖原来的水深和泥面线，在实际工程中通常结合高潮位和低潮位来设置
![[Pasted image 20230419152412.png]]

#### 1.9.2 定义风载荷(Wind)

勾选 `Wind`
![[Pasted image 20230419152606.png]]

一般通过定义风速来计算风载荷，勾选 `Velocity` 填写数值。
`Reference height` 为参考高度，一般默认为 `10m` 
`Wind height variation` 中可以选择对应规范
![[Pasted image 20230419152840.png]]

`Wind (deg)` 角度一般为 `0°`
参考值：
![[Pasted image 20230419153032.png]]

在 `Wind II` 中设置风面( `Wind Area` )，一般用于闭合结构，不设置则默认为杆件受风。

#### 1.9.3 定义流载荷(Current)

勾选 `Current`
![[Pasted image 20230419153523.png]]
在Tab `Curr I` 中的 `Mudline elevation override` 中选择是否需要重新定义泥面线
然后在 `Current Table` 中定义流速， `Distance` 为泥面线开始向上
![[Pasted image 20230419153753.png]]
定义两层然后软件就会算出中间的流速(怀疑默认均匀分布)
![[Pasted image 20230419154002.png]]

在Tab `Curr II` 中 `Blocking factor option` 为遮蔽系数，即水流前方构件对水流后方构件的水流遮蔽作用
![[Pasted image 20230419154201.png]]

#### 1.9.4 定义浮力(Dead load)

勾选 `Dead load`
![[Pasted image 20230419154301.png]]
![[Pasted image 20230419154324.png]]
`Buoyancy method` 为浮力的计算方法
![[Pasted image 20230419154417.png]]

`Direction of gravity` 为重力的计算方向
`Include the buoyance below the mudline` 为是否要包括泥面以下的浮力

### 1.10 荷载工况组合

`Load` -> `Combine`
![[Pasted image 20230419161158.png]]

定义组合名，添加载荷，设置系数即可。
![[Pasted image 20230419161150.png]]

#### 1.11 分析选项设置

`Option` -> `Load Condition Selection`

