---
number headings: auto, first-level 1, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发 

# 1 目录

```toc
```

# 2 数据结构与机制

## 2.1 数据结构

在内核中，`kfifo` <font color="#c00000">并不像</font> `list_head` <font color="#c00000">一样有通用的数据结构</font>。`kfifo` 选择了<font color="#c00000">为每一个队列实例都创建一个匿名结构体类型</font>。

在内核中，其先定义了一个私有的结构体类型 `struct __kfifo` ：

```C
struct __kfifo {
	unsigned int	in;    // 入队偏移量(指在data中的偏移量)
	unsigned int	out;   // 出队偏移量
	unsigned int	mask;  // 环形缓冲区的大小掩码
	unsigned int	esize; // 单个元素的大小
	void			*data; // 环形缓冲区内存指针
};
```

随后对于内核开发者，使用 `DEFINE_KFIFO(fifo, type, size)` 即可完成队定义，其中：
- `fifo` 为队列名
- `type` 为队列存储的元素类型
- `size` 为队列大小，<font color="#c00000">其值必须大于2</font>，<font color="#c00000">且为2的整数幂</font>
随后该宏会生成如下的定义代码：

```C
struct {     						// 匿名结构体
	union {
		struct __kfifo	kfifo;
		type		*type;  		// 运行时不会被使用，仅用于编译时静态类型检查
		const type	*const_type;	// 运行时不会被使用
		char		(*rectype)[0];	// 运行时不会被使用
		type		*ptr;			// 运行时不会被使用
		type const	*ptr_const;		// 运行时不会被使用
	};
	type buf[((size < 2) || (size & (size - 1))) ? -1 : size];
} fifo = (typeof(fifo)) 
{
	{ 
	    {
	        .in    = 0,
	        .out   = 0,
	        .mask  = __is_kfifo_ptr(&(fifo)) ? 0 : ARRAY_SIZE((fifo).buf) - 1,  
	        .esize = sizeof(*(fifo).buf),  
	        .data  = __is_kfifo_ptr(&(fifo)) ? NULL : (fifo).buf, 
	    }
	}  
}
```

其中：
- 在 `kfifo` 的后续API设计中，其大量使用了宏函数，因此 `union.type` 、 `union.const_type` 等成员均用于宏函数的类型检查：
	- `typeof(*__tmp->const_type) __val = (val);` (但是 `__val` 后续并没有被使用)
	- 上述宏指令实际上并不会做任何事情，但当传入的数据与队列元素数据类型不符时，编译器就会报错。
- 在创建环形静态缓冲区时，`type buf[((size < 2) || (size & (size - 1))) ? -1 : size];` <font color="#c00000">做了如下限制</font>：
	1. <font color="#c00000">队列大小必须大于2</font>
	2. <font color="#c00000">队列大小必须是2的幂</font>
	<font color="#c00000">否则编译时会报错</font>。
- 宏 `__is_kfifo_ptr` 用于判定环形队列中，数组是寄存在结构体中还是外部空间中

## 2.2 队列机制

正如数据结构子章节中所述，队列的大小必须大于2，且为2的整数幂。而由于环形队列的引索到达末尾后需要回绕到前部，现在考虑如下几种实现方式：

```C
// 使用位掩码实现(当且仅当size为2的整数幂时可用)
unsigned int index = current_index;
unsigned int next_index = (index + 1) & mask; // 等价于 (index + 1) % size

// 普通的取余
unsigned int next_index = (index + 1) % size;

// if判断法
unsigned int next_index = index + 1 < size ? 0 : index + 1;
```

那么明显的位掩码的效率更高。

<font color="#c00000">需要注意</font>：`kfifo` <span style="background:#fff88f"><font color="#c00000">并非线程安全</font></span>

# 3 相关API

## 3.1 声明fifo(DECLARE_KFIFO)

```C
/**
 * DECLARE_KFIFO - macro to declare a fifo object
 * @fifo: name of the declared fifo
 * @type: type of the fifo elements
 * @size: the number of elements in the fifo, this must be a power of 2
 */
#define DECLARE_KFIFO(fifo, type, size)	STRUCT_KFIFO(type, size) fifo
```

该宏函数：
- 功能含义：声明一个内嵌数组的FIFO结构体变量
- 参数：
	- `fifo` 为队列名
	- `type` 为队列存储的元素类型
	- `size` 为队列大小，<font color="#c00000">其值必须大于2</font>，<font color="#c00000">且为2的整数幂</font>
- 注意：
	- 该宏只声明一个fifo对象，但并不初始化其成员值。
	- 需要使用 `INIF_KFIFO` 初始化。
	- <font color="#c00000">通常用于嵌入结构体中</font>。
		- `DECLARE_KFIFO` <span style="background:#fff88f"><font color="#c00000">已经声明了缓冲区大小</font></span>，<font color="#c00000">在定义结构体时会在结构体内部直接占用对应大小的缓冲区</font>，随后使用 `INIF_KFIFO` 初始化即可，不用担心缓冲区分配到某个函数栈上(这也是其和 `DECLARE_KFIFO_PTR` 的区别)。
	- 此时的kfifo的结构本身是静态定义的。

