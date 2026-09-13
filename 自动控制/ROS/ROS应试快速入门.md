---
number headings: auto, first-level 1, max 6, 1.1
---
#ROS 

# 1 目录

```toc
```

# 2 ROS的基本对象

## 2.1 Node

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

## 2.2 通信模型(Topic、Service、Action)

ROS中主要有如下三种通信模型：
- `Topic` ：分为发布者和订阅者，通常用于传输连续数据
- `Service` ：通常用于一次性的请求，类似于RPC
- `Action` ：用于可反馈的长时间的任务，例如机械臂操作等

## 2.3 坐标系转换(TF/TF2)

其主要用于定义和动态维护一个坐标变换树。

## 2.4 

