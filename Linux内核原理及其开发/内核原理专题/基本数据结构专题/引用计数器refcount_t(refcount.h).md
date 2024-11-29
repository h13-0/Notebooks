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
	- 明显地，直接在 `f_op->release` 中释放 `struct mdev_info` 将无法保证正在执行的操作会被顺利完成，例如：
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

	// 2. 挥手
	kfree
```