## 3.2 声明fifo指针(DECLARE_KFIFO_PTR)

```C
/**
 * DECLARE_KFIFO_PTR - macro to declare a fifo pointer object
 * @fifo: name of the declared fifo
 * @type: type of the fifo elements
 */
#define DECLARE_KFIFO_PTR(fifo, type)	STRUCT_KFIFO_PTR(type) fifo
```

该宏函数：
- 功能含义：
- 注意：
	- 该函数与 `DECLARE_KFIFO` 的区别仅在于 `DECLARE_KFIFO` <font color="#c00000">得到的队列缓冲区在结构体内部</font>，`DECLARE_KFIFO_PTR` <font color="#c00000">得到的队列不包含缓冲区</font>，<font color="#c00000">需要后续分配</font>。
	- 需要使用 `kfifo_alloc` 初始化。
	- 此时的kfifo的结构本身是静态定义的。

## 3.3 定义fifo(DEFINE_KFIFO)

```C
/**
 * DEFINE_KFIFO - macro to define and initialize a fifo
 * @fifo: name of the declared fifo datatype
 * @type: type of the fifo elements
 * @size: the number of elements in the fifo, this must be a power of 2
 *
 * Note: the macro can be used for global and local fifo data type variables.
 */
#define DEFINE_KFIFO(fifo, type, size)
```

该宏函数：
- 功能含义：定义并初始化一个内嵌数组的FIFO
	- 该宏一次性完成声明和初始化，是最常用的方式

## 3.4 初始化fifo(INIT_KFIFO)

```C
/**
 * INIT_KFIFO - Initialize a fifo declared by DECLARE_KFIFO
 * @fifo: name of the declared fifo datatype
 */
#define INIT_KFIFO(fifo)
```

该宏函数：
- 功能含义：<font color="#c00000">初始化一个</font><span style="background:#fff88f"><font color="#c00000">使用</font></span> `DECLARE_KFIFO` <span style="background:#fff88f"><font color="#c00000">声明的队列</font></span>
- 注意：
	- `DECLARE_KFIFO` <span style="background:#fff88f"><font color="#c00000">已经声明了缓冲区大小</font></span>，<font color="#c00000">也就是该函数实际上不会分配空间</font>，即不用担心如下的情况：
```C
struct my_device {
    struct spinlock lock;
    // ... 其他成员
    DECLARE_KFIFO(fifo, u8, 256); // 直接内嵌定义并初始化
};

// 在此步就已经为缓冲区静态分配空间了
static my_device dev;

int my_func(){
    INIT_KFIFO(dev.fifo); // 不用担心缓冲区在 `my_func` 的栈上。
    ...
}
```


## 3.5 为fifo指针动态分配内存(kfifo_alloc)

```C
/**
 * kfifo_alloc - dynamically allocates a new fifo buffer
 * @fifo: pointer to the fifo
 * @size: the number of elements in the fifo, this must be a power of 2
 * @gfp_mask: get_free_pages mask, passed to kmalloc()
 *
 * This macro dynamically allocates a new fifo buffer.
 *
 * The number of elements will be rounded-up to a power of 2.
 * The fifo will be release with kfifo_free().
 * Return 0 if no error, otherwise an error code.
 */
#define kfifo_alloc(fifo, size, gfp_mask)
```

该宏函数：
- 功能含义：为使用外部缓冲区的kfifo动态分配内存
	- 其中，`size` 可以不是2的整数幂，但是会被向上取到整数幂(所以没有实际意义)
- 返回值：返回0表示成功

## 3.6 使用预分配的缓存初始化fifo(kfifo_init)

```C
/**
 * kfifo_init - initialize a fifo using a preallocated buffer
 * @fifo: the fifo to assign the buffer
 * @buffer: the preallocated buffer to be used
 * @size: the size of the internal buffer, this have to be a power of 2
 *
 * This macro initializes a fifo using a preallocated buffer.
 *
 * The number of elements will be rounded-up to a power of 2.
 * Return 0 if no error, otherwise an error code.
 */
#define kfifo_init(fifo, buffer, size)
```

该宏函数：
- 功能含义：类似于 `kfifo_alloc` ，但使用用户提前分配好的 `buffer` ，而非重新分配
- 返回值：返回0表示成功
- 注意：
	- `size` 必须为2的整数幂

## 3.7 释放fifo的缓冲区(kfifo_free)

```C
/**
 * kfifo_free - frees the fifo
 * @fifo: the fifo to be freed
 */
#define kfifo_free(fifo)
```

该宏函数：
- 功能含义：释放通过 `kfifo_alloc` 分配的缓冲区
- 注意：
	- 只释放fifo的缓冲区(`fifo->data`)，不释放fifo结构本身(fifo结构本身基本上都是静态分配的)。

