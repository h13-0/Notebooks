---
number headings: auto, first-level 2, max 6, 1.1
---
#机器学习 #CV 

## 1 目录

```toc
```

## 2 基本原理

将待卷积数据与conv kernel中对应的元素相乘后累加，即可得到输出结果。

### 2.1 一维卷积形式

例如给定计算参数：
- $input=[f_0, f_1, f_2, ..., f_8]$
- $kernel=[k_0, k_1, k_2]$，需要注意：
	- $kernel\_size=2\times k+1$
- $stride=1$，为每次卷积操作的步长
- $padding=0$，为对原数据增加的边界大小
则有：
1. 先对kernel左右翻转，有：$[k_2, k_1, k_0]$
2. 对input进行padding操作，由于 $padding=0$，故跳过
3. 按照stride进行相乘累加操作：
	- 记输出 $Output=[O_0, O_1, ..., O_n]$，则有：
		1. $O_0=f_0\times k_2+f_1\times k_1+f_2\times k_0$
		2. $O_1=f_1\times k_2+f_2\times k_1+f_3\times k_0$
		3. ...
		4. $O_n=f_n\times k_2+f_{n+1}\times k_1+f_{n+2}\times k_0$

注：
1. 数学上的 `kernel` 需要在第一步中进行左右翻转，但是CV中通常不用。
2. 输出尺寸为：
$$
Output\_size=\frac{input\_size+2\times padding - k}{stride}+1
$$

Demo：


### 2.2 二维形式
