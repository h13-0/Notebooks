---
number headings: auto, first-level 2, max 6, 1.1
---
#后端 #Java 

## 1 目录

```toc
```

## 2 基本概念

### 2.1 静态资源与动态资源

在Web后端中，资源可以分为静态资源和动态资源两种。
静态资源是指在服务端响应请求时不需要使用代码去动态生成的资源，例如 `.html` 文件和 `.css` 文件等。
动态资源是指在服务端响应请求时需要使用代码去动态生成的资源。

### 2.2 Servlet

Servlet(Server applet)是一个技术标准，由Sun公司定义的一套动态资源规范，用于在处理客户端请求时协同调度和响应数据。是Web应用中的控制器。
从代码上来讲，Servlet是一套接口，其<font color="#c00000">必须运行于特定的容器中</font>(通常是Tomcat)，<font color="#c00000">不能独立运行</font>。

## 3 Servlet基本流程

Servlet容器(通常为Tomcat)在接收到http请求后，其会使用如下的流程将请求转化为Servlet所规定的对象，交由实现了Servlet Service的APP完成请求内容的生成。
其工作内容主要如下：
1. 容器在接收到http请求后，容器会将http请求转换为 `HttpServletRequest` 对象，该对象中包含了http请求中的

![[1681699577344.png]]

