---
number headings: auto, first-level 2, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发 

## 1 目录

```toc
```

## 2 Readme

本笔记主要针对 `linux/fs/open.c` 中的系统调用进行分析。

## 3 系统调用及其分析

### 3.1 open ^qyilk5

`open` 系统调用的基本处理流程如下：
1. 检测大文件支持；对于内核架构：
	1. 32位的内核需要检测在编译时是否将 `off_t` 配置为32位：
		1. 如果被配置为32位，即 `CONFIG_ARCH_32BIT_OFF_T` 被启用，则 `off_t` 最多支持2GB的偏移量。<font color="#c00000">若用户态程序想要读取大文件</font>，<font color="#c00000">则用户态需要显式定义</font> `_FILE_OFFSET_BITS=64` 或使用 `O_LARGEFILE` 标志来启用64位的`off_t` 。
		2. <font color="#c00000">如果未被配置为32位</font>，即 `CONFIG_ARCH_32BIT_OFF_T` 未启用，则<font color="#c00000">默认开启大文件模式</font>。
	2. 64位的内核通常无须配置该项，原生支持64位的 `off_t` ，默认开启大文件模式。
2. 调用返回 `long do_sys_open(int dfd, const char __user *filename, int flags, umode_t mode)` ：
	1. 调用 `build_open_how` 将用户态的 `umode_t` 转化为内核态的 `open_how` 结构体，同时过滤掉非法标志位或模式位。在该结构体中：
		1. 成员 `__u64 flags` ：表示用户态使用 `open` 时指定的行为，例如读写、文件创建、文件追加等。
		2. 成员 `__u64 mode` ：当需要创建文件时，文件的权限。不需要创建文件时该成员值为0。
		3. 成员 `__u64 resolve` ：指定用于路径解析的方式，例如禁止解析符号链接、避免跨越设备边界进行路径解析等。
	2. 调用返回 `static long do_sys_openat2(int dfd, const char __user *filename, struct open_how *how)` ：
		1. 调用 `build_open_flags` 将 `open_how` 转换为 `flags` ，同时进行大量的文件行为标识符、文件权限以及路径解析的方式的参数检查，如果失败则返回对应错误码。成功时返回0。
		2. 调用 `getname` 获取文件名，如果失败则返回对应错误码。
		3. 调用 `get_unused_fd_flags` 获取一个未使用的文件标识符。
		4. 当 `fd` 大于0时，调用 `struct file *do_filp_open(int dfd, struct filename *pathname, const struct open_flags *op)` 打开文件：
			1. 调用 `set_nameidata` 
			2. 调用 `struct file *path_openat(struct nameidata *nd, const struct open_flags *op, unsigned flags)` 打开文件：
				1. 调用 `alloc_empty_file` 创建一个空的文件对象( `struct file` )。
				2. 根据标识符选择打开临时文件、普通文件、创建文件夹等行为。
				3. 调用 `fput` 减少对文件对象的引用。
			3. 处理特殊错误。
			4. 调用 `restore_nameidata`
			5. 返回 `struct file` 对象。
		5. 当 `do_filp_open` 执行成功时，返回内核文件对象 `struct file` ，并调用 `fd_install` 向 `fd_table` 中添加一个 `fd` 及其对应的 `file` 对象。
		6. 当 `do_filp_open` 发生错误时，调用 `put_unused_fd` 归还未使用的 `fd` ，并用 `fd` 存放错误信息
		7. 返回第5或6步的 `fd` 。

### 3.2 close ^4b5xl4

`close` 系统调用的基本处理流程如下：
1. 调用 `struct file *file_close_fd(unsigned int fd);` ，从 `fdt` ( `fd_table` )中寻找 `fd` 对应的 `file` 结构体指针。 
2. 调用 `filp_flush` 刷新文件缓冲区。
	1. 检查文件计数器是否已经为0，如果发现已经为0，则输出错误信息，并<font color="#c00000">可选地使用</font> `BUG()` <font color="#c00000">停止系统</font>。
	2. 当设置了 `f_op->flush` 时调用 `f_op->flush` 。
	3. 检查文件是否为路径，如果是则：
		1. 调用 `dnotify_flush` 处理目录通知。
		2. 调用 `locks_remove_posix` 移除该文件的POSIX锁。
3. 调用 `void __fput_sync(struct file *);` <font color="#c00000">减少文件的引用计数器</font>(下面全都在干这个)，并当最后一个引用被释放时：
	1. 原子地减少引用计数。
	2. 当计数器为0时，调用 `void __fput(struct file *file)` 释放文件的最后一个引用：
		1. 检查该文件是否已经被成功打开，如果未被成功打开则直接释放 `struct file` 结构体。
		2. <font color="#7f7f7f">执行</font> `might_sleep` <font color="#7f7f7f">标注，该标注在release模式下无效，在调试模式下可以在原子上下文中捕获该标注，并打印堆栈等信息。</font>
		3. 调用 `fsnotify_close` 向监听者触发文件关闭事件。
		4. 调用 `eventpoll_release` 回收与 `epoll` 相关的资源。
		5. 调用 `locks_remove_file` 释放与该文件相关的所有锁。
		6. 调用 `security_file_release` ，该函数是Linux安全模块的钩子函数，允许安全模块对该事件的监听。
		7. <font color="#c00000">在文件开启了异步通知，并且驱动程序定义了</font> `f_op->fasync` <font color="#c00000">时，调用</font> `f_op->fasync` <font color="#c00000">将该文件从驱动程序的通知队列中移除</font>。
		8. <font color="#c00000">当驱动程序定义了</font> `f_op->release` <font color="#c00000">时，调用</font> `f_op->release` <font color="#c00000">释放文件</font>。
		9. 使用宏 `S_ISCHR` 检查 `inode` 是否是一个字符设备，如果满足如下若干条件则减少对字符设备的引用计数：
			1. 是一个字符设备。
			2. 该文件模式未设置为目录模式。
		10. 调用 `void module_put(struct module *module)` <font color="#c00000">减少对该文件的内核模块的引用计数</font>。
		11. 调用 `void put_pid(struct pid *pid)` 减少对该PID结构体的引用计数。
		12. 调用 `void put_file_access(struct file *file)` 减少对该文件的读取和写入计数器。
		13. 调用 `dput` 减少对该文件的目录项结构体( `struct dentry` )的引用。
		14. 检测该文件是否设置了 `FMODE_NEED_UNMOUNT` (是否需要取消挂载该挂载实例)，如果设置了则调用 `dissolve_on_fput` 取消挂载。
		15. 调用 `mntput` 减少对文件系统挂载实例( `struct vfsmount` )的引用。
		16. 调用 `file_free` 释放 `struct file` 结构体。
4. 检测 `filp_flush` 的特定错误。
5. 返回 `filp_flush` 的返回值。

需要注意的是：
1. 在Linux的相当多资源管理中，通常都不会直接立即释放某一资源。基本上都是通过引用计数器来释放，这样可以保证已经开始执行的操作正常的完成。

