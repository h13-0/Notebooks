#嵌入式 #Linux驱动开发 #操作系统 

## 目录

```toc

```

# 定义

`pr_fmt` 为内核模块定义打印tag的一种常用方式, <span style="background:#fff88f"><font color="#c00000">常用</font></span>使用方式如下：

```C
#define pr_fmt(fmt) ${TAG} ": " fmt
```

上述 `${TAG}` 通常为内核模块名等。该 `pr_fmt` 宏通常不会被内核模块开发者直接使用, 内核模块开发者通常使用 `pr_level` 进行日志输出, 即：

```C
pr_emerg(msg)
pr_alert(msg)
pr_crit(msg)
pr_err(msg)
pr_warning(msg)
pr_warn(msg)
pr_notice(msg)
pr_info(msg)
pr_debug(msg)
```

注：
1. 上述为<font color="#c00000">常用</font>使用方式，也就是说可以利用该宏实现任何想要的输出格式。
2. 由于实现原理所限, 该宏

## 应用

在 `drivers/i2c/i2c-core.c` 中可见如下应用：

```C
#define pr_fmt(fmt) "i2c-core: " fmt

...

pr_info("%s enter.\n", __func__);
```

## 原理

上述提到的给内核开发者使用的 `pr_level` 的若干API被定义在 `printk.h` 中, 

