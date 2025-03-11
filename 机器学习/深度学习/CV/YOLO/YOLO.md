---
number headings: auto, first-level 2, max 6, 1.1
---
#机器学习 #CV

## 1 Note

本笔记是主线YOLO的学习笔记，不包含分支版本。

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

#### 4.1.1 Head结构

在YOLO v2中，Head接收的特征图尺寸为 $7\times 7\times 1024$ (与YOLO v1一致)，但是其Head结构变化为：



其中，在Bounding Box的回归上，不再使用YOLO v1的直接回归，而是与预测检测框(anchor框)的偏差进行回归，并且每个网络制定n个anchor box，且在训练时只有最接近ground truth的检测框进行损失的计算

#### 4.1.2 anchor的引入



#### 4.1.3 anchor初始化

anchor的确定主要有如下三种方式：
1. 人为经验选取
2. k-means聚类
3. 作为超参数学习

在YOLO v2中，anchor的选取会根据数据集进行k-means进行聚类。

明显地，anchor数量越多，定位精度越高，最终作者选定k=5进行聚类。
	![[Pasted image 20250310204250.png]]




### 4.2 Backbone

YOLO v2的主干网络被切换为Darknet-19：
	![[Pasted image 20250310183902.png]]
相比于YOLO v1的类似于GoogLeNet的Backbone，Darknet的主要改进为：
1. 为每一个卷积层添加[[YOLO#^frk3ft|批量归一化(BN)]]。
2. 替换全连接为1x1的Conv




### 4.3 其他改进点

#### 4.3.1 批量归一化(Batch Normalization，BN) ^frk3ft





