---
number headings: auto, first-level 2, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发

## 1 目录

```toc
```

## 2 Readme


## 3 引用计数器

### 3.1 设计目的

例如需要实现一个可以被多线程读写的设备(可以直接使用该章节中的设备假设：[[Linux驱动开发笔记#^qdfcky]]），那么则有如下基础设定：
1. 用户态进程在尝试打开该文件后会得到一个文件描述符 `fd` 。
2. 用户可以通过该 `fd` 执行对设备读写和关闭操作。
3. 通常来说<font color="#c00000">内核中的驱动需要维护一个结构体</font>(设为 `struct mdev_info` )<font color="#c00000">去存储与该</font> `fd` <font color="#c00000">相关的数据结构</font>，用于完成后续的 `read` 、 `write` 等操作。
4. 用户调用 `close` 关闭设备之前，允许用户调用 `read` 、 `write` 等操作。
5. 用户在调用 `close` 完全关闭所有对该设备的打开后， `f_op->release` 会被执行。
6. 当用户调用 `close` 关闭设备时，后续的 `read` 、 `write` 等均会被拒绝，<font color="#c00000">但是在调用</font> `close` <font color="#c00000">前的所有未完成的操作仍需要正常执行</font>。

那么考虑如下的场景：

![[Linux驱动开发笔记#8 9 4 1 1 场景一：正在处理read的过程中，close被调用并执行完毕]]

那么明显地，现在内核需要一个更靠谱的引用计数方式。而在事实上， `refcount_t` 本质也只是使用了一个原子变量，其定义如下：

```C
/**
 * typedef refcount_t - variant of atomic_t specialized for reference counts
 * @refs: atomic_t counter field
 *
 * The counter saturates at REFCOUNT_SATURATED and will not move once
 * there. This avoids wrapping the counter and causing 'spurious'
 * use-after-free bugs.
 */
typedef struct refcount_struct {
	atomic_t refs;
} refcount_t;
```

### 3.2 操作流程及相关API

由于 `refcount_t` 只使用了一个原子变量，因此其操作的大致流程与原子变量几乎一致：
1. 声明 `refcount_t` ，略。
2. 定义 `refcount_t` ，使用


#### 3.2.1 设置引用次数refcount_set(refcount_t \*r, int n)









