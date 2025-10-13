---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 

# 1 目录

```toc
```

# 2 常见格式及区别

## 2.1 vmlinux

vmlinux是<font color="#c00000">内核源码编译出来的原始文件</font>，elf格式，未压缩处理。vm是指虚拟内存(即用硬盘空间做内存)。
该镜像不可用作引导，可用于定位内核问题


## 2.2 Image

使用 `objcopy` 处理vmlinux后生成的二进制内核镜像，未压缩，可以用引导启动。

## 2.3 Image.gz



## 2.4 zImage

使用gzip压缩Image后，添加了解压功能头的格式

## 2.5 bzImage



## 2.6 uImage

在zImage前添加一个64字节的头，描述文件类型、加载位置和大小等信息，适用于<font color="#c00000">老版本</font>uboot的引导镜像。


## 2.7 vmlinuz

是可引导的、压缩的内核

# 3 

## 3.1 initrd

