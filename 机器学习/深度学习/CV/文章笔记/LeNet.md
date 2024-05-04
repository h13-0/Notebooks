#机器学习 #CV

## 目录

```toc
```

## 文章信息

- 文章原名：`Backpropagation Applied to Handwritten Zip Code Recognition` 
- 文章连接：[https://ieeexplore.ieee.org/document/6795724](https://ieeexplore.ieee.org/document/6795724)(Sci-Hub有)
- 作者信息：
	- Y.LeCun
	- B.Boser  
	- J.S.Denker  
	- D.Henderson  
	- R.E.Howard  
	- W. Hubbard  
	- L.D.Jackel  
 - 机构：贝尔实验室，AT&T Bell Laboratories, Holmdei, NJ 07733 USA

## 文章重要内容

### 2. 邮编

#### 2.1 数据集

用于训练和测试网络的数据集由9298个分段数字组成，这些数字来自美国邮件上出现的手写邮政编码。这些图像的示例如图1所示。数字是由许多不同的人书写的，使用了各种各样的尺寸、书写风格和工具，并有着广泛不同的注意程度。<font color="#c00000">7291个例子用于训练网络</font>，<font color="#c00000">2007个例子用于测试泛化性能</font>。<font color="#c00000">该数据库的一个重要特征是，训练集和测试集都包含许多模糊、不可分类甚至错误分类的示例</font>。

#### 2.2 预处理

在信封上定位邮政编码，并将每个数字与相邻数字分开，这本身就是一项非常艰巨的任务，由邮政服务承包商完成（Wang和Srihari，1988年）。在这一点上，<font color="#c00000">数字图像的大小不同，但通常在40乘60像素左右</font>。<font color="#c00000">然后应用线性变换以使图像适合于16乘16像素的图像</font>。<font color="#c00000">这种变换保留了字符的纵横比，并在图像中的无关标记被去除后执行</font>。由于线性变换，产生的图像不是二进制的，而是具有多个灰度级，因为原始图像中的可变数量的像素可以落入目标图像中的给定像素中。<font color="#c00000">每个图像的灰度级被缩放和平移到-1到1的范围内</font>。

### 3. 网络设计

#### 3.1 输入和输出