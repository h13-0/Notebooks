#操作系统 #Linux系统原理 #Linux内核源码分析

# 目录

```toc
```

# v4l2_frmsizetypes

版本：`6.10.0-rc1` <!--格式要求见注1-->
原代码范围：`819-898` <!--方便章节排序-->
分析状态：⌛ <!--✅表示已处理完毕、⌛表示未处理完毕-->

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
	- 功能含义：离散分辨率枚举，用于指示当前枚举类型为离散值
- `V4L2_FRMSIZE_TYPE_CONTINUOUS` ：
	- 功能含义：连续分辨率枚举
- `V4L2_FRMSIZE_TYPE_STEPWISE` ：
	- 功能含义：步进分辨率枚举
- 版本演化历史：