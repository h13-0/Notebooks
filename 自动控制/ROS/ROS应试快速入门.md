---
number headings: auto, first-level 1, max 6, 1.1
---
#ROS 

# 1 目录

```toc
```

# 2 ROS版本区别

|  区别项   | <center>ROS1</center> | <center>ROS2</center> |
| :----: | --------------------- | --------------------- |
| 通信发现机制 | 依赖ROS Master          | 去中心化发现                |
|  底层通信  | TCPROS/UDPROS         | DDS                   |
|  实时性   | 相对较弱                  | 更强调实时性                |
|  多机通信  | 支持但较弱                 | 较强                    |
| 多线程执行  | 相对简单                  | 机制更完善                 |
|  平台支持  | 主要是Linux              | Linux/Windows/macOS等  |

# 3 ROS的基本对象

## 3.1 Node

在ROS中，功能模块通常被视作一个Node，例如IMU、Camera、lidar等。
在软件设计层面，其基本为一个C++对象+ROS通信接口，例如：

```CPP
class ImuNode : public rclcpp::Node {
public:
    ImuNode() : Node("imu_node") {
    }
};
```

随后可以单独运行：

```Shell
ros2 run my_package imu_node
```

但是一个机器人会有多个Node，不可能手动拉起，因此通常使用Python一次性拉起所有Node，在拉起的过程中也可以配置各个Node。

## 3.2 通信模型(Topic、Service、Action)

ROS中主要有如下三种通信模型：
- `Topic` ：分为发布者和订阅者，通常用于传输连续数据
- `Service` ：通常用于一次性的请求，类似于RPC
- `Action` ：用于可反馈的长时间的任务，例如机械臂操作等

## 3.3 调度器(Executor)

ROS中Executor主要负责调用Node，当Node订阅的事件、定时器等条件满足时，就执行对应回调。

## 3.4 坐标系转换(TF/TF2)

其主要用于定义和动态维护一个坐标变换树。

## 3.5 

