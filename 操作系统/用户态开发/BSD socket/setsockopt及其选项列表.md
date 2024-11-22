---
number headings: auto, first-level 2, max 6, 1.1
---
#BSD_Socket

## 1 目录

```toc
```

## 2 setsockopt函数概述


## 3 setsockopt选项列表

本章节已开启链接，如非必要请勿修改章节名称、序号和文档名。

### 3.1 SO_REUSEADDR 端口复用

已验证的支持平台：
- Linux
- Windows

开启该选项后：
- 允许多个<font color="#c00000">开启了端口复用的</font>进程重复打开该端口
- 在多个进程同时打开该端口后，每个进程<font color="#c00000">均有可能收到来自该端口的请求</font>

使用场景：
- 在程序崩溃或被强制结束时，其所绑定的某一端口上可能会留存有未被来得及关闭的连接。此时若有新的进程尝试重新绑定该端口，则可能遇到端口仍然被占用的错误。则此时使用本option可解决此问题。





