---
number headings: auto, first-level 1, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发 

# 1 目录

```toc
```

# 2 数据结构与定义

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

随后对于内核开发者，使用 `DEFINE_KFIFO(fifo, type, size)` 即可完成队列定义：

```C
/**
 * DEFINE_KFIFO - macro to define and initialize a fifo
 * @fifo: name of the declared fifo datatype
 * @type: type of the fifo elements
 * @size: the number of elements in the fifo, this must be a power of 2
 *
 * Note: the macro can be used for global and local fifo data type variables.
 */
#define DEFINE_KFIFO(fifo, type, size) \
	DECLARE_KFIFO(fifo, type, size) = \
	(typeof(fifo)) { \
		{ \
			{ \
			.in	= 0, \
			.out	= 0, \
			.mask	= __is_kfifo_ptr(&(fifo)) ? \
				  0 : \
				  ARRAY_SIZE((fifo).buf) - 1, \
			.esize	= sizeof(*(fifo).buf), \
			.data	= __is_kfifo_ptr(&(fifo)) ? \
				NULL : \
				(fifo).buf, \
			} \
		} \
	}
```

其中：
- `fifo` 为队列名
- `type` 为队列存储的元素类型
- `size` 为队列大小
随后该宏会生成如下的定义代码：

```C
struct {
	union {
		struct __kfifo	kfifo;
		type		*type;
		const type	*const_type;
		char		(*rectype)[0];
		type		*ptr;
		type const	*ptr_const;
	}
} fifo = (typeof(fifo)) {
{ 
    {
        .in    = 0, \  
               .out   = 0, \  
               .mask  = __is_kfifo_ptr(&(fifo)) ? \  
                        0 : \  
                        ARRAY_SIZE((fifo).buf) - 1, \  
               .esize = sizeof(*(fifo).buf), \  
               .data  = __is_kfifo_ptr(&(fifo)) ? \  
                      NULL : \  
                      (fifo).buf, \  
               } \  
        } \  
}



```




