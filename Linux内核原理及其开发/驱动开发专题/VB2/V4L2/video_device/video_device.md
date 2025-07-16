---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 #Linux驱动开发 #V4L2 

## 1 目录

```toc
```

## 2 video_device用户态开发概述

### 2.1 基础知识

本章节的基础知识无序排列。

#### 2.1.1 颜色空间

##### 2.1.1.1 YUV

YUV通常用于模拟视频领域，且其能很好的兼容黑白视频和彩色视频。其通道定义为：
- Y：明度，单通道使用即为黑白视频
- U：蓝色偏移量成分
- V：红色偏移量成分
与RGB的转换公式为：
$$Y=0.299R+0.587G+0.114B$$
$$U=0.492\cdot (B-Y)$$
$$V=0.877\cdot (R-Y)$$
且：
$$Y\in [0,255], U\in [-112,+112], V\in [-157,+157]$$
明显地，V的上下限之差大于255。

YUV的UV分量可视化图如下：
	![[Pasted image 20250626172747.png]]

#### 2.1.2 平面(planes) ^29c6mw

平面是指像素数据的排列交织的方式，也就是内存布局的平面数，例如：

| <center>格式类型</center> | <center>示例格式</center> | 平面数 | <center>内存布局</center>                   |
| --------------------- | --------------------- | --- | --------------------------------------- |
| RGB打包                 | RGB24, BGR32          | 1   | `[RGBRGBRGB...]`                        |
| YUV打包                 | YUYV, UYVY            | 1   | `[YUYVYUYV...]`                         |
| YUV平面                 | NV12, YUV420          | 2-3 | `[YYYY...]` + `[UVUV...]`               |
| YUV完全平面               | YUV420P               | 3   | `[YYYY...]` + `[UUUU...]` + `[VVVV...]` |
相比于RGB的单平面，YUV等多平面可以带来更多的兼容性优势。
并且也有一些硬件多平面数据处理。

在Linux中，默认最大平面数为8( `VIDEO_MAX_PLANES` )。

#### 2.1.3 元数据 ^h63jbf

除了图像像素数据之外，与视频帧相关的附加信息。
常见元数据有：
- 格式参数：
	- 分辨率
	- 像素格式
	- 色彩空间
	- 位深度
- 时间信息：
	- 时间戳
	- 帧间隔
	- 持续时间
- 采集参数：
	- 曝光时间
	- ISO
	- 白平衡
	- 焦距
	- 光圈
等。
元数据的传递方式有：
1. 附加平面(最常见)
2. 拓展控制( `VIDEOC_G_EXT_CTRLS` )
3. 元数据专用队列

其数据结构的定义通常通过有如下方式共享：
1. 头文件共享
2. 使用标准化的描述符( `V4L2_META_FMT_*` )
3. 使用 `ioctl` 查询元数据格式

### 2.2 视频设备用户态开发(/dev/video*)

#### 2.2.1 基本工作流程

视频设备的基本工作流程如下：
	![[视频设备用户态流程.svg]]

#### 2.2.2 打开设备节点

和普通字符设备一样，使用Linux操作摄像头时，第一步依旧是打开摄像头对应的文件节点。

```C
#include <fcntl.h>
#include <stdio.h>

int fd = open(device, O_RDWR);  
if(fd < 0) {  
    printf("open device: %s failed.\r\n", device);  
}
```

#### 2.2.3 查询设备能力 ^vda0ux

一些设备往往能够同时输出不知一种数据类型，例如一个电视采集卡可以将有线电视的信号转化为linux的音视频输入：
	![[Pasted image 20250326133304.png]]

而当我们想要确认该设备是否有需要的输出能力、或可能需要该设备同时输出多种数据类型时，就需要查询设备能力( `capability` )从而做进一步判断。
查询API为：

```C
#include <sys/ioctl.h>
struct v4l2_capability cap = { 0 };  
int ret = ioctl(fd, VIDIOC_QUERYCAP, &cap);  
if(ret < 0) {  
    printf("get v4l2_capability failed");  
}
```

参考查询结果：
	![[Pasted image 20250325165307.png]]

上述查询结果可以按照如下方式使用：

```C
#include <sys/ioctl.h>
struct v4l2_capability cap = { 0 };  
int ret = ioctl(fd, VIDIOC_QUERYCAP, &cap);  
if(ret < 0) {  
    printf("get v4l2_capability failed.\r\n");  
}

if (cap.capabilities & V4L2_CAP_VIDEO_CAPTURE)  
    printf("Support video capture.\r\n");  
  
if (cap.capabilities & V4L2_CAP_AUDIO)  
    printf("Support audio input.\r\n");  
  
if (cap.capabilities & V4L2_CAP_RADIO)  
    printf("Support radio input.\r\n");

...
```

#### 2.2.4 枚举输出格式

在V4L2中，获取一个设备支持的所有输出格式需要依靠类似于遍历的方法实现(该方法被称为枚举、Enumeration)，其示例如下：

```C
struct v4l2_fmtdesc fmtdesc = { 0 };
fmtdesc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
//fmtdesc.index = 0;
while (1) {
    ret = ioctl(fd, VIDIOC_ENUM_FMT, &fmtdesc);
    if (ret == 0)
    {
        // 输出获取到的格式列表
        printf("-----------------------------------------------\r\n");
        printf("fmtdesc.index=%d\r\n", fmtdesc.index);
        printf("fmtdesc.type=%d\r\n", fmtdesc.type);
        printf("fmtdesc.flags=%d\r\n", fmtdesc.flags);
        printf("fmtdesc.description=%s\r\n", fmtdesc.description);
        printf("fmtdesc.pixelformat=%c.%c.%c.%c\r\n",
            fmtdesc.pixelformat >> 0  & 0xff,
            fmtdesc.pixelformat >> 8  & 0xff,
            fmtdesc.pixelformat >> 16 & 0xff,
            fmtdesc.pixelformat >> 24 & 0xff
        );

        // 4. 枚举指定视频格式支持的分辨率(暂时注释，需要结合下一章节)
        // enum_frame_size(fd, fmtdesc.pixelformat);
    } else {
        printf("video format enumeration end.\r\n");
        break;
    }
    fmtdesc.index ++;
}
```

注：
- 该API的文档可见[7.14. ioctl VIDIOC_ENUM_FMT — The Linux Kernel documentation](https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/vidioc-enum-fmt.html)。

示例输出为：

```text
-----------------------------------------------
fmtdesc.index=0
fmtdesc.type=1
fmtdesc.flags=0
fmtdesc.description=32-bit BGRA/X 8-8-8-8
fmtdesc.pixelformat=B.G.R.4
-----------------------------------------------
fmtdesc.index=1
fmtdesc.type=1
fmtdesc.flags=0
fmtdesc.description=32-bit A/XRGB 8-8-8-8
fmtdesc.pixelformat=R.G.B.4
-----------------------------------------------
fmtdesc.index=2
fmtdesc.type=1
fmtdesc.flags=0
fmtdesc.description=24-bit BGR 8-8-8
fmtdesc.pixelformat=B.G.R.3
-----------------------------------------------
fmtdesc.index=3
fmtdesc.type=1
fmtdesc.flags=0
fmtdesc.description=24-bit RGB 8-8-8
fmtdesc.pixelformat=R.G.B.3
...
```

#### 2.2.5 枚举指定输出格式的分辨率

与枚举输出格式类似，枚举分辨率也需要进行类似的操作，其需要指定：
- `frame_size.pixel_format` ：要查询的目标格式
且需要注意Linux支持如下三种分辨率步进方式：
1. 离散分辨率，即设备只支持几个特定的离散分辨率。
	- 此时  `frame_size.type=V4L2_FRMSIZE_TYPE_DISCRETE` 。
	- 此时该 `ioctl` 操作需要多次枚举，每次会得到一个离散分辨率。
2. 连续分辨率，设备支持在该分辨率范围内任意指定。
	- 此时 `frame_size.type=V4L2_FRMSIZE_TYPE_CONTINUOUS` 。
	- 通常只需要一次枚举。
3. 步进分辨率，设备只能在该分辨率范围内步进选择。
	- 此时 `frame_size.type=V4L2_FRMSIZE_TYPE_STEPWISE` 。
	- 在不同长宽比例下需要多次枚举。

示例程序：

```C
void enum_frame_size(int fd, uint32_t format)
{
    struct v4l2_frmsizeenum frame_size = { 0 };
    frame_size.pixel_format = format;
    int ret = 0;
    while (1)
    {
        ret = ioctl(fd, VIDIOC_ENUM_FRAMESIZES, &frame_size);
        if (ret == 0)
        {
            switch (frame_size.type) {
            case V4L2_FRMSIZE_TYPE_DISCRETE:
                // 设备支持的帧尺寸是离散的
                printf("frame_size.type=V4L2_FRMSIZE_TYPE_DISCRETE\r\n");
                printf("frame_size.discrete.width=%d\r\n", frame_size.discrete.width);
                printf("frame_size.discrete.height=%d\r\n", frame_size.discrete.height);
                break;

            case V4L2_FRMSIZE_TYPE_CONTINUOUS:
                // 设备支持连续的帧尺寸范围
                printf("frame_size.type=V4L2_FRMSIZE_TYPE_CONTINUOUS\r\n");
                printf("frame_size.stepwise.min_width=%d\r\n", frame_size.stepwise.min_width);
                printf("frame_size.stepwise.max_width=%d\r\n", frame_size.stepwise.max_width);
                printf("frame_size.stepwise.step_width=%d\r\n", frame_size.stepwise.step_width);
                printf("frame_size.stepwise.min_height=%d\r\n", frame_size.stepwise.min_height);
                printf("frame_size.stepwise.max_height=%d\r\n", frame_size.stepwise.max_height);
                printf("frame_size.stepwise.step_height=%d\r\n", frame_size.stepwise.step_height);
                break;

            case V4L2_FRMSIZE_TYPE_STEPWISE:
                // 设备支持的帧尺寸在一个范围内，并且可以按特定步长进行调整
                printf("frame_size.type=V4L2_FRMSIZE_TYPE_STEPWISE\r\n");
                printf("frame_size.stepwise.min_width=%d\r\n", frame_size.stepwise.min_width);
                printf("frame_size.stepwise.max_width=%d\r\n", frame_size.stepwise.max_width);
                printf("frame_size.stepwise.step_width=%d\r\n", frame_size.stepwise.step_width);
                printf("frame_size.stepwise.min_height=%d\r\n", frame_size.stepwise.min_height);
                printf("frame_size.stepwise.max_height=%d\r\n", frame_size.stepwise.max_height);
                printf("frame_size.stepwise.step_height=%d\r\n", frame_size.stepwise.step_height);
                break;

            default:
                break;
            }
        } else {
            printf("frame size enumeration end.\r\n");
            break;
        }
        frame_size.index ++;
    }
}
```

