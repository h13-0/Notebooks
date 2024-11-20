---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 #Linux驱动开发 

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
	2. <u>将用户态传递来的数组转化为链表形式存储</u>，并将数据从用户区拷贝到内核区
	3. 调用 `poll_initwait` 初始化等待队列
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

### 4.2 poll_table

```C

```

### struct poll_wqueues

