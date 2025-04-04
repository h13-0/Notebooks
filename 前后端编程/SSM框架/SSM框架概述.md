---
number headings: auto, first-level 2, max 6, 1.1
---
#后端 #Java #SSM框架

## 1 目录

```toc
```

## 2 前置基础

本笔记需要如下的前置基础：
- [[前后端编程/JavaWeb/Readme|JavaWeb系列]]

## 3 所用学习资料

本章节所参考的学习资料有：
1. 尚硅谷的SSM系列课程。

## 4 SSM框架概述

SSM框架指的是由Spring、Spring MVC、MyBatis三个组件构成的框架。

上述的Spring指的是Spring Framework。而Spring通常有狭义和广义的含义：
- 狭义的Spring：Spring Framework。
	- 其所提供的功能有：
		- IoC控制反转与DI依赖注入(Inversion of Control、Dependency injection)
		- AOP面相切面编程(Aspect-Oriented Programming)
		- TX事务管理(Transaction Management)
		- MVC框架(Model、View、Controller)
- 广义的Spring：Spring技术栈，即Spring全家桶。
	- Spring全家桶包含：
		- Spring Boot
		- Spring Data
		- Spring Cloud
		- Spring Security
		- ...

### 4.1 Spring Framework框架简介

Spring Framework共计含有20多个子模块，其框架图如下图所示：

![[Pasted image 20241008164128.png]]

其主要功能有：
- Core Container：核心容器，在 Spring 环境下使用任何功能都必须基于 IOC 容器。
- AOP、Aspects：提供了面向切面编程。
- TX：声明式事务管理
- Spring MVC：提供了面向Web应用程序的集成功能。