示例输出如下：

```text
frame_size.type=V4L2_FRMSIZE_TYPE_CONTINUOUS
frame_size.stepwise.min_width=2
frame_size.stepwise.max_width=8192
frame_size.stepwise.step_width=1
frame_size.stepwise.min_height=1
frame_size.stepwise.max_height=8192
frame_size.stepwise.step_height=1
frame size enumeration end.
```

#### 2.2.6 设置指定的视频格式和分辨率

示例如下：

```C
struct v4l2_format fmt = { 0 };
fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
fmt.fmt.pix.width = 1920;
fmt.fmt.pix.height = 1080;
fmt.fmt.pix.pixelformat = v4l2_fourcc('R', 'G', 'B', '3'); // RGB 8-8-8

// 需要注意当分辨率设置错误等情况时，可能并不会按照你的目标分辨率进行设置。
printf("try to set pix.width=%d\r\n", fmt.fmt.pix.width);
printf("try to set pix.height=%d\r\n", fmt.fmt.pix.height);
printf("try to set pix.height=%d\r\n", fmt.fmt.pix.height);
printf("try to set pix.pixelformat=%c.%c.%c.%c\r\n",
       fmt.fmt.pix.pixelformat >> 0  & 0xff,
       fmt.fmt.pix.pixelformat >> 8  & 0xff,
       fmt.fmt.pix.pixelformat >> 16 & 0xff,
       fmt.fmt.pix.pixelformat >> 24 & 0xff
);

ret = ioctl(fd, VIDIOC_S_FMT, &fmt);
if(ret < 0) {
    printf("exec ioctl(fd, VIDIOC_S_FMT) failed with ret %d.\r\n", ret);
}

// 需要检查实际分辨率等信息
printf("get pix.width=%d\r\n", fmt.fmt.pix.width);
printf("get pix.height=%d\r\n", fmt.fmt.pix.height);
printf("get pix.pixelformat=%c.%c.%c.%c\r\n",
       fmt.fmt.pix.pixelformat >> 0  & 0xff,
       fmt.fmt.pix.pixelformat >> 8  & 0xff,
       fmt.fmt.pix.pixelformat >> 16 & 0xff,
       fmt.fmt.pix.pixelformat >> 24 & 0xff
);
```

需要注意当分辨率等信息设置错误时，驱动可能会调整你的分辨率，从而导致实际分辨率和目标分辨率不一致的情况，因此设置完毕后需要再校验一下结果。

若图像格式设置错误，则通常会操作失败。

#### 2.2.7 申请缓冲区 ^2l9q6s

