---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 #Linux驱动开发 #操作系统 

# 1 目录

```toc
```

# 2 缓冲区队列(vb2_queue)

vb2_queue(视频缓冲区队列)提供了远超普通队列的功能特性，例如：
- V4L2所支持的ioctl操作(例如缓冲区申请、流控制等)
- 多路复用机制(poll/select)
- 时间戳处理
- 同步机制
- 内存管理
- DMA支持
等。

## 2.1 数据结构(struct vb2_queue)

```C
/**
 * struct vb2_queue - a videobuf2 queue.
 *
 * @type:	private buffer type whose content is defined by the vb2-core
 *		caller. For example, for V4L2, it should match
 *		the types defined on &enum v4l2_buf_type.
 * @io_modes:	supported io methods (see &enum vb2_io_modes).
 * @dev:	device to use for the default allocation context if the driver
 *		doesn't fill in the @alloc_devs array.
 * @dma_attrs:	DMA attributes to use for the DMA.
 * @bidirectional: when this flag is set the DMA direction for the buffers of
 *		this queue will be overridden with %DMA_BIDIRECTIONAL direction.
 *		This is useful in cases where the hardware (firmware) writes to
 *		a buffer which is mapped as read (%DMA_TO_DEVICE), or reads from
 *		buffer which is mapped for write (%DMA_FROM_DEVICE) in order
 *		to satisfy some internal hardware restrictions or adds a padding
 *		needed by the processing algorithm. In case the DMA mapping is
 *		not bidirectional but the hardware (firmware) trying to access
 *		the buffer (in the opposite direction) this could lead to an
 *		IOMMU protection faults.
 * @fileio_read_once:		report EOF after reading the first buffer
 * @fileio_write_immediately:	queue buffer after each write() call
 * @allow_zero_bytesused:	allow bytesused == 0 to be passed to the driver
 * @quirk_poll_must_check_waiting_for_buffers: Return %EPOLLERR at poll when QBUF
 *              has not been called. This is a vb1 idiom that has been adopted
 *              also by vb2.
 * @supports_requests: this queue supports the Request API.
 * @requires_requests: this queue requires the Request API. If this is set to 1,
 *		then supports_requests must be set to 1 as well.
 * @uses_qbuf:	qbuf was used directly for this queue. Set to 1 the first
 *		time this is called. Set to 0 when the queue is canceled.
 *		If this is 1, then you cannot queue buffers from a request.
 * @uses_requests: requests are used for this queue. Set to 1 the first time
 *		a request is queued. Set to 0 when the queue is canceled.
 *		If this is 1, then you cannot queue buffers directly.
 * @allow_cache_hints: when set user-space can pass cache management hints in
 *		order to skip cache flush/invalidation on ->prepare() or/and
 *		->finish().
 * @non_coherent_mem: when set queue will attempt to allocate buffers using
 *		non-coherent memory.
 * @lock:	pointer to a mutex that protects the &struct vb2_queue. The
 *		driver can set this to a mutex to let the v4l2 core serialize
 *		the queuing ioctls. If the driver wants to handle locking
 *		itself, then this should be set to NULL. This lock is not used
 *		by the videobuf2 core API.
 * @owner:	The filehandle that 'owns' the buffers, i.e. the filehandle
 *		that called reqbufs, create_buffers or started fileio.
 *		This field is not used by the videobuf2 core API, but it allows
 *		drivers to easily associate an owner filehandle with the queue.
 * @ops:	driver-specific callbacks
 * @mem_ops:	memory allocator specific callbacks
 * @buf_ops:	callbacks to deliver buffer information.
 *		between user-space and kernel-space.
 * @drv_priv:	driver private data.
 * @subsystem_flags: Flags specific to the subsystem (V4L2/DVB/etc.). Not used
 *		by the vb2 core.
 * @buf_struct_size: size of the driver-specific buffer structure;
 *		"0" indicates the driver doesn't want to use a custom buffer
 *		structure type. In that case a subsystem-specific struct
 *		will be used (in the case of V4L2 that is
 *		``sizeof(struct vb2_v4l2_buffer)``). The first field of the
 *		driver-specific buffer structure must be the subsystem-specific
 *		struct (vb2_v4l2_buffer in the case of V4L2).
 * @timestamp_flags: Timestamp flags; ``V4L2_BUF_FLAG_TIMESTAMP_*`` and
 *		``V4L2_BUF_FLAG_TSTAMP_SRC_*``
 * @gfp_flags:	additional gfp flags used when allocating the buffers.
 *		Typically this is 0, but it may be e.g. %GFP_DMA or %__GFP_DMA32
 *		to force the buffer allocation to a specific memory zone.
 * @min_queued_buffers: the minimum number of queued buffers needed before
 *		@start_streaming can be called. Used when a DMA engine
 *		cannot be started unless at least this number of buffers
 *		have been queued into the driver.
 *		VIDIOC_REQBUFS will ensure at least @min_queued_buffers + 1
 *		buffers will be allocated. Note that VIDIOC_CREATE_BUFS will not
 *		modify the requested buffer count.
 * @min_reqbufs_allocation: the minimum number of buffers to be allocated when
 *		calling VIDIOC_REQBUFS. Note that VIDIOC_CREATE_BUFS will *not*
 *		modify the requested buffer count and does not use this field.
 *		Drivers can set this if there has to be a certain number of
 *		buffers available for the hardware to work effectively.
 *		This allows calling VIDIOC_REQBUFS with a buffer count of 1 and
 *		it will be automatically adjusted to a workable	buffer count.
 *		If set, then @min_reqbufs_allocation must be larger than
 *		@min_queued_buffers + 1.
 *		If this field is > 3, then it is highly recommended that the
 *		driver implements the V4L2_CID_MIN_BUFFERS_FOR_CAPTURE/OUTPUT
 *		control.
 * @alloc_devs:	&struct device memory type/allocator-specific per-plane device
 */
/*
 * Private elements (won't appear at the uAPI book):
 * @mmap_lock:	private mutex used when buffers are allocated/freed/mmapped
 * @memory:	current memory type used
 * @dma_dir:	DMA mapping direction.
 * @bufs:	videobuf2 buffer structures. If it is non-NULL then
 *		bufs_bitmap is also non-NULL.
 * @bufs_bitmap: bitmap tracking whether each bufs[] entry is used
 * @max_num_buffers: upper limit of number of allocated/used buffers.
 *		     If set to 0 v4l2 core will change it VB2_MAX_FRAME
 *		     for backward compatibility.
 * @queued_list: list of buffers currently queued from userspace
 * @queued_count: number of buffers queued and ready for streaming.
 * @owned_by_drv_count: number of buffers owned by the driver
 * @done_list:	list of buffers ready to be dequeued to userspace
 * @done_lock:	lock to protect done_list list
 * @done_wq:	waitqueue for processes waiting for buffers ready to be dequeued
 * @streaming:	current streaming state
 * @start_streaming_called: @start_streaming was called successfully and we
 *		started streaming.
 * @error:	a fatal error occurred on the queue
 * @waiting_for_buffers: used in poll() to check if vb2 is still waiting for
 *		buffers. Only set for capture queues if qbuf has not yet been
 *		called since poll() needs to return %EPOLLERR in that situation.
 * @waiting_in_dqbuf: set by the core for the duration of a blocking DQBUF, when
 *		it has to wait for a buffer to become available with vb2_queue->lock
 *		released. Used to prevent destroying the queue by other threads.
 * @is_multiplanar: set if buffer type is multiplanar
 * @is_output:	set if buffer type is output
 * @is_busy:	set if at least one buffer has been allocated at some time.
 * @copy_timestamp: set if vb2-core should set timestamps
 * @last_buffer_dequeued: used in poll() and DQBUF to immediately return if the
 *		last decoded buffer was already dequeued. Set for capture queues
 *		when a buffer with the %V4L2_BUF_FLAG_LAST is dequeued.
 * @fileio:	file io emulator internal data, used only if emulator is active
 * @threadio:	thread io internal data, used only if thread is active
 * @name:	queue name, used for logging purpose. Initialized automatically
 *		if left empty by drivers.
 */
struct vb2_queue {
	unsigned int			type;
	unsigned int			io_modes;
	struct device			*dev;
	unsigned long			dma_attrs;
	unsigned int			bidirectional:1;
	unsigned int			fileio_read_once:1;
	unsigned int			fileio_write_immediately:1;
	unsigned int			allow_zero_bytesused:1;
	unsigned int		   quirk_poll_must_check_waiting_for_buffers:1;
	unsigned int			supports_requests:1;
	unsigned int			requires_requests:1;
	unsigned int			uses_qbuf:1;
	unsigned int			uses_requests:1;
	unsigned int			allow_cache_hints:1;
	unsigned int			non_coherent_mem:1;

	struct mutex			*lock;
	void				*owner;

	const struct vb2_ops		*ops;
	const struct vb2_mem_ops	*mem_ops;
	const struct vb2_buf_ops	*buf_ops;

	void				*drv_priv;
	u32				subsystem_flags;
	unsigned int			buf_struct_size;
	u32				timestamp_flags;
	gfp_t				gfp_flags;
	u32				min_queued_buffers;
	u32				min_reqbufs_allocation;

	struct device			*alloc_devs[VB2_MAX_PLANES];

	/* private: internal use only */
	struct mutex			mmap_lock;
	unsigned int			memory;
	enum dma_data_direction		dma_dir;
	struct vb2_buffer		**bufs;
	unsigned long			*bufs_bitmap;
	unsigned int			max_num_buffers;

	struct list_head		queued_list;
	unsigned int			queued_count;

	atomic_t			owned_by_drv_count;
	struct list_head		done_list;
	spinlock_t			done_lock;
	wait_queue_head_t		done_wq;

	unsigned int			streaming:1;
	unsigned int			start_streaming_called:1;
	unsigned int			error:1;
	unsigned int			waiting_for_buffers:1;
	unsigned int			waiting_in_dqbuf:1;
	unsigned int			is_multiplanar:1;
	unsigned int			is_output:1;
	unsigned int			is_busy:1;
	unsigned int			copy_timestamp:1;
	unsigned int			last_buffer_dequeued:1;

	struct vb2_fileio_data		*fileio;
	struct vb2_threadio_data	*threadio;

	char				name[32];

#ifdef CONFIG_VIDEO_ADV_DEBUG
	/*
	 * Counters for how often these queue-related ops are
	 * called. Used to check for unbalanced ops.
	 */
	u32				cnt_queue_setup;
	u32				cnt_wait_prepare;
	u32				cnt_wait_finish;
	u32				cnt_prepare_streaming;
	u32				cnt_start_streaming;
	u32				cnt_stop_streaming;
	u32				cnt_unprepare_streaming;
#endif
};
```

