---
number headings: auto, first-level 2, max 6, 1.1
---
#机器学习 #CV #YOLO 

## 1 Note

本笔记是主线YOLO的学习笔记，不包含分非主线版本。
参考资料：
- 若干主线YOLO论文
- YOLO目标检测(杨建华 李瑞峰)
本笔记仅用于本人硕士研究方向的学习，故无需保证准确性和严谨性。YOLO v7及以前的主线YOLO模型的学习应当参考 *YOLO目标检测(杨建华李瑞峰)* 而非本笔记。

## 2 目录

```toc
```

## 3 YOLO v1

### 3.1 基础概念

目标检测模型的基本概念有：
- <font color="#9bbb59">FP</font>：False Positive，假正例，即误检
- <font color="#9bbb59">TP</font>：True Positive，真正例
- <font color="#9bbb59">FN</font>：False Negative，假负例，即漏检
- <font color="#9bbb59">真实目标数</font>：记作 $M$ ，$M=FN+TP$
- <font color="#9bbb59">预测目标数</font>：记作 $N$ ，$N=TP+FP$
- <font color="#9bbb59">召回率</font>：又叫查全率，记作Recall
	- $Recall=\displaystyle \frac{TP}{M}$
- <font color="#9bbb59">漏检率</font>：记作MissRate
	- $MissRate=\displaystyle \frac{TP}{N}$
- <font color="#9bbb59">精度</font>：Precision
	- $Precision=\displaystyle \frac{TP}{N}$
- <font color="#9bbb59">交并比</font>：IoU，假设A、B两个框位置关系如下：
	- ![[Pasted image 20250306200752.png]]
	- 则：
		- $IoU(A, B)=\displaystyle \frac{|A\cap B|}{|A \cup B|}, IoU\in [0, 1]$
- $F_1$ 分数： $F_1-Score$
	- $F_1-Score=(\displaystyle \frac{Recall^{-1}+Precision^{-1}}{2})^{-1}$
- <font color="#9bbb59">平均精准度</font>： $AP$，同一模型的 $Precision$ - $Recall$ 曲线与坐标轴围成的面积。
	- ![[Pasted image 20250306201232.png]]
	- $AP=\displaystyle \int^{1}_{0}{Precision(r)dr}$
- <font color="#9bbb59">平均精度均值</font>： $mAP$。
	- $mAP=\displaystyle \sum^{n}_{k=1}{AP_k}$

### 3.2 主要改进

### 3.3 Backbone

YOLO v1的主干网络是普通CNN网络，各层信息如下表所示：

| Layer       | Input                    | Layer_info      | Output                   |
| ----------- | ------------------------ | --------------- | ------------------------ |
| Input       |                          |                 | $448\times 448\times 3$  |
| Conv 1      | $448\times 448\times 3$  | k=7x7, stride=2 | $224\times 224\times 64$ |
| Max_Pooling | $224\times 224\times 64$ | k=7x7, stride=2 | $112\times 112\times 64$ |
| Conv 2      | $112\times 112\times 64$ |                 |                          |
|             |                          |                 |                          |
|             |                          |                 |                          |
|             |                          |                 |                          |
|             |                          |                 |                          |
| Conv        |                          |                 | $7\times 7\times 1024$   |

最终的输出是1024个通道的 $7\times 7$ 的特征图。

### 3.4 Head

#### 3.4.1 Head基本结构及输出

YOLO v1的Head使用的是全连接网络，其网络结构如下：

| Layer | Input                  | Output                                                                        |
| ----- | ---------------------- | ----------------------------------------------------------------------------- |
| FC 1  | $7\times 7\times 1024$ | $4096\times 1$                                                                |
| FC 2  | $4096\times 1$         | $S\times S\times (B\times 5+C)$ <br>VOC数据集中为 $7\times 7\times (2\times 5+20)$ |
其中：
- $S$ ：图像被划分的网格数，默认为7。
- $B$ ：每个网格预测的Box数量，被设置为2。
	- 存储<font color="#c00000">Box位置大小信息</font>，以及<font color="#c00000">Box存在概率</font>，即 $[x, y, w, h, prob]$ 。因此B的系数为5。
