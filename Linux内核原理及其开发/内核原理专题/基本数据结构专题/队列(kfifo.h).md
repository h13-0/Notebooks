---
number headings: auto, first-level 1, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发 

# 1 目录

```toc
```

# 2 数据结构与定义

在内核中，`kfifo` <font color="#c00000">并不像</font> `list_head` <font color="#c00000">一样有通用的数据结构</font>。`kfifo` 选择了<font color="#c00000">为每一个队列实例都创建一个匿名结构体类型</font>，

