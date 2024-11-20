---
number headings: auto, first-level 2, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发


## 1 目录

```toc
```

## 2 Readme

本笔记仅记录 `include/linux/types.h` 下定义的基本数据结构及其设计。

## 3 链表锚点 ^xl7wru

### 3.1 双向链表锚地(struct list_head)

本笔记所述头文件下定义了如下的双向链表锚点：

```C
struct list_head {
	struct list_head *next, *prev;
};
```

与普通的链表定义不同的是，链表锚点并不

### 3.2 单向链表








