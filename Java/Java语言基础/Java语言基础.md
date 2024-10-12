---
number headings: auto, first-level 2, max 6, 1.1
---
#Java 

## 1 目录

```toc
```

## 2 基本定义

### 2.1 Java SE、EE、ME的区别和联系

<span style="background:#fff88f"><font color="#c00000">Java SE是Java平台的基础，是Java平台的标准版本</font></span>。<font color="#c00000">Java EE、ME都依赖于Java SE</font>；<font color="#c00000">Java EE、ME都是基于Java SE的拓展</font>。

#### 2.1.1 Java SE

Java SE的全称是Java Standard Edition，




#### 2.1.2 Java EE

Java EE的全称是Java Enterprise Edition，定位是Java的企业版，应用于企业级分布式应用程序。其主要包含的拓展有：
- Servlet和JSP：用于开发动态网页和处理 HTTP 请求。
- EJB(Enterprise JavaBeans)：用于处理企业级业务逻辑。
- JPA(Java Persistence API)：用于数据持久化，简化与数据库的交互。
- JMS(Java Message Service)：提供消息中间件，支持消息队列。
- JAX-RS和JAX-WS：用于开发Web服务。


### 2.2 JDK、JRE、JVM的区别和联系







## 3 基础的语言特性

### 3.1 注解(Annotation)

注解可以理解为是有特殊功能的注释。注释是给人看的，注解是同时给人和程序员看的。
注解在JDK5.0引入


### 3.2 反射





## 4 面相对象的若干特性及其实现

本章节的学习需要的前置基础有：
- [[面相对象的程序设计]]

### 4.1 类

### 4.2 接口

接口在定义时直接使用 `interface` 关键字进行定义。在接口中定义的方法默认是抽象的，因此不需要使用 `abstract` 关键字。此外，接口中还包含默认方法(default methods)和静态方法(static methods)。

