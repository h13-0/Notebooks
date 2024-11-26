---
number headings: auto, first-level 2, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发 

## 1 目录

```toc
```

## 2 Readme

本笔记主要针对 `linux/fs/read_write.c` 中的系统调用进行分析。

## 3 系统调用及其分析

### 3.1 read ^4c1l78

`read` 系统调用的基本处理流程如下：
1. `sys_read` 直接调用返回 `ssize_t ksys_read(unsigned int fd, char __user *buf, size_t count)` ：
	1. 调用 `fdget_pos` 从 `int` 类型的 `fd` 转换为用户所打开的文件结构体对象 `struct fd` 。
		- `struct fd` 定义如下：
		```C
struct fd {
	struct file *file;
	unsigned int flags;
};
		```
	2. 当 `.file != NULL` 时：
		1. 使用 `file_ppos` 获取当前文件的偏移量
		2. 调用 `ssize_t vfs_read(struct file *file, char __user *buf, size_t count, loff_t *pos)` ：
			1. 使用 `file->f_mode` 判定文件是否可读，否则返回 `-EBADF` 。
			2. 使用 `file->f_mode` 判定打开方式是否可读，否则返回 `-EINVAL` 。
			3. 使用 `access_ok` 判定进程是否有权访问传来的<font color="#c00000">内存区域</font>，否则返回 `-EFAULT` 。
			4. 使用 `rw_verify_area` 判定进程访问的<font color="#c00000">文件区域</font>是否可读，否则原值返回该函数的值。
			5. 调用 `f_op->read` ，如果没有定义 `f_op->read` 则调用 `f_op->read_iter` 。若都未定义则返回 `-EINVAL` 。
			6. 当读取字节数大于0时，调用 `fsnotify_access` 告知事件监听系统该文件已被读取。
			7. 当读取字节数大于0时，调用 `add_rchar` 增肌进程的读取字节数计数器。
			8. 调用 `inc_syscr` 增加进程的读操作次数计数器。
		3. 更新文件偏移量
	3. 若 `.file == NULL` ，则返回 `-EBADF` 。

