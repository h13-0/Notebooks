#文档翻译 #Linux驱动开发 #操作系统

原文版本：Linux 6.8

## 翻译

如果要向内核添加新的ioctl，则应该使用 `<linux/ioctl.h>` 中定义的 `_IO` 宏

|       |     |                                                                           |
| ----- | --- | ------------------------------------------------------------------------- |
| _IO   | an  | ioctl with no parameters                                                  |
| _IOW  | an  | ioctl with write parameters (<font color="#c00000">copy_from_user</font>) |
| _IOR  | an  | ioctl with read parameters (<font color="#c00000">copy_to_user</font>)    |
| _IOWR | an  | ioctl with both write and read parameters.                                |
上述的 `read` 和 `write` 应当像普通系统调用的命名规则一样，针对用户态视角来进行设计，而不是内核态视角。例如名为 `SET_FOO` 的cmd应当选用 `_IOW` ，<font color="#c00000">因为其数据是从用户空间传向内核空间的</font>(<font color="#c00000">copy_from_user</font>)、该指令以用户视角是写入，以内核视角是读取。而名为 `GET_FOO` 的cmd应当选用 `_IOR` ，因为其数据流向为内核空间到用户空间。

`_IO` 、 `_IOW` 、 `_IOR` 或 `_IOWR` 的第一个参数(即 `type` 字段，[注1](ioctl-number.rst#^q5ti6p))是下方表格中的识别 `letter` 或 `number` 。由于驱动类型众多，许多驱动与其他驱动共用一个 `letter` 。

如果您正在为一个新设备编写驱动程序，并且需要一个 `letter` ，请选择一个有足够扩展空间的未使用块：32到256的ioctl命令。您可以通过修补这个文件并将修补程序提交给 Linus Torvalds 来注册这个块。或者你可以发电子邮件给我(mec@shout.net)，我会为你注册一个

## 补充

1. 在 `<asm-generic/ioctl.h>` 中，这类宏的定义为： ^q5ti6p
```C
/*
 * Used to create numbers.
 *
 * NOTE: _IOW means userland is writing and kernel is reading. _IOR
 * means userland is reading and kernel is writing.
 */
#define _IO(type,nr)		_IOC(_IOC_NONE,(type),(nr),0)
#define _IOR(type,nr,size)	_IOC(_IOC_READ,(type),(nr),(_IOC_TYPECHECK(size)))
#define _IOW(type,nr,size)	_IOC(_IOC_WRITE,(type),(nr),(_IOC_TYPECHECK(size)))
#define _IOWR(type,nr,size)	_IOC(_IOC_READ|_IOC_WRITE,(type),(nr),(_IOC_TYPECHECK(size)))
#define _IOR_BAD(type,nr,size)	_IOC(_IOC_READ,(type),(nr),sizeof(size))
#define _IOW_BAD(type,nr,size)	_IOC(_IOC_WRITE,(type),(nr),sizeof(size))
#define _IOWR_BAD(type,nr,size)	_IOC(_IOC_READ|_IOC_WRITE,(type),(nr),sizeof(size))
```

