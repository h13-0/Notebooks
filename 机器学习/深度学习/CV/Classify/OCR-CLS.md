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
	这部分网络会将图像横向扫描计算卷积，
