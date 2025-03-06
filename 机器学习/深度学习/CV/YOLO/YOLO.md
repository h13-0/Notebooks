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

| Layer | Input | Output |
| ----- | ----- | ------ |
|       |       |        |




### 3.4 Head

YOLO v1的Head使用的是全连接网络，


### 3.5 YOLO v2

### 3.6 Head





