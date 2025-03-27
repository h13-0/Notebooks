---
number headings: auto, first-level 2, max 6, 1.1
---
#Linux用户态开发 

## 1 目录

```toc
```

## 2 函数原型及用户态调用

mmap即内存映射技术，其可以将物理文件-内存区域或内存区域-内存区域之间建立映射关系。
#TODO 


```C
#include <sys/mman.h>

void *mmap(void addr[.length], size_t length, int prot, int flags,
    int fd, off_t offset);

int munmap(void addr[.length], size_t length);
```