其普通公有成员：
- `unsigned int type` ：
	- 功能含义：缓冲区类型，子系统所定义的枚举匹配
		- 之所以这里使用 `unsigned int` 类型，是因为在该队列被用于V4L2子系统时应当使用[[video_device#^u8ke9r|enum v4l2_buf_type]]，而在DVB中应当使用 `enum dvb_buf_type` 。
	- 维护方：初始化前<font color="#c00000">驱动必须配置</font>
- `unsigned int io_modes` ：
	- 功能含义：所支持的IO模式，为 `enum vb2_io_modes` 类型(如 `VB2_MMAP` 、 `VB2_USERPTR` 等，可组合使用)
	- 维护方：初始化前<font color="#c00000">驱动必须配置</font>
- `struct device *dev` ：
	- 功能含义：默认DMA分配设备
	- 维护方：当使用DMA时驱动推荐设置
- `unsigned long dma_attrs` ：
	- 功能含义：DMA的映射属性
	- 维护方：驱动可选设置
- `unsigned int bidirectional:1` ：
	- 功能含义：强制使用DMA双向映射
	- 维护方：硬件需要同时读写缓冲区时配置
- `unsigned int fileio_read_once:1` ：
	- 功能含义：每次 `stream_on` 只能读取一次缓冲区，后续的 `read()` 会返回 `EOF` ，如需要再次读取则需要重新 `stream_on` 。主要用于模拟文件I/O行为。
	- 维护方：
- `unsigned int fileio_write_immediately:1` ：
	- 功能含义：每次 `write()` 调用都会立即将缓冲区入队。主要用于模拟文件I/O行为。
	- 维护方：
- `unsigned int allow_zero_bytesused:1` ：
	- 功能含义：允许 `bytesused=0` 的缓冲区
	- 维护方：初始化前驱动可选设置
- `unsigned int quirk_poll_must_check_waiting_for_buffers:1` ：
	- 功能含义：旋转是否兼容旧vb1的行为
		- 在vb1中，用户在 `QBUF` 前调用 `poll` 会报错
	- 维护方：驱动可选设置
- `unsigned int supports_requests:1` ：
	- 功能含义：选择是否支持 `Request API` 
	- 维护方：初始化前驱动可选设置
- `unsigned int requires_requests:1` ：
	- 功能含义：选择是否必须支持 `Request API` 
	- 维护方：初始化前驱动可选设置
- `unsigned int uses_qbuf:1` ：
	- 功能含义：V4L2框架标记是否使用了 `VIDEOC_QBUF` 而不是通过 `Request API` 。
	- 维护方：V4L2配置，驱动只读访问
- `unsigned int uses_requests:1` 
	- 功能含义：V4L2框架标记是否使用了 `Request API` 而不是通过 `VIDEOC_QBUF` 。
	- 维护方：V4L2配置，驱动只读访问
- `unsigned int allow_cache_hints:1` ：
	- 功能含义：是否允许用户空间传递缓存管理提示，如用户空间的 `v4l2_buffer.flags` 字段中设置 `V4L2_BUF_FLAG_NO_CACHE_INVALIDATE` 或 `V4L2_BUF_FLAG_NO_CACHE_CLEAN` 。
	- 维护方：初始化前驱动可选设置，当驱动可以利用该信息优化缓存操作时使用
- `unsigned int non_coherent_mem:1` ：
	- 功能含义：指示分配的内存是非一致性的，即内存类型不一致
	- 维护方：初始化前驱动可选设置
- `struct mutex *lock` ：
	- 功能含义：V4L2框架执行下方若干回调时自动上锁、解锁所操作的锁
	- 维护方：驱动可选维护，默认或设置为 `NULL` 时V4L2将不再带锁运行(如 `queue_setup` 、 `buf_queue` 等操作)
- `void *owner` ：
	- 功能含义：指向拥有该buffer的文件句柄( `struct file` )
	- 维护方：V4L2框架维护，驱动只读
- `const struct vb2_ops *ops` ：
	- 功能含义：vb2相关回调函数，详见[[VB2概述#^tqizjf|vb2相关回调函数]]。
	- 维护方：<font color="#c00000">驱动必须配置</font>
- `const struct vb2_mem_ops *mem_ops` ：
	- 功能含义：内存分配操作函数，详见[[VB2概述#^6l340x|vb2内存操作函数]]。不过该成员存在一些预设配置，如： 
		- `vb2_vmalloc_memops` ：使用 `vmalloc` 分配内存
		- `vb2_kmalloc_memops` ：使用 `kmalloc` 分配内存
		- `vb2_dma_contig_memops` ：分配物理连续的DMA内存
		- `vb2_dma_sg_memops` ：使用 `scatter-gather` 进行DMA映射，适用于大块非连续内存
	- 维护方：<font color="#c00000">驱动必须配置</font>
- `const struct vb2_buf_ops *buf_ops` ：
	- 功能含义：缓冲区操作函数，详见[[VB2概述#^6o1wj3|vb2缓冲区操作函数]]。
	- 维护方：驱动可选配置，通常用 `vb2_common_ops` 
- `void *drv_priv` ：
	- 功能含义：驱动私有数据指针，通常指向包含 `vb2_queue` 的驱动自定义结构体
	- 维护方：驱动按需配置和管理
- `u32 subsystem_flags` ：
	- 功能含义：子系统标志位，用于区分该 `buffer` 被V4L2还是DVB或其他子系统使用。
		- 在 `vb2-core` 中没有使用，但是V4L2子系统可能会用
	- 维护方：由各子系统设置，驱动只读
- `unsigned int buf_struct_size` ：
	- 功能含义：驱动自定义缓冲区结构大小，当为0时使用各子系统默认结构，例如V4L2使用 `struct vb2_v4l2_buffer` ，当非0时驱动必须定义一个结构，该结构的第一个成员必须是子系统特定的结构。
	- 维护方：驱动可选设置
- `u32 timestamp_flags` ：
	- 功能含义：时间戳标志，由驱动设置以指示时间戳的时钟源，可指定：
		- `V4L2_BUF_FLAG_TIMESTAMP_*` 
		- `V4L2_BUF_FLAG_TSTAMP_SRC_*` 
	- 维护方：初始化前由驱动可选配置
- `gfp_t gfp_flags` ：
	- 功能含义：分配缓冲区时使用的额外GFP标志，如 `GFP_DMA` 
	- 维护方：
- `u32 min_queued_buffers` ：
	- 功能含义：启动流所需的最小缓冲数
	- 维护方：驱动可选设置，默认为0
	- 注意：
		- 该参数并不影响 `VIDIOC_REQBUFS` 的分配数量，<font color="#c00000">其只是流开启前必须排队的缓冲区数量</font>，以及在一定程度上间接影响缓冲区分配数。
		- 框架实际分配的缓冲区数量为 `max(user, min_reqbufs_allocation)` (即下一成员)
- `u32 min_reqbufs_allocation` ：
	- 功能含义：`REQBUFS` 的最小分配数
	- 维护方：驱动可选设置，V4L2自动限制到 `min_reqbufs_allocation > min_queued_buffers + 1` 
	- 注意：
		- <font color="#c00000">实际缓冲区大小介于</font> `min_queued_buffers` <font color="#c00000">和</font> `VIDEO_MAX_FRAME` <font color="#c00000">之间</font>
- `struct device *alloc_devs[VB2_MAX_PLANES]` ：
	- 功能含义：每个平面分配的DMA设备，如果没有使用则为NULL
	- 维护方：驱动可在 `queue_setup` 或注册前按需初始化
private成员(<font color="#c00000">驱动只读访问或禁止访问</font>)：
- `struct mutex mmap_lock` ：
	- 功能含义：保护 `mmap` 的互斥锁，V4L2在 `mmap` 调用期间自动加锁解锁。
	- 驱动访问：禁止访问
- `unsigned int memory` ：
	- 功能含义：当前队列使用的内存类型，例如 `VB2_MEMORY_MMAP` 、 `VB2_MEMORY_USERPTR` 等。
	- 驱动访问：只读访问
- `enum dma_data_direction dma_dir` ：
	- 功能含义：DMA数据传输方向，V4L2根据 `is_output` 自动设置
	- 驱动访问：只读访问
- `struct vb2_buffer **bufs` ：
	- 功能含义：指向缓冲区指针数组，每个元素代表一个分配的缓冲区
	- 驱动访问：禁止直接访问，可通过 `vb2_get_buffer` 间接访问
- `unsigned long *bufs_bitmap` ：
	- 功能含义：存储 `bufs` 中已被使用的索引的位图
	- 驱动访问：禁止访问
- `unsigned int max_num_buffers` ：
	- 功能含义：队列支持的最大缓冲区数量
	- 驱动访问：只读访问
- `struct list_head queued_list` ：
	- 功能含义：已被用户塞入队列但未被驱动处理的缓冲去链表
	- 驱动访问：禁止直接遍历，应在 `buf_queue` 回调中处理单个缓冲区
- `unsigned int queued_count` ：
	- 功能含义：`queued_list` 中的缓冲区数量
	- 驱动访问：只读
- `atomic_t owned_by_drv_count` ：
	- 功能含义：驱动当前拥有的缓冲区计数，也就是已传递给驱动但驱动未处理完成的缓冲区数
		- 当驱动通过 `buf_queue` 接收缓冲区时原子+1
		- 当驱动调用 `vb2_buffer_done()` 时原子-1
	- 驱动访问：只读
- `struct list_head done_list` ：
	- 功能含义：驱动已完成并等待出队的缓冲区列表
	- 驱动访问：禁止访问，`vb2_buffer_done()` 会使缓冲进入该队列
- `spinlock_t done_lock` ：
	- 功能含义：保护 `done_list` 的自旋锁，V4L2/VB2框架在添加/移除缓冲区时使用
	- 驱动访问：禁止访问
- `wait_queue_head_t done_wq` ：
	- 功能含义：等待队列，阻塞在 `DQBUF` 的进程
	- 驱动访问：禁止访问，`vb2_buffer_done()` 间接触发
- `unsigned int streaming:1` 
	- 功能含义：当前是否在流状态
- `unsigned int start_streaming_called:1`
	- 功能含义：`start_streaming` 是否被成功调用
- `unsigned int error:1` 
	- 功能含义：队列是否发生致命错误
- `unsigned int waiting_for_buffers:1` ：
	- 功能含义：用于 `poll()` 系统调用，标记是否在等待缓冲区
	- 驱动访问：只读
- `unsigned int waiting_in_dqbuf:1` ：
	- 功能含义：标记当前是否有线程在 `DQBUF` 中阻塞等待缓冲区
	- 驱动访问：只读
- `unsigned int is_multiplanar:1` 
	- 功能含义：是否为多平面缓存
- `unsigned int is_output:1` 
	- 功能含义：是否为输出队列
- `unsigned int is_busy:1` 
	- 功能含义：标记队列是否至少分配过一个缓冲区，当所有缓冲区被释放时清除
	- 驱动访问：只读
- `unsigned int copy_timestamp:1` 
	- 功能含义：是否在 `DQBUF` 时复制时间戳到用户空间
	- 驱动访问：只读
- `unsigned int last_buffer_dequeued:1` 
	- 功能含义：最后一个缓冲是否已出队
		- 用途：`poll` 和 `DQBUF` 可通过此成员立即返回
	- 驱动访问：只读
- `struct vb2_fileio_data *fileio` ：
	- 功能含义：文件I/O模拟器状态数据(当使用 `read()/write()` 而非 `mmap` 时)
	- 驱动访问：禁止访问
- `struct vb2_threadio_data *threadio` ：
	- 功能含义：线程I/O状态数据
	- 驱动访问：禁止访问
- `char name[32]` ：
	- 功能含义：队列名称，用于调试日志输出，框架自动生成
	- 驱动访问：可直接读取，或通过 `vb2_queue_init_name()` 间接设置

## 2.2 vb2相关回调函数(struct vb2_ops) ^tqizjf

视频缓冲区队列有如下的回调函数：

```C
/**
 * struct vb2_ops - driver-specific callbacks.
 *
 * These operations are not called from interrupt context except where
 * mentioned specifically.
 *
 * @queue_setup:	called from VIDIOC_REQBUFS() and VIDIOC_CREATE_BUFS()
 *			handlers before memory allocation. It can be called
 *			twice: if the original number of requested buffers
 *			could not be allocated, then it will be called a
 *			second time with the actually allocated number of
 *			buffers to verify if that is OK.
 *			The driver should return the required number of buffers
 *			in \*num_buffers, the required number of planes per
 *			buffer in \*num_planes, the size of each plane should be
 *			set in the sizes\[\] array and optional per-plane
 *			allocator specific device in the alloc_devs\[\] array.
 *			When called from VIDIOC_REQBUFS(), \*num_planes == 0,
 *			the driver has to use the currently configured format to
 *			determine the plane sizes and \*num_buffers is the total
 *			number of buffers that are being allocated. When called
 *			from VIDIOC_CREATE_BUFS(), \*num_planes != 0 and it
 *			describes the requested number of planes and sizes\[\]
 *			contains the requested plane sizes. In this case
 *			\*num_buffers are being allocated additionally to
 *			the buffers already allocated. If either \*num_planes
 *			or the requested sizes are invalid callback must return %-EINVAL.
 * @wait_prepare:	release any locks taken while calling vb2 functions;
 *			it is called before an ioctl needs to wait for a new
 *			buffer to arrive; required to avoid a deadlock in
 *			blocking access type.
 * @wait_finish:	reacquire all locks released in the previous callback;
 *			required to continue operation after sleeping while
 *			waiting for a new buffer to arrive.
 * @buf_out_validate:	called when the output buffer is prepared or queued
 *			to a request; drivers can use this to validate
 *			userspace-provided information; this is required only
 *			for OUTPUT queues.
 * @buf_init:		called once after allocating a buffer (in MMAP case)
 *			or after acquiring a new USERPTR buffer; drivers may
 *			perform additional buffer-related initialization;
 *			initialization failure (return != 0) will prevent
 *			queue setup from completing successfully; optional.
 * @buf_prepare:	called every time the buffer is queued from userspace
 *			and from the VIDIOC_PREPARE_BUF() ioctl; drivers may
 *			perform any initialization required before each
 *			hardware operation in this callback; drivers can
 *			access/modify the buffer here as it is still synced for
 *			the CPU; drivers that support VIDIOC_CREATE_BUFS() must
 *			also validate the buffer size; if an error is returned,
 *			the buffer will not be queued in driver; optional.
 * @buf_finish:		called before every dequeue of the buffer back to
 *			userspace; the buffer is synced for the CPU, so drivers
 *			can access/modify the buffer contents; drivers may
 *			perform any operations required before userspace
 *			accesses the buffer; optional. The buffer state can be
 *			one of the following: %DONE and %ERROR occur while
 *			streaming is in progress, and the %PREPARED state occurs
 *			when the queue has been canceled and all pending
 *			buffers are being returned to their default %DEQUEUED
 *			state. Typically you only have to do something if the
 *			state is %VB2_BUF_STATE_DONE, since in all other cases
 *			the buffer contents will be ignored anyway.
 * @buf_cleanup:	called once before the buffer is freed; drivers may
 *			perform any additional cleanup; optional.
 * @prepare_streaming:	called once to prepare for 'streaming' state; this is
 *			where validation can be done to verify everything is
 *			okay and streaming resources can be claimed. It is
 *			called when the VIDIOC_STREAMON ioctl is called. The
 *			actual streaming starts when @start_streaming is called.
 *			Optional.
 * @start_streaming:	called once to enter 'streaming' state; the driver may
 *			receive buffers with @buf_queue callback
 *			before @start_streaming is called; the driver gets the
 *			number of already queued buffers in count parameter;
 *			driver can return an error if hardware fails, in that
 *			case all buffers that have been already given by
 *			the @buf_queue callback are to be returned by the driver
 *			by calling vb2_buffer_done() with %VB2_BUF_STATE_QUEUED.
 *			If you need a minimum number of buffers before you can
 *			start streaming, then set
 *			&vb2_queue->min_queued_buffers. If that is non-zero
 *			then @start_streaming won't be called until at least
 *			that many buffers have been queued up by userspace.
 * @stop_streaming:	called when 'streaming' state must be disabled; driver
 *			should stop any DMA transactions or wait until they
 *			finish and give back all buffers it got from &buf_queue
 *			callback by calling vb2_buffer_done() with either
 *			%VB2_BUF_STATE_DONE or %VB2_BUF_STATE_ERROR; may use
 *			vb2_wait_for_all_buffers() function
 * @unprepare_streaming:called as counterpart to @prepare_streaming; any claimed
 *			streaming resources can be released here. It is
 *			called when the VIDIOC_STREAMOFF ioctls is called or
 *			when the streaming filehandle is closed. Optional.
 * @buf_queue:		passes buffer vb to the driver; driver may start
 *			hardware operation on this buffer; driver should give
 *			the buffer back by calling vb2_buffer_done() function;
 *			it is always called after calling VIDIOC_STREAMON()
 *			ioctl; might be called before @start_streaming callback
 *			if user pre-queued buffers before calling
 *			VIDIOC_STREAMON().
 * @buf_request_complete: a buffer that was never queued to the driver but is
 *			associated with a queued request was canceled.
 *			The driver will have to mark associated objects in the
 *			request as completed; required if requests are
 *			supported.
 */
struct vb2_ops {
	int (*queue_setup)(struct vb2_queue *q,
			   unsigned int *num_buffers, unsigned int *num_planes,
			   unsigned int sizes[], struct device *alloc_devs[]);

	void (*wait_prepare)(struct vb2_queue *q);
	void (*wait_finish)(struct vb2_queue *q);

	int (*buf_out_validate)(struct vb2_buffer *vb);
	int (*buf_init)(struct vb2_buffer *vb);
	int (*buf_prepare)(struct vb2_buffer *vb);
	void (*buf_finish)(struct vb2_buffer *vb);
	void (*buf_cleanup)(struct vb2_buffer *vb);

	int (*prepare_streaming)(struct vb2_queue *q);
	int (*start_streaming)(struct vb2_queue *q, unsigned int count);
	void (*stop_streaming)(struct vb2_queue *q);
	void (*unprepare_streaming)(struct vb2_queue *q);

	void (*buf_queue)(struct vb2_buffer *vb);

	void (*buf_request_complete)(struct vb2_buffer *vb);
};
```

其成员：
- `int (*queue_setup)(...)` 
	- 功能含义：队列配置回调，在 `VIDIOC_REQBUFS` 或 `VIDIOC_CREATE_BUFS` 时调用
	- 被调用时机：
		- 在 `VIDIOC_REQBUFS` 中会被调用两次：
			1. 第一次调用：由驱动计算所需缓冲区数量( `num_buffers` )和平面数量( `num_planes` )，并指定每个平面的总字节数( `sizes` 参数)。
			2. 第二次调用：给定实际申请下来的缓冲区数量，驱动校验是否满足期望。
		- 在 `VIDIOC_CREATE_BUFS` 中只会被调用一次，且晚于 `VIDIOC_REQBUFS` 。
		- 也就是说当且仅当 `num_planes=0` 时为第一次调用，此时驱动应当指定若干参数；<font color="#c00000">后续调用中</font> `num_planes!=0` <font color="#c00000">且只能做参数校验</font>。
	- 可选性：<font color="#c00000">驱动必须实现</font>
	- 参数：
		- `struct vb2_queue *q` ：需要配置的vb2缓冲区指针
		- `unsigned int *num_buffers` ：驱动所需的缓冲区数量
		- `unsigned int *num_planes` ：驱动所需的[[video_device#^29c6mw|平面]]数量，其：
			- 当其在 `VIDIOC_REQBUFS` 调用时， `num_planes` 为0，需要驱动根据 `q->format` 配置所需平面数
			- 在 `VIDIOC_CREATE_BUFS` 调用时， `num_planes` 为用户所请求的平面数，
		- `unsigned int sizes[]` ：存储每个平面的总字节数，由驱动指定；数组由V4L2提前分配，数组长度为 `VIDEO_MAX_PLANES` (通常为8)。
			- 维护方：V4L2框架
		- `struct device *alloc_devs[]` ：存储每个平面所分配的设备，尺寸与 `sizes` 一致，通常在分配特殊内存时使用。
- `void (*wait_prepare)(struct vb2_queue *q)` 
	- 功能含义：在即将让用户态线程进入等待事件和阻塞之前，驱动所需要完成的准备的处理回调。
		- 在该回调中：
			- 驱动<font color="#c00000">通常需要</font>对 `vb2_queue.lock` 进行解锁
			- 驱动可能需要同步解除I2C等子系统的互斥锁，并让硬件恢复到一个安全状态
	- 等待事件举例：
		- 当用户已经把队列中所有缓冲区都读取了，并且请求下一个缓冲区时，用户态进入等待事件
		- 当队列已经填满，且用户申请入队下一个缓冲区时，用户态进入等待事件
		- 在 `streamon` 时，如果设置了 `min_buffers` 并且当前入队的缓冲区数量不足，可能会等待
	- 被调用时机：
		- 在触发等待事件后，即将阻塞用户态进程之前
	- <span style="background:#fff88f"><font color="#c00000">机制及触发流程</font></span>：
		1. 用户申请入队/出队操作
		2. <font color="#c00000">V4L2框架获取设备的锁</font>( `vb2_queue.lock` 中指定的互斥锁)，从而进行设备状态的互斥管理，并进入驱动回调
		3. 在驱动的入队/出队回调中，若：
			1. 不满足出入队条件(队满入队、队空出队)时返回 `-EAGAIN` 
				1. 对于不满足出入队条件的分支，则V4L2会调用 `wait_prepare` 完成用户即将进入等待事件的一些准备(具体见功能含义)
				2. V4L2框架休眠用户线程
				3. 中断等事件处理完毕，满足入队/出队需求，驱动调用 `vb2_buffer_done` 等告知V4L2框架等待结束
				4. V4L2框架唤醒用户线程，并调用 `wait_finish` 
				5. V4L2框架进行后续处理
			2. 满足出入队条件时将缓冲区填入参数的指针中，并返回 `0` 
				1. 对于满足出入队条件的分支，则不会调用 `wait_prepare/finish` 操作，并且立即释放 `vb2_queue.lock` 并进行后处理
		4. 目的：<font color="#c00000">该设计确保等待期间</font>，<font color="#c00000">新的中断事件中不会等待</font> `wait_prepare/finish` <font color="#c00000">操作组中操作的互斥锁</font>(避免了死锁)，并且设备可以安全处理中断事件。
	- 可选性：驱动可选实现，若不实现则使用默认行为(解锁 `vb2_queue.lock` )
- `void (*wait_finish)(struct vb2_queue *q)` 
	- 功能含义：用户态线程完成等待事件之后的回调。
	- 被调用时机：
		- 在等待事件完成后，用户态线程被唤醒之后，V4L2后续处理事件之前
	- 可选性：同上。
- `int (*buf_out_validate)(struct vb2_buffer *vb)` 
	- 功能含义：<span style="background:#fff88f"><font color="#c00000">专用于输出设备(用户->设备)</font></span><font color="#c00000">的校验回调函数</font>，校验输出缓冲区的数据是否有效(例如校验缓冲区长度是否足够、元数据格式、DMA地址、时间戳等)
	- 被调用时机：用户态使用 `VIDEOC_QBUF` 输出数据之后
	- 可选性：输出设备驱动可选实现
- `int (*buf_init)(struct vb2_buffer *vb)` 
	- 功能含义：在缓冲区初始化时被调用，用于驱动对缓冲区进行额外的初始化
	- 被调用时机： `REQBUFS` 或 `CREATE_BUFS` 时调用
	- 可选性：驱动可选实现
- `int (*buf_prepare)(struct vb2_buffer *vb)` 
	- 功能含义：在每次将缓冲区加入队列( `QBUF` )前调用，用于验证和准备缓冲区(如检查大小、填充数据等)
	- 可选性：驱动可选实现
- `void (*buf_finish)(struct vb2_buffer *vb)` 
	- 功能含义：在缓冲区从队列中取出( `DQBUF` )后调用，用于在返回缓冲区给用户空间之前做后处理(如更新元数据)
	- 可选性：驱动可选实现
- `void (*buf_cleanup)(struct vb2_buffer *vb)` 
	- 功能含义：当缓冲区被释放( `REQBUFS(0)` 或关闭)时调用，用于清理驱动私有的缓冲区资源
	- 可选性：驱动可选实现
- `int (*prepare_streaming)(struct vb2_queue *q)` 
	- 功能含义：在进入流状态前调用，用于检查硬件和配置是否就绪
	- 可选性：驱动可选实现
- `int (*start_streaming)(struct vb2_queue *q, unsigned int count)` 
	- 功能含义：在用户态调用 `STREAMON` 且队列至少有一个缓冲区时被调用
	- 可选性：<font color="#c00000">驱动必须实现</font>
- `void (*stop_streaming)(struct vb2_queue *q)` 
	- 功能含义：当用户态调用 `STREAMOFF` 时被调用，用于停止流传输
	- 可选性：<font color="#c00000">驱动必须实现</font>
- `void (*unprepare_streaming)(struct vb2_queue *q)` 
	- 功能含义：
	- 可选性：驱动可选实现
- `void (*buf_queue)(struct vb2_buffer *vb)` 
	- 功能含义<font color="#c00000">[重要]</font>：用户空间使用 `VIDIOC_QBUF` 将缓冲区放会队列后框架会调用该函数，驱动应当在此启动硬件操作。当硬件操作完毕后，驱动必须调用 `vb2_buffer_done` 通知V4L2缓冲区已处理完成(状态为 `DONE` 或 `ERROR` )
	- 可选性：<font color="#c00000">驱动必须实现</font>
- `void (*buf_request_complete)(struct vb2_buffer *vb)` 
	- 功能含义：
	- 可选性：当需要支持请求API(request)时驱动需要实现

## 2.3 vb2内存操作函数(struct vb2_buf_ops) ^6l340x





## 2.4 缓冲区操作函数(struct vb2_buf_ops) ^6o1wj3





## 2.5 相关API

### 2.5.1 队列初始化函数(vb2_queue_init)

```C
#include <media/videobuf2-v4l2.h>

/**
 * vb2_queue_init() - initialize a videobuf2 queue
 * @q:		pointer to &struct vb2_queue with videobuf2 queue.
 *
 * The vb2_queue structure should be allocated by the driver. The driver is
 * responsible of clearing it's content and setting initial values for some
 * required entries before calling this function.
 * q->ops, q->mem_ops, q->type and q->io_modes are mandatory. Please refer
 * to the struct vb2_queue description in include/media/videobuf2-core.h
 * for more information.
 */
int __must_check vb2_queue_init(struct vb2_queue *q);
```

该函数通常在 `probe` 或打开设备回调时被驱动调用。当函数执行成功时返回 `0` 。

### 2.5.2 队列释放函数(vb2_queue_release)


```C
void vb2_queue_release(struct vb2_queue *q);
```


### 2.5.3 


vb2_reqbufs

vb2_querybuf

vb2_qbuf
vb2_dqbuf
vb2_streamon
vb2_streamoff
vb2_is_streaming
vb2_queue_error

### 2.5.4 (vb2_buffer_done)





## 2.6 提供的机制



# 3 缓冲区(vb2_buffer)



