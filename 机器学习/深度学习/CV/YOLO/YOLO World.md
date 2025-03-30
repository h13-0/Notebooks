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
推荐使用后者。

## 2 目录

```toc
```

## 3 YOLO World Head

YOLO World的主要改进集中于检测头
