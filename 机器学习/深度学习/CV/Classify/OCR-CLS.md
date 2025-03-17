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
	- 这部分网络会将图像横向扫描计算卷积，每个扫描窗口 $(w, h)=(8, 32)$ ，即感受野被设计为 $width:height=1:4$ 的卷积操作(方便处理英文字母)，且其扫描窗口重叠率为50%。
	- 需要注意的是：
		- 第一个扫描窗口和最后一个扫描窗口只有一半宽度的图像输入。
		- 假设图像输入宽度为 $(w, h)=(160, 32)$ ，<font color="#c00000">则其扫描窗口数量为40个</font>(实际输入宽度上限不限)。
	- 其卷积结构如下图所示：
		- ![[Pasted image 20250317192641.png]]
	- 在上述卷积操作中，其三次 `MaxPooling` 参数分别为(从下向上，格式为 `wxh` )：
		- `Window=2x2` ，将宽高减半
		- `Window=2x2` ，将宽高减半
		- `Window=1x2` ，将高度减半
		- `Window=1x2` ，将高度减半
	- 最终其<font color="#c00000">每个感受野</font>(即上图蓝框)被转化为 `[Channel, height, width]=[512, 1, 1]` 的特征向量。
	- 而假设：
		- 输入图像 $(w, h)=(160, 32)$ ，则其特征向量为 `[Channel, height, width]=[512, 1, 40]` 
		- 输入图像 $(w, h)=(224, 32)$ ，则其特征向量为 `[Channel, height, width]=[512, 1, 56]` 
2. RNN部分：
	1. 在CRNN中，其使用的RNN网络类型为LSTM：
		1. 由于LSTM是单向的，其只依赖于过去的时间步，必须遵循时间步顺序进行递推。而OCR中字体左右半部及其特征是互相作用的，因此RCNN将两个LSTM按照相反的方向组装为一个双向LSTM。
		2. RCNN使用了两层双向LSTM以增强对抽象特征的理解，其每层各256个单元双向LSTM单元。



