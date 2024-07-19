#机器学习 #CV 

## 目录

```toc
```

## 文章信息

- 文章标题：`SA-NET: SHUFFLE ATTENTION FOR DEEP CONVOLUTIONAL NEURAL NETWORKS`
- 文章链接：[http://arxiv.org/abs/2102.00240](http://arxiv.org/abs/2102.00240)
- 

## 前置概念

- <font color="#9bbb59">GAP</font>：Global Averaging Pooling，TODO
- <font color="#9bbb59">Group Norm</font>：

## 论文思想

Shuffle Unit结合了对通道间的注意力(Channel attention)和对空间的注意力(Spatial attention)，随后所有的子特征被聚合并允许在不同的特征之间互相传递信息。

Shuffle Unit<font color="#c00000">保证输入和输出的维度相同</font>，方便将Shuffle Unit插入到任何需要引入注意力机制的地方。

## 文章重要译文

### 3. Shuffle Attention

在本章节，首先介绍了SA(Shuffle Attention)模块的构建过程，该模块将输入的特征映射分成若干组，并使用Shuffle Unit将对通道间的注意力(Channel attention)和对空间的注意力(Spatial attention)集成到每个组的一个块中。然后，对所有子特征进行聚合，并利用“通道洗牌”(Channel shuffle)操作符实现不同子特征之间的信息通信。然后，我们展示了如何对深层CNN使用SA模块。最后，通过仿真验证了该方法的有效性和可靠性。SA模块的总体架构如图2所示。
![[0003.jpg]]
<center>图2：SA模块的概述。</center>
<center>它采用“通道分割”并行处理每组的子特征。对于通道注意力分支，使用<font color="#9bbb59">GAP</font>生成<font color="#9bbb59">通道统计数据</font>，然后使用一对参数对通道向量进行缩放和移位。对于空间注意力分支，采用<a href="url"><font color="#9bbb59">Group Norm</font></a>生成空间统计数据，然后创建类似于通道分支的紧凑特征。然后将这两个分支连接起来。之后，所有子特征都被聚合，最后我们利用“<font color="#9bbb59">通道洗牌</font>”操作符来实现不同子特征之间的信息通信。</center>

#### 3.1 特征分组(Feature Grouping)
