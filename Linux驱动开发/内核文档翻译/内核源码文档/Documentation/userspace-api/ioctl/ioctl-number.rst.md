#文档翻译 #Linux驱动开发 #操作系统

原文版本：Linux 6.8

## 翻译

如果要向内核添加新的ioctl，则应该使用 `<linux/ioctl.h>` 中定义的 `_IO` 宏

|       |     |                                              |
| ----- | --- | -------------------------------------------- |
| _IO   | an  | ioctl with no parameters                     |
| _IOW  | an  | ioctl with write parameters (copy_from_user) |
| _IOR  | an  | ioctl with read parameters (copy_to_user)    |
| _IOWR | an  | ioctl with both write and read parameters.   |
上述的 `read` 和




