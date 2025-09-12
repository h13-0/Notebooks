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

随后对于内核开发者，使用 `DEFINE_KFIFO(fifo, type, size)` 即可完成队列定义，其中：
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

正如数据结构子章节中所述，队列的大小必须大于2，且为2的整数幂。而由于环形队列




