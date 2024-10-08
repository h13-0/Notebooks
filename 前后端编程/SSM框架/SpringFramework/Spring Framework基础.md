---
number headings: auto, first-level 2, max 6, 1.1
---
#后端 #Java #SSM框架

## 1 目录

```toc
```

## 2 Spring Framework框架简介

![[SSM框架概述#4 1 Spring Framework框架简介]]

## 3 IoC控制反转与DI依赖注入

正如上一章节所述，Spring Framework提供了如下的功能：
- 自动创建、保存组件对象(即组件对象实例化)
- 自动进行组件对象的生命周期管理
- 自动进行组件的组装(DI依赖注入)
- 自动进行事务管理(TX)
- 与Spring全家桶的其他框架进行整合交互
而Spring要求的组件称为 `Spring Bean` ，其是在[[Java Bean]]要求的基础上进行规定的。

在Spring文档中， `Spring Bean` 被如下定义：

	In Spring, the objects that form the backbone of your application and that are managed by the Spring IoC container are called beans. A bean is an object that is instantiated, assembled, and otherwise managed by a Spring IoC container.

即：<font color="#c00000">构成应用程序主干并由Spring IoC容器管理的对象称为bean</font>。

|     | <center>[[Java Bean]]</center> | <center>Spring Bean</center>                                                                                                                                        |
| --- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 要求  | 任何符合要求的类都可以称之为Java Bean。       | <font color="#c00000">Spring Bean是在Spring IoC容器中被实例化、管理和维护的对象</font>。<br><font color="#c00000">一个Bean可以是任何普通的Java对象</font>，例如 POJO、Service、Respository、Controller等。 |

### 3.1 IoC控制反转与组件

通常来说Spring项目由如下三层组成：

![[Pasted image 20241008172108.png]]

通常来说：
- 控制层通常被命名为 `XxController` 。
- 业务逻辑层通常被命名为 `XxService` 。
- 持久化层通常被命名为 `XxMapper` 或者 `XxDao` 。

每一层都由组件构成，并且这些组件必须被放入Spring容器中才能使用一些由Spring提供的特性。而各层之间存在的有依赖关系，例如控制层在接收到请求后，会逐层调用业务逻辑层、持久化层后才能响应该请求。

而Spring可以管理并负责这些组件之间的依赖并完成装配。但是依赖信息需要由程序员按照如下三种方式之一来配置：
1. `xml` 配置方式
2. 注解配置方式
3. java类配置方式

### 3.2 Spring IoC容器接口及其实现类

在Spring中， `org.springframework.beans.factory` 包中定义了Spring IoC容器接口 `BeanFactory` 。在这个接口的定义下，Spring还提供了：

| 类型名                                  | 简介                                                        |
| ------------------------------------ | --------------------------------------------------------- |
| `ClassPathXmlApplicationContext`     | 通过读取类路径下(src下)的xml格式的配置文件创建IoC容器对象                        |
| `FileSystemXmlApplicationContext`    | 通过文件系统路径(其他路径)读取xml格式的配置文件创建IoC容器对象                       |
| `AnnotationConfigApplicationContext` | 通过读取Java配置类创建IoC容器对象                                      |
| `WebApplicationContext`              | 专门为Web应用准备，基于Web环境创建IoC容器对象，<br>并将对象引入存入ServletContext域中。 |

等常用接口。





