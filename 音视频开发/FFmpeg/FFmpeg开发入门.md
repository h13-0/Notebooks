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

### 3.1.1 常用API

#### 3.1.1.1 设置日志等级 ^oxdoti

```C
void av_log_set_level(int level)
```

其可选日志等级有：
- `AV_LOG_QUIET` ：
- `AV_LOG_PANIC` ：
- `AV_LOG_FATAL` ：
- `AV_LOG_ERROR`
- `AV_LOG_WARNING`
- `AV_LOG_INFO`
- `AV_LOG_VERBOSE`
- `AV_LOG_DEBUG`
- `AV_LOG_TRACE`

#### 3.1.1.2 输出日志

```C
void av_log(void *avcl, int level, const char *fmt,...)
```

