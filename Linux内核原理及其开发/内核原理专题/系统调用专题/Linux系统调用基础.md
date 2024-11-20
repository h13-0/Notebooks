---
number headings: auto, first-level 2, max 6, 1.1
---
#操作系统 #Linux系统原理 #Linux内核开发

## 1 目录

```toc
```

## 2 Readme


## 3 Linux系统调用名称及其定义方式

在Linux系统中，系统调用在其内核中的入口函数名格式均为 `sys_${func_name}` ，例如 `read` 函数在内核中的入口函数名为 `sys_read` 。

而在内核中，其使用 `include/linux/syscall.h` 中如下的宏定义进行定义：

```C
#define SYSCALL_DEFINE1(name, ...) SYSCALL_DEFINEx(1, _##name, __VA_ARGS__)  
#define SYSCALL_DEFINE2(name, ...) SYSCALL_DEFINEx(2, _##name, __VA_ARGS__)  
#define SYSCALL_DEFINE3(name, ...) SYSCALL_DEFINEx(3, _##name, __VA_ARGS__)  
#define SYSCALL_DEFINE4(name, ...) SYSCALL_DEFINEx(4, _##name, __VA_ARGS__)  
#define SYSCALL_DEFINE5(name, ...) SYSCALL_DEFINEx(5, _##name, __VA_ARGS__)  
#define SYSCALL_DEFINE6(name, ...) SYSCALL_DEFINEx(6, _##name, __VA_ARGS__)
```

在上述的 `SYSCALL_DEFINE${n}` 的格式中，最后跟随的参数 `${n}` 表示该系统调用的参数个数。