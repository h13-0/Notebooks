---
number headings: auto, first-level 2, max 6, 1.1
---
#机器学习 #CV #YOLO

## 1 Note

> YOLO-World 是一种基于 YOLOv8 架构的开放词汇目标检测模型，通过视觉-语言建模和大规模数据预训练，实现了零样本（Zero-Shot）检测能力，能够识别训练数据中未出现的新类别物体。其核心优势在于高效性和灵活性，在实时检测场景中表现出色。
> YOLO-World 的研发团队主要由腾讯 PCG ARC Lab（应用研究中心） 的成员主导，核心成员包括技术专家肖一（化名）及其团队。

以上内容总结自DeepSeek-R1。
YOLO World目前主要有两个实现：
- YOLO World的官方实现：[https://github.com/AILab-CVC/YOLO-World](https://github.com/AILab-CVC/YOLO-World)
- YOLO World的Ultralytics版本可直接参见：[https://github.com/ultralytics/ultralytics](https://github.com/ultralytics/ultralytics)
推荐使用后者，本文也是基于Ultralytics实现进行分析。

## 2 目录

```toc
```

## 3 YOLO World Head

Ultralytics版本的YOLO World的主要改进集中于检测头。在[[YOLO#^2jvvoq|YOLO v8 Head]]中已经提到，YOLO v8的检测头是解耦和形式的：
	![[Pasted image 20250311183521.png]]
假定YOLO v8的输入固定为 $(h, w)=(640, 640)$ ，Classifier分支(在Ultralytics代码中为 `Detector.cv3` )的主要张量流如下：
1. 输入三组不同尺寸的特征张量
2. 使用两次3x3卷积和一次1x1卷积将输出维度改变到 `num_cls` ，即输出下图所示的张量：
	![[msedge_UP1btIA2cJ.png]]
3. 使用 $Sigmoid$ 将输出映射到值域 $[0, 1]$ 中
4. 使用NMS对结果进行后处理

而YOLO World<span style="background:#fff88f"><font color="#c00000">只修改了Classifier分支</font></span>，其把文本的语义向量融合进了 `Detector.cv3` 中。假设输入目标提示词共计 $k$ 个，则这 $k$ 个提示词分别对应 $k$ 个Classes，经过CLIP后会生成 `[Batch, k, 512]` 的张量，并开始运算：
1. 先使用卷积将输入特征维度对齐到512维( `WorldDetector.cv3` )：
	![[msedge_T0wwVlfWlG.png]]
	此时特征图上每个Pixel(或者说Grid cell)都是一个512维度的特征向量
2. 然后将上述特征图上的每个Pixel的512维特征向量与文本特征的512维向量相乘，并缩放( `WorldDetector.cv4` )：
	![[msedge_Mhu6eOX6Ed.png]]






最终结构为：[[YOLO-World Head结构.drawio.svg]]
![[YOLO-World Head结构.drawio.svg]]