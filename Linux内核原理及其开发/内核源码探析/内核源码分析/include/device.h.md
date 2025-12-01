#操作系统 #Linux系统原理 #Linux内核源码分析

# 目录

```toc
```

# devm_kzalloc

版本：`6.10.0-rc1` <!--格式要求见注1-->
原代码范围：`326-329` <!--方便章节排序-->
分析状态：⌛ <!--✅表示已处理完毕、⌛表示未处理完毕-->

函数签名： `void *devm_kzalloc(struct device *dev, size_t size, gfp_t gfp)`
- 功能简述： ^vkk5ej
	- 为设备对象分配零内存，<font color="#c00000">并将设备挂载到链表中</font>，<span style="background:#fff88f"><font color="#c00000">当设备释放或驱动解绑时自动释放内存</font></span>
		- 若使用 `kzalloc` ，<font color="#c00000">则需要在上述时机手动</font> `kfree` 。此外无区别
	- 其可以为私有设备类型分配内存，且无需将 `struct device *dev` 成员放到首个位置
- 参数：
	- `struct device *dev` ：需要进行资源记录(`devres`)的基础
	- `size_t size` ：${功能含义}
	- `gfp_t gfp`
- 调用栈分析：
	1. 调用并返回 `devm_kmalloc` ，并额外附加至零标记