V4L2框架一共提供了如下三种缓冲区：
- `V4L2_MEMORY_MMAP` ：使用 `mmap` 将内核分配的DMA缓冲区映射到用户空间
	- 数据流动：`硬件 -(DMA)-> DMA缓冲区 <-(内存映射)->用户空间`
	- 在用户态编程时，[[mmap#^go6lxw|mmap]]<font color="#c00000">的操作对象是将一个fd的offset处映射到指定内存区域</font>，因此在使用mmap方式操作缓冲区时也是<font color="#c00000">获取到缓冲区</font><span style="background:#fff88f"><font color="#c00000">相对于fd的offset</font></span>后进行操作。
	- 无需拷贝，性能较好。
- `V4L2_MEMORY_USERPTR` ：用户提供缓冲区，驱动直接通过DMA将数据写入这些缓冲区，而无需CPU介入。
	- 标准语义的数据流动：`硬件 -(DMA)-> 离散的用户空间`
	- 部分CPU可能不支持直接DMA到可能离散的用户内存空间。
	- V4L2的标准语义中也明确排除了使用CPU模拟拷贝的实现。大多数驱动实现也通常会直接拒绝提供该方法而非使用CPU模拟。
- `V4L2_MEMORY_DMABUF` ：允许用户直接使用DMA句柄，可以实现跨设备传输
	- 数据流动：`硬件 -(DMA)-> DMA句柄对应的缓冲区` ，允许多个设备公用一个DMA句柄。
	- 减少跨设备内存拷贝
上述三种缓冲区并非所有设备都支持，通常来说：
- `V4L2_MEMORY_MMAP` ：一定支持，这是V4L2的基础模式。
- `V4L2_MEMORY_USERPTR` ：由于用户空间内存不连续，需要额外拷贝。
- `V4L2_MEMORY_DMABUF` ：依赖内核DMA-BUF框架和硬件IOMMU，只有现代SoC支持。

查询支持能力可以使用如下的方法查询：

```C
if (cap.capabilities & V4L2_BUF_CAP_SUPPORTS_MMAP)
    printf("Support MMAP.\r\n");

if (cap.capabilities & V4L2_BUF_CAP_SUPPORTS_USERPTR)
    printf("Support USERPTR.\r\n");

if (cap.capabilities & V4L2_BUF_CAP_SUPPORTS_DMABUF)
    printf("Support DMABUF.\r\n");
```

随后使用如下API完成缓冲区申请：

```C
// 6. 申请缓冲区，缓冲区类型为队列
struct v4l2_requestbuffers req_buffers = { 0 };
req_buffers.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
req_buffers.count = 4;  // 缓冲区数量通常大于2
req_buffers.memory = V4L2_MEMORY_MMAP;

ret = ioctl(fd, VIDIOC_REQBUFS, &req_buffers);
if(ret < 0) {
    printf("request buffer failed with msg: %s.\r\n", strerror(errno));
}
// 需要注意获得的缓冲区数量不等于申请到的缓冲区数量
printf("The number of obtained buffers=%d.\r\n", req_buffers.count);
```

需要注意：
1. <span style="background:#fff88f"><font color="#c00000">获得的缓冲区数量不一定等于申请到的缓冲区数量</font></span>(并且很常见)。驱动会设定总缓冲区数量上限，并借此限制缓冲区数量上限(必然不会让用户态程序随便拉满缓冲区数量)。
2. 执行 `ioctl(fd, VIDIOC_REQBUFS, &req_buffers);` ，有如下逻辑：
	1. 释放旧缓冲区
	2. 当缓冲区类型：
		1. 为 `V4L2_MEMORY_MMAP` 时，内核会分配指定数量的内存。
		2. 为 `V4L2_MEMORY_USERPTR` 时，内核会进行虚拟地址记录，暂不分配物理内存。在后续 `VIDIOC_QBUF` 调用时，会PIN住该内存页防止换出。
		3. 为 `V4L2_MEMORY_DMABUF` 时，注册外部DMA句柄。在后续 `VIDIOC_QBUF` 调用时会传递句柄。
	3. 准备硬件资源，例如DMA

#### 2.2.8 将缓存加入缓存队列

将缓存加入缓存队列的目的是： ^iuf8ml
- 显式的避免用户和内核同时操作同一片缓冲区，避免用户态访问到被内核正在使用且保护的缓冲区导致用户态挂掉。
- 提供一种用户态-内核态的缓冲区同步机制，该机制如下：
	1. 用户态将空的/使用过的缓冲区塞入内核态队列
	2. 用户态通过系统调用使得内核态将填满数据的[[V4L2概述#^qftknt|缓冲区出队]]并返回给用户态

因此，在用户态初始化V4L2摄像头时，其操作如下：

```C
struct v4l2_buffer buffer = { 0 };
buffer.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
buffer.memory = V4L2_MEMORY_MMAP;
for(int i = 0; i < req_buffers.count; i++)
{
    buffer.index = i;
    ret = ioctl(fd, VIDIOC_QBUF, &buffer);
    if(ret < 0) {
        printf("Enqueue buffer failed with msg: %s\r\n", strerror(errno));
    }
}
```

而在后续获取图像时，图像会通过缓冲区返回给用户态。用户态图像接收完毕后也需要将缓冲区重新塞回队列中。

#### 2.2.9 mmap映射缓存

如前文所述，[[mmap#^go6lxw|mmap]]<font color="#c00000">的操作对象是将一个fd的offset处映射到指定内存区域</font>。
在这里需要的操作对象就是：
- 设备文件fd
- 使用 `VIDIOC_QUERYBUF` 查询得到的offset

示例如下：

```C
void* addr[req_buffers.count];
memset(addr, 0, sizeof addr);
// 查询缓存信息
for(int i = 0; i < req_buffers.count; i++)
{
    buffer.index = i;
    ret = ioctl(fd, VIDIOC_QUERYBUF, &buffer);
    if(ret < 0) {
        printf("Query buffer failed with msg: %s\r\n", strerror(errno));
    } else {
        printf("V4L2 MMAP buffer[%d] offset=%d\r\n", i, buffer.m.offset);
        // mmap
        addr[i] = mmap(NULL /* start anywhere */ ,
                    buffer.length, PROT_READ | PROT_WRITE, MAP_SHARED,
                    fd, buffer.m.offset);
    }
}
```

#### 2.2.10 开启流传输

```C
enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;  
ret = ioctl(fd, VIDIOC_STREAMON, &type);  
if(ret < 0) {  
    printf("VIDIOC_STREAMON failed with msg: %s\r\n", strerror(errno));  
}
```

#### 2.2.11 缓冲区出队 ^qftknt

当驱动采集到图像后，就会将图像放入缓冲区，再将缓冲区放入队列中。
而用户态想要读取图像时，就可以使用如下的方法将已经完成数据填装的缓冲区从队列中出队：

```C
memset(&buffer, 0x00, sizeof buffer);  
buffer.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;  
int frame_id = 0;  
while(!exit)  
{  
    // 缓冲区出队  
    ret = ioctl(fd, VIDIOC_DQBUF, &buffer);  
    if(ret < 0) {  
        printf("VIDIOC_DQBUF failed with msg: %s\r\n", strerror(errno));  
    } else {  
        printf("VIDIOC_DQBUF get buffer index=%d, frame_nums=%d\r\n", buffer.index, frame_id);  
        
        do_sth(...);
        
        frame_id++;  
        // 重新将frame塞回队列中  
        ret = ioctl(fd, VIDIOC_QBUF, &buffer);  
        if(ret < 0) {  
            printf("Enqueue buffer failed with msg: %s\r\n", strerror(errno));  
        }  
    }  
}
```

注：
- `buffer.type` 字段需要设置。

#### 2.2.12 完整示例代码

```C
#include <linux/videodev2.h>

#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdbool.h>

const char* device = "/dev/video1";

void enum_frame_size(int fd, uint32_t format)
{
    struct v4l2_frmsizeenum frame_size = { 0 };
    frame_size.pixel_format = format;
    int ret = 0;
    while (1)
    {
        ret = ioctl(fd, VIDIOC_ENUM_FRAMESIZES, &frame_size);
        if (ret == 0)
        {
            switch (frame_size.type) {
            case V4L2_FRMSIZE_TYPE_DISCRETE:
                // 设备支持的帧尺寸是离散的
                printf("frame_size.type=V4L2_FRMSIZE_TYPE_DISCRETE\r\n");
                printf("frame_size.discrete.width=%d\r\n", frame_size.discrete.width);
                printf("frame_size.discrete.height=%d\r\n", frame_size.discrete.height);
                break;

            case V4L2_FRMSIZE_TYPE_CONTINUOUS:
                // 设备支持连续的帧尺寸范围
                printf("frame_size.type=V4L2_FRMSIZE_TYPE_CONTINUOUS\r\n");
                printf("frame_size.stepwise.min_width=%d\r\n", frame_size.stepwise.min_width);
                printf("frame_size.stepwise.max_width=%d\r\n", frame_size.stepwise.max_width);
                printf("frame_size.stepwise.step_width=%d\r\n", frame_size.stepwise.step_width);
                printf("frame_size.stepwise.min_height=%d\r\n", frame_size.stepwise.min_height);
                printf("frame_size.stepwise.max_height=%d\r\n", frame_size.stepwise.max_height);
                printf("frame_size.stepwise.step_height=%d\r\n", frame_size.stepwise.step_height);
                break;

            case V4L2_FRMSIZE_TYPE_STEPWISE:
                // 设备支持的帧尺寸在一个范围内，并且可以按特定步长进行调整
                printf("frame_size.type=V4L2_FRMSIZE_TYPE_STEPWISE\r\n");
                printf("frame_size.stepwise.min_width=%d\r\n", frame_size.stepwise.min_width);
                printf("frame_size.stepwise.max_width=%d\r\n", frame_size.stepwise.max_width);
                printf("frame_size.stepwise.step_width=%d\r\n", frame_size.stepwise.step_width);
                printf("frame_size.stepwise.min_height=%d\r\n", frame_size.stepwise.min_height);
                printf("frame_size.stepwise.max_height=%d\r\n", frame_size.stepwise.max_height);
                printf("frame_size.stepwise.step_height=%d\r\n", frame_size.stepwise.step_height);
                break;

            default:
                break;
            }
        } else {
            printf("frame size enumeration end.\r\n");
            break;
        }
        frame_size.index ++;
    }
}


int main(int argc, char **argv)
{
    // 0. 准备必要变量
    bool exit = false;


    // 1. 打开设备文件
    int fd = open(device, O_RDWR);
    if(fd < 0) {
        printf("open device: %s failed.\r\n", device);
        return -1;
    }

    // 2. 查询设备能力(设备能否提供视频输入、音频输入、收音功能等)
    struct v4l2_capability cap = { 0 };
    int ret = ioctl(fd, VIDIOC_QUERYCAP, &cap);
    if(ret < 0) {
        printf("get v4l2_capability failed.\r\n");
        return -2;
    }

    if (cap.capabilities & V4L2_CAP_VIDEO_CAPTURE)
        printf("Support video capture.\r\n");

    if (cap.capabilities & V4L2_CAP_AUDIO)
        printf("Support audio input.\r\n");

    if (cap.capabilities & V4L2_CAP_RADIO)
        printf("Support radio input.\r\n");

    if (cap.capabilities & V4L2_CAP_STREAMING)
        printf("Support streaming I/O.\r\n");

    if (cap.capabilities & V4L2_CAP_READWRITE)
        printf("Support read/write I/O.\r\n");

    if (cap.capabilities & V4L2_BUF_CAP_SUPPORTS_MMAP)
        printf("Support MMAP.\r\n");

    if (cap.capabilities & V4L2_BUF_CAP_SUPPORTS_USERPTR)
        printf("Support USERPTR.\r\n");

    if (cap.capabilities & V4L2_BUF_CAP_SUPPORTS_DMABUF)
        printf("Support DMABUF.\r\n");

    // 3. 枚举所支持的视频格式
    struct v4l2_fmtdesc fmtdesc = { 0 };
    fmtdesc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    //fmtdesc.index = 0;
    while (1) {
        ret = ioctl(fd, VIDIOC_ENUM_FMT, &fmtdesc);
        if (ret == 0)
        {
            // 输出获取到的格式列表
            printf("-----------------------------------------------\r\n");
            printf("fmtdesc.index=%d\r\n", fmtdesc.index);
            printf("fmtdesc.type=%d\r\n", fmtdesc.type);
            printf("fmtdesc.flags=%d\r\n", fmtdesc.flags);
            printf("fmtdesc.description=%s\r\n", fmtdesc.description);
            printf("fmtdesc.pixelformat=%c.%c.%c.%c\r\n",
                fmtdesc.pixelformat >> 0  & 0xff,
                fmtdesc.pixelformat >> 8  & 0xff,
                fmtdesc.pixelformat >> 16 & 0xff,
                fmtdesc.pixelformat >> 24 & 0xff
            );

            // 4. 枚举指定视频格式支持的分辨率
            enum_frame_size(fd, fmtdesc.pixelformat);
        } else {
            printf("video format enumeration end.\r\n");
            break;
        }
        fmtdesc.index ++;
    }

    // 5. 设置视频格式和分辨率
    struct v4l2_format fmt = { 0 };
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width = 1920;
    fmt.fmt.pix.height = 1080;
    fmt.fmt.pix.pixelformat = v4l2_fourcc('M', 'G', 'P', 'G'); // RGB 8-8-8

    // 需要注意当分辨率设置错误等情况时，可能并不会按照你的目标分辨率进行设置。
    printf("try to set pix.width=%d\r\n", fmt.fmt.pix.width);
    printf("try to set pix.height=%d\r\n", fmt.fmt.pix.height);
    printf("try to set pix.height=%d\r\n", fmt.fmt.pix.height);
    printf("try to set pix.pixelformat=%c.%c.%c.%c\r\n",
           fmt.fmt.pix.pixelformat >> 0  & 0xff,
           fmt.fmt.pix.pixelformat >> 8  & 0xff,
           fmt.fmt.pix.pixelformat >> 16 & 0xff,
           fmt.fmt.pix.pixelformat >> 24 & 0xff
    );

    ret = ioctl(fd, VIDIOC_S_FMT, &fmt);
    if(ret < 0) {
        printf("exec ioctl(fd, VIDIOC_S_FMT) failed with msg: %s.\r\n", strerror(errno));
        return -5;
    }

    // 需要检查实际分辨率等信息
    printf("get pix.width=%d\r\n", fmt.fmt.pix.width);
    printf("get pix.height=%d\r\n", fmt.fmt.pix.height);
    printf("get pix.height=%d\r\n", fmt.fmt.pix.height);
    printf("get pix.pixelformat=%c.%c.%c.%c\r\n",
        fmt.fmt.pix.pixelformat >> 0  & 0xff,
        fmt.fmt.pix.pixelformat >> 8  & 0xff,
        fmt.fmt.pix.pixelformat >> 16 & 0xff,
        fmt.fmt.pix.pixelformat >> 24 & 0xff
    );

    // 6. 申请缓冲区，缓冲区类型为队列
    struct v4l2_requestbuffers req_buffers = { 0 };
    req_buffers.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req_buffers.count = 4;  // 缓冲区数量通常大于2
    req_buffers.memory = V4L2_MEMORY_MMAP;

    ret = ioctl(fd, VIDIOC_REQBUFS, &req_buffers);
    if(ret < 0) {
        printf("request buffer failed with msg: %s.\r\n", strerror(errno));
        return -6;
    }
    // 需要注意获得的缓冲区数量不等于申请到的缓冲区数量
    printf("The number of obtained buffers=%d.\r\n", req_buffers.count);

    // 7. 将申请到的缓冲加入到驱动队列
    struct v4l2_buffer buffer = { 0 };
    buffer.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buffer.memory = V4L2_MEMORY_MMAP;
    for(int i = 0; i < req_buffers.count; i++)
    {
        buffer.index = i;
        ret = ioctl(fd, VIDIOC_QBUF, &buffer);
        if(ret < 0) {
            printf("Enqueue buffer failed with msg: %s\r\n", strerror(errno));
            return -7;
        }
    }

    // 8. 映射缓存
    void* addr[req_buffers.count];
    memset(addr, 0, sizeof addr);
    // 8.1 查询缓存信息
    for(int i = 0; i < req_buffers.count; i++)
    {
        buffer.index = i;
        ret = ioctl(fd, VIDIOC_QUERYBUF, &buffer);
        if(ret < 0) {
            printf("Query buffer failed with msg: %s\r\n", strerror(errno));
            return -8;
        } else {
            printf("V4L2 MMAP buffer[%d] offset=%d\r\n", i, buffer.m.offset);

            // 8.2 mmap
            addr[i] = mmap(NULL /* start anywhere */ ,
                        buffer.length, PROT_READ | PROT_WRITE, MAP_SHARED,
                        fd, buffer.m.offset);
        }
    }

    // 9. 开启流传输
    enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    ret = ioctl(fd, VIDIOC_STREAMON, &type);
    if(ret < 0) {
        printf("VIDIOC_STREAMON failed with msg: %s\r\n", strerror(errno));
        return -9;
    }

    // 10. 循环获取图像
    memset(&buffer, 0x00, sizeof buffer);
    buffer.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    int frame_id = 0;
    while(!exit)
    {
        // 10.1 缓冲区出队
        ret = ioctl(fd, VIDIOC_DQBUF, &buffer);
        if(ret < 0) {
            printf("VIDIOC_DQBUF failed with msg: %s\r\n", strerror(errno));
        } else {
            // TODO
            printf("VIDIOC_DQBUF get buffer index=%d, frame_nums=%d\r\n", buffer.index, frame_id);

            frame_id++;

            // 重新将frame塞回队列中
            ret = ioctl(fd, VIDIOC_QBUF, &buffer);
            if(ret < 0) {
                printf("Enqueue buffer failed with msg: %s\r\n", strerror(errno));
            }
        }
    }

    return 0;
}

```


### 2.3 video_device用户态工具



## 3 video_device内核态开发

内核态开发必须拥有如下的基础知识：
- [[VB2概述]]
- [[V4L2概述#^dyadtz|V4L2基础概述]]

### 3.1 VB2的v4l2特化

#### 3.1.1 缓冲区类型枚举(enum v4l2_buf_type) ^u8ke9r

在[[VB2概述]]中，`vb2_queue` 等通常需要指定

```C
enum v4l2_buf_type {
	V4L2_BUF_TYPE_VIDEO_CAPTURE        = 1,  // 视频捕获队列
	V4L2_BUF_TYPE_VIDEO_OUTPUT         = 2,  // 视频输出队列
	V4L2_BUF_TYPE_VIDEO_OVERLAY        = 3,  // 视频叠加队列[已过时，现用M2M]
	V4L2_BUF_TYPE_VBI_CAPTURE          = 4,  // 垂直消隐期(VBI)数据捕获
	V4L2_BUF_TYPE_VBI_OUTPUT           = 5,  // 垂直消隐期(VBI)数据输出
	V4L2_BUF_TYPE_SLICED_VBI_CAPTURE   = 6,  // 切片式垂直消隐期数据捕获
	V4L2_BUF_TYPE_SLICED_VBI_OUTPUT    = 7,  // 切片式垂直消隐期数据输出
	V4L2_BUF_TYPE_VIDEO_OUTPUT_OVERLAY = 8,  // 视频输出覆盖[已过时，现用M2M等]
	V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE = 9,  // 多平面视频捕获
	V4L2_BUF_TYPE_VIDEO_OUTPUT_MPLANE  = 10, // 多平面视频输出
	V4L2_BUF_TYPE_SDR_CAPTURE          = 11, // 软件定义无线电(SDR)捕获
	V4L2_BUF_TYPE_SDR_OUTPUT           = 12, // 软件定义无线电(SDR)输出
	V4L2_BUF_TYPE_META_CAPTURE         = 13, // 元数据捕获
	V4L2_BUF_TYPE_META_OUTPUT	       = 14, // 元数据输出
	/* Deprecated, do not use */
	V4L2_BUF_TYPE_PRIVATE              = 0x80,
};
```

#### 3.1.2 队列初始化函数(vb2_queue_init)

```C
#include <media/videobuf2-v4l2.h>

/**
 * vb2_queue_init() - initialize a videobuf2 queue
 * @q:		pointer to &struct vb2_queue with videobuf2 queue.
 *
 * The vb2_queue structure should be allocated by the driver. The driver is
 * responsible of clearing it's content and setting initial values for some
 * required entries before calling this function.
 * q->ops, q->mem_ops, q->type and q->io_modes are mandatory. Please refer
 * to the struct vb2_queue description in include/media/videobuf2-core.h
 * for more information.
 */
int __must_check vb2_queue_init(struct vb2_queue *q);
```

该函数通常在 `probe` 或打开设备回调时被驱动调用。当函数执行成功时返回 `0` 。

#### 3.1.3 队列释放函数(vb2_queue_release)

```C
/**
 * vb2_queue_release() - stop streaming, release the queue and free memory
 * @q:		pointer to &struct vb2_queue with videobuf2 queue.
 *
 * This function stops streaming and performs necessary clean ups, including
 * freeing video buffer memory. The driver is responsible for freeing
 * the vb2_queue structure itself.
 */
void vb2_queue_release(struct vb2_queue *q);
```

看注释即可。

#### 3.1.4 VB2 ioctl helper




#### 3.1.5 手动操作函数

##### 3.1.5.1 申请缓冲区(vb2_reqbufs)

```C
/**
 * vb2_reqbufs() - Wrapper for vb2_core_reqbufs() that also verifies
 * the memory and type values.
 *
 * @q:		pointer to &struct vb2_queue with videobuf2 queue.
 * @req:	&struct v4l2_requestbuffers passed from userspace to
 *		&v4l2_ioctl_ops->vidioc_reqbufs handler in driver.
 */
int vb2_reqbufs(struct vb2_queue *q, struct v4l2_requestbuffers *req);
```

该函数通常在 `videoc_reqbufs` 回调中被驱动调用，调用链为：
1. [[video_device#^2l9q6s|用户空间申请缓冲区]]( `ioctl(fd, VIDIOC_REQBUFS, &req_buffers)` )
2. V4L2框架将ioctl导入[[video_device#^r8lfyg|v4l2_ioctl_ops]]的 `vidioc_reqbufs` 中
3. 在 `vidioc_reqbufs` 中调用 `vb2_reqbufs` 。
注：
- 驱动可以不关心上述逻辑，只需要将 `v4l2_ioctl_ops.vidioc_reqbufs` 指向 `vb2_ioctl_reqbufs` 即可。但也可以自行实现。

##### 3.1.5.2 查询缓冲区信息(vb2_querybuf)

```C
/*
 * vb2_querybuf() - query video buffer information
 * @q:		vb2 queue
 * @b:		buffer struct passed from userspace to vidioc_querybuf handler
 *		in driver
 *
 * Should be called from vidioc_querybuf ioctl handler in driver.
 * This function will verify the passed v4l2_buffer structure and fill the
 * relevant information for the userspace.
 *
 * The return values from this function are intended to be directly returned
 * from vidioc_querybuf handler in driver.
 */
int vb2_querybuf(struct vb2_queue *q, struct v4l2_buffer *b);
```




### 3.2 video_device设备类型(enum vfl_devnode_type) ^4ac1hk

正如[[V4L2概述#2 2 V4L2设备模型概述 4783s6|V4L2设备模型概述]]所述， `video_device` 包含了多种子设备类型，例如视频设备、收音机设备等。在内核中通过 `enum vfl_devnode_type` 进行区分，其定义如下：

```C
/**
 * enum vfl_devnode_type - type of V4L2 device node
 *
 * @VFL_TYPE_VIDEO:	for video input/output devices
 * @VFL_TYPE_VBI:	for vertical blank data (i.e. closed captions, teletext)
 * @VFL_TYPE_RADIO:	for radio tuners
 * @VFL_TYPE_SUBDEV:	for V4L2 subdevices
 * @VFL_TYPE_SDR:	for Software Defined Radio tuners
 * @VFL_TYPE_TOUCH:	for touch sensors
 * @VFL_TYPE_MAX:	number of VFL types, must always be last in the enum
 */
enum vfl_devnode_type {
	VFL_TYPE_VIDEO,
	VFL_TYPE_VBI,
	VFL_TYPE_RADIO,
	VFL_TYPE_SUBDEV,
	VFL_TYPE_SDR,
	VFL_TYPE_TOUCH,
	VFL_TYPE_MAX /* Shall be the last one */
};
```

其分别有如下对应关系：
- `VFL_TYPE_VIDEO` ：视频设备 `/dev/video*` 
- `VFL_TYPE_VBI` ：垂直消隐期设备： `/dev/vbi*`
- `VFL_TYPE_RADIO` ：收音机设备： `/dev/radio*` 
- `VFL_TYPE_SDR` ：软件无线电： `/dev/swradio*` 
- `VFL_TYPE_TOUCH` ：基于视频的触摸设备(例如红外触摸屏)： `/dev/v4l-touch*`
其通过在[[video_device#^cjcnad|注册video_device设备]]时指定参数来确定其设备类型。

### 3.3 video_device基础特性

正如[[V4L2概述#2 2 1 基础设备模型 4783s6|基础设备模型]]所述，video_device提供了包含视频设备( `/dev/video*` )、收音机设备( `/dev/radio*` )等功能模型。

其数据结构定义如下：

```C
/**
 * struct video_device - Structure used to create and manage the V4L2 device
 *	nodes.
 *
 * @entity: &struct media_entity
 * @intf_devnode: pointer to &struct media_intf_devnode
 * @pipe: &struct media_pipeline
 * @fops: pointer to &struct v4l2_file_operations for the video device
 * @device_caps: device capabilities as used in v4l2_capabilities
 * @dev: &struct device for the video device
 * @cdev: character device
 * @v4l2_dev: pointer to &struct v4l2_device parent
 * @dev_parent: pointer to &struct device parent
 * @ctrl_handler: Control handler associated with this device node.
 *	 May be NULL.
 * @queue: &struct vb2_queue associated with this device node. May be NULL.
 * @prio: pointer to &struct v4l2_prio_state with device's Priority state.
 *	 If NULL, then v4l2_dev->prio will be used.
 * @name: video device name
 * @vfl_type: V4L device type, as defined by &enum vfl_devnode_type
 * @vfl_dir: V4L receiver, transmitter or m2m
 * @minor: device node 'minor'. It is set to -1 if the registration failed
 * @num: number of the video device node
 * @flags: video device flags. Use bitops to set/clear/test flags.
 *	   Contains a set of &enum v4l2_video_device_flags.
 * @index: attribute to differentiate multiple indices on one physical device
 * @fh_lock: Lock for all v4l2_fhs
 * @fh_list: List of &struct v4l2_fh
 * @dev_debug: Internal device debug flags, not for use by drivers
 * @tvnorms: Supported tv norms
 *
 * @release: video device release() callback
 * @ioctl_ops: pointer to &struct v4l2_ioctl_ops with ioctl callbacks
 *
 * @valid_ioctls: bitmap with the valid ioctls for this device
 * @lock: pointer to &struct mutex serialization lock
 *
 * .. note::
 *	Only set @dev_parent if that can't be deduced from @v4l2_dev.
 */

struct video_device {
#if defined(CONFIG_MEDIA_CONTROLLER)
	struct media_entity entity;
	struct media_intf_devnode *intf_devnode;
	struct media_pipeline pipe;
#endif
	const struct v4l2_file_operations *fops;

	u32 device_caps;

	/* sysfs */
	struct device dev;
	struct cdev *cdev;

	struct v4l2_device *v4l2_dev;
	struct device *dev_parent;

	struct v4l2_ctrl_handler *ctrl_handler;

	struct vb2_queue *queue;

	struct v4l2_prio_state *prio;

	/* device info */
	char name[64];
	enum vfl_devnode_type vfl_type;
	enum vfl_devnode_direction vfl_dir;
	int minor;
	u16 num;
	unsigned long flags;
	int index;

	/* V4L2 file handles */
	spinlock_t		fh_lock;
	struct list_head	fh_list;

	int dev_debug;

	v4l2_std_id tvnorms;

	/* callbacks */
	void (*release)(struct video_device *vdev);
	const struct v4l2_ioctl_ops *ioctl_ops;
	DECLARE_BITMAP(valid_ioctls, BASE_VIDIOC_PRIVATE);

	struct mutex *lock;
};
```

该数据结构中：
- 基础成员：
	- `char name[64]` 
		- 功能含义：设备名称，暴露于用户空间来表示设备。例如 `USB Camera` 。
		- 维护方：<font color="#c00000">驱动必须配置</font>
			- 由驱动方(`struct driver`)设置。
	- `enum vfl_devnode_type vfl_type`
		- 功能含义：描述设备类型，详见[[V4L2概述#^4ac1hk|设备类型枚举]]，例如：
			- `VFL_TYPE_VIDEO` 视频输入输出设备(`/dev/videox`)
			- `VFL_TYPE_RADIO` 无线电调谐器(`/dev/radiox`)
		- 维护方：<font color="#c00000">驱动必须配置</font>
			- 由驱动方设置。
	- `enum vfl_devnode_direction vfl_dir`
		- 功能含义：设备数据流向：
			- `VFL_DIR_RX` 接收(即<span style="background:#fff88f"><font color="#c00000">内核->用户</font></span>，<font color="#c00000">需要以用户态视角来看</font>)
			- `VFL_DIR_TX` 发送(即用户->内核)
			- `VFL_DIR_M2M` 内存到内存(常用于硬件编码器)
		- 维护方：<font color="#c00000">驱动必须配置</font>
			- 由驱动方设置。
	- `int minor` 
		- 功能含义：设备节点的次设备号，即 `/dev/videoX` 中的 `X` 。与V4L2子设备类型相关(例如 `struct video_device` 等)
		- 维护方：V4L2框架自动配置，初始化为 `-1` ，注册设备时填充。
	- `u16 num`
		- 功能含义：同类型(同 `vfl_type` )设备节点编号
		- 维护方：V4L2框架自动配置。
	- `unsigned long flags`
		- 功能含义：设备状态标识，例如是否已注册、是否热插拔等，用于内部管理设备的生命周期。
		- 维护方：V4L2框架配置
	- `int index` 
		- 功能含义：设备在同一驱动管理的多个设备实例中的index，<font color="#c00000">V4L2可能依赖该值用于生成唯一的设备名或sysfs路径</font>。
		- 维护方：驱动建议配置。
	- `u32 device_caps`
		- 功能含义：描述设备的能力(对应用户态[[V4L2概述#^vda0ux|查询设备能力]])
		- 维护方：<font color="#c00000">驱动必须配置</font>
	- `void (*release)(struct video_device *vdev)`
		- 功能含义：设备释放回调
		- 维护方：<font color="#c00000">驱动必须实现及设置</font>
	- `struct mutex *lock` 
		- 功能含义：互斥锁
		- 维护方：若驱动没有实例化该锁，则V4L2会实例化该锁。
			- 对于一些设备，可能需要和其他机制(如DMA)进行同步，V4L2可选地将该成员交由驱动就是为了方便与其他机制联动。
			- 若该锁来自于驱动，则释放时V4L2不会销毁该锁；若该锁由V4L2创建，则V4L2会负责释放该锁。
- 电视信号能力：
	- `v4l2_std_id tvnorms` 
		- 功能含义：设备支持的电视制式(如 `V4L2_STD_NTSC`、`V4L2_STD_PAL`)
		- 维护方：仅当设备涉及电视信号时需设置
- 设备模型及文件接口：
	- `struct device dev` 
		- 功能含义：指向V4L2中属于 `video_device` 的独立设备，<span style="background:#fff88f"><b><font color="#c00000">而非父设备</font></b></span>。通常用 `video_device.dev.parent` 指向父设备实例。
		- 维护方：V4L2框架自动初始化
	- `struct device *dev_parent`
		- 功能含义：可选覆盖的父设备的 `struct device` 指针，可用于配置为非标准父设备结构。
			- 当需要配置为非标准父设备时，在注册V4L2子设备之前驱动手动设置即可。
			- 当注册V4L2子设备时若未配置该项，则V4L2会将 `dev->parent` 设为 `v4l2_dev->dev` 。
		- 维护方：V4L2框架自动配置，驱动可选覆盖。
	- `struct v4l2_device *v4l2_dev` 
		- 功能含义：指向父V4L2设备实例
		- 维护方：<font color="#c00000">驱动必须设置</font>
	- `struct cdev *cdev` 
		- 功能含义：内嵌的字符设备对象，用于在文件系统中暴露 `/dev/videoX`
		- 维护方：V4L2框架自动创建。
	- `const struct v4l2_file_operations *fops`
		- 功能含义：文件操作接口。该成员为 `v4l2_file_operations` 类型。
			- 相比于普通的 `file_operations` 类型简化了相当多的成员(如 `flush` 、 `fsyns` 、 `read_iter` 等)
			- 具体可见[[video_device#^r8lfyg|v4l2_ioctl_ops]]
		- 维护方：<font color="#c00000">驱动必须定义和提供</font>，必须实现的成员有：
			- `owner` ：通常指向 `THIS_MODULE`
			- `open` ：设备打开函数
			- `release` ：设备释放函数
			- `unlocked_ioctl` ：通常指向V4L2实现的 `video_ioctl2`
			- `mmap` ：
	- `const struct v4l2_ioctl_ops *ioctl_ops`
		- 功能含义：ioctl操作函数表，定义设备支持的 `ioctl` 命令
		- 维护方：<font color="#c00000">驱动必须提供至少如下两个基本命令</font>
			- `vidioc_querycap` ：查询设备能力(`VIDIOC_QUERYCAP`)
			- `vidioc_g_fmt_vid_*` ：获取输入或输出设备的当前数据格式(`VIDIOC_G_FMT`)
	- `DECLARE_BITMAP(valid_ioctls, BASE_VIDIOC_PRIVATE)`
		- 功能含义：使用位图标记的设备所支持的 `ioctl` 命令，用于快速检查某个 `ioctl` 命令是否有效
		- 维护方：V4L2框架根据 `ioctl_ops` 自动生成，驱动无需设置。
- 文件句柄与同步
	- `struct list_head fh_list`
		- 功能含义：当前打开的设备文件句柄( `struct v4l2_fh` )链表，管理所有活动的文件句柄(用户空间 `open` 所获得的句柄，用户每多一个句柄链表就多一个成员)。
		- 维护方：由V4L2框架维护
	- `spinlock_t fh_lock`
		- 功能含义：保护 `fh_list` 的自旋锁，当驱动需要读取 `fh_list` 时需要先持有该锁。
		- 维护方：由V4L2框架维护
- 设备控制相关成员：
	- `struct v4l2_ctrl_handler *ctrl_handler`
		- 功能含义：用户可配置的参数项，例如亮度、对比度等
		- 维护方：驱动可选设置
	- `struct vb2_queue *queue`
		- 功能含义：指向视频缓冲区队列，管理视频缓冲区的分配、入队、出队和流控制
		- 维护方：驱动可选配置
	- `struct v4l2_prio_state *prio`
		- 功能含义：设备优先级状态，同[[V4L2概述#^3rx2nr|设备优先级状态]]
		- 维护方：驱动可选，若未设置，默认使用 `v4l2_dev->prio` 
- 媒体控制器相关成员(取决于内核是否开启该功能)：
	- `struct media_entity entity`
		- 功能含义：表示设备在媒体控制器框架中的实体(如摄像头传感器、编码器等)。
			- 描述设备在媒体流水线中的拓扑关系和功能，用于媒体控制器配置(如 `media-ctl` 工具)。
		- 当启用 `CONFIG_MEDIA_CONTROLLER` 后必须设置。
	- `struct media_intf_devnode *intf_devnode`
		- 功能含义：媒体控制器接口
	- `struct media_pipeline pipe`
		- 功能含义：表示设备参与的媒体管线
- 内核调试标志
	- `int dev_debug`
		- 功能含义：内部调试标志，用于内核开发
		- 维护方：驱动不应当修改。

#### 3.3.1 相关API

##### 3.3.1.1 注册video_device设备 ^cjcnad

```C
#include <media/v4l2-dev.h>

/**
 *  video_register_device - register video4linux devices
 *
 * @vdev: struct video_device to register
 * @type: type of device to register, as defined by &enum vfl_devnode_type
 * @nr:   which device node number is desired:
 *	(0 == /dev/video0, 1 == /dev/video1, ..., -1 == first free)
 *
 * Internally, it calls __video_register_device(). Please see its
 * documentation for more details.
 *
 * .. note::
 *	if video_register_device fails, the release() callback of
 *	&struct video_device structure is *not* called, so the caller
 *	is responsible for freeing any data. Usually that means that
 *	you video_device_release() should be called on failure.
 */
static inline int __must_check video_register_device(
		struct video_device *vdev,
		enum vfl_devnode_type type,
		int nr);
```

##### 3.3.1.2 向video_device中添加/获取驱动私有数据

```C
/**
 * video_set_drvdata - sets private data from &struct video_device.
 *
 * @vdev: pointer to &struct video_device
 * @data: private data pointer
 */
static inline void video_set_drvdata(struct video_device *vdev, void *data)
{
	dev_set_drvdata(&vdev->dev, data);
}

/**
 * video_get_drvdata - gets private data from &struct video_device.
 *
 * @vdev: pointer to &struct video_device
 *
 * returns a pointer to the private data
 */
static inline void *video_get_drvdata(struct video_device *vdev)
{
	return dev_get_drvdata(&vdev->dev);
}
```

上述函数操作的是 `vdev->dev->driver_data` 。

##### 3.3.1.3 获取file结构体中的video_device指针

```C
/**
 * video_devdata - gets &struct video_device from struct file.
 *
 * @file: pointer to struct file
 */
struct video_device *video_devdata(struct file *file);
```

#### 3.3.2 模型基本机制

##### 3.3.2.1 上下文实例

需要注意的是：
- <font color="#c00000">V4L2并未提供统一的video_device的上下文实例定义</font>，<font color="#c00000">在V4L2内部只需要操作</font>[[V4L2概述#3 2 4 通用文件句柄管理 v4l2_fh kyd4a1|通用文件管理句柄]]对象，即 `struct v4l2_fh` 。 ^3kv1kh
- 驱动开发者应当根据实际需求自行设计上下文实例，例如添加互斥锁、队列等。

例如 `vim2m` 设备中的上下文实例定义为：

```C
struct vim2m_ctx {
	struct v4l2_fh		fh;
	struct vim2m_dev	*dev;

	struct v4l2_ctrl_handler hdl;

	/* Processed buffers in this transaction */
	u8			num_processed;

	/* Transaction length (i.e. how many buffers per transaction) */
	u32			translen;
	/* Transaction time (i.e. simulated processing time) in milliseconds */
	u32			transtime;

	struct mutex		vb_mutex;
	struct delayed_work	work_run;

	/* Abort requested by m2m */
	int			aborting;

	/* Processing mode */
	int			mode;

	enum v4l2_colorspace	colorspace;
	enum v4l2_ycbcr_encoding ycbcr_enc;
	enum v4l2_xfer_func	xfer_func;
	enum v4l2_quantization	quant;

	/* Source and destination queue data */
	struct vim2m_q_data   q_data[2];
};
```

##### 3.3.2.2 VFS open请求

在VFS向 `video_device` 对应的字符设备发起 `open` 请求时，其会被V4L2内部的 `v4l2_open` 函数统一处理，具体机制逻辑为：
1. 对 `video_device` 管理所用的统一互斥锁 `videodev_lock` 加锁
2. 获取文件指针对应的 `video_device` 实例
3. 执行参数检查
4. 为 `video_device` 增加引用
5. <font color="#c00000">对</font> `videodev_lock` <font color="#c00000">解锁</font>，也就是说<font color="#c00000">用户实现的</font> `open` <font color="#c00000">方法不会占用该锁</font>。
6. 调用注册在 `video_device.ops` 中的 `v4l2_file_operations.open` 方法。
7. 若 `video_device` 启用了debug，则打印上一步中的函数返回值。
8. 将第6步的函数返回值作为 `v4l2_open` 函数的返回值返回。

其对应的最简标准语义应当为：
1. 为该文件指针分配对应的上下文句柄并初始化( `v4l2_fh_init` 等操作)
2. 将<font color="#c00000">文件句柄</font> `&ctx->fh` (<span style="background:#fff88f"><font color="#c00000">而非上下文</font></span>) 存入 `filep->private_data` 中。
	- 不可存其他数据，也不可不存，因为V4L2内部要使用该数据。可见章节[[V4L2概述#^3kv1kh|上下文实例]]。
3. 注册上下文句柄( `v4l2_fh_add` )

### 3.4 机制模型

#### 3.4.1 源控制 ^8230im




#### 3.4.2 媒体请求(media_request) ^dhev4l

在用户态章节编程中已经提到，用户可以使用 `ioctl` 进行媒体设备配置，例如：

```C
ioctl(fd, VIDIOC_S_FMT, &fmt);       // 设置分辨率
ioctl(fd, VIDIOC_S_CTRL, &exposure); // 设置曝光
ioctl(fd, VIDIOC_QBUF, &buffer);     // 提交缓冲区
```

但是考虑如下的需求与情景：
1. 上述demo中，如果分辨率设置成功，曝光设置失败，如何fallback
2. 部分硬件要求分辨率与帧率同时设置(例如不能同时高分辨率和高帧率)
3. 当用户要求两个ioctl指令同时生效时应当如何实现

因此在保留原有ioctl机制的基础上，V4L2又设计了媒体请求机制，其允许将一系列请求按顺序包装为一个媒体请求对象，<font color="#c00000">原子地执行更改</font>：

```C
// 创建媒体请求对象
struct media_request request = create_request();

// 将操作绑定至请求（尚未生效）
request_add_operation(request, VIDIOC_S_FMT, &fmt);      
request_add_operation(request, VIDIOC_S_CTRL, &exposure);
request_add_operation(request, VIDIOC_QBUF, &buffer);

// 原子提交（全成功或全回滚）
ioctl(fd, MEDIA_REQUEST_IOC_QUEUE, &request); 
```

##### 3.4.2.1 媒体请求操作回调(media_device_ops) ^xvploq

媒体请求回调( `media_device_ops` )的数据结构定义如下：

```C
/**
 * struct media_device_ops - Media device operations
 * @link_notify: Link state change notification callback. This callback is
 *		 called with the graph_mutex held.
 * @req_alloc: Allocate a request. Set this if you need to allocate a struct
 *	       larger then struct media_request. @req_alloc and @req_free must
 *	       either both be set or both be NULL.
 * @req_free: Free a request. Set this if @req_alloc was set as well, leave
 *	      to NULL otherwise.
 * @req_validate: Validate a request, but do not queue yet. The req_queue_mutex
 *	          lock is held when this op is called.
 * @req_queue: Queue a validated request, cannot fail. If something goes
 *	       wrong when queueing this request then it should be marked
 *	       as such internally in the driver and any related buffers
 *	       must eventually return to vb2 with state VB2_BUF_STATE_ERROR.
 *	       The req_queue_mutex lock is held when this op is called.
 *	       It is important that vb2 buffer objects are queued last after
 *	       all other object types are queued: queueing a buffer kickstarts
 *	       the request processing, so all other objects related to the
 *	       request (and thus the buffer) must be available to the driver.
 *	       And once a buffer is queued, then the driver can complete
 *	       or delete objects from the request before req_queue exits.
 */
struct media_device_ops {
	int (*link_notify)(struct media_link *link, u32 flags,
			   unsigned int notification);
	struct media_request *(*req_alloc)(struct media_device *mdev);
	void (*req_free)(struct media_request *req);
	int (*req_validate)(struct media_request *req);
	void (*req_queue)(struct media_request *req);
};
```

该结构体有如下的成员：
- `int (*link_notify)(struct media_link *link, u32 flags, unsigned int notification)`
	- 功能含义：媒体链路变更通知回调
	- 标准语义：
		- 返回0时表示成功，其他值表示失败并组织非法配置
	- 维护方：驱动可选实现
- `struct media_request *(*req_alloc)(struct media_device *mdev)`
	- 功能含义：更高级的自定义的 `media_request` 对象内存实现
		- "更高级"指：
			- 使用DMA内存(则此时无法使用 `kmalloc` 的默认实现)
			- 分配比标准 `media_device` 更大的内存，例如驱动定义了一个继承自 `media_device` 的更大的对象时
	- 必须和 `req_free` 同时定义或缺省
	- 维护方：驱动可选实现
- `void (*req_free)(struct media_request *req)`
	- 功能含义：`req_alloc` 对应的资源回收函数
	- 维护方：驱动可选实现
- `int (*req_validate)(struct media_request *req)`
	- 功能含义：验证媒体请求( `media_request` )的合法性
	- 标准语义：
		- 返回0时表示请求合法，非0非法
- `void (*req_queue)(struct media_request *req)`
	- 功能含义：提交已经验证的媒体请求到硬件执行
	- 标准语义：
		- 该函数不能失败(因为已经被 `req_validate` 验证)


#### 3.4.3 通用文件句柄管理(v4l2_fh) ^kyd4a1


#### 3.4.4 v4l2-ioctl


##### 3.4.4.1 v4l2_ioctl_ops ^r8lfyg



其中：
- 设备能力和基本信息查询：
	- `int (*vidioc_querycap)(struct file *file, void *fh, struct v4l2_capability *cap)` ：
		- 功能含义：用户空间调用 `VIDIOC_QUERYCAP` 时触发回调
		- 标准语义：
			- 需要在 `cap` 中存放设备的基本信息，通常包含：
				- 驱动名(例如 `bttv` )
				- 板卡名(例如 `Hauppauge WinTV` )
				- 总线名(例如 `"PCI:" + pci_name(pci_dev)` )
			- 当成功时返回0
- 格式枚举类回调( `vidioc_enum_fmt_*` )：
	- `int (*vidioc_enum_fmt_vid_cap)(...)` ：
		- 功能含义：视频捕获( `VideoCapture` )所支持的<font color="#c00000">像素格式</font>枚举回调
		- 注：
			1. 本类别回调函数的参数均为 `struct file *file, void *fh, struct v4l2_fmtdesc *f` 
			2. V4L2将设备能力的枚举拆分主要是为了兼容历史代码和方便驱动实现。
			3. 后续类似枚举回调与本回调类似。
		- 标准语义：
			- 参数 `struct v4l2_fmtdesc *f` 的 `f->index` 成员为用户空间枚举的引索。
		- 维护方：驱动按需维护
	- `int (*vidioc_enum_fmt_vid_overlay)(...)` ：
		- 功能含义：视频覆盖所支持的像素格式枚举回调
	- `int (*vidioc_enum_fmt_vid_out)(...)` ：
		- 功能含义：视频输出所支持的像素格式枚举回调
	- `int (*vidioc_enum_fmt_sdr_cap)(...)` ：
		- 功能含义：SDR捕获所支持的像素格式枚举回调
	- `int (*vidioc_enum_fmt_sdr_out)(...)` ：
		- 功能含义：SDR输出所支持的格式枚举回调
	- `int (*vidioc_enum_fmt_meta_cap)(...)` ：
		- 功能含义：元数据捕获所支持的格式枚举回调
	- `int (*vidioc_enum_fmt_meta_out)(...)` ：
		- 功能含义：元数据输出所支持的格式枚举回调
- 获取/设置格式类回调( `vidioc_s_fmt_*` / `vidioc_g_fmt_*` )：
	- `int (*vidioc_g_fmt_vid_cap)(...)`
		- <span style="background:#fff88f"><font color="#c00000">注意</font></span>：
			1. 在<span style="background:#fff88f"><font color="#c00000">所有</font></span><font color="#c00000">获取/设置格式类</font>回调的标准行为定义中，<span style="background:#fff88f"><font color="#c00000">当且仅当</font></span> `v4l2_format.type` <font color="#c00000">非法时才可以返回错误值</font>，<font color="#c00000">其他情况下应当由驱动修改到可接受的格式类型</font><span style="background:#fff88f"><font color="#c00000">并返回成功</font></span>。
				- 原文(`Documentation/userspace-api/media/v4l/vidioc-g-fmt.rst`)： `Drivers should not return an error code unless the type field is invalid`
			2. 获取/设置格式类回调文档可见 `Documentation/userspace-api/media/v4l/vidioc-g-fmt.rst`
	- `int (*vidioc_g_fmt_vid_overlay)(...)`
	- `int (*vidioc_g_fmt_vid_out)(...)`
	- 
- 缓冲区管理：
- 分辨率枚举：
	- `int (*vidioc_enum_framesizes)(struct file *file, void *fh, struct v4l2_frmsizeenum *fsize)` ：
		- 功能含义：用户态的分辨率枚举功能 `ioctl(VIDIOC_ENUM_FRAMESIZES)` 的回调
		- 注：
			1. 分辨率枚举文档可见 `Documentation/userspace-api/media/v4l/vidioc-enum-framesizes.rst`
- 帧率枚举：


### 3.5 功能模型

功能模型是指V4L2为一些常见特定设备需求所提供的通用机制。并不是所有的video_device都需要依赖对应的基础机制，使用上述的机制模型也可实现驱动功能。

#### 3.5.1 内存到内存设备(v4l2_m2m_dev) ^vvh0h5

V4L2的内存到内存设备模型<span style="background:#fff88f"><font color="#c00000">适用于一进一出或多进多出</font></span>的<font color="#c00000">视频转换设备</font>，例如：
- 视频编解码器
- 视频格式转换
- 图像处理设备
等，此类设备通常涉及视频编解码、图像缩放、色彩空间转换等。<span style="background:#fff88f"><font color="#c00000">不适用于</font></span>视频输出设备、视频生成设备等。

因此，V4L2的基本模型包含了一进一出两个数据队列，并为该模型提供了若干通用机制。

##### 3.5.1.1 M2M设备模型及机制

V4L2 M2M设备的基本模型如下图([[V4L2_M2M设备.drawio.svg]])所示：
	![[V4L2_M2M设备.drawio.svg]]

M2M设备模型主要提供了如下的机制及支持：
1. 完成了设备的异步处理机制
2. 提供缓冲区管理机制
3. 提供作业调度和同步服务

上述许多机制具有不错的泛用性。但是对于物理摄像头等，应当使用对应的 `videobuf2` 等专用机制。

##### 3.5.1.2 数据结构定义

```C
/**
 * struct v4l2_m2m_dev - per-device context
 * @source:		&struct media_entity pointer with the source entity
 *				Used only when the M2M device is registered via
 *				v4l2_m2m_register_media_controller().
 * @source_pad:		&struct media_pad with the source pad.
 *				Used only when the M2M device is registered via
 *				v4l2_m2m_register_media_controller().
 * @sink:		&struct media_entity pointer with the sink entity
 *				Used only when the M2M device is registered via
 *				v4l2_m2m_register_media_controller().
 * @sink_pad:	&struct media_pad with the sink pad.
 *				Used only when the M2M device is registered via
 *				v4l2_m2m_register_media_controller().
 * @proc:		&struct media_entity pointer with the M2M device itself.
 * @proc_pads:	&struct media_pad with the @proc pads.
 *				Used only when the M2M device is registered via
 *				v4l2_m2m_unregister_media_controller().
 * @intf_devnode:	&struct media_intf devnode pointer with the interface
 *					with controls the M2M device.
 * @curr_ctx:		currently running instance
 * @job_queue:		instances queued to run
 * @job_spinlock:	protects job_queue
 * @job_work:		worker to run queued jobs.
 * @job_queue_flags:	flags of the queue status, %QUEUE_PAUSED.
 * @m2m_ops:		driver callbacks
 */
struct v4l2_m2m_dev {
	struct v4l2_m2m_ctx	*curr_ctx;
#ifdef CONFIG_MEDIA_CONTROLLER
	struct media_entity	*source;
	struct media_pad	source_pad;
	struct media_entity	sink;
	struct media_pad	sink_pad;
	struct media_entity	proc;
	struct media_pad	proc_pads[2];
	struct media_intf_devnode *intf_devnode;
#endif

	struct list_head	job_queue;
	spinlock_t		job_spinlock;
	struct work_struct	job_work;
	unsigned long		job_queue_flags;

	const struct v4l2_m2m_ops *m2m_ops;
};
```

其成员：
- 与当前运行实例相关的成员： ^eienff
	- `struct v4l2_m2m_ctx *curr_ctx` 
		- 功能含义：当前正在运行的实例信息，其包含文件句柄、输出队列、捕获队列、驱动私有指针等数据。
		- 维护方：由V4L2框架管理
	- `struct list_head job_queue` 
		- 功能含义：正在等待处理的实例信息链表，先进先出。
			- 通常驱动不需要手动操作该数据结构。当需要操作时，V4L2也有专用的辅助函数而不需要手动操作(例如 `v4l2_m2m_cleanup_queue` )。
		- 维护方：由V4L2框架管理
	- `spinlock_t job_spinlock` 
		- 功能含义：任务队列的自旋锁。
			- 通常驱动不需要手动操作该数据结构，操作时也通常直接使用辅助函数。
		- 维护方：由V4L2框架管理
	- `struct work_struct job_work` 
		- 功能含义：工作队列的工作项。当有任务需要处理时，V4L2框架会调度这个工作项，它最终会调用驱动提供的操作来响应任务。
		- 维护方：由V4L2框架管理
	- `unsigned long job_queue_flags` 
		- 功能含义：标记任务队列的状态，目前只有 `QUEUE_PAUSED` 这一种状态，表示队列被暂停，不再处理新任务。
		- 维护方：由V4L2框架管理，驱动可以通过 `v4l2_m2m_job_finish` 等函数间接影响状态。
- 操作回调成员：
	- `const struct v4l2_m2m_ops *m2m_ops`
		- 功能含义：指向驱动实现的操作回调函数集的指针。
			- 具体可见[[V4L2概述#^r39fw1|m2m设备操作回调]]。
			- 至少提供 `device_run` 回调。
		- 维护方：<font color="#c00000">必须由驱动设置</font>。
- 媒体控制器相关成员：
	- `struct media_entity *source` 
		- 功能含义：输入数据源媒体的实例
		- 维护方：使用媒体控制器功能时由驱动设置
	- `struct media_pad source_pad`
		- 功能含义：输入数据源的媒体接口
		- 维护方：使用媒体控制器功能时由驱动设置
	- `struct media_entity sink`
		- 功能含义：输出目标的媒体实体
		- 维护方：与sink配对使用
	- `struct media_pad sink_pad`
		- 功能含义：输出目标的媒体接口
		- 维护方：使用媒体控制器功能时由驱动设置
	- `struct media_entity proc`
		- 功能含义：M2M设备自身的处理实体
		- 维护方：使用媒体控制器功能时由驱动设置
	- `struct media_pad proc_pads[2]`
		- 功能含义：处理实体的接口
		- 维护方：与proc配对使用
	- `struct media_intf_devnode *intf_devnode`
		- 功能含义：控制M2M设备的接口节点
		- 维护方：使用媒体控制器功能时由驱动设置

##### 3.5.1.3 M2M设备操作回调(v4l2_m2m_ops) ^r39fw1

该数据结构定义为：

```C
/**
 * struct v4l2_m2m_ops - mem-to-mem device driver callbacks
 * @device_run:	required. Begin the actual job (transaction) inside this
 *		callback.
 *		The job does NOT have to end before this callback returns
 *		(and it will be the usual case). When the job finishes,
 *		v4l2_m2m_job_finish() or v4l2_m2m_buf_done_and_job_finish()
 *		has to be called.
 * @job_ready:	optional. Should return 0 if the driver does not have a job
 *		fully prepared to run yet (i.e. it will not be able to finish a
 *		transaction without sleeping). If not provided, it will be
 *		assumed that one source and one destination buffer are all
 *		that is required for the driver to perform one full transaction.
 *		This method may not sleep.
 * @job_abort:	optional. Informs the driver that it has to abort the currently
 *		running transaction as soon as possible (i.e. as soon as it can
 *		stop the device safely; e.g. in the next interrupt handler),
 *		even if the transaction would not have been finished by then.
 *		After the driver performs the necessary steps, it has to call
 *		v4l2_m2m_job_finish() or v4l2_m2m_buf_done_and_job_finish() as
 *		if the transaction ended normally.
 *		This function does not have to (and will usually not) wait
 *		until the device enters a state when it can be stopped.
 */
struct v4l2_m2m_ops {
	void (*device_run)(void *priv);
	int (*job_ready)(void *priv);
	void (*job_abort)(void *priv);
};
```

其成员：
- `void (*device_run)(void *priv)`
	- 功能含义：驱动处理实际具体M2M任务的<font color="#c00000">入口</font>(也就是说通常不把实际的任务放到这里)。
		- 该函数需要从 `void *priv` 中找到 `v4l2_m2m_dev->curr_ctx` ，并从中找到当前实例正在处理的队列，并执行对应方法。
	- 被执行时机(条件)，需要同时满足：
		1. 已调用 `VIDIOC_STREAMON` 启动 `OUTPUT` 和 `CAPTURE` 队列
		2. 两个队列中都有可用缓冲区(除非 `job_ready` 自定义条件)
		3. 设备当前空闲(无运行中任务)
		4. (如果实现) `job_ready` 返回 `true`
	- 维护方：<span style="background:#fff88f"><font color="#c00000">必须实现</font></span>
	- <span style="background:#fff88f"><font color="#c00000">关键规则</font></span>：
		- <span style="background:#fff88f"><font color="#c00000">该函数禁止阻塞、休眠</font></span>
		- <font color="#c00000">任务完成后通过中断通知</font>(异步，这也是为什么说该函数是入口的原因)，需要调用 `v4l2_m2m_job_finish` 或 ` v4l2_m2m_buf_done_and_job_finish ` 来通知V4L2框架对应任务已经执行完毕。
		- 若任务失败，则调用 `v4l2_m2m_buf_done_and_job_finish(..., VB2_BUF_STATE_ERROR)` 来通知V4L2任务失败。
- `int (*job_ready)(void *priv)`
	- 功能含义：询驱动(设备)当前能否<font color="#c00000">立即</font>开启新任务
	- 维护方：可选
	- <span style="background:#fff88f"><font color="#c00000">关键规则</font></span>：
		- <span style="background:#fff88f"><font color="#c00000">该函数禁止阻塞、休眠</font></span>
		- 该函数应当快速返回
- `void (*job_abort)(void *priv)`
	- 功能含义：任务紧急终止
	- 被执行时机(下列之一)：
		- 用户空间调用 `VIDIOC_STREAMOFF` 停止流
		- 设备文件描述符关闭( `close(fd)` )
		- 模块卸载/设备移除
		- 严重错误发生(如DMA错误)
	- 维护方：可选
	- 关键规则：
		- 该函数禁止等待，必须立即返回，无须等待设备停止(类似于设置 `exit_flag` )：
			- 通常需要通知硬件停止，并将缓冲区标记为错误状态。
		- <font color="#c00000">运行完成后必须调用</font>`v4l2_m2m_job_finish()` <font color="#c00000">或变体</font>
		- 该操作需要注意和保证硬件安全
		- 在该函数调用时，`device_run` 可能还在运行，需要注意并发问题。

##### 3.5.1.4 队列初始化机制

正如上述章节所述，M2M设备拥有输入输出两个队列。








在程序实现方面，M2M基本特性有：
- M2M模型中，驱动需要提供如下接口：
	- `deice_run` \[<font color="#c00000">必须</font>\]：当队列中有需要处理的数据时，V4L2框架会调用该回调。
	- `job_ready` ：
	具体可见[[V4L2概述#3 1 4 3 m2m设备操作回调 v4l2_m2m_ops r39fw1|M2M设备操作回调]]。
- 每一个V4L2 M2M设备可以被多个用户空间实例打开(多个进程或多个线程)，具体使用[[V4L2概述#^eienff|多实例成员]]进行实现。


##### 3.5.1.5 M2M实例分析

为了方便分析，本章节选用 `/drivers/media/test-drivers/vim2m.c` 进行分析。

在该驱动中同时实现了一个设备( `vim2m_pdev` )和一个驱动( `vim2m_pdrv` )，并使用对应API进行了注册：

```C
static struct platform_driver vim2m_pdrv = {
	.probe		= vim2m_probe,
	.remove_new	= vim2m_remove,
	.driver		= {
		.name	= MEM2MEM_NAME,
	},
};

static struct platform_device vim2m_pdev = {
	.name		= MEM2MEM_NAME,
	.dev.release	= vim2m_dev_release,
};

static int __init vim2m_init(void)
{
	int ret;

	ret = platform_device_register(&vim2m_pdev);
	if (ret)
		return ret;

	ret = platform_driver_register(&vim2m_pdrv);
	if (ret)
		platform_device_unregister(&vim2m_pdev);

	return ret;
}
```

其所实现的设备为平台设备，平台设备会在设备或驱动注册时触发[[Linux设备模型#^76yg8m|平台设备驱动匹配机制]]。在本例中，通过将平台设备和平台驱动的 `name` 字段设置为同一个字符串从而进行匹配。

在上述驱动及设备实现的方法中，仅需要关注 `probe` 函数的实现，剩下的 `remove` 和 `release` 则是水到渠成的析构方法。

```C
static int vim2m_probe(struct platform_device *pdev)
{
	struct vim2m_dev *dev;
	struct video_device *vfd;
	int ret;

	dev = kzalloc(sizeof(*dev), GFP_KERNEL);
	if (!dev)
		return -ENOMEM;

	ret = v4l2_device_register(&pdev->dev, &dev->v4l2_dev);
	if (ret)
		goto error_free;

	atomic_set(&dev->num_inst, 0);
	mutex_init(&dev->dev_mutex);

	dev->vfd = vim2m_videodev;
	vfd = &dev->vfd;
	vfd->lock = &dev->dev_mutex;
	vfd->v4l2_dev = &dev->v4l2_dev;

	video_set_drvdata(vfd, dev);
	v4l2_info(&dev->v4l2_dev,
		  "Device registered as /dev/video%d\n", vfd->num);

	platform_set_drvdata(pdev, dev);

	dev->m2m_dev = v4l2_m2m_init(&m2m_ops);
	if (IS_ERR(dev->m2m_dev)) {
		v4l2_err(&dev->v4l2_dev, "Failed to init mem2mem device\n");
		ret = PTR_ERR(dev->m2m_dev);
		dev->m2m_dev = NULL;
		goto error_dev;
	}

#ifdef CONFIG_MEDIA_CONTROLLER
	dev->mdev.dev = &pdev->dev;
	strscpy(dev->mdev.model, "vim2m", sizeof(dev->mdev.model));
	strscpy(dev->mdev.bus_info, "platform:vim2m",
		sizeof(dev->mdev.bus_info));
	media_device_init(&dev->mdev);
	dev->mdev.ops = &m2m_media_ops;
	dev->v4l2_dev.mdev = &dev->mdev;
#endif

	ret = video_register_device(vfd, VFL_TYPE_VIDEO, 0);
	if (ret) {
		v4l2_err(&dev->v4l2_dev, "Failed to register video device\n");
		goto error_m2m;
	}

#ifdef CONFIG_MEDIA_CONTROLLER
	ret = v4l2_m2m_register_media_controller(dev->m2m_dev, vfd,
						 MEDIA_ENT_F_PROC_VIDEO_SCALER);
	if (ret) {
		v4l2_err(&dev->v4l2_dev, "Failed to init mem2mem media controller\n");
		goto error_v4l2;
	}

	ret = media_device_register(&dev->mdev);
	if (ret) {
		v4l2_err(&dev->v4l2_dev, "Failed to register mem2mem media device\n");
		goto error_m2m_mc;
	}
#endif
	return 0;

#ifdef CONFIG_MEDIA_CONTROLLER
error_m2m_mc:
	v4l2_m2m_unregister_media_controller(dev->m2m_dev);
#endif
error_v4l2:
	video_unregister_device(&dev->vfd);
	/* vim2m_device_release called by video_unregister_device to release various objects */
	return ret;
error_m2m:
	v4l2_m2m_release(dev->m2m_dev);
error_dev:
	v4l2_device_unregister(&dev->v4l2_dev);
error_free:
	kfree(dev);

	return ret;
}
```

注：
- 上述 `vim2m_probe` 函数第24行 `v4l2_info(&dev->v4l2_dev, "Device registered as /dev/video%d\n", vfd->num);` 应当移动到第47行 `video_register_device` 之后。该bug已经在Linux 6.16被修复。

忽略其错误及垃圾清理，其流程如下：
1. 初始化私有结构体
2. 调用 `v4l2_device_register` 完成：
	1. 初始化指定的 `v4l2_device` 对象
	2. 将 `v4l2_device` 记录到 `device.driver_data`
3. 初始化互斥锁和实例计数器
4. 初始化并配置video设备：
	1. 
5. 初始化内存到内存框架(m2m)
6. 注册video设备到内核




