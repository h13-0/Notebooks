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

## 2.2 FFmpeg解码概述

在[[音视频开发/音视频开发入门#^rk4p2m|流媒体结构]]我们已经了解了如下的音视频流四层结构：
	![[Resources/音视频流四层结构.drawio.svg]]
而在FFmpeg进行解码和播放时，则会分别对应如下的工作流程：
	![[../Resources/FFmpeg解码工作流.drawio.svg]]
针对上述流程，有如下补充：
- FFmpeg解码流程实际上主要就分为如下几步：
	1. 从网络流或文件系统中抓取封装文件
	2. 从封装文件中获取<font color="#c00000">流</font><span style="background:#fff88f"><font color="#c00000"><u><b>信息</b></u></font></span>
	3. 从流信息中构造解码器
	4. 循环从封装文件中提取编码后的数据包给解码器
	5. 循环从解码器中获取解码后的原始音视频数据
- 数据结构部分：
	- `AVFormatContext` ：封装文件上下文
	- `AVStream` ：<font color="#c00000">流信息</font>，<span style="background:#fff88f"><font color="#c00000">而非流数据</font></span>
	- `AVCodecParameters` ：编码数据流的属性
	- `AVCodecID` ：编码类型枚举
	- `AVCodec` ：编解码器的单例预定义(指明每个编解码器的回调函数等)
	- `AVCodecContext` ：编解码器上下文
	- `AVPacket` ：编码后的数据片段
	- `AVFrame` ：基础数据帧
		- 对于视频是单帧原始数据
		- 对于音频是一段采样点构成的数组，即一段PCM数据

# 3 基础数据结构

## 3.1 封装数据包对象(AVPacket)




# 4 常用API

## 4.1 从封装中读取数据包(av_read_frame)

```C
int av_read_frame(AVFormatContext *s, AVPacket *pkt);
```

功能含义：
- 从封装上下文中读取数据包
注意：
- 其在成功调用后，`AVPacket *pkt` 中的引用计数器会 `+1` 
- 当调用者不再需要其中的数据时，需要手动调用 `av_packet_unref` 解除对其的引用


## 4.2 将数据包传递给解码器(avcodec_send_packet)

```C
int avcodec_send_packet(AVCodecContext *avctx, const AVPacket *avpkt);
```

功能含义：
- 将数据包传递给解码器，并等待解码
注意：
- 当 `AVPacket *avpkt` 传递给解码器后，其引用计数器会 `+1`
- 直到[[音视频开发/FFmpeg/FFmpeg开发入门#^bgy9em|在解码器中处理完毕并]]后 


## 4.3 从解码器中读取解码后的帧(avcodec_receive_frame) ^bgy9em




## 4.4 




# 5 libavformat模块

## 5.1 基础IO操作

FFmpeg的基础IO操作主要分为 `avio_*` 和 `ffurl_*` 这两个系列，其具体区别为：

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

### 5.1.1 avio系列函数

`avio_*` 系列的IO操作函数均需要维护对应的上下文：
- 文件操作需要 `AVIOContext` 上下文
- 目录操作需要 `AVIODirContext` 上下文

#### 5.1.1.1 打开文件

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

#### 5.1.1.2 读取目录条目

```C
int avio_read_dir(AVIODirContext *s, AVIODirEntry **next)	
```

#### 5.1.1.3 关闭目录

```C
int avio_close_dir(AVIODirContext **s)	
```

### 5.1.2 ffurl系列函数

#### 5.1.2.1 打开文件

```C

```



#### 5.1.2.2 打开目录

```C
int avio_open_dir(AVIODirContext **s, const char *url, AVDictionary **options)	
```

其参数：
- `AVIODirContext **s` ：目录上下文
- `const char *url` ：目录的URL
- `AVDictionary **options` ：包含协议私密配置的词典，返回时该参数将被销毁，并替换为包含缺失选项的词典，可能为 `NULL` 

## 5.2 解复用

### 5.2.1 打开媒体文件(avformat_open_input)

```C
int avformat_open_input(AVFormatContext **ps, const char *url,
	const AVInputFormat *fmt, AVDictionary **options)	
```

该函数会打开一个输入流并读取头部。在此步骤中编解码器并没有被打开
其参数：
- `AVFormatContext **ps` ：格式化IO上下文的二级指针。当打开失败时其会返回 `NULL` 
- `const char *url` ：媒体文件的URL
- `const AVInputFormat *fmt` ：指定解析时使用的封装格式(`MP4`、`FLV` 等)，需要注意：
	- 传入 `NULL` 时自动检测封装格式
	- 传入非 `NULL` 时则会按照指定的格式进行解析(即使和实际格式不匹配)
- `AVDictionary **options` ：由key和value组成的选项字典

### 5.2.2 关闭媒体文件(avformat_close_input)

```C


```

# 6 libavutil模块

## 6.1 FFmpeg日志系统的使用

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

### 6.1.1 常用API

#### 6.1.1.1 设置日志等级 ^oxdoti

```C
void av_log_set_level(int level)
```

#### 6.1.1.2 输出日志 ^gsjiaj

```C
void av_log(void *avcl, int level, const char *fmt,...)
```

其参数：
- `void *avcl` ：指向第一个字段为 `AVClass` 的结构体的指针，若为<font color="#c00000">常规日志则为</font> `NULL`
- `int level` ：日志等级
- `const char *fmt` ：格式化字符串
- `...` ：可变参数

