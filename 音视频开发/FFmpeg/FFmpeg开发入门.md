---
number headings: auto, first-level 1, max 6, 1.1
---
#音视频开发 

# 1 目录

```toc
```

# 2 概述

## 2.1 FFmpeg模块结构

FFmpeg主要有如下几个子模块：
- `libavcodec` ：提供了一系列编码器的实现
- `libavformat` ：提供了流协议、容器格式及基本IO访问
- `libavutil` ：提供了hasher、解码器和各种工具函数
- `libavfilter` ：提供了各种音视频过滤器
- `libavdevice` ：提供了访问捕获设备和回放设备的接口
- `libswresample` ：提供了混音和重采样
- `libswscale` ：提供了色彩转换和缩放功能



# 3 libavutil模块

## 3.1 FFmpeg日志系统的使用

FFmpeg日志系统的声明位于头文件 `libavutil/log.h` 其简易使用流程为：
1. [[音视频开发/FFmpeg/FFmpeg开发入门#^oxdoti|设置日志等级]]
2. [[音视频开发/FFmpeg/FFmpeg开发入门#^gsjiaj|输出日志]]

在FFmpeg中，日志等级有如下几种：
- `AV_LOG_QUIET` ：
- `AV_LOG_PANIC` ：
- `AV_LOG_FATAL` ：
- `AV_LOG_ERROR` ：
- `AV_LOG_WARNING` ：
- `AV_LOG_INFO` ：
- `AV_LOG_VERBOSE` ：
- `AV_LOG_DEBUG` ：
- `AV_LOG_TRACE` ：

### 3.1.1 常用API

#### 3.1.1.1 设置日志等级 ^oxdoti

```C
void av_log_set_level(int level)
```

#### 3.1.1.2 输出日志 ^gsjiaj

```C
void av_log(void *avcl, int level, const char *fmt,...)
```

其参数：
- `void *avcl` ：指向第一个字段为 `AVClass` 的结构体的指针，若为<font color="#c00000">常规日志则为</font> `NULL`
- `int level` ：日志等级
- `const char *fmt` ：格式化字符串
- `...` ：可变参数

# 4 libavformat模块

## 4.1 IO操作

FFmpeg的IO操作主要分为 `avio_*` 和 `ffurl_*` 这两个系列，其具体区别为：

|  特性  | <center>`avio_*`</center>                                               | <center>`ffurl_*`</center>              |
| :--: | ----------------------------------------------------------------------- | --------------------------------------- |
| 设计目的 | FFmpeg<font color="#c00000">为应用开发者提供的接口</font>                          | FFmpeg内部使用的接口                           |
| 缓冲区  | <font color="#c00000">默认带缓冲区</font>                                     | 不带缓冲区，直接操作IO                            |
|  性能  | <font color="#c00000">极快</font>，同时适合频繁小操作                               | 频繁小操作时速度慢                               |
| 数据感知 | <font color="#c00000">支持高级数据类型读写</font><br>(`int`、`string` 、` line ` 等) | <font color="#c00000">只支持处理原生字节流</font> |
| 底层依赖 | 依赖 `ffurl` 或用户回调                                                        | 依赖系统API                                 |

因此对于应用开发者而言，<font color="#c00000">通常只需要使用</font> `avio_*` <font color="#c00000">系列接口</font>或更高级的：
- `avformat_*` ：高级封装格式层IO
- `av_file_*` ：内存映射IO
系列接口。
需要注意上述系列函数均<span style="background:#fff88f"><font color="#c00000">同时兼容URL和普通文件系统</font></span>。

### 4.1.1 avio系列函数

`avio_*` 系列的IO操作函数均需要维护对应的上下文：
- 文件操作需要 `AVIOContext` 上下文
- 目录操作需要 `AVIODirContext` 上下文

#### 4.1.1.1 打开文件

```C
int avio_open(AVIOContext **s, const char *url, int flags)	
```

该函数会创建并初始化一个 `AVIOContext` ，用于访问 `url` 指示的资源。
其参数：
- `AVIOContext **s` ：指向 `AVIOContext *` 的指针，用于将 `AVIOContext *` 返回给调用者
- `const char *url` ：文件的url路径
- `int flags`
其返回值：
- 大于等于0时表示成功
- 负值表示 `AVERROR` 值

#### 4.1.1.2 读取目录条目

```C
int avio_read_dir(AVIODirContext *s, AVIODirEntry **next)	
```

#### 4.1.1.3 关闭目录

```C
int avio_close_dir(AVIODirContext **s)	
```

### 4.1.2 ffurl系列函数

#### 4.1.2.1 打开文件

```C

```



#### 4.1.2.2 打开目录

```C
int avio_open_dir(AVIODirContext **s, const char *url, AVDictionary **options)	
```

其参数：
- `AVIODirContext **s` ：目录上下文
- `const char *url` ：目录的URL
- `AVDictionary **options` ：包含协议私密配置的词典，返回时该参数将被销毁，并替换为包含缺失选项的词典，可能为 `NULL` 

## 4.2 多媒体流操作

在[[../音视频开发入门|音视频开发入门]]中就已经讲到，音视频文件或流中均包含一个或多个音频流或视频流，这些流中又包含音视频shu ju

