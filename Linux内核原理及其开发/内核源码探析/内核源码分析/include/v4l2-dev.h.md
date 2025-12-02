#操作系统 #Linux系统原理 #Linux内核源码分析

# 目录

```toc
```



# video_device ^bd1jcw

版本：`6.10.0-rc1` <!--格式要求见注1-->
原代码范围：`216-309` <!--方便章节排序-->
分析状态：⌛ <!--✅表示已处理完毕、⌛表示未处理完毕-->

对象功能含义：视频设备对象
数据结构定义：

```C
/*
 * Newer version of video_device, handled by videodev2.c
 *	This version moves redundant code from video device code to
 *	the common handler
 */

/**
 * struct video_device - Structure used to create and manage the V4L2 device
 *	nodes.
 *
 * @entity: &struct media_entity
 * @intf_devnode: pointer to &struct media_intf_devnode
 * @pipe: &struct media_pipeline
 * @fops: pointer to &struct v4l2_file_operations for the video device
 * @device_caps: device capabilities as used in v4l2_capabilities
 * @dev: &struct device for the video device
 * @cdev: character device
 * @v4l2_dev: pointer to &struct v4l2_device parent
 * @dev_parent: pointer to &struct device parent
 * @ctrl_handler: Control handler associated with this device node.
 *	 May be NULL.
 * @queue: &struct vb2_queue associated with this device node. May be NULL.
 * @prio: pointer to &struct v4l2_prio_state with device's Priority state.
 *	 If NULL, then v4l2_dev->prio will be used.
 * @name: video device name
 * @vfl_type: V4L device type, as defined by &enum vfl_devnode_type
 * @vfl_dir: V4L receiver, transmitter or m2m
 * @minor: device node 'minor'. It is set to -1 if the registration failed
 * @num: number of the video device node
 * @flags: video device flags. Use bitops to set/clear/test flags.
 *	   Contains a set of &enum v4l2_video_device_flags.
 * @index: attribute to differentiate multiple indices on one physical device
 * @fh_lock: Lock for all v4l2_fhs
 * @fh_list: List of &struct v4l2_fh
 * @dev_debug: Internal device debug flags, not for use by drivers
 * @tvnorms: Supported tv norms
 *
 * @release: video device release() callback
 * @ioctl_ops: pointer to &struct v4l2_ioctl_ops with ioctl callbacks
 *
 * @valid_ioctls: bitmap with the valid ioctls for this device
 * @lock: pointer to &struct mutex serialization lock
 *
 * .. note::
 *	Only set @dev_parent if that can't be deduced from @v4l2_dev.
 */

struct video_device {
#if defined(CONFIG_MEDIA_CONTROLLER)
	struct media_entity entity;
	struct media_intf_devnode *intf_devnode;
	struct media_pipeline pipe;
#endif
	const struct v4l2_file_operations *fops;

	u32 device_caps;

	/* sysfs */
	struct device dev;
	struct cdev *cdev;

	struct v4l2_device *v4l2_dev;
	struct device *dev_parent;

	struct v4l2_ctrl_handler *ctrl_handler;

	struct vb2_queue *queue;

	struct v4l2_prio_state *prio;

	/* device info */
	char name[64];
	enum vfl_devnode_type vfl_type;
	enum vfl_devnode_direction vfl_dir;
	int minor;
	u16 num;
	unsigned long flags;
	int index;

	/* V4L2 file handles */
	spinlock_t		fh_lock;
	struct list_head	fh_list;

	int dev_debug;

	v4l2_std_id tvnorms;

	/* callbacks */
	void (*release)(struct video_device *vdev);
	const struct v4l2_ioctl_ops *ioctl_ops;
	DECLARE_BITMAP(valid_ioctls, BASE_VIDIOC_PRIVATE);

	struct mutex *lock;
};
```

