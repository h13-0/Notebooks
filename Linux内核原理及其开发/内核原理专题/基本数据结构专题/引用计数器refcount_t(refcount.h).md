---
number headings: auto, first-level 2, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发

## 1 目录

```toc
```

## 2 Readme


## 3 引用计数器

### 3.1 设计目的

例如需要实现一个可以被多线程读写的设备(可以直接使用该章节中的设备假设：[[Linux驱动开发笔记#^qdfcky]]），那么则有如下基础设定：
1. 用户态进程在尝试打开该文件后会得到一个文件描述符 `fd` 。
2. 用户可以通过该 `fd` 执行对设备读写和关闭操作。
3. 通常来说<font color="#c00000">内核中的驱动需要维护一个结构体</font>(设为 `struct mdev_info` )<font color="#c00000">去存储与该</font> `fd` <font color="#c00000">相关的数据结构</font>，用于完成后续的 `read` 、 `write` 等操作。
4. 用户调用 `close` 关闭设备之前，允许用户调用 `read` 、 `write` 等操作。
5. 用户在调用 `close` 完全关闭所有对该设备的打开后， `f_op->release` 会被执行。
6. 当用户调用 `close` 关闭设备时，后续的 `read` 、 `write` 等均会被拒绝，<font color="#c00000">但是在调用</font> `close` <font color="#c00000">前的所有未完成的操作仍需要正常执行</font>。

那么考虑如下的问题：
1. 在内核中的驱动正在响应用户的操作请求<font color="#c00000">的</font><span style="background:#fff88f"><font color="#c00000">过程中</font></span>， `f_op->release` 被调用，那么仍在处理的操作请求如何完成？
	1. 明显地，直接在 `f_op->release` 中释放 `struct mdev_info` 将无法保证正在执行的操作会被顺利完成，例如下方代码中，在完成 `mdev_read` 中的 `do_operation1` 后被下处理器，并完成 `mdev_release` 函数，随后 `do_operation2` 就会触发错误：
	```C
static ssize_t mdev_read(struct file *filep, char __user *buf, size_t count, loff_t *ppos)
{
	// 1. 获取info数据结构
	struct mdev_info *mdev_info_p = filep->private_data;

	// 2. 执行操作1
	do_operation1(mdev_info_p);

	// 3. 执行操作2
	do_operation2(mdev_info_p);

	return ...;
}

static int mdev_release(struct inode *node, struct file *filep)
{
	// [错误示范] 直接释放相关数据结构
	// 1. 获取info数据结构
	struct mdev_info *mdev_info_p = filep->private_data;

	// 2. 回收数据结构
	kfree(mdev_info_p);

	return 0;
}
	```
	2. 则此时可以考虑使用计数器的方式代替直接的 `free` 操作：
	```C
struct mdev_info {
	// ...

    // ref counter for mdev_info, used to complete incomplete requests.
    atomic_t ref_counts;
};

/**
 * @brief: add references to mdev_info.
 */
static void mdev_info_get(struct mdev_info *info)
{
	atomic_inc(&info->ref_counts);
}

/**
 * @brief: remove the reference to mpipe_info, andelease the memory space
 *          when the last reference is released.
 */
static void mdev_info_put(struct mdev_info *info)
{
    if(atomic_dec_and_test(&info->ref_counts))
    {
        vfree(info);
    }
}

static int mdev_open(struct inode *node, struct file *filep)
{
	//...

	// success.
	// 增加对该结构体的引用计数
	mdev_info_get(mdev_info);

	return 0;
}

static ssize_t mdev_read(struct file *filep, char __user *buf, size_t count, loff_t *ppos)
{
	// 1. 获取info数据结构
	struct mdev_info *mdev_info_p = filep->private_data;

	// 2. 增加引用计数器
	mdev_info_get(mdev_info);

	// 3. 执行操作1
	do_operation1(mdev_info_p);

	// 4. 执行操作2
	do_operation2(mdev_info_p);

	// 5. 解除引用奇数
	mdev_info_put(mdev_info);

	return ...;
}

static int mdev_release(struct inode *node, struct file *filep)
{
	// [错误示范] 普通计数器
	// 1. 获取info数据结构
	struct mdev_info *mdev_info_p = filep->private_data;

	// 2. 解除驱动对该info的引用计数
	mdev_info_put(mdev_info_p);

	return 0;
}
	```
	3. 但是依旧有问题，例如：
		1. 用户发起read请求，并执行到 `mdev_read` 的 `struct mdev_info *mdev_info_p = filep->private_data;` 处被下处理器，<font color="#c00000">此时引用计数器并未增加</font>。
		2. 随后内核处理用户的文件关闭请求，并完成 `mdev_release` 的执行。<font color="#c00000">此时引用计数器被成功归0</font>， `struct mdev_info` <font color="#c00000">被成功释放</font>。
		3.  `mdev_read` <font color="#c00000">继续执行</font>，<span style="background:#fff88f"><font color="#c00000">此时计数器为-1</font></span>，且需要访问的