- $C$ ：预测任务的种类数，VOC数据集中为20。
	- <font color="#c00000">存储每个类别的概率</font>

根据Head的Output定义，其可以理解为：
	![[Pasted image 20250326193709.png]]
- Head使用了两层全连接将7x7x1024的特征图转化为了7x7x30的"特征图"，如下：
	![[Pasted image 20250310184415.png]]
- 也可以理解为分别使用全连接输出到类别和bounding box：
	![[Pasted image 20250311183521.png]]

#### 3.4.2 后处理(非极大值抑制，nms)


### 3.5 缺陷

YOLO v1的主要问题有：
1. 由于YOLOv1每个网格的检测框只有2个，对于密集型目标检测和小物体检测都不能很好适用。
2. 进行推理时，当同一类物体出现的不常见的长宽比时泛化能力偏弱。
3. 由于损失函数的问题，定位误差是影响检测效果的主要原因，尤其是大小物体的处理上，还有待加强。

## 4 YOLO v2

### 4.1 Head

#### 4.1.1 anchor的引入



#### 4.1.2 anchor初始化

anchor的确定主要有如下三种方式：
1. 人为经验选取
2. k-means聚类
3. 作为超参数学习

在YOLO v2中，anchor的选取会根据数据集进行k-means进行聚类。

明显地，anchor数量越多，定位精度越高，最终作者选定k=5进行聚类。
	![[Pasted image 20250310204250.png]]

#### 4.1.3 anchor box与bounding box

在YOLO v1中，Bounding box的输出是直接由神经网络输出的 $[x, y, w, h]$ 四个参数进行确定。
而在引入了anchor box的YOLO v2中，Bouding box的确定变成了 $[t_x, t_y, t_w, t_h, t_o]$ 五个参数，其到Bounding box之间的关系为：
- $Sigmoid(t_x)=\Delta x$，为Bounding box中心距离Grid cell左上角的距离，值域 $[0, 1]$
- $Sigmoid(t_y)=\Delta y$
- $\displaystyle e^{\displaystyle t_w}=k_w$，为相对anchor box宽度的倍数
- $\displaystyle e^{\displaystyle t_h}=k_h$
则具体的Bounding box换算规则如下图所示：
	![[Pasted image 20250311185133.png]]

#### 4.1.4 Head结构

在YOLO v2中，Head接收的特征图尺寸为 $13\times 13\times 1024$ ，其每个grid cell设置了k=5个anchor，则共计会检出 $13\times 13\times 5=845$ 个检测框，$Recall$ 相比YOLO v1大幅提升。

其中，在Bounding Box的回归上，不再使用YOLO v1的直接回归，而是与预测检测框(anchor框)的偏差进行回归，并且每个网络制定n个anchor box，且在训练时只有最接近ground truth的检测框进行损失的计算

#TODO

### 4.2 Backbone

YOLO v2的主干网络被切换为Darknet-19：
	![[Pasted image 20250310183902.png]]
注：
- 上图Darknet-19的：
	- 输入尺寸为 $224\times 224$ 
	- 输出尺寸为 $7\times 7$
	但是在YOLO v2的Backbone中：
	- 输入为 $416\times 416$
	- 输出尺寸为 $13\times 13$