其成员：
- 基础成员：
	- `char name[64]` 
		- 功能含义：设备名称，暴露于用户空间来表示设备。例如 `USB Camera` 。
		- 维护方：<font color="#c00000">驱动必须配置</font>
			- 由驱动方(`struct driver`)设置。
	- `enum vfl_devnode_type vfl_type`
		- 功能含义：描述设备类型，详见[[video_device#^4ac1hk|设备类型枚举]]，例如：
			- `VFL_TYPE_VIDEO` 视频输入输出设备(`/dev/videox`)
			- `VFL_TYPE_RADIO` 无线电调谐器(`/dev/radiox`)
		- 维护方：通常由驱动在注册 `video_device` 时指定，也可以在注册前配置，并在注册时将对应的参数值指定为 `-1` 从而让v4l2使用该结构体的值
	- `enum vfl_devnode_direction vfl_dir`
		- 功能含义：设备数据流向：
			- `VFL_DIR_RX` 接收(即<span style="background:#fff88f"><font color="#c00000">内核->用户</font></span>，<font color="#c00000">需要以用户态视角来看</font>)
			- `VFL_DIR_TX` 发送(即用户->内核)
			- `VFL_DIR_M2M` 内存到内存(常用于硬件编码器)
		- 维护方：<font color="#c00000">通常由驱动在注册驱动</font>
	- `int minor` 
		- 功能含义：设备节点的次设备号，即 `/dev/videoX` 中的 `X` 。与V4L2子设备类型相关(例如 `struct video_device` 等)
		- 维护方：V4L2框架自动配置，初始化为 `-1` ，注册设备时填充。
	- `u16 num`
		- 功能含义：同类型(同 `vfl_type` )设备节点编号
		- 维护方：V4L2框架自动配置。
	- `unsigned long flags`
		- 功能含义：设备状态标识，例如是否已注册、是否热插拔等，用于内部管理设备的生命周期。
		- 维护方：V4L2框架配置
	- `int index` 
		- 功能含义：设备在同一驱动管理的多个设备实例中的index，<font color="#c00000">V4L2可能依赖该值用于生成唯一的设备名或sysfs路径</font>。
		- 维护方：驱动建议配置。
	- `u32 device_caps`
		- 功能含义：描述设备的能力(对应用户态[[video_device#^vda0ux|查询设备能力]])
		- 维护方：<font color="#c00000">驱动必须配置</font>
	- `void (*release)(struct video_device *vdev)`
		- 功能含义：设备释放回调
		- 维护方：<font color="#c00000">驱动必须实现及设置</font>
	- `struct mutex *lock` 
		- 功能含义：互斥锁
		- 维护方：若驱动没有实例化该锁，则V4L2会实例化该锁。
			- 对于一些设备，可能需要和其他机制(如DMA)进行同步，V4L2可选地将该成员交由驱动就是为了方便与其他机制联动。
			- 若该锁来自于驱动，则释放时V4L2不会销毁该锁；若该锁由V4L2创建，则V4L2会负责释放该锁。
- 电视信号能力：
	- `v4l2_std_id tvnorms` 
		- 功能含义：设备支持的电视制式(如 `V4L2_STD_NTSC`、`V4L2_STD_PAL`)
		- 维护方：仅当设备涉及电视信号时需设置
- 设备模型及文件接口：
	- `struct device dev` 
		- 功能含义：指向V4L2中属于 `video_device` 的独立设备，<span style="background:#fff88f"><b><font color="#c00000">而非父设备</font></b></span>。通常用 `video_device.dev.parent` 指向父设备实例。
		- 维护方：V4L2框架负责维护
	- `struct device *dev_parent`
		- 功能含义：可选覆盖的父设备的 `struct device` 指针，可用于配置为非标准父设备结构。
			- 当需要配置为非标准父设备时，在注册V4L2子设备之前驱动手动设置即可。
			- 当注册V4L2子设备时若未配置该项，则V4L2会将 `dev->parent` 设为 `v4l2_dev->dev` 。
		- 维护方：V4L2框架自动配置，驱动可选覆盖。
	- `struct v4l2_device *v4l2_dev` 
		- 功能含义：指向父V4L2设备实例
		- 维护方：<font color="#c00000">驱动必须设置</font>
	- `struct cdev *cdev` 
		- 功能含义：内嵌的字符设备对象，用于在文件系统中暴露 `/dev/videoX`
		- 维护方：V4L2框架自动创建。
	- `const struct v4l2_file_operations *fops`
		- 功能含义：文件操作接口。
			- 相比于普通的 `file_operations` 类型简化了相当多的成员(如 `flush` 、 `fsyns` 、 `read_iter` 等)
		- 维护方：<font color="#c00000">驱动必须定义和提供</font>，其中：
			- <font color="#c00000">必须自行实现的成员有</font>：
				- `owner` ：通常指向 `THIS_MODULE`
				- `open` ：设备打开函数
				- `release` ：设备释放函数
			- 可直接使用helpers的有：
				- `unlocked_ioctl` ：通常指向V4L2实现的 `video_ioctl2` 
				- `compat_ioctl32` 
				- `mmap` ：
	- `const struct v4l2_ioctl_ops *ioctl_ops`
		- 功能含义：ioctl操作函数表，定义设备支持的 `ioctl` 命令，具体可见章节：[[video_device#^r8lfyg|v4l2_ioctl_ops]]。
		- 维护方：<font color="#c00000">驱动必须提供至少如下两个基本命令</font>
			- `vidioc_querycap` ：查询设备能力(`VIDIOC_QUERYCAP`)
			- `vidioc_g_fmt_vid_*` ：获取输入或输出设备的当前数据格式(`VIDIOC_G_FMT`)
	- `DECLARE_BITMAP(valid_ioctls, BASE_VIDIOC_PRIVATE)`
		- 功能含义：使用位图标记的设备所支持的 `ioctl` 命令，用于快速检查某个 `ioctl` 命令是否有效
		- 维护方：V4L2框架根据 `ioctl_ops` 自动生成，驱动无需设置。
- 文件句柄与同步
	- `struct list_head fh_list`
		- 功能含义：当前打开的设备文件句柄( `struct v4l2_fh` )链表，管理所有活动的文件句柄(用户空间 `open` 所获得的句柄，用户每多一个句柄链表就多一个成员)。
		- 维护方：由V4L2框架维护
	- `spinlock_t fh_lock`
		- 功能含义：保护 `fh_list` 的自旋锁，当驱动需要读取 `fh_list` 时需要先持有该锁。
		- 维护方：由V4L2框架维护
- 设备控制相关成员：
	- `struct v4l2_ctrl_handler *ctrl_handler`
		- 功能含义：用户可配置的参数项，例如亮度、对比度等
		- 维护方：驱动可选设置
	- `struct vb2_queue *queue`
		- 功能含义：指向视频缓冲区队列，管理视频缓冲区的分配、入队、出队和流控制
		- 维护方：驱动可选配置
	- `struct v4l2_prio_state *prio`
		- 功能含义：设备优先级状态，同[[V4L2概述#^3rx2nr|设备优先级状态]]
		- 维护方：驱动可选，若未设置，默认使用 `v4l2_dev->prio` 
- 媒体控制器相关成员(取决于内核是否开启该功能)：
	- `struct media_entity entity`
		- 功能含义：表示设备在媒体控制器框架中的实体(如摄像头传感器、编码器等)。
			- 描述设备在媒体流水线中的拓扑关系和功能，用于媒体控制器配置(如 `media-ctl` 工具)。
		- 当启用 `CONFIG_MEDIA_CONTROLLER` 后必须设置。
	- `struct media_intf_devnode *intf_devnode`
		- 功能含义：媒体控制器接口
	- `struct media_pipeline pipe`
		- 功能含义：表示设备参与的媒体管线
- 内核调试标志
	- `int dev_debug`
		- 功能含义：内部调试标志，用于内核开发
		- 维护方：驱动不应当修改。
- 版本演化历史：
