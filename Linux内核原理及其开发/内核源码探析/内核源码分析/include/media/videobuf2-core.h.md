#操作系统 #Linux系统原理 #Linux内核源码分析

# 目录

```toc
```

# vb2_queue ^xxcufl

版本：`6.10.0-rc1` <!--格式要求见注1-->
原代码范围：`480-687` <!--方便章节排序-->
分析状态：⌛ <!--✅表示已处理完毕、⌛表示未处理完毕-->

对象功能含义：VB2缓冲区队列
数据结构定义：

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
 *		     for backward compat<font color="#c00000">i</font>bility.
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
	- 维护方：当使用DMA时驱动推荐设置，存储上下文请用成员 `drv_priv`
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
	- 维护方：驱动按需配置和管理，<font color="#c00000">通常用于存储上下文指针</font>
- `u32 subsystem_flags` ：
	- 功能含义：子系统标志位，用于区分该 `buffer` 被V4L2还是DVB或其他子系统使用。
		- 在 `vb2-core` 中没有使用，但是V4L2子系统可能会用
	- 维护方：由各子系统设置，驱动只读
- `unsigned int buf_struct_size` ：
	- 功能含义：表示在标准的 `struct vb2_buffer` 后，要额外预留多少空间，用于存储驱动的数据。
		- <font color="#c00000">也就是说可以通过设置比</font> `struct vb2_queue` <font color="#c00000">更大的值</font>，<font color="#c00000">从而附加自己的数据</font>。<font color="#c00000">且自己的数据必须附加在末尾</font>，即自定义的结构体的第一个元素必须是 `struct vb2_queue` 。
		- 在内核中 `struct v4l2_m2m_buffer` 即是一个附加数据的例子，使用 `struct v4l2_m2m_buffer* buf = (struct v4l2_m2m_buffer*)vb2_buf` 和 `buf.list` 访问自行的数据。
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
		- <font color="#c00000">实际缓冲区大小介于</font> `min_queued_buffers` <font color="#c00000">和</font> `VIDEO_MAX_FRAME` <font color="#c00000">之间</font>
- `u32 min_reqbufs_allocation` ：
	- 功能含义：`REQBUFS` 的最小分配数
	- 维护方：驱动可选设置，V4L2自动限制到 `min_reqbufs_allocation > min_queued_buffers + 1` 
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

版本演化历史：
- 在 `4.8-rc1` 之前，`struct vb2_queue` 中并没有 `struct device *dev` 成员。此时可依赖成员 `void *drv_priv` 。



