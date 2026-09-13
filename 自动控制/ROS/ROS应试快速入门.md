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



## 2.2 通信模型(Topic、Service、Action)

ROS中主要有如下三种通信模型：
- `Topic` ：分为发布者和订阅者，通常用于传输连续数据
- `Service` ：通常用于一次性的请求
- `Action` ：yo


## 2.3 Message


## 2.4 

