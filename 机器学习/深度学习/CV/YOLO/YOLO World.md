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
推荐使用后者，本文也是基于Ultralytics的YOLO World v2实现进行分析。

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

而YOLO World<span style="background:#fff88f"><font color="#c00000">只修改了Classifier分支</font></span>，其把文本的语义向量融合进了Classifier分支中。假设输入目标提示词共计 $k$ 个，则这 $k$ 个提示词分别对应 $k$ 个Classes，经过CLIP后会生成 `[Batch, k, 512]` 的张量，并开始运算：
1. 先使用卷积将输入特征维度对齐到512维( `WorldDetector.cv3` )：
	![[msedge_T0wwVlfWlG.png]]
	此时特征图上每个Pixel(或者说Grid cell)都是一个512维度的特征向量
2. 然后将上述特征图上的每个Pixel的512维特征向量与文本特征的512维向量相乘并统一线性缩放( `WorldDetector.cv4` )：
	![[msedge_pEeefPS9jB 1.png]]
	此时就已经拥有了与普通YOLO v8一致的张量输出，后续处理与YOLO v8完全一致。

最终结构为：[[YOLO-World Head结构.drawio.svg]]
![[YOLO-World Head结构.drawio.svg]]

## 4 loss&Train

> [!attention]
> 截止2025-05-10，Ultralytics中的损失函数计算与原论文不符，其依旧使用传统YOLO的损失函数设计。且训练结果异常。故本章节为原论文中的loss设计。

### 4.1 总损失函数设计




### 4.2 图像(区域)-文本对比损失(L\_con)

#### 4.2.1 图像-文本对比损失定义

将给定图像所对应的文本索引作为分类标签，使用交叉熵构造图像-文本对比损失 $L_{con}$ ：
#TODO

#### 4.2.2 图像-文本对生成

在YOLO World的训练中，其并非直接使用数据集中的区域-文本对进行训练，而是通过以下的数据增强方式进行：
1. 利用n-gram算法从文本中提取名词短语
2. 采用预训练开放词汇检测器(如GLIP)为图像中的名词短语生成伪框，提供粗粒度区域-文本对
3. 使用预训练CLIP(注意一个是GLIP一个是CLIP)评估图像-文本对和区域-文本对的相关性，过滤低相关性伪标注和图像。
在该论文中，作者使用该方法从CC3M中采样标注246k图像，获得了821k伪标注。

### 4.3 预训练

在预训练阶段，作者采用AdamW优化器，初始学习率为0.002，权重衰减为0.05。YOLO-World在32张NVIDIA V100 GPU上预训练100个epoch，总批次大小(batch size)为512。

其训练的数据集包含：
	![[msedge_HpOuPZoYqP.png]]
预训练使用的检测数据集标注包含：
- 边界框
- 类别标签或名词短语

## 5 可视化实验


用官方的示例图进行实验：
- 输入texts：`["person", "building", "bus", "tree", "tree with little flowers"]`
- 输入图像：
	- ![[bus.jpg]]
- 检测结果：
	- ![[yoloword_demo.jpg]]
上述 `WorldDetector.cv4` 输出的相似度张量可视化为(经过转置回 $(w, h)$ 顺序)：
- "building"：
	- ![[yoloword_building_mix.jpg]]
- "bus"：
	- ![[yoloword_bus_mix.jpg]]
- "people"：
	- ![[yoloword_people_mix.jpg]]

## 6 Appendix

### 6.1 开放训练

#### 6.1.1 Ultralytics实现

> [!attention]
> 截止2025-05-10，Ultralytics中的损失函数计算与原论文不符，其依旧使用传统YOLO的损失函数设计。且训练结果异常。

Ultralytics提供的开放集训练的参考示例为：

```python
data = dict(  
    train=dict(  
        yolo_data=["Objects365.yaml"], #可以改用任意的多类别yolo数据集进行训练
        grounding_data=[  
            dict(  
                img_path="../datasets/flickr30k/images",  
                json_file="../datasets/final_flickr_separateGT_train.json",  
            ),  
        ],  
    ),  
    val=dict(yolo_data=["lvis.yaml"]),  #可以改用任意yolo数据集进行验证，但是种类数需要大于等于训练集中 `yolo_data` 的种类数，具体可见下一子章节的 `model.set_classes`
)

model = YOLOWorld("yolov8s-worldv2.yaml")  
model.train(data=data, trainer=WorldTrainerFromScratch)
```

