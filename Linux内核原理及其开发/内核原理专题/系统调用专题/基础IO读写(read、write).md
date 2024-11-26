---
number headings: auto, first-level 2, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发 

## 1 目录

```toc
```

## 2 Readme


## 3 系统调用及其分析

### 3.1 read

`read` 系统调用被定义在 `linux/fs/read_write.c` 中，其基本处理流程如下：
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
			3. 使用 `access_ok` 判定用户传来的内存区域是否可访问，否则返回 `-EFAULT` 。
			4. 
		3. 更新文件偏移量
	3. 若 `.file == NULL` ，则返回 `-EBADF` 。

