#操作系统 #Linux系统原理 #Linux内核源码分析

# 目录

```toc
```

# v4l2_frmsizetypes

版本：`6.10.0-rc1` <!--格式要求见注1-->
原代码范围：`819-898` <!--方便章节排序-->
分析状态：✅ <!--✅表示已处理完毕、⌛表示未处理完毕-->

对象功能含义：
数据结构定义：

```C
/*
 *	F R A M E   S I Z E   E N U M E R A T I O N
 */
enum v4l2_frmsizetypes {
	V4L2_FRMSIZE_TYPE_DISCRETE	= 1,
	V4L2_FRMSIZE_TYPE_CONTINUOUS	= 2,
	V4L2_FRMSIZE_TYPE_STEPWISE	= 3,
};
```

其成员：
- `V4L2_FRMSIZE_TYPE_DISCRETE` ：
	- 功能含义：离散分辨率枚举，表示设备只支持几个特定的离散分辨率
- `V4L2_FRMSIZE_TYPE_CONTINUOUS` ：
	- 功能含义：连续分辨率枚举，表示设备支持在一个连续范围内可随意指定
- `V4L2_FRMSIZE_TYPE_STEPWISE` ：
	- 功能含义：步进分辨率枚举，表示设备只能在分辨率范围内步进选择
- 版本演化历史：

注：
- 本章节内容与用户态中的[[Linux内核原理及其开发/驱动开发专题/VB2/V4L2/video_device/video_device#^v0i94g|枚举指定输出格式的分辨率]]对应行为一致。
- 具体的分辨率值、步进、分辨率范围需要联合[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/videodev2.h#^puydyk|v4l2_frmsize_discrete]]和[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/videodev2.h#^jgxacp|v4l2_frmsize_stepwise]]进行设置。

# v4l2_frmsize_discrete ^puydyk

版本：`${linux内核版本号}` <!--格式要求见注1-->
原代码范围：`xxx-xxx` <!--方便章节排序-->
分析状态：⌛ <!--✅表示已处理完毕、⌛表示未处理完毕-->

对象功能含义：
数据结构定义：

```C

```

其成员：
- `${成员签名}` ：
	- 功能含义：
- 版本演化历史：


# v4l2_frmsize_stepwise ^jgxacp

版本：`${linux内核版本号}` <!--格式要求见注1-->
原代码范围：`xxx-xxx` <!--方便章节排序-->
分析状态：⌛ <!--✅表示已处理完毕、⌛表示未处理完毕-->

对象功能含义：
数据结构定义：

```C

```

其成员：
- `${成员签名}` ：
	- 功能含义：
- 版本演化历史：