其中：
- `Objects365` 为包含365类目标的YOLO类型数据集
- `flickr30k` 为包含BoundingBox、Prompt的数据集
- `lvis` 也为普通YOLO类型数据集
上述数据集可以直接替换为同类型数据集。

##### 6.1.1.1 训练

在训练开始时， `WorldTrainer` 会按照 `val` 中数据集类型名称进行 `model.set_classes` ：

```python
def on_pretrain_routine_end(trainer):
    """Callback to set up model classes and text encoder at the end of the pretrain routine."""
    if RANK in {-1, 0}:
        # Set class names for evaluation
        names = [name.split("/")[0] for name in list(trainer.test_loader.dataset.data["names"].values())]
        de_parallel(trainer.ema.ema).set_classes(names, cache_clip_model=False)
    device = next(trainer.model.parameters()).device
    trainer.text_model, _ = trainer.clip.load("ViT-B/32", device=device)
    for p in trainer.text_model.parameters():
        p.requires_grad_(False)
```

`model.set_classes` 执行了如下的操作：
1. 计算text prompt的特征向量，并存入 `self.txt_feats` (仅在验证时会使用 `self.txt_feats` ，训练时实时传入特征向量)
2. <font color="#c00000">将当前模型的</font> `nc` <font color="#c00000">设置为传入文本段的个数</font>

加载后的数据集数据内容为：
- `flickr30k` 加载后为 `GroundingDataset` ：
	- `category_names` ：list，合并重复项后的提示语句，共计94185条。
		![[Pasted image 20250424100941.png]]
	- `im_files` ：list，图像文件路径，共计148116条。
	- `labels` ：list，元素为每张图片中所包含的BoundingBox、text等信息，共计148116条。
		![[Pasted image 20250424102112.png]]
		- `im_file` ：图像文件路径
		- `shape` ：图像尺寸
		- `cls` ：list，元素为对应到 `texts` 中的index
		- `bboxes` ：np.ndarray，数据为BoundingBox
			![[Pasted image 20250424102514.png]]
		- `texts` ：list，元素为包含提示的list
			![[Pasted image 20250424102300.png]]


### 6.2 封闭集训练

观察上述网络结构，不难发现，训练YOLO World只需要在普通的训练脚本前加一行：

```Python
model.set_classes(["..", ...])
```

即可。

### 6.3 关键章节翻译

#### 6.3.1 章节3.4 预训练方案

本节介绍在大规模检测、定位和图文数据集上预训练YOLO-World的训练策略。

##### 6.3.1.1 基于区域-文本对比损失的学习

给定马赛克采样图像 $I$ 和文本集合 $T$，YOLO-World输出 $K$ 个物体预测 $\{B_k, s_k\}_{k=1}^K$ 以及标注 $\Omega = \{B_i, t_i\}_{i=1}^N$。我们遵循并利用任务对齐的标签分配策略，将预测与真实标注匹配，并为每个正样本预测分配文本索引作为分类标签。基于此词汇表，我们通过物体-文本(区域-文本)相似度与物体-文本分配的交叉熵，构建区域-文本对比损失 $L_{con}$。此外，采用IoU损失和分布式焦点损失进行边界框回归，总训练损失定义为：
$$
L(I) = L_{con} + \lambda_I \cdot (L_{iou} + L_{dfl})
$$
其中 $\lambda_I$ 为指示因子：当输入图像 $I$ 来自检测或定位数据时设为1，来自图文数据时设为0。考虑到图文数据可能包含噪声框，我们仅对具有精确边界框的样本计算回归损失。

##### 6.3.1.2 基于图文数据的伪标签生成

我们提出一种自动标注方法生成区域-文本对，而非直接使用图文对进行预训练。具体包含三步：
1. **名词短语提取**：利用n-gram算法从文本中提取名词短语；
2. **伪标签生成**：采用预训练开放词汇检测器(如GLIP)为图像中的名词短语生成伪框，提供粗粒度区域-文本对；
3. **过滤策略**：
   - 使用预训练CLIP评估图像-文本对和区域-文本对的相关性，过滤低相关性伪标注和图像；
   - 通过非极大值抑制(NMS)等方法去除冗余边界框。

(详细方法见附录)通过该方案，我们从CC3M中采样标注246k图像，获得821k伪标注。