相比于YOLO v1的类似于GoogLeNet的Backbone，Darknet的主要改进为：
1. 为每一个卷积层添加[[YOLO#^frk3ft|批量归一化(BN)]]。
2. 替换全连接层为BatchNormalization+1x1的Conv，需要注意：
	- 1x1 Conv参数设置：
		- 输入张量为 `[1, 1, input_channels]`
		- 输出张量为 `[1, 1, output_channels]`
		- 输入输出特征图均为 $1\times 1$
	- 性能对比可见[[BN_Conv与FCN性能对比]]。




### 4.3 其他改进点

#### 4.3.1 批量归一化(Batch Normalization，BN) ^frk3ft


#### 4.3.2 降采样

![[Pasted image 20250326195338.png]]
![[2025_3_26.jpg]]



## 5 YOLO v8

### 5.1 网络总体结构

![[Pasted image 20250329224715.png]]

记输入图像尺寸为 $(w, h)$ ，则其Neck传递给Head的Tensor及其尺寸、<font color="#c00000">下采样倍率</font>分别为： ^v0lzhq
- Tensor(batch, 192, h/8, w/8)，下采样8倍
- Tensor(batch, 192, h/16, w/16)，下采样16倍
- Tensor(batch, 192, h/32, w/32)，下采样32倍

### 5.2 Head

#### 5.2.1 Distribution Focal Loss

![[chrome_mNpFBgaj14.png]]

在以往的模型中，检测框的坐标通常被认为是一个确定的值，概率仅分布在一个点上。该概率分布为狄拉克分布(Dirac分布)，其数学表示为：
$$
\begin{equation}
\varphi(x)=\left\{
    \begin{array}{lr}
	0&, x\neq x_0, \\
	+\infty&, x=x_0  
    \end{array}
\right.
\end{equation}
$$
$$
\int_{-\infty}^{+\infty}{\varphi(x)}dx=1
$$
而在复杂场景中，边界往往难以精确给出，例如如下两个例子：
![[chrome_p00Lh2rL0S.png]]
![[chrome_UqLOn0s4ga.png]]
注：
- 上述概率分布为网络输出，而非实际概率。
- 上述<font color="#6425d0">紫色箭头所匹配的边界和概率分布</font>为明确边界及其概率分布，<font color="#c00000">红色箭头所匹配的边界和概率分布</font>为模糊边界及其概率分布

而在YOLO v8中，每个Bounding box包含 $(Left, Top, Right, Button)$ 信息的向量，切针对L、T、R、B中的每个值，网络都会输出 $reg\_max$ 个值，并使用 $Softmax$ 计算每个值对应的概率，最终对离散值及其概率进行累加得预测结果：
	![[chrome_9g0W2nHoap.png]]
在YOLO v8中，$reg\_max$ 的默认值为16。明显地，该向量解码后的值域为 $[0, 15]$ ，<font color="#c00000">直接使用时无法覆盖到足够大的目标</font>。而YOLO v8的解决方法是：
$$LTBR预测值=DFL预测值\times 下采样倍数$$
其中：
- [[YOLO#^v0lzhq|下采样倍数]]指从输入图像开始，到传入Head的特征图为止的下采样倍数。
需要注意：
1. 当待检测物体的<font color="#c00000">二分之一宽度或高度</font>接近或超过 $32\times 15=480$ 时，<span style="background:#fff88f"><font color="#c00000">需要增加</font></span> $reg\_max$ <span style="background:#fff88f"><font color="#c00000">的值</font></span>。

而Distribution Focal Loss本质是一个损失函数，其基于交叉熵来定义。

#### 5.2.2 Grid cell输出

YOLO v8使用了三个尺度的特征图(80x80、40x40、20x20)，这些特征图上的<font color="#c00000">每个Grid cell会预测输出一个Bounding box</font>，其每个Grid cell输出尺寸为：
$$
4\times reg\_max+1+Classes
$$
其定义如下：
- Bounding box：$4\times reg\_max$
	- Left：网络输出 $reg\_max$ 个Left的预测值，并计算期望值作为边框左侧的输出。
	- Top
	- Right
	- Button
- 含物体概率：表示该box含有物体的概率，使用 $Sigmoid$ 激活
- 类别概率：每个类别一个值，使用 $Sigmoid$ 激活

即：
- 在 $640\times 640$ 输入时(即默认情况)，YOLO v8会输出 $80\times 80+40\times 40+20\times 20=8400$ 个预测框。
- 在 $w\times h; w, h=k\times 32$ 时，YOLO v8会输出 $(4k)^2+(2k)^2+k^2=21k^2$ 个预测框。

#### 5.2.3 Head基本结构 ^2jvvoq

YOLO v8 Head基本结构及部分细节应当参照下图，Obsidian可能无法正常渲染该图，可能需要单独查看[[YOLO v8 Head结构.svg]]：
![[YOLO v8 Head结构.svg]]
