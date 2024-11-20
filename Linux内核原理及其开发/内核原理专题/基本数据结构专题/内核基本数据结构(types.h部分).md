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

在C语言大型项目中，<font color="#c00000">往往要使用类型想当繁多的链表</font>。<font color="#c00000">但是如果分别为每一个链表都加入增、删、改、查、搜索、排序等功能的话代码又显得相当繁琐</font>。因此需要将链表的常用操作统一拆分出来。

在面向对象语言中，可以考虑定义一个链表基类即可实现上述需求。但是C语言结构体并不具备面向对象的继承关系，因此在C语言中实现一个通用的链表通常使用如下两种方式实现：
1. 在通用链表中定义一个 `void *data` 成员，随后 `void *data` 交由开发者自行控制和处理。使用这种方法的例子有[clibs-list](https://github.com/clibs/list)。
	- 优点：不使用宏，
	- 缺点：所有链表的类型均会被统一为同一个链表类型，例如 `list_t` 。
2. 设计一个链表锚点



### 3.1 双向链表锚地(struct list_head)

本笔记所述头文件下定义了如下的双向链表锚点：

```C
struct list_head {
	struct list_head *next, *prev;
};
```

与普通的链表定义不同的是，普通链表在自身结构体内定义 `next` 等成员，并将数据荷载也定义在对应的结构体中。


### 3.2 单向链表








