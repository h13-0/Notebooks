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


### 3.3 epoll

epoll相关函数定义在了 `fs/eventpoll.c` 中，其主要有如下函数：
- `int epoll_create(int size);`
- `int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);`
- `int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout);`

#### 3.3.1 epoll_create

```C
/*
 * Open an eventpoll file descriptor.
 */
static int do_epoll_create(int flags)
{
	int error, fd;
	struct eventpoll *ep = NULL;
	struct file *file;

	/* Check the EPOLL_* constant for consistency.  */
	BUILD_BUG_ON(EPOLL_CLOEXEC != O_CLOEXEC);

	if (flags & ~EPOLL_CLOEXEC)
		return -EINVAL;
	/*
	 * Create the internal data structure ("struct eventpoll").
	 */
	error = ep_alloc(&ep);
	if (error < 0)
		return error;
	/*
	 * Creates all the items needed to setup an eventpoll file. That is,
	 * a file structure and a free file descriptor.
	 */
	fd = get_unused_fd_flags(O_RDWR | (flags & O_CLOEXEC));
	if (fd < 0) {
		error = fd;
		goto out_free_ep;
	}
	file = anon_inode_getfile("[eventpoll]", &eventpoll_fops, ep,
				 O_RDWR | (flags & O_CLOEXEC));
	if (IS_ERR(file)) {
		error = PTR_ERR(file);
		goto out_free_fd;
	}
#ifdef CONFIG_NET_RX_BUSY_POLL
	ep->busy_poll_usecs = 0;
	ep->busy_poll_budget = 0;
	ep->prefer_busy_poll = false;
#endif
	ep->file = file;
	fd_install(fd, file);
	return fd;

out_free_fd:
	put_unused_fd(fd);
out_free_ep:
	ep_clear_and_put(ep);
	return error;
}

SYSCALL_DEFINE1(epoll_create, int, size)
{
	if (size <= 0)
		return -EINVAL;

	return do_epoll_create(0);
}
```


