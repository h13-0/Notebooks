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
- $kernel=[k_0, k_1, k_2]$
- $stride=1$，为每次卷积操作的步长
- $padding=0$，为对元
- 
则有：
1. 先对kernel左右翻转，有：$[k_2, k_1, k_0]$
2. 华东
注：
3. 数学上的 `kernel` 需要进行第一步