---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 

# 1 目录

```toc
```

# 2 常见格式及区别

## 2.1 vmlinux

vmlinux是内核源码编译出来的原始文件，elf格式，未压缩处理

## 2.2 Image



## 2.3 Image.gz



## 2.4 zImage

使用gzip压缩Image后，添加了解压功能头的格式


## 2.5 uImage

在zImage前添加一个64字节的头，描述文件类型、加载位置和大小等信息，适用于老版本uboot的引导镜像。


