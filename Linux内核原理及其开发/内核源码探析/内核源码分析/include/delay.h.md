#操作系统 #Linux系统原理 #Linux内核源码分析

# 目录

```toc
```

# mdelay

版本：`6.10.0-rc1` <!--格式要求见注1-->
原代码范围：`44-46` <!--方便章节排序-->
分析状态：⌛ <!--✅表示已处理完毕、⌛表示未处理完毕-->

函数签名： `#define mdelay(n)`
- 功能简述： ^he4myr
	- <span style="background:#fff88f"><font color="#c00000">忙等</font></span>指定毫秒数。<span style="background:#fff88f"><font color="#c00000">需要注意</font></span>，在Linux中：
		- `delay` 系函数为<font color="#c00000">忙等</font>，不会休眠，不会让出CPU。<span style="background:#fff88f"><font color="#c00000">可在</font></span>[[Linux驱动开发笔记#^fw453g|中断上下文]]<span style="background:#fff88f"><font color="#c00000">中使用</font></span>
		- `sleep` 系函数为<font color="#c00000">休眠</font>，不可在原子或中断上下文中使用。
- 参数：
	- `n` ：要等待的整数毫秒数，实际等待时间可能略多<font color="#c00000">而不会略少</font>
- 调用栈分析：
	1. 三元运算符判断+执行 `udelay` 

# ndelay

版本：`6.10.0-rc1` <!--格式要求见注1-->
原代码范围：`50-54` <!--方便章节排序-->
分析状态：⌛ <!--✅表示已处理完毕、⌛表示未处理完毕-->

函数签名： `void ndelay(unsigned long x)`
- 功能简述： ^a2f3jf
	- <font color="#c00000">忙等</font>指定纳秒。<span style="background:#fff88f"><font color="#c00000">需要注意</font></span>，在Linux中：
		- `delay` 系函数为<font color="#c00000">忙等</font>，不会休眠，不会让出CPU。<span style="background:#fff88f"><font color="#c00000">可在</font></span>[[Linux驱动开发笔记#^fw453g|中断上下文]]<span style="background:#fff88f"><font color="#c00000">中使用</font></span>
		- `sleep` 系函数为<font color="#c00000">休眠</font>，不可在原子或中断上下文中使用。
- 参数：
	- `unsigned long x` ：要等待的纳秒数，实际等待时间可能略多<font color="#c00000">而不会略少</font>
- 调用栈分析：
	1. 向上取整 $x/1000$ 
	2. 调用 `udelay` 等待对应微秒数

# msleep

该函数定义详见 ${定义处} 。


# usleep_range

版本：`6.10.0-rc1` <!--格式要求见注1-->
原代码范围：`66-69` <!--方便章节排序-->
分析状态：⌛ <!--✅表示已处理完毕、⌛表示未处理完毕-->

函数签名： `void usleep_range(unsigned long min, unsigned long max)`
- 功能简述： ^rbwl1s
	- 休眠一段时间，时长为指定范围，<font color="#c00000">单位微秒</font>
	- 具体休眠时长取决于调度器与系统负载，无严格数学分布
- 参数：
	- `unsigned long min` ：最短休眠时长
	- `unsigned long max` ：期望最大休眠时长(不严格保证)
- 调用栈分析：
	1. 调用 `usleep_range_state`

