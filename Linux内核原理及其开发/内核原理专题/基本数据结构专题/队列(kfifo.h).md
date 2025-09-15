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

## 3.7 释放fifo的缓冲区()

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
	- 只释放fifo的缓冲区(`fifo->data`)，不释放fifo结构本身。

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
- 

## 3.10 获取fifo中已入队元素个数(kfifo_len)
