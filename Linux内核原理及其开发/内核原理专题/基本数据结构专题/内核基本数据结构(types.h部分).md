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
	- 优点：不使用宏。
	- 缺点：所有链表的类型均会被统一为同一个链表类型，例如 `list_t` 。
2. 设计链表锚点：
	1. 在链表锚点内部定义数据引索指针，例如 `*next` 、 `*prev` 等指针，例如：
	```C
struct list_head {
	struct list_head *next, *prev;
};
	```
	2. 将链表锚点添加到需要托管的链表节点的结构体中，例如：
	```C
struct my_data_list {
    int data;
    struct list_head list;
};
	```
	3. 则此时可以使用 `.list` 成员找到上一个或下一个链表节点的 `.list` 成员。<font color="#c00000">但是此时的问题是如何使用</font> `.list` <font color="#c00000">成员完成获取链表的节点等操作</font>。
	4. 此时就可以考虑使用宏函数 `container_of` 等方法解决上述问题，例如：
		- <font color="#c00000">通过宏自动计算字段在结构体中的偏移量来获取整个结构体的地址</font>。
	- 优点：任何一个链表都可以定义为其自己的类型，这在大型项目中想当有用。
	- 缺点：使用了宏。

### 3.1 双向链表锚地(struct list_head)

```C
struct list_head {
	struct list_head *next, *prev;
};
```



### 3.2 单向链表








