#文档翻译 #Linux驱动开发 #操作系统

原文版本：Linux 6.8

## 翻译

如果要向内核添加新的ioctl，则应该使用 `<linux/ioctl.h>` 中定义的 `_IO` 宏

|       |     |                                                                           |
| ----- | --- | ------------------------------------------------------------------------- |
| _IO   | an  | ioctl with no parameters                                                  |
| _IOW  | an  | ioctl with write parameters (<font color="#c00000">copy_from_user</font>) |
| _IOR  | an  | ioctl with read parameters (<font color="#c00000">copy_to_user</font>)                                 |
| _IOWR | an  | ioctl with both write and read parameters.                                |
上述的 `read` 和 `write` 应当像普通系统调用的命名规则一样，针对用户态视角来进行设计，而不是内核态视角。例如名为 `SET_FOO` 的cmd应当选用 `_IOW` ，<font color="#c00000">因为其数据是从用户态传向内核态的</font>。