## 3.8 检查fifo是否被初始化

```C
/**
 * kfifo_initialized - Check if the fifo is initialized
 * @fifo: address of the fifo to check
 *
 * Return %true if fifo is initialized, otherwise %false.
 * Assumes the fifo was 0 before.
 */
#define kfifo_initialized(fifo) ((fifo)->kfifo.mask)
```

该宏函数：
- 功能含义：检查fifo是否被初始化
- 返回值：已初始化返回 `true` ，否则返回 `false`

## 3.9 获取fifo的容量(kfifo_size)

```C
/**
 * kfifo_size - returns the size of the fifo in elements
 * @fifo: address of the fifo to be used
 */
#define kfifo_size(fifo)	((fifo)->kfifo.mask + 1)
```

该宏函数：
- 功能含义：获取fifo的容量
- 返回值：容量

## 3.10 获取fifo中已入队元素个数(kfifo_len)

```C
/**
 * kfifo_len - returns the number of used elements in the fifo
 * @fifo: address of the fifo to be used
 */
#define kfifo_len(fifo)
```

该宏函数：
- 功能含义：获取fifo中已入队元素个数
- 返回值：已入队元素个数

## 3.11 获取fifo的空闲容量(kfifo_avail)

## 3.12 判断fifo是否为空(kfifo_is_empty)

## 3.13 判断fifo是否为满(kfifo_is_full)

## 3.14 向fifo中添加元素(kfifo_put)

```C
/**
 * kfifo_put - put data into the fifo
 * @fifo: address of the fifo to be used
 * @val: the data to be added
 *
 * This macro copies the given value into the fifo.
 * It returns 0 if the fifo was full. Otherwise it returns the number
 * processed elements.
 *
 * Note that with only one concurrent reader and one concurrent
 * writer, you don't need extra locking to use these macro.
 */
#define	kfifo_put(fifo, val)
```

该宏函数：
- 功能含义：向fifo中添加元素(入队)
- 参数：
	- `fifo` ：所使用的fifo<font color="#c00000">的地址</font>
	- `val` ：要放入的值
- 返回值：<font color="#c00000">成功时返回1</font>，失败时返回0(队满)

## 3.15 从fifo中取出元素(kfifo_get)

```C
/**
 * kfifo_get - get data from the fifo
 * @fifo: address of the fifo to be used
 * @val: address where to store the data
 *
 * This macro reads the data from the fifo.
 * It returns 0 if the fifo was empty. Otherwise it returns the number
 * processed elements.
 *
 * Note that with only one concurrent reader and one concurrent
 * writer, you don't need extra locking to use these macro.
 */
#define	kfifo_get(fifo, val)
```

该宏函数：
- 功能含义：从fifo中取出单个元素
- 参数：
	- `fifo` ：所使用的fifo<font color="#c00000">的地址</font>
	- `val` ：<font color="#c00000">存放取出元素的地址</font>
- 返回值：<font color="#c00000">成功时返回1</font>，失败时返回0(队空)

## 3.16 查看fifo的下一个元素但不取出(kfifo_peek)


## 3.17 向fifo中添加若干个元素(kfifo_in)

```C
/**
 * kfifo_in - put data into the fifo
 * @fifo: address of the fifo to be used
 * @buf: the data to be added
 * @n: number of elements to be added
 *
 * This macro copies the given buffer into the fifo and returns the
 * number of copied elements.
 *
 * Note that with only one concurrent reader and one concurrent
 * writer, you don't need extra locking to use these macro.
 */
#define	kfifo_in(fifo, buf, n)
```

该宏函数：
- 功能含义：向fifo中添加若干个元素
- 参数：
	- `fifo` ：所使用的fifo<font color="#c00000">的地址</font>
	- `buf` ：要添加的元素所在数组(连续内存)
	- `n` ：要添加的元素个数
- 返回值：<font color="#c00000">实际添加的元素个数</font>

## 3.18 从fifo中取出若干个元素(kfifo_out)

```C
/**
 * kfifo_out - get data from the fifo
 * @fifo: address of the fifo to be used
 * @buf: pointer to the storage buffer
 * @n: max. number of elements to get
 *
 * This macro gets some data from the fifo and returns the numbers of elements
 * copied.
 *
 * Note that with only one concurrent reader and one concurrent
 * writer, you don't need extra locking to use these macro.
 */
#define	kfifo_out(fifo, buf, n)
```

该宏函数：
- 功能含义：从fifo中取出若干个元素
- 参数：
	- `fifo` ：所使用的fifo<font color="#c00000">的地址</font>
	- `buf` ：要取出元素寄存的地址
	- `n` ：要取出的元素个数
- 返回值：<font color="#c00000">实际取出的元素个数</font>

## 3.19 查看队头若干个元素但不取出(kfifo_out_peek)



