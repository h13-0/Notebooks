---
number headings: auto, first-level 2, max 6, 1.1
---
#后端 #Java 

## 1 目录

```toc
```

## 2 前置基础

学习本章节除了需要完成[[前后端编程/Readme|Readme]]中要求的前置基础外，还需要完成[[Tomcat 基础笔记]]的学习。

## 3 基本概念

### 3.1 静态资源与动态资源

在Web后端中，资源可以分为静态资源和动态资源两种。
静态资源是指在服务端响应请求时不需要使用代码去动态生成的资源，例如 `.html` 文件和 `.css` 文件等。
动态资源是指在服务端响应请求时需要使用代码去动态生成的资源。

### 3.2 Servlet

Servlet(Server applet)是一个技术标准，由Sun公司定义的一套动态资源规范，用于在处理客户端请求时协同调度和响应数据。是Web应用中的控制器。
从代码上来讲，Servlet是一套接口，其<font color="#c00000">必须运行于特定的容器中</font>(通常是Tomcat)，<font color="#c00000">不能独立运行</font>。

## 4 Servlet基本流程

Servlet容器(通常为Tomcat)在接收到http请求后，其会使用如下的流程将请求转化为Servlet所规定的对象，交由实现了Servlet Service的APP完成请求内容的生成。
其工作内容主要如下：
1. 容器在接收到http请求后，容器会将http请求转换为 `HttpServletRequest` 对象，该对象中包含了http请求中的所有信息(例如http请求头和请求体)。
2. 容器在创建 `HttpServletRequest` 对象的<span style="background:#fff88f"><font color="#c00000">同时会创建</font></span>一个 `HttpServletResponse` 对象，用于承装需要响应给客户端的信息，该对象会被转换为http的响应报文。该对象包含http响应行、响应头和响应体。
3. 随后容器会根据请求的路径找到响应该请求的Servlet，并将Servlet实例化，调用Servlet实现的service方法，同时将 `HttpServletRequest` 和 `HttpServletResponse` 对象引用传递给service方法。

![[1681699577344.png]]

## 5 Servlet Demo

### 5.1 在Java中实现Servlet的服务内容

如上一章节所述，Servlet是一套接口，因此需要定义一个class来实现这套接口。该接口要求实现 `service` 方法，原型为：
```java
protected void service(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException;
```

`service` 方法主要需要实现的工作内容为：
0. 创建一个类，实现 `Servlet` 接口或者继承 `HttpServlet` 或完成其他实现接口的方式。
1. 从 `request` 中获取http请求的所有参数及信息。
2. 根据参数生成对应的响应数据。
3. 将响应数据放入 `response` 对象中。
随后可得到简单的Servlet类，其代码如下：

```Java
package indi.h13.servlet;  
  
import jakarta.servlet.ServletException;  
import jakarta.servlet.http.HttpServlet;  
import jakarta.servlet.http.HttpServletRequest;  
import jakarta.servlet.http.HttpServletResponse;  
  
import java.io.IOException;  
  
public class UserServlet extends HttpServlet {  
    @Override  
    protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {  
        String username = req.getParameter("username");  
        if("root".equals(username)) {  
            resp.getWriter().println("username is root");  
        } else {  
            resp.getWriter().println("username is not root");  
        }  
    }  
}
```

### 5.2 映射和配置Servlet的请求路径

在完成了Servlet接口的实现后，需要让Tomcat将对应请求转发到对应的Servlet实例中。
建立映射有如下两种方式，通常采用第二种注解的方式。

#### 5.2.1 修改配置文件

随后需要在 `WEB-INF/web.xml` 中映射Servlet的请求路径，其需要在 `web-app` 块下添加如下代码：

```xml






```









