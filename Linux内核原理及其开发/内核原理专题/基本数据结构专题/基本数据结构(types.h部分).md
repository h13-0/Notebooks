---
number headings: auto, first-level 1, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发


# 1 目录

```toc
```

# 2 Readme

本笔记仅记录 `include/linux/types.h` 下定义的基本数据结构及其设计。

# 3 通用接口

## 3.1 获取容器指针(container_of)

`container_of` 的定义如下：

```C
/**
 * container_of - cast a member of a structure out to the containing structure
 * @ptr:	the pointer to the member.
 * @type:	the type of the container struct this is embedded in.
 * @member:	the name of the member within the struct.
 *
 */
#define container_of(ptr, type, member) ({			\
	const typeof( ((type *)0)->member ) *__mptr = (ptr);	\
	(type *)( (char *)__mptr - offsetof(type,member) );})
```

其在使用时只需要分别填入指针、类型和成员即可，例如：

```C
struct base {
	int prop;
}

struct base *prop2base(int *prop)
{
	return container_of(prop, struct base, prop);
}
```

需要注意的是，其可以<span style="background:#fff88f"><font color="#c00000">连续跨越多级</font></span><font color="#c00000">获得更高级的容器</font>，例如：

```C
// 基础类
struct base {
	int prop;
}

// 拓展类
struct advance {
	struct base base_mem;
	int ...;
}

// 拓展类实例
struct advance instance = { 0 };

// 基础类成员指针
int *prop = &instance.base_mem.prop;
```

现在我们想由这个基础类成员指针获取拓展类容器，则可以直接：

```C
// 连续跨越多级获取容器
struct advance *prop2advance(int *prop)
{
	return container_of(prop, struct advance, base_mem.prop);
}

struct advance *container = prop2advance(prop);
```

# 4 原子变量(atomic_t)

## 4.1 相关API

### 4.1.1 初始化原子变量(atomic_init)


### 4.1.2 读取原子变量(atomic_read)

```C
/**
 * atomic_read() - atomic load with relaxed ordering
 * @v: pointer to atomic_t
 *
 * Atomically loads the value of @v with relaxed ordering.
 *
 * Unsafe to use in noinstr code; use raw_atomic_read() there.
 *
 * Return: The value loaded from @v.
 */
static __always_inline int
atomic_read(const atomic_t *v)
```


### 4.1.3 设置原子变量(atomic_set)



### 4.1.4 加法运算(atomic_add)



### 4.1.5 减法运算(atomic_sub)



### 4.1.6 自增运算(atomic_inc)



### 4.1.7 自减运算(atomic_dec)

### 4.1.8 位运算并返回


### 4.1.9 位运算不返回
















