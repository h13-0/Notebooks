---
number headings: auto, first-level 1, max 6, 1.1
---
#嵌入式 #Linux驱动开发 #V4L2 

# 1 目录

```toc
```

# 2 video_device用户态开发概述

## 2.1 基础知识 ^ks4hji

本章节的基础知识无序排列。

### 2.1.1 原始视频格式

原始视频格式相关内容可见章节[[音视频开发/音视频开发入门#^w9205z|原始视频格式]]：
![[音视频开发/音视频开发入门#2 2 原始视频格式 w9205z]]

其中，需要额外补充的是：
- 在Linux中，默认最大平面数为8( `VIDEO_MAX_PLANES` )，而通常对于视频数据来说，其平面数通常不会多于4(FFmpeg中也是固定为4)。

## 2.2 视频设备用户态开发(/dev/video*)

### 2.2.1 基本工作流程

视频设备的基本工作流程如下：
	![[视频设备用户态流程.svg]]

### 2.2.2 打开设备节点

和普通字符设备一样，使用Linux操作摄像头时，第一步依旧是打开摄像头对应的文件节点。

```C
#include <fcntl.h>
#include <stdio.h>

int fd = open(device, O_RDWR);  
if(fd < 0) {  
    printf("open device: %s failed.\r\n", device);  
}
```

### 2.2.3 查询设备能力 ^vda0ux

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

### 2.2.4 枚举输出格式

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

### 2.2.5 枚举指定输出格式的分辨率 ^v0i94g

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

### 2.2.6 设置指定的视频格式和分辨率

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

### 2.2.7 申请缓冲区 ^2l9q6s

#### 2.2.7.1 V4L2缓冲区类型 ^ekflbd

V4L2框架一共提供了如下三种缓冲区：
- `V4L2_MEMORY_MMAP` ：使用 `mmap` 将内核分配的缓冲区映射到用户空间
	- 数据流动：`硬件 -(DMA)-> DMA缓冲区 <-(内存映射)->用户空间`
	- 在用户态编程时，[[mmap#^go6lxw|mmap]]<font color="#c00000">的操作对象是将一个fd的offset处映射到指定内存区域</font>，因此在使用mmap方式操作缓冲区时也是<font color="#c00000">获取到缓冲区</font><span style="background:#fff88f"><font color="#c00000">相对于fd的offset</font></span>后进行操作。
	- 无需拷贝，性能较好。
	- 注意：
		- 具体分配什么类型的内存取决于驱动的后端实现，<font color="#c00000">大多数情况下是DMA缓冲区</font>，<font color="#c00000">但也不绝对</font>
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

#### 2.2.7.2 API调用

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

### 2.2.8 将缓存加入缓存队列

将缓存加入缓存队列的目的是： ^iuf8ml
- 显式的避免用户和内核同时操作同一片缓冲区，避免用户态访问到被内核正在使用且保护的缓冲区导致用户态挂掉。
- 提供一种用户态-内核态的缓冲区同步机制，该机制如下：
	1. 用户态将空的/使用过的缓冲区塞入内核态队列
	2. 用户态通过系统调用使得内核态将填满数据的[[video_device#^qftknt|缓冲区出队]]并返回给用户态

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

注：
- 可参阅：[[VB2概述#^nijdvg|VB2缓冲区状态与生命周期]]

### 2.2.9 mmap映射缓存

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

### 2.2.10 开启流传输

```C
enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;  
ret = ioctl(fd, VIDIOC_STREAMON, &type);  
if(ret < 0) {  
    printf("VIDIOC_STREAMON failed with msg: %s\r\n", strerror(errno));  
}
```

### 2.2.11 缓冲区出队 ^qftknt

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

### 2.2.12 输入设备完整示例代码

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

### 2.2.13 输出设备完整示例代码


### 2.2.14 m2m设备完整实例代码

可见[[mm2m_device#^j7ak9n|mm2m用户态测试]]。

## 2.3 video_device用户态工具



# 3 video_device内核态开发

内核态开发必须拥有如下的基础知识：
- [[VB2概述]]
- [[V4L2概述#^dyadtz|V4L2基础概述]]

## 3.1 VB2的v4l2特化

### 3.1.1 缓冲区类型枚举(enum v4l2_buf_type) ^u8ke9r

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

### 3.1.2 VB2 v4l2_ioctl_ops helper ^1yz9a7

VB2框架为V4L2提供了如下的 `v4l2_ioctl_ops` 的预置实现：

```C
/* struct v4l2_ioctl_ops helpers */

int vb2_ioctl_reqbufs(struct file *file, void *priv,
			  struct v4l2_requestbuffers *p);
int vb2_ioctl_create_bufs(struct file *file, void *priv,
			  struct v4l2_create_buffers *p);
int vb2_ioctl_prepare_buf(struct file *file, void *priv,
			  struct v4l2_buffer *p);
int vb2_ioctl_querybuf(struct file *file, void *priv, struct v4l2_buffer *p);
int vb2_ioctl_qbuf(struct file *file, void *priv, struct v4l2_buffer *p);
int vb2_ioctl_dqbuf(struct file *file, void *priv, struct v4l2_buffer *p);
int vb2_ioctl_streamon(struct file *file, void *priv, enum v4l2_buf_type i);
int vb2_ioctl_streamoff(struct file *file, void *priv, enum v4l2_buf_type i);
int vb2_ioctl_expbuf(struct file *file, void *priv,
	struct v4l2_exportbuffer *p);
int vb2_ioctl_remove_bufs(struct file *file, void *priv,
			  struct v4l2_remove_buffers *p);
```


明显地，上述helpers通过函数的参数 `struct v4l2_buffer *p` 来跳过驱动的数据结构定义来获取需要操作的缓冲对象。

在上述helpers中：
- 

注意：
- <font color="#c00000">上述helpers需要设置</font> `video_device.queue` <font color="#c00000">后才可以使用</font>

### 3.1.3 手动操作函数

#### 3.1.3.1 申请缓冲区(vb2_reqbufs)

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
- 驱动可以不关心上述逻辑，只需要使用VB2提供的预置实现即可，后续同类型函数不再赘述。

#### 3.1.3.2 查询缓冲区信息(vb2_querybuf)

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




## 3.2 video_device设备类型(enum vfl_devnode_type) ^4ac1hk

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

## 3.3 video_device基础特性

正如[[V4L2概述#2 2 1 基础设备模型 4783s6|基础设备模型]]所述，video_device提供了包含视频设备( `/dev/video*` )、收音机设备( `/dev/radio*` )等功能模型。

### 3.3.1 数据结构

其数据结构定义见章节[[Linux内核原理及其开发/内核源码探析/内核源码分析/include/v4l2-dev.h#^bd1jcw|video_device]]：
![[Linux内核原理及其开发/内核源码探析/内核源码分析/include/v4l2-dev.h#video_device bd1jcw]]

### 3.3.2 相关API

#### 3.3.2.1 注册video_device设备 ^cjcnad

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

#### 3.3.2.2 取消注册video_device设备

```C
/**
 * video_unregister_device - Unregister video devices.
 *
 * @vdev: &struct video_device to register
 *
 * Does nothing if vdev == NULL or if video_is_registered() returns false.
 */
void video_unregister_device(struct video_device *vdev);
```

注意：
1. 该函数的参数可以为 `NULL` 
2. `video_device` <font color="#c00000">可以反复被该函数取消注册</font>(若传入对象未被注册则直接返回)
	- 其判断 `video_device` 是否被注册依赖于 `vdev->flags` 中的 `V4L2_FL_REGISTERED` 位
3. 对于需要取消注册的 `video_device` 对象，V4L2会自己释放由其负责维护的成员(例如 `dev` 成员)
4. <font color="#c00000">当</font> `video_device` <font color="#c00000">的引用计数器归0时</font>，<span style="background:#fff88f"><font color="#c00000">其会自动调用</font></span> `video_device.release` <span style="background:#fff88f"><font color="#c00000">回调</font></span>，因此在驱动注册设备的错误回滚中需要注意 `fallback` 与 `video_device.release` 的配合。

#### 3.3.2.3 向video_device中添加/获取驱动私有数据

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

#### 3.3.2.4 获取file结构体中的video_device指针

```C
/**
 * video_devdata - gets &struct video_device from struct file.
 *
 * @file: pointer to struct file
 */
struct video_device *video_devdata(struct file *file);
```

#### 3.3.2.5 获取设备节点名称

```C
/**
 * video_device_node_name - returns the video device name
 *
 * @vdev: pointer to &struct video_device
 *
 * Returns the device name string
 */
static inline const char *video_device_node_name(struct video_device *vdev)
{
	return dev_name(&vdev->dev);
}
```

### 3.3.3 模型基本机制

#### 3.3.3.1 V4L2上下文实例 ^kyd4a1

V4L2为每个可以被打开的文件节点(或设备)设计了一个统一的上下文实例，其用于记录每一个用户态打开后的句柄。其基本数据结构为：

```C
/**
 * struct v4l2_fh - Describes a V4L2 file handler
 *
 * @list: list of file handlers
 * @vdev: pointer to &struct video_device
 * @ctrl_handler: pointer to &struct v4l2_ctrl_handler
 * @prio: priority of the file handler, as defined by &enum v4l2_priority
 *
 * @wait: event' s wait queue
 * @subscribe_lock: serialise changes to the subscribed list; guarantee that
 *		    the add and del event callbacks are orderly called
 * @subscribed: list of subscribed events
 * @available: list of events waiting to be dequeued
 * @navailable: number of available events at @available list
 * @sequence: event sequence number
 *
 * @m2m_ctx: pointer to &struct v4l2_m2m_ctx
 */
struct v4l2_fh {
	struct list_head	list;
	struct video_device	*vdev;
	struct v4l2_ctrl_handler *ctrl_handler;
	enum v4l2_priority	prio;

	/* Events */
	wait_queue_head_t	wait;
	struct mutex		subscribe_lock;
	struct list_head	subscribed;
	struct list_head	available;
	unsigned int		navailable;
	u32			sequence;

	struct v4l2_m2m_ctx	*m2m_ctx;
};
```

其成员：
- `struct list_head list` ：
	- 功能含义：该上下文所在文件上下文链表的<font color="#c00000">节点</font>(而非表头)
	- 维护方：V4L2框架自动维护
- `struct video_device *vdev` ：
	- 功能含义：当前文件句柄所关联的 `video_device` 实例
	- 维护方：<font color="#c00000">由驱动设置</font>(通常在 `open` 函数初始化 `v4l2_fh` 时设置)
- `struct v4l2_ctrl_handler *ctrl_handler` ：
	- 功能含义：指向用户可配置的参数项句柄，例如亮度、对比度等
	- 维护方：在需要控制项时由驱动管理
- `enum v4l2_priority prio` ：
	- 功能含义：表示该句柄的优先级
	- 维护方：用户空间通过 `VIDIOC_S_PRIORITY` (ioctl)设置，随后框架负责将优先级存储到该字段。内存可能需要读取使用。
- `wait_queue_head_t wait` ：
	- 功能含义：队列等待头，用户空间触发等待事件时会在该队列等待(如 `poll` 等)
	- 维护方：V4L2负责维护，且在发生自定义事件时驱动可通过该队列唤醒队列
- `struct mutex subscribe_lock` ：
	- 功能含义：互斥锁，用于保护下一个成员 `subscribed` 链表
	- 维护方：V4L2负责维护，驱动不需要访问
- `struct list_head subscribed` ：
	- 功能含义：用于链接文件句柄所订阅的事件(`struct v4l2_subscribed_event`)
	- 维护方：V4L2负责维护。
- `struct list_head available` ：
	- 功能含义：用于链接存储已经发生但未被用户空间读取(出队)的事件(`struct v4l2_kevent`)，这些事件在链表里按照发生的先后顺序排列。
	- 维护方：V4L2负责维护，驱动可通过 `v4l2_event_queue` 添加事件。
- `unsigned int navailable` ：
	- 功能含义：`available` 中的数量
	- 维护方：V4L2负责维护
- `u32 sequence` ：
	- 功能含义：事件序列号，每当新事件添加到 `available` 链表时，该序列号会递增并作为该事件的序列号。可用于用户空间检测事件丢失。
	- 维护方：V4L2负责维护
- `struct v4l2_m2m_ctx *m2m_ctx` ：
	- 功能含义：专为M2M设备提供的[[video_device#^3axphz|M2M上下文实例]]指针，当不为M2M设备时，该指针为 `NULL` 。
	- 维护方：
		- 对于M2M设备，驱动创建 `v4l2_fh` 时就应当创建该成员，关闭该句柄时释放该成员
		- 对于非M2M设备，保持为 `NULL` 即可。

需要注意的是：
- <font color="#c00000">V4L2并未提供统一的video_device的上下文实例定义</font>，<font color="#c00000">在V4L2内部只需要操作</font>[[video_device#^kyd4a1|通用文件管理句柄]]对象，即 `struct v4l2_fh` 。 ^3kv1kh
- 驱动开发者应当根据实际需求自行设计上下文实例，例如添加互斥锁、队列、若干设备参数等。

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

##### 3.3.3.1.1 相关API

###### 3.3.3.1.1.1 初始化文件句柄(v4l2_fh_init)

```C
/**
 * v4l2_fh_init - Initialise the file handle.
 *
 * @fh: pointer to &struct v4l2_fh
 * @vdev: pointer to &struct video_device
 *
 * Parts of the V4L2 framework using the
 * file handles should be initialised in this function. Must be called
 * from driver's v4l2_file_operations->open\(\) handler if the driver
 * uses &struct v4l2_fh.
 */
void v4l2_fh_init(struct v4l2_fh *fh, struct video_device *vdev);
```

该函数：
- 功能含义：初始化指针指向的文件句柄，并关联到对应的 `video_device` 
- 注意事项：
	1. <font color="#c00000">必须</font>在 `v4l2_file_operations->open()` 中被调用
	2. <font color="#c00000">必须</font>所有使用 `struct v4l2_fh` 的驱动中都要调用
	3. 必须在 `v4l2_fh_add()` 前被调用
	4. 此函数只初始化文件句柄，并不将其加入到设备列表中(该功能是 `v4l2_fh_add` 负责)

###### 3.3.3.1.1.2 添加文件句柄到设备列表(v4l2_fh_add)

```C
/**
 * v4l2_fh_add - Add the fh to the list of file handles on a video_device.
 *
 * @fh: pointer to &struct v4l2_fh
 *
 * .. note::
 *    The @fh file handle must be initialised first.
 */
void v4l2_fh_add(struct v4l2_fh *fh);
```

该函数：
- 功能含义：
	1. 将文件句柄添加到视频设备的文件句柄列表中
	2. 使文件句柄能够接收设备事件和通知
	3. 设置 `struct file.private_data` 指向文件句柄
- 注意事项：
	1. 此操作会使文件句柄开始接收设备事件

###### 3.3.3.1.1.3 从设备列表移除文件句柄(v4l2_fh_del)

```C
/**
 * v4l2_fh_del - Remove file handle from the list of file handles.
 *
 * @fh: pointer to &struct v4l2_fh
 *
 * On error filp->private_data will be %NULL, otherwise it will point to
 * the &struct v4l2_fh.
 *
 * .. note::
 *    Must be called in v4l2_file_operations->release\(\) handler if the driver
 *    uses &struct v4l2_fh.
 */
void v4l2_fh_del(struct v4l2_fh *fh);
```

该函数：
- 功能含义：
	1. 从视频设备的文件句柄列表中移除指定的文件句柄
	2. 停止文件句柄接收设备事件和通知
	3. 设置 `struct file.private_data` 为 NULL
- 注意事项：
	1. 必须在 `v4l2_file_operations->release()` 中被调用
	2. 必须在 `v4l2_fh_exit()` 之前调用

###### 3.3.3.1.1.4 释放文件句柄相关资源

```C
/**
 * v4l2_fh_exit - Release resources related to a file handle.
 *
 * @fh: pointer to &struct v4l2_fh
 *
 * Parts of the V4L2 framework using the v4l2_fh must release their
 * resources here, too.
 *
 * .. note::
 *    Must be called in v4l2_file_operations->release\(\) handler if the
 *    driver uses &struct v4l2_fh.
 */
void v4l2_fh_exit(struct v4l2_fh *fh);
```

该函数：
- 功能含义：释放文件句柄
- 注意事项：
	1. 必须在 `v4l2_file_operations->release()` 中被调用
	2. 在 `v4l2_fh_del()` 之后调用

###### 3.3.3.1.1.5 检查某文件句柄是否是设备的唯一句柄(v4l2_fh_is_singular)

```C
/**
 * v4l2_fh_is_singular - Returns 1 if this filehandle is the only filehandle
 *	 opened for the associated video_device.
 *
 * @fh: pointer to &struct v4l2_fh
 *
 * If @fh is NULL, then it returns 0.
 */
int v4l2_fh_is_singular(struct v4l2_fh *fh);
```

该函数：
- 功能含义：
	- 检查给定的文件句柄是否是关联视频设备上唯一打开的文件句柄
- 返回值：如果该 `fh` 是该设备唯一的打开句柄，则返回 `1` ，否则返回 `0`

#### 3.3.3.2 VFS open请求 ^qykuuk

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
1. 为该文件指针分配对应的<font color="#c00000">video_device的上下文句柄</font>并初始化其中的[[video_device#^kyd4a1|v4l2上下文实例]]( `v4l2_fh_init` 等操作)
2. 将[[video_device#^kyd4a1|v4l2上下文实例]](是 `&ctx->fh` <span style="background:#fff88f"><font color="#c00000">而非video_device的上下文</font></span>，虽然通常等价) 存入 `filep->private_data` 中。
	- 通常 `fh` 会是 `ctx` 的第一个成员，因此通常二者等价。
	- 虽然v4l2在open回调中允许不使用[[video_device#^kyd4a1|v4l2上下文实例]]，但是其提供的功能需要自行实现，因此通常还是使用该特性。
3. 注册v4l2上下文实例( `v4l2_fh_add` )

注意：
1. 在不使用v4l2上下文实例时，`filep->private_data` 允许存储video_device的上下文句柄。
2. 不管 `filep->private_data` 中存入的是什么，<span style="background:#fff88f"><font color="#c00000">该值会出现在</font></span>：
	- [[video_device#^r8lfyg|v4l2_ioctl_ops]]的所有回调的参数 `void* fh` 中
		- 该参数指针为 `void*` 而非 `struct v4l2_fh*` 就是因为 `open` 回调中

## 3.4 机制模型

### 3.4.1 源控制 ^8230im




### 3.4.2 媒体请求(media_request) ^dhev4l

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

#### 3.4.2.1 媒体请求操作回调(media_device_ops) ^xvploq

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

### 3.4.3 v4l2-ioctl


#### 3.4.3.1 v4l2_ioctl_ops ^r8lfyg

> [!attention]
> - 本结构体中的所有回调均<font color="#c00000">已拥有了</font> `struct video_device.lock` ，<font color="#c00000">不需要再额外加锁!!!</font>
> - 而[[VB2概述]]中讲的[[VB2概述#^tqizjf|struct vb2_ops]]中需要操作(不难理解，因为vb2框架并不管video设备)

该结构体包含了众多ioctl回调接口(具体可见源码定义)，其主要包括：
- 设备能力和基本信息查询：
	- `int (*vidioc_querycap)(struct file *file, void *fh, struct v4l2_capability *cap)` ：
		- 功能含义：用户空间调用 `VIDIOC_QUERYCAP` 时触发回调
		- 参数：
			- `struct file *file` ：用户的打开实例
			- `void *fh` 为：[[video_device#^qykuuk|open]]回调中设置的 `file->private_data` 的值，通常为 `struct v4l2_fh` 且与video_device的上下文句柄等价
			- `struct v4l2_capability *cap` ：
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
	- 该类型的标准语义为：
		- 功能含义：
			1. 在<span style="background:#fff88f"><font color="#c00000">所有</font></span><font color="#c00000">获取/设置/尝试格式类</font>回调的标准行为定义中，<span style="background:#fff88f"><font color="#c00000">当且仅当</font></span> `v4l2_format.type` <font color="#c00000">非法时才可以返回错误值</font>，<font color="#c00000">其他情况下应当由驱动修改到可接受的格式类型</font><span style="background:#fff88f"><font color="#c00000">并返回成功</font></span>。
				- 原文(`Documentation/userspace-api/media/v4l/vidioc-g-fmt.rst`)： `Drivers should not return an error code unless the type field is invalid`
				- 尽管对用户层的请求已经做过一次路由转发，<font color="#c00000">但是驱动仍需要检查</font>
			2. 获取/设置格式类回调文档可见 `Documentation/userspace-api/media/v4l/vidioc-g-fmt.rst`
		- 注意：
			- 所有<font color="#c00000">与应用程序交换数据的</font>V4L2设备<font color="#c00000">都需要实现对应的获取/设置格式类回调</font>
	- `int (*vidioc_g_fmt_vid_cap)(...)` 
	- `int (*vidioc_g_fmt_vid_overlay)(...)` 
	- `int (*vidioc_g_fmt_vid_out)(...)` 
	- 
- 缓冲区管理(<font color="#c00000">这些回调通常不需要自行实现</font>，参考语义在使用helpers时仅供了解)：
	- `int (*vidioc_reqbufs)(struct file *file, void *fh, struct v4l2_requestbuffers *b)` ：
		- 功能含义：请求分配缓冲区回调
		- 参考语义：
			1. 验证 `b->type` 和 `b->memory` 是否受支持
			2. 如果 `b->count == 0`，则释放所有缓冲区并返回 `0` 
			3. 分配 `b->count` 个缓冲区
			4. 设置 `b->count` 为实际分配的缓冲区数量
			5. 初始化缓冲区队列状态
		- 返回值：成功时为 `0` ，否则为负的错误码
		- 实现参考：
			1. 完成 `b->type` 和 `b->memory` 验证
			2. 调用并返回 `vb2_core_reqbufs` 完成后续语义
	- `int (*vidioc_querybuf)(struct file *file, void *fh, struct v4l2_buffer *b)` ：
		- 功能含义：查询已分配缓冲区的信息，如物理地址、长度和偏移量
		- 参考语义：
			1. 验证 `b->type` 是否合法
			2. 验证 `b->index` 是否在有效范围内
			3. 根据内存类型填充相应字段：
				- `MMAP` ：`b->m.offset` 、`b->length`
				- `USERPTR` ：`b->m.userptr` 、`b->length`
				- `DMABUF` ：`b->m.fd`
			4. 填充其他字段：`b->flags` 、 `b->field` 、`b->timestamp` 等
		- 返回值：成功时为 `0` ，无效索引返回 `-EINVAL` 
		- 实现参考：
			1. 从 `file` 中找到 `video_device` ，并提取要查询的队列
			2. 调用 `vb2_querybuf` 完成后续语义
- 分辨率枚举：
	- `int (*vidioc_enum_framesizes)(struct file *file, void *fh, struct v4l2_frmsizeenum *fsize)` ：
		- 功能含义：用户态的分辨率枚举功能 `ioctl(VIDIOC_ENUM_FRAMESIZES)` 的回调
		- 注：
			1. 分辨率枚举文档可见 `Documentation/userspace-api/media/v4l/vidioc-enum-framesizes.rst`
- 帧率枚举：
- 尝试格式类回调(`vidioc_try_fmt_*`)：
	- 该类型的标准语义为：
		- 功能含义：
			- 等价于对应的 `vidioc_s_fmt_*` ，除了：
				- 不改变驱动程序状态(原文： `it does not change driver state.`)
				- 在任何时刻都可以被调用，不会返回 `-EBUSY` 
			- `VIDIOC_TRY_FMT` <font color="#c00000">返回的格式必须与</font> `VIDIOC_S_FMT` <font color="#c00000">为同一输入或输出返回的格式相同</font>
		- 返回值：
			- `0` ：表示尝试设置成功，且驱动已更新为目标格式
			- `-EINVAL` ：表示驱动不支持该缓冲区

注：
- v4l2以及VB2提供了多种模型下的helper，例如：
	- [[video_device#^1yz9a7|VB2 v4l2_ioctl_ops helper]]
	等。

### 3.4.4 切片特性 ^3vrjl8

对于输出设备而言，其一个常见的特性为切片特性，其支持将一个完整帧拆分为若干切片进行分段提交。该特性的几个常见用途有：
- 对于编码器，部分视频流格式支持将同一个帧切分为多个切片并行处理，可利用该特性提高硬件的并行效率。
- 对于高分辨率场景进行切片可降低内存占用。
- 将一个完整帧切成若干切片，当第一个切片到达时即可开启任务，可降低处理延迟。
因此该特性常见于输出队列(用户->内核)，不过也有罕见的使用切片的捕获队列。

该特性的开启需要：
1. 在驱动声明设备能力时，使用 `V4L2_BUF_CAP_SUPPORTS_M2M_HOLD_CAPTURE_BUF` 标志
2. 在用户配置 `v4l2_buffer` 时：
	1. 在每个帧切片传输完毕前的每一个切片都要在 `v4l2_buffer.flag` 中开启上述标志
	2. 在每个帧切片传输接收后取消上述标志，即帧切片传输完毕

切片的具体切分方法


### 3.4.5 排空 ^u38eft

排空(Draining)状态通常发生在编码器或解码器的终止过程中，其与捕获设备终止过程的区别在于：
- 用户发起捕获设备的终止时，<font color="#c00000">用户通常不需要尚未处理完毕的帧</font>，<span style="background:#fff88f"><font color="#c00000">驱动通常也会将这些帧标记为错误帧</font></span>。
- 而用户在发起编解码器的终止时，<font color="#c00000">用户往往是因为该视频片段已经完全提交给驱动</font>，<span style="background:#fff88f"><font color="#c00000">并且希望驱动能继续处理已经提交的帧</font></span>。
在进行排空时，其通常有如下协作流程：
1. 用户通过命令发起排空(`V4L2_ENC_CMD_STOP`)
2. 当驱动处理完所有帧后，驱动发起 `V4L2_EVENT_EOS` (End Of Stream)事件

### 3.4.6 多输入单输出机制 ^10xf45

多输入单输出机制主要有如下的使用情况：
1. [[video_device#^3vrjl8|切片处理]]，多个切片处理为一个输出帧
2. 视频流编码的帧间压缩，例如H264的 `参考帧 + 当前帧 -> 压缩帧` 
3. 图像合成，例如 `背景层 + 前景层 + 遮罩层 -> 合成图像` 
4. 视频稳定器，例如 `当前帧 - 运动矢量 -> 稳定帧`  
5. HDR处理，例如 `短曝光帧 + 长曝光帧 -> HDR 帧` 

## 3.5 功能模型

功能模型是指V4L2为一些常见特定设备需求所提供的通用机制。并不是所有的video_device都需要依赖对应的基础机制，使用上述的机制模型也可实现驱动功能。

### 3.5.1 内存到内存模型(v4l2_m2m_dev) ^vvh0h5

V4L2的内存到内存设备模型<span style="background:#fff88f"><font color="#c00000">适用于一进一出或多进多出</font></span>的<font color="#c00000">视频转换设备</font>，例如：
- 视频格式转换：
	- 视频编解码器，例如：
		- H.264编码器，其输入为普通的 `YUV` 格式的帧，输出为 `H264` 的视频帧
	- 虚拟摄像头，例如 `v4l2loopback` 
- 图像处理设备
等，此类设备通常涉及视频编解码、图像缩放、色彩空间转换等。<span style="background:#fff88f"><font color="#c00000">不适用于</font></span>视频输出设备、视频生成设备等。

因此，V4L2的基本模型包含了一进一出两个数据队列，并为该模型提供了若干通用机制。

需要注意：
1. <span style="background:#fff88f"><font color="#c00000">m2m模型是为同一个打开实例设计的</font></span>，<font color="#c00000">必须在同一个线程的同一个打开中使用</font>。而非类似于IPC的loopback模式。
2. 与 `video_device` 和 `v4l2_device` 不同的是，`v4l2_m2m_dev` <span style="background:#fff88f"><font color="#c00000">并不是设备</font></span>：
	1. <font color="#c00000">该对象没有嵌入</font> `struct device` 
	2. <font color="#c00000">该对象不会注册到sysfs中</font>
	`v4l2_m2m_dev` <font color="#c00000">应当属于<u>M2M设备上下文</u></font>
2. `v4l2_m2m_dev` 独立于 `video_device` ，其允许多个 `video_device` 共享同一个m2m设备(尽管一般不这么做)：
	- <font color="#c00000">关联时机并不在</font>m2m实例化或 `video_device` <font color="#c00000">注册时绑定</font>，<span style="background:#fff88f"><font color="#c00000">其在</font></span> `video_device` <span style="background:#fff88f"><font color="#c00000">被打开时</font></span>，<font color="#c00000">创建用户上下文实例时关联</font>。
3. 注意区分：
	1. `v4l2_m2m_dev` 为M2M设备上下文：
		- 每个物理M2M设备只有一个 `v4l2_m2m_dev` 实现
		- 通常在驱动程序的 `probe` 中通过 `v4l2_m2m_init` 创建
		- 其负责管理M2M设备的资源，包含：
			- 作业队列
			- 管理多个用户上下文
			- 提供硬件回调的注册等
		- 不直接与用户交互，而是通过 `video_device` 和 `v4l2_m2m_ctx` 间接交互
	2. `v4l2_m2m_ctx` 为用户上下文：
		- M2M设备的每次打开都会有一个 `v4l2_m2m_ctx` 实例
		- 通常在驱动程序的 `open` 回调中通过 `v4l2_m2m_ctx_init` 创建
		- 其代表一个用户会话，包含：
			- 源队列、目标队列的缓冲区信息
			- 该会话的状态
			- 所属的设备上下文指针

#### 3.5.1.1 M2M模型及机制

V4L2 M2M模型如[[V4L2_M2M设备.drawio.svg|下图]]所示：
	![[V4L2_M2M设备.drawio.svg]]

M2M内部使用了输入输出两个队列进行实现，因此其也拥有如下的与普通VB2设备相似的特性：
1. 完成了设备的异步处理机制
2. 提供缓冲区管理机制
3. 提供作业调度和同步服务
与普通捕获设备不同的是，本设备需要着重注意以下机制：
- [[video_device#^3vrjl8|切片特性]]
- [[video_device#^u38eft|排空]]

#### 3.5.1.2 数据结构定义

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
			- 具体可见[[video_device#^r39fw1|m2m设备操作回调]]。
			- 至少提供 `device_run` 回调。
		- 维护方：<font color="#c00000">驱动必须在注册设备时传入该参数</font>(而非直接设置)
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

#### 3.5.1.3 M2M用户上下文实例 ^3axphz

```C
/**
 * struct v4l2_m2m_ctx - Memory to memory context structure
 *
 * @q_lock: struct &mutex lock
 * @new_frame: valid in the device_run callback: if true, then this
 *		starts a new frame; if false, then this is a new slice
 *		for an existing frame. This is always true unless
 *		V4L2_BUF_CAP_SUPPORTS_M2M_HOLD_CAPTURE_BUF is set, which
 *		indicates slicing support.
 * @is_draining: indicates device is in draining phase
 * @last_src_buf: indicate the last source buffer for draining
 * @next_buf_last: next capture queud buffer will be tagged as last
 * @has_stopped: indicate the device has been stopped
 * @ignore_cap_streaming: If true, job_ready can be called even if the CAPTURE
 *			  queue is not streaming. This allows firmware to
 *			  analyze the bitstream header which arrives on the
 *			  OUTPUT queue. The driver must implement the job_ready
 *			  callback correctly to make sure that the requirements
 *			  for actual decoding are met.
 * @m2m_dev: opaque pointer to the internal data to handle M2M context
 * @cap_q_ctx: Capture (output to memory) queue context
 * @out_q_ctx: Output (input from memory) queue context
 * @queue: List of memory to memory contexts
 * @job_flags: Job queue flags, used internally by v4l2-mem2mem.c:
 *		%TRANS_QUEUED, %TRANS_RUNNING and %TRANS_ABORT.
 * @finished: Wait queue used to signalize when a job queue finished.
 * @priv: Instance private data
 *
 * The memory to memory context is specific to a file handle, NOT to e.g.
 * a device.
 */
struct v4l2_m2m_ctx {
	/* optional cap/out vb2 queues lock */
	struct mutex			*q_lock;

	bool				new_frame;

	bool				is_draining;
	struct vb2_v4l2_buffer		*last_src_buf;
	bool				next_buf_last;
	bool				has_stopped;
	bool				ignore_cap_streaming;

	/* internal use only */
	struct v4l2_m2m_dev		*m2m_dev;

	struct v4l2_m2m_queue_ctx	cap_q_ctx;

	struct v4l2_m2m_queue_ctx	out_q_ctx;

	/* For device job queue */
	struct list_head		queue;
	unsigned long			job_flags;
	wait_queue_head_t		finished;

	void				*priv;
};
```

其公有成员：
- `struct mutex *q_lock` ：
	- 功能含义：保护实例的互斥锁
	- 维护方：驱动可选维护，当驱动不提供时V4L2会负责维护
- `bool new_frame` ：
	- 功能含义：在 `device_run` 回调中，用于表示当前处理的缓冲区是否是一个新帧的开始或是已有帧的一个切片。
		- 只有当设备支持切片功能时，该成员才有可能为 `false` ，否则永远为 `true` 
	- 维护方：V4L2负责维护，驱动读取
- `bool is_draining` ：
	- 功能含义：表示当前设备是否在排空状态(`draining`)，并决定后续处理逻辑。
	- 维护方：V4L2负责维护，驱动读取
- `struct vb2_v4l2_buffer *last_src_buf` ：
	- 功能含义：指向输出队列中的最后一个源缓冲区，主要用于排空事件处理，以及是否到达最后的一个帧。
	- 维护方：V4L2框架在开始排空时设置，驱动可用于读取或检查
- `bool next_buf_last` ：
	- 功能含义：标记下一个缓冲区应当标记为LAST
	- 维护方：V4L2框架设置
- `bool has_stopped` ：
	- 功能含义：设备是否已被停止
	- 维护方：V4L2框架负责维护
- `bool ignore_cap_streaming` ：
	- 功能含义：是否忽略捕获队列的streaming状态检查
	- 维护方：驱动可选设置，框架在 `v4l2_m2m_job_ready` 中检查
- `void *priv` ：
	- 功能含义：驱动私有数据指针
	- 维护方：驱动管理与访问
其私有成员：
- `struct v4l2_m2m_dev *m2m_dev` ：
	- 功能含义：指向所述的M2M设备
	- 驱动访问：只读访问
- `struct v4l2_m2m_queue_ctx cap_q_ctx` ：
	- 功能含义：捕获队列上下文
	- 驱动访问：驱动通过VB2接口进行访问其成员 `struct vb2_queue q` 
- `struct v4l2_m2m_queue_ctx out_q_ctx` ：
	- 功能含义：输出队列上下文
	- 驱动访问：驱动通过VB2接口进行访问其成员 `struct vb2_queue q` 
- `struct list_head queue` ：
	- 功能含义：作业队列的链表头
	- 驱动访问：
- `unsigned long job_flags` ：
	- 功能含义：当前作业的状态标志
		- 当用户态将一对缓冲区分别放到输入和输出队列时就构成了一个任务。
		- 该标志包含：
			- `TRANS_QUEUED` ：作业已排队
			- `TRANS_RUNNING` ：作业执行中
			- `TRANS_ABORT` ：作业被终止
- `wait_queue_head_t finished` ：
	- 功能含义：作业完成等待队列，通常挂有用户的 `poll` 等系统调用的等待线程。
	- 驱动访问：驱动调用 `v4l2_m2m_job_finish()` 后会间接执行唤醒。
注：
- 该对象可不用由驱动手动初始化，直接使用子章节对应的API进行初始化即可

##### 3.5.1.3.1 初始化m2m的打开上下文实例

```C
/**
 * v4l2_m2m_ctx_init() - allocate and initialize a m2m context
 *
 * @m2m_dev: opaque pointer to the internal data to handle M2M context
 * @drv_priv: driver's instance private data
 * @queue_init: a callback for queue type-specific initialization function
 *	to be used for initializing vb2_queues
 *
 * Usually called from driver's ``open()`` function.
 */
struct v4l2_m2m_ctx *v4l2_m2m_ctx_init(struct v4l2_m2m_dev *m2m_dev,
		void *drv_priv,
		int (*queue_init)(void *priv, struct vb2_queue *src_vq, struct vb2_queue *dst_vq));
```

该函数：
- 功能含义：初始化一个[[video_device#^3axphz|m2m用户上下文实例]]
	- 当用户打开了m2m对应的video设备句柄时(即 `open` 回调中)，除了需要创建一个[[video_device#^kyd4a1|通用文件管理句柄]]以外，还需要专门初始化该句柄的m2m用户上下文实例成员(`v4l2_fh.m2m_ctx`)，而本函数则通常用于负责此部分工作。
- 参数：
	- `struct v4l2_m2m_dev *m2m_dev` ：
		- 功能含义：指向m2m对象实例，其通常通过 `open(struct file *file)` 中的 `file` 指针获取，具体如下：
			- 在 `probe` 函数中：
				1. 将 `m2m_dev` 绑定到驱动的设备对象结构体中
				2. 通过 `video_set_drvdata` 为 `video_device` 绑定设备对象指针
			- 在 `open` 函数中：
				1. 通过 `video_devdata(file)` 获取 `video_device` 指针
				2. 通过 `video_get_drvdata` 获取设备对象指针
				3. 通过设备对象指针获取m2m对象实例
	- `void *drv_priv` ：
		- 功能含义： 驱动的实例私有数据指针
			- <span style="background:#fff88f"><font color="#c00000">其值为</font></span> `v4l2_m2m_ops` <span style="background:#fff88f"><font color="#c00000">的三个回调函数的参数</font></span>，<font color="#c00000">通常填入设备自定义的大的上下文实例指针</font>。
	- `int (*queue_init)(void *priv, struct vb2_queue *src_vq, struct vb2_queue *dst_vq)` ：
		- 功能含义：该成员为[[video_device#^1knefg|队列初始化回调]]，负责对M2M的两个 `vb2_queue` 进行特定初始化，具体可见子章节。

###### 3.5.1.3.1.1 队列初始化回调 ^1knefg

正如上文所述，`queue_init` 回调会在 `v4l2_m2m_ctx_init` 执行期间被调用，其主要任务包含：
1. 配置输入输出队列的输入输出方向
2. 配置缓冲区内存类型(`VB2_MMAP` 、 `VB2_USERPTR` 等)
3. 配置 `vb2_ops` 回调，可见[[VB2概述#^tqizjf|vb2相关回调函数]] 
4. 调用 `vb2_queue_init` 初始化配置好的两个缓冲队列
等，每个队列的初始化与普通摄像头的缓冲区队列初始化类似。

该回调函数的原型应符合如下定义：

```C
int (*queue_init)(void *priv, struct vb2_queue *src_vq, struct vb2_queue *dst_vq);
```

其中：
- 参数：
	- `void* priv` ：为 `v4l2_m2m_ctx_init` 时的 `drv_priv` 参数，指向驱动的私有数据
	- `struct vb2_queue *src_vq` ：为源队列指针(用户->内核)，通常为 `OUTPUT` 类型
	- `struct vb2_queue *dst_vq` ：为目标队列指针(用户<-内核)，通常为 `CAPTURE` 类型

#### 3.5.1.4 M2M设备操作回调(v4l2_m2m_ops) ^r39fw1

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
	- 功能含义：驱动处理实际具体M2M任务的<font color="#c00000">入口</font>，<font color="#c00000">作业不需要在此回调返回前结束</font>(也就是说通常不把实际的任务放到这里)。
	- 参数：
		- `void *priv` ：为 `v4l2_m2m_ctx_init` 时传入的 `drv_priv` 参数
	- 被执行时机(条件)，<font color="#c00000">需要同时满足</font>：
		1. 已调用 `VIDIOC_STREAMON` 启动 `OUTPUT` 和 `CAPTURE` 队列
		2. 两个队列中都有可用缓冲区(除非 `job_ready` 自定义条件)
		3. 设备当前空闲(无运行中任务)
		4. (如果实现) `job_ready` 返回 `true`
	- 维护方：<span style="background:#fff88f"><font color="#c00000">必须实现</font></span>
	- <span style="background:#fff88f"><font color="#c00000">关键规则</font></span>：
		- <span style="background:#fff88f"><font color="#c00000">该函数禁止阻塞、休眠</font></span>
		- <font color="#c00000">任务完成后必须通过中断通知</font>(<span style="background:#fff88f"><font color="#c00000">异步</font></span>，这也是为什么说该函数是入口的原因)，需要调用 `v4l2_m2m_job_finish` 或 ` v4l2_m2m_buf_done_and_job_finish ` 来通知V4L2框架对应任务已经执行完毕。
		- 若任务失败，则调用 `v4l2_m2m_buf_done_and_job_finish(..., VB2_BUF_STATE_ERROR)` 来通知V4L2任务失败。
- `int (*job_ready)(void *priv)` 
	- 功能含义：询驱动(设备)当前能否<font color="#c00000">立即</font>开启新任务(每个buffer都被视作新任务)
	- 维护方：可选
	- <span style="background:#fff88f"><font color="#c00000">关键规则</font></span>：
		- <span style="background:#fff88f"><font color="#c00000">该函数禁止阻塞、休眠</font></span>
		- 该函数应当快速返回
		- 返回<font color="#c00000">非</font>0表示设备已经准备好，返回0表示设备尚未ready
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
		- <font color="#c00000">运行完成后必须调用</font> `v4l2_m2m_job_finish()` <font color="#c00000">或</font> `v4l2_m2m_buf_done_and_job_finish()` 
		- 该操作需要注意和保证硬件安全
		- 在该函数调用时，`device_run` 可能还在运行，需要注意并发问题。

#### 3.5.1.5 相关API

##### 3.5.1.5.1 初始化M2M对象

```C
/**
 * v4l2_m2m_init() - initialize per-driver m2m data
 *
 * @m2m_ops: pointer to struct v4l2_m2m_ops
 *
 * Usually called from driver's ``probe()`` function.
 *
 * Return: returns an opaque pointer to the internal data to handle M2M context
 */
struct v4l2_m2m_dev *v4l2_m2m_init(const struct v4l2_m2m_ops *m2m_ops);
```

该函数：
- 参数为驱动实现的M2M回调
- 返回值为指针，但是并不能简单的使用 `==NULL` 判定是否成功，其需要使用 `IS_ERR` 宏进行判定

##### 3.5.1.5.2 通知m2m作业完成

```C
/**
 * v4l2_m2m_job_finish() - inform the framework that a job has been finished
 * and have it clean up
 *
 * @m2m_dev: opaque pointer to the internal data to handle M2M context
 * @m2m_ctx: m2m context assigned to the instance given by struct &v4l2_m2m_ctx
 *
 * Called by a driver to yield back the device after it has finished with it.
 * Should be called as soon as possible after reaching a state which allows
 * other instances to take control of the device.
 *
 * This function has to be called only after &v4l2_m2m_ops->device_run
 * callback has been called on the driver. To prevent recursion, it should
 * not be called directly from the &v4l2_m2m_ops->device_run callback though.
 */
void v4l2_m2m_job_finish(struct v4l2_m2m_dev *m2m_dev,
			 struct v4l2_m2m_ctx *m2m_ctx);
```

该函数：
- 语义为：
	- 通知M2M框架当前硬件作业已完成，框架可以执行清理并调度下一个作业
	- 其必须在 `device_run` 调用完成后被调用(<font color="#c00000">也不可在</font> `device_run` <font color="#c00000">中直接调用</font>)
	- 随后框架会执行后续清理任务，并调度下一个作业，具体包含：
		1. 从运行队列移除当前作业
		2. 清除该任务的标志(清除"在队列中"和"在运行中"的标志)
		3. 唤醒等待该任务完成的线程
		4. 将当前在运行的任务设置为空
		5. 当下一作业存在时，调度下一作业
- 注：
	- 该函数不应当用于支持[[video_device#^10xf45|多输入单输出机制]]的驱动程序，即需要保持捕获缓冲区机制的设备。此类设备应当使用 `v4l2_m2m_buf_done_and_job_finish()` 接口
	- <font color="#c00000">该接口不负责标记缓冲区状态</font>，<font color="#c00000">驱动需要在该接口调用前完成缓冲区标记</font>，<font color="#c00000">并准备释放缓冲区控制权</font>(即调用该接口后，驱动不应当再操作该缓冲区)
	- 驱动调用该接口后，驱动不再拥有设备控制权(设备控制权按照上下文进行管理，同一时间只能有一个上下文拥有设备控制权)

##### 3.5.1.5.3 完成对缓冲区的处理并通知m2m作业完成

```C
/**
 * v4l2_m2m_buf_done_and_job_finish() - return source/destination buffers with
 * state and inform the framework that a job has been finished and have it
 * clean up
 *
 * @m2m_dev: opaque pointer to the internal data to handle M2M context
 * @m2m_ctx: m2m context assigned to the instance given by struct &v4l2_m2m_ctx
 * @state: vb2 buffer state passed to v4l2_m2m_buf_done().
 *
 * Drivers that set V4L2_BUF_CAP_SUPPORTS_M2M_HOLD_CAPTURE_BUF must use this
 * function instead of job_finish() to take held buffers into account. It is
 * optional for other drivers.
 *
 * This function removes the source buffer from the ready list and returns
 * it with the given state. The same is done for the destination buffer, unless
 * it is marked 'held'. In that case the buffer is kept on the ready list.
 *
 * After that the job is finished (see job_finish()).
 *
 * This allows for multiple output buffers to be used to fill in a single
 * capture buffer. This is typically used by stateless decoders where
 * multiple e.g. H.264 slices contribute to a single decoded frame.
 */
void v4l2_m2m_buf_done_and_job_finish(struct v4l2_m2m_dev *m2m_dev,
				      struct v4l2_m2m_ctx *m2m_ctx,
				      enum vb2_buffer_state state);
```

其主要用于需要[[video_device#^10xf45|多输入单输出机制]]的设备中，即需要保持捕获缓冲区机制的设备。

##### 3.5.1.5.4 添加用户入队的缓冲区到m2m的对应队列中

```C
/**
 * v4l2_m2m_buf_queue() - add a buffer to the proper ready buffers list.
 *
 * @m2m_ctx: m2m context assigned to the instance given by struct &v4l2_m2m_ctx
 * @vbuf: pointer to struct &vb2_v4l2_buffer
 *
 * Call from vb2_queue_ops->ops->buf_queue, vb2_queue_ops callback.
 */
void v4l2_m2m_buf_queue(struct v4l2_m2m_ctx *m2m_ctx,
			struct vb2_v4l2_buffer *vbuf);
```

该函数：
- 功能含义：该函数会将传递来的 `vbuf` 添加到对应的就绪队列中
	- 该函数应当在 `vb2_queue_ops->ops->buf_queue` 中被调用
- 参数：
	- `struct v4l2_m2m_ctx *m2m_ctx` ：要添加到的m2m的上下文
	- `struct vb2_v4l2_buffer *vbuf` ：









