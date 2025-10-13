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
该镜像不可用作引导，可以使用 `readelf` 、 `nm` 、 `objdump` 等工具对其符号进行分析和调试，其包含全部符号与调试信息，`System.map` 也是从此处提取。

## 2.2 vmlinuz

是<font color="#c00000">x86上的可引导的、压缩的内核</font>，添加l。z表示 `zip` 。

## 2.3 bzImage

即 `big zImage` ，是x86的新格式的内核镜像，用于引导更大的内核。

## 2.4 Image

使用 `objcopy` 处理vmlinux后生成的<font color="#c00000">ARM/ARM64平台的</font>二进制内核镜像，未压缩，<font color="#c00000">可以用引导启动</font>。

## 2.5 Image.gz

是Image的压缩版本，可用于ARM64 u-boot和fastboot引导

## 2.6 zImage

使用gzip压缩Image后，添加了解压功能头的格式

## 2.7 uImage

在zImage前添加一个64字节的头，描述文件类型、加载位置和大小等信息，适用于<font color="#c00000">老版本</font>uboot的引导镜像，通常用于ARM和MIPS架构。


# 3 

## 3.1 initrd

引导时的临时根文件系统，可压缩