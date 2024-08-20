#嵌入式 #Linux驱动开发 #操作系统 

## 目录

```toc

```

# 定义

`pr_fmt` 为内核模块定义打印tag的一种常用方式, 使用方式如下：

```C
#define pr_fmt(fmt) ${TAG} ": " fmt
```

上述 `${TAG}` 通常为内核模块名等。该 `pr_fmt` 宏通常不会被内核模块开发者直接使用, 内核模块开发者通常使用 `pr_level` 进行日志输出，即：


## 应用

在 `drivers/i2c/i2c-core.c` 中可见如下应用：

```C
#define pr_fmt(fmt) "i2c-core: " fmt

...

pr_info("%s enter.\n", __func__);
```

## 原理



