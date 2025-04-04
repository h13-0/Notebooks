---
number headings: auto, first-level 2, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发 

## 1 目录

```toc
```

## 2 Readme



## 3 系统调用及其分析

### 3.1 select



### 3.2 poll

`poll` 系统调用的处理流程如下：

程序入口 `sys_poll()` ：
1. 设置poll_select的超时时间
2. 调用 `int ret = do_sys_poll(ufds, nfds, to)` ：
	1. 初始化变量
	2. <u>将用户态传递来的数组转化为链表形式存储</u>，并将数据从用户区拷贝到内核区，<font color="#c00000">同时将过大的pollfd数组进行分段</font>，转存到[[IO多路复用接口(select、poll、epoll)#4 2 struct poll_list|struct poll_list]]中，<font color="#c00000">以避免栈溢出或超过单个内存页</font>。
	3. 调用 `poll_initwait` 初始化[[IO多路复用接口(select、poll、epoll)#4 4 struct poll_wqueues|struct poll_wqueues]]等待队列。
	4. 调用 `do_poll` 执行实际的轮询操作，监视文件描述符并等待事件发生或超时： `static int do_poll(struct poll_list *list, struct poll_wqueues *wait, struct timespec64 *end_time)` <font color="#c00000">(poll函数会在这里阻塞)</font>：
		1. 处理无须等待的情况。当无须等待时，立即将 `timed_out` 置1。
		2. 轮询 `list` 中的文件描述符，调用 `do_pollfd` 检查是否有事件发生。 `__poll_t do_pollfd(struct pollfd *pollfd, poll_table *pwait, bool *can_busy_poll, __poll_t busy_flag)` ：
			1. <font color="#a5a5a5">通过fd获取到对应的fd结构体。</font>
			2. 调用 `demangle_poll(pollfd->events)` 将事件掩码转换为内核使用的形式。
			3. 向掩码中追加 `EPOLLERR` 和 `EPOLLHUP` 事件，用于监听错误和挂起事件。
			4. 调用 `vfs_poll` 转发到 `file->f_op->poll` 。该函数只负责转发到 `file_operations` 中定义的 `poll` 函数。
				- poll函数标准语义
			5. 将 `vfs_poll` 返回的事件掩码与用户请求的事件掩码进行逻辑与操作。
			6. <font color="#a5a5a5">归还fd结构体，解除对该结构体的引用。</font>
			7. 将内核使用的事件掩码转换成用户使用的形式。
			8. 返回掩码
		3. 如果上述子函数返回了非零掩码，则计数器 `count` ++。
		4. 如果：
			1. `count == 0` ，则检查当前线程是否有需要处理的信号，如有则返回 `-ERESTARTNOHAND` 。
			2. `count != 0` 或超时，则 `break` 。
			3. 上述情况都不满足(即事件未到达)，则调用 `poll_schedule_timeout` ，将进程状态改变为 `TASK_INTERRUPTIBLE` (可中断休眠)并进入休眠。
	5. 调用 `poll_freewait` 清理等待队列。
	6. 遍历 `poll_list` 链表，将每个 `pollfd` 的结果( `revents` 字段)复制回用户空间的 `ufds` 数组。
	7. 错误处理与返回。

### 3.3 epoll

epoll相关函数定义在了 `fs/eventpoll.c` 中，其主要有如下函数：
- `int epoll_create(int size);`
- `int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);`
- `int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout);`

#### 3.3.1 epoll_create


#### 3.3.2 epoll_ctl


#### 3.3.3 epoll_wait


## 4 关键数据结构及其含义

### 4.1 struct pollfd

`struct pollfd` 与用户空间中定义一致，定义如下：

```C
struct pollfd {
	int fd;
	short events;
	short revents;
};
```

具体含义即用户态表现可见[[IO模型#^n3ntl8]]。

### 4.2 struct poll_list

`struct poll_list` 的定义如下：

```C
struct poll_list {
	struct poll_list *next;
	unsigned int len;
	struct pollfd entries[];
};
```

该结构体是一个链表，<font color="#c00000">用于分割数量过大的pollfd数组，以避免栈溢出或超过单个内存页</font>。
其中：
- `struct poll_list *next` ：为下一节点的指针。
- `unsigned int len` ：表示在 `entries` 数组中存储的 `pollfd` 结构的数量。
- `struct pollfd entries[]` ：一个柔性数组，存储实际的 `pollfd` 结构数组。

### 4.3 struct poll_table_struct(poll_table)

`struct poll_table_struct` 或 `poll_table` 的定义如下：

```C
typedef struct poll_table_struct {
	poll_queue_proc _qproc;
	__poll_t _key;
} poll_table;
```

该数据结构用于管理 `poll` 、 `select` 和 `epoll` 系统调用中的等待队列机制。
其中：
- `poll_queue_proc _qproc` ：为一个函数指针，用于指向一个回调函数，该函数在需要将当前进程添加到等待队列时调用。
- `__poll_t _key` ：IO复用系统调用时所选择监听的事件掩码。

### 4.4 struct poll_table_entry

`struct poll_table_entry` 的定义如下：

```C
struct poll_table_entry {
	struct file *filp;
	__poll_t key;
	wait_queue_entry_t wait;
	wait_queue_head_t *wait_address;
};
```

<font color="#c00000">该数据结构用于存储poll类操作时与单个文件相关的poll类查询信息</font>(例如等待的文件对象、等待的事件掩码、等待的线程、线程的等待队列)。
其中：
- `struct file *filp` ：为指向Linux kernel中文件对象的指针。
- `__poll_t key` ：IO复用系统调用时所选择监听的事件掩码。
- `wait_queue_entry_t wait` ：用于将当前进程挂起，直到感兴趣的事件在文件描述符上发生。
- `wait_queue_head_t *wait_address` ：存储进程等待队列的队列头指针。
	- 该结构体定义于 `include/linux/wait.h` ，其中有如下两个元素：
		- `spinlock_t lock` ：自旋锁
		- `struct list_head head` ：链表锚点，详见[[内核基本数据结构(types.h部分)#^xl7wru|链表锚点]]。该链表锚点用于定义在结构体内，方便组织成链表结构。

### 4.5 struct poll_table_page

`struct poll_table_page` 的定义如下：

```C
struct poll_table_page {
	struct poll_table_page * next;
	struct poll_table_entry * entry;
	struct poll_table_entry entries[];
};
```


### 4.6 struct poll_wqueues

`struct poll_wqueues` 的定义如下：

```C
/*
 * Structures and helpers for select/poll syscall
 */
struct poll_wqueues {
	poll_table pt;
	struct poll_table_page *table;
	struct task_struct *polling_task;
	int triggered;
	int error;
	int inline_index;
	struct poll_table_entry inline_entries[N_INLINE_POLL_ENTRIES];
};
```

其中：
- `poll_table pt` ：其包含轮询的回调指针和所监听的事件掩码。
- `struct poll_table_page *table` ：
- `struct task_struct *polling_task` ：
- `int triggered` ：标志位，表示是否有事件被触发。
- `int error` ：当轮询过程中发生错误时，此字段将存储错误码。
- `int inline_index` ：用于指示下一个空闲的 `inline_entries` 插槽的索引。
- `struct poll_table_entry inline_entries` ：一个固定大小的数组，存放poll类操作查询信息的对象。