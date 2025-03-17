---
number headings: auto, first-level 2, max 6, 1.1
---
#机器学习 #CV 

## 1 Readme

本文仅探讨一些OCR算法在字符分类上的一些算法。

## 2 目录

```toc
```

## 3 CRNN

论文：[An End-to-End Trainable Neural Network for Image-based Sequence Recognition and Its Application to Scene Text Recognition](https://arxiv.org/abs/1507.05717)。

简单来讲CRNN就是CNN和RNN的结合体，其输入是不定长的文本图像，输出也是不定长的文本输出。其主要依靠RNN完成不定长输出特性。

其大体网络结构如下图所示：
	![[Pasted image 20250317192020.png]]
接下来将从下向上讲解网络每一部分的原理和作用：
1. 卷积部分：
	![[Pasted image 20250317192124.png]]
	这部分网络会将图像横向扫描计算卷积，其感受野被设计为 $width:height=1:4$ 的卷积操作(方便处理英文字母)，且其扫描窗口重叠率为50%。
	其卷积结构如下图所示：
	![[Pasted image 20250317192641.png]]
	在上述卷积操作中，其三次 `MaxPooling` 操作参数分别为(从下向上，格式为 `wxh` )：
	- `Window=2x2` ，将长宽减半
	- `Window=2x2` ，将长宽减半
	- `Window=1x2` ，将高度减半
	- `Window=1x2` ，将高度减半
	最终其每个感受视被转化为 `[Channel, height, width]=[512, 1, 40]` 的特征向量。
