#机器学习 #CV 

## 目录

```toc
```

## 文章信息

- 文章标题：`SA-NET: SHUFFLE ATTENTION FOR DEEP CONVOLUTIONAL NEURAL NETWORKS`
- 文章链接：[http://arxiv.org/abs/2102.00240](http://arxiv.org/abs/2102.00240)
- 

## 论文思想

Shuffle Unit结合了对通道间的注意力(Channel attention)和对空间的注意力(Spatial attention)，随后所有的子特征被聚合并允许在不同的特征之间互相传递信息。

Shuffle Unit<font color="#c00000">保证输入和输出的维度相同</font>，方便将Shuffle Unit插入到任何需要引入注意力机制的地方。

## 文章重要译文

### 3. Shuffle Attention

在本章节，首先介绍了SA(Shuffle Attention)模块的构建过程，该模块将输入的特征映射分成若干组，并使用 Shuffle Unit 将频道注意和空间注意集成到每个组的一个块中。然后，对所有子特征进行聚合，并利用“通道洗牌”操作符实现不同子特征之间的信息通信。然后，我们展示了如何对深层 CNN 采用 SA。最后，通过仿真验证了该方法的有效性和可靠性。SA 模块的总体架构如图2所示。