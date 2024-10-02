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

#### 5.2.1 修改配置文件方式

随后需要在 `WEB-INF/web.xml` 中映射Servlet的请求路径，其需要在 `web-app` 块下添加如下代码：

```xml
<!--  
1. 配置Servlet类，其配置项及其含义为：  
        servlet-name: 用于关联请求的映射路径  
        servlet-class: 完成该请求所需要实例化的Servlet类  
-->  
<servlet>  
    <servlet-name>userServlet</servlet-name>  
    <servlet-class>indi.h13.servlet.UserServlet</servlet-class>  
</servlet>  
  
<!--  
2. 配置和完成请求路径和servlet-name之间的映射。  
-->  
<servlet-mapping>  
    <servlet-name>userServlet</servlet-name>  
    <url-pattern>/isRoot</url-pattern>  
</servlet-mapping>
```

更多特性详见[[Servlet 简介#7 1 url-pattern的相关写法]]。

#### 5.2.2 注解方式

使用注解方式进行映射配置要求：
- Tomcat版本大于等于7.0
- Servlet版本大于等于3.0
随后只需要在接口类前使用如下的注解即可完成映射：

```Java
@WebServlet("/isRoot")
```

即：

```Java
@WebServlet("/isRoot")
public class UserServlet extends HttpServlet {  
    @Override  
    protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {  
	    // ...
    }  
}
```

注意点：
1. 记得写斜线 `/` ，不然启动会报错
2. 上述注解的默认参数名为 `value` 或 `urlPatterns` (这两个参数名互为别名，等价)，即 `@WebServlet(value="/isRoot")` 与上述等价。
3. <font color="#c00000">上述参数名的类型为数组类型</font>，<span style="background:#fff88f"><font color="#c00000">因此支持直接定义多个映射路径</font></span>：`@WebServlet(value={ "/isRoot", "isRootV1", "isRootV2" })` (大部分情况并无此需求)

### 5.3 测试与HTTP请求

在启动Tomcat App之后，使用Postman发送如下请求，即可验证上述实现成功运行。

![[Postman_KuLBO6HN6d.png]]

### 5.4 \[附加\]Servlet及其jar库

Servlet APP的开发依赖于jar库，具体的库为 `servlet-api.jar` ，存放于Tomcat的 `lib\` 下。
在使用IDEA开发时，引入Tomcat Server时就已经引入对应的jar包。而手动引入jar包的方式和普通开发一致。

![[idea64_bQp8ojUQcR.png]]

而在项目依赖中可以可看到Tomcat的作用域为 `provided` ，<u><span style="background:#fff88f"><font color="#c00000">其含义为编译时不携带该依赖</font></span></u>(部署环境已提供)。

![[idea64_SuSeW5L51D.png]]

## 6 Servlet常用API

### 6.1 设置HTTP Header

HTTP Header中常见的属性有：
- 通过 `Content-Length` 获取资源大小
- 通过 `Content-Type` 获取资源类型，<span style="background:#fff88f"><font color="#c00000">应当为MIME格式</font></span>
- 通过 `Last-Modified` 获取资源最后修改时间

而在Servlet中可以使用如下的方法设置HTTP Header：

```Java
responce.setHeader("key", "value");
```

例如：

```Java
responce.setHeader("Content-Type", "image/jpeg");
```

<span style="background:#fff88f"><font color="#c00000">而在基于Tomcat的SpringBoot中也是这样配置的</font></span>。


## 7 web.xml的详细讲解

### 7.1 url-pattern的相关特性

#### 7.1.1 url-pattern的多对一精确匹配

在前述章节中介绍了如下的url-pattern配置方法：
![[Servlet 简介#5 2 1 修改配置文件方式]]

而在上述代码中，Tomcat完成了如下工作：
1. 通过指定的 `url-pattern` 找到了响应该url的 `servlet-name`
2. 使用 `servlet-name` 找到了响应该请求需要实例化的类( `servlet-class` )

而需要拓展的用法有：
1. 一个 `servlet-mapping` 中可以绑定多个 `url-pattern` ，从而响应多个url请求，例如：
```xml
<!--  
1. 配置Servlet类，其配置项及其含义为：  
        servlet-name: 用于关联请求的映射路径  
        servlet-class: 完成该请求所需要实例化的Servlet类  
-->  
<servlet>  
    <servlet-name>userServlet</servlet-name>  
    <servlet-class>indi.h13.servlet.UserServlet</servlet-class>  
</servlet>  
  
<!--  
2. 配置和完成请求路径和servlet-name之间的映射。  
-->  
<servlet-mapping>  
    <servlet-name>userServlet</servlet-name>  
    <url-pattern>/isRoot</url-pattern>  
    <url-pattern>/checkUserName</url-pattern>  
</servlet-mapping>
```
2. 一个 `servlet` 标签可以对应多个 `servlet-mapping` ，从而响应多个url请求，例如：
```xml
<!--  
1. 配置Servlet类，其配置项及其含义为：  
        servlet-name: 用于关联请求的映射路径  
        servlet-class: 完成该请求所需要实例化的Servlet类  
-->  
<servlet>  
    <servlet-name>userServlet</servlet-name>  
    <servlet-class>indi.h13.servlet.UserServlet</servlet-class>  
</servlet>  
  
<!--  
2. 配置和完成请求路径和servlet-name之间的映射。  
-->  
<servlet-mapping>  
    <servlet-name>userServlet</servlet-name>  
    <url-pattern>/isRoot</url-pattern>  
</servlet-mapping>
<servlet-mapping>  
    <servlet-name>userServlet</servlet-name>  
    <url-pattern>/checkUserName</url-pattern>  
</servlet-mapping>
```
<font color="#c00000">不过一般还是用第一种方法</font>。

<span style="background:#fff88f"><font color="#c00000">综上，基本规则如下</font></span>：
1. 一个 `servlet-name` 可以对应多个 `url-pattern` ，反之不可。
2. 一个 `servlet` 标签可以对应多个 `servlet-mapping` ，反之不可。

#### 7.1.2 url-pattern的多对一模糊匹配

模糊匹配主要有如下两种规则：
1. `/` ：匹配全部，但是不包含jsp文件
2. `/*` ：匹配全部，包含jsp文件

例如：

```xml
<servlet>  
    <servlet-name>userServlet</servlet-name>  
    <servlet-class>indi.h13.servlet.UserServlet</servlet-class>  
</servlet>  

<servlet-mapping>  
    <servlet-name>userServlet</servlet-name>  
    <url-pattern>/isRoot/</url-pattern>  
</servlet-mapping>
```

则会匹配 `/isRoot/` 下除了 `*.jsp` 的所有路径，即：
- `localhost/isRoot/aaa` -> 可被匹配
- `localhost/isRoot/aaa.jsp` -> <font color="#c00000">不可匹配</font>

而：

```xml
<servlet>  
    <servlet-name>userServlet</servlet-name>  
    <servlet-class>indi.h13.servlet.UserServlet</servlet-class>  
</servlet>  

<servlet-mapping>  
    <servlet-name>userServlet</servlet-name>  
    <url-pattern>/isRoot/*</url-pattern>  
</servlet-mapping>
```

则会同时匹配 `localhost/isRoot/aaa` 和 `localhost/isRoot/aaa.jsp` 。
<span style="background:#fff88f"><font color="#c00000">同样的，模糊匹配也可以用于模糊匹配固定的后缀路径</font></span>：

```xml
<servlet>  
    <servlet-name>userServlet</servlet-name>  
    <servlet-class>indi.h13.servlet.UserServlet</servlet-class>  
</servlet>  

<servlet-mapping>  
    <servlet-name>userServlet</servlet-name>  
    <url-pattern>*.txt</url-pattern>  
</servlet-mapping>
```

则会把所有后缀为 `.txt` 的请求均映射到对应接口。<span style="background:#fff88f"><font color="#c00000">但是需要注意</font></span> `*.txt` <span style="background:#fff88f"><font color="#c00000">前面不可加</font></span> `/` ，因为 `/*` 会导致歧义。

### 7.2 配置Servlet的生命周期

本子章节应当阅读完[[Servlet 简介#8 2 1 Servlet默认情况下的生命周期]]后再进行学习。
![[Servlet 简介#8 2 2 1 在web xml中配置]]

## 8 Servlet的生命周期

### 8.1 Servlet生命周期相关方法的定义或重写

Servlet的生命大致有如下若干阶段：
1. 实例化阶段，由构造器调用，可定义于构造方法。
2. 初始化阶段，定义于 `Servlet.init` 方法。
3. 接受请求并服务阶段，定义于 `Servlet.service` 方法。
4. 销毁阶段，定义于 `Servlet.destory` 方法。
上述各方法的定义方式如下：

```Java
@WebServlet("/ServletLifeCycleTest")  
public class ServletLifeCycle extends HttpServlet {  
    /**  
     * @brief 重写实例化方法  
     */  
    public ServletLifeCycle() {  
        System.out.println("ServletLifeCycle obj created.");  
    }  
  
    /**  
     * @brief 重写初始化方法  
     * @throws ServletException  
     * @note 注意需要重写的是无参数的 `init` 方法  
     */  
    @Override  
    public void init() throws ServletException {  
        super.init();  
        System.out.println("ServletLifeCycle obj inited.");  
    }  
  
    /**  
     * @brief 重写service方法  
     * @param req  
     * @param resp  
     * @throws ServletException  
     * @throws IOException  
     */    @Override  
    protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {  
        System.out.println("ServletLifeCycle.service() has been executed.");  
    }  
  
    /**  
     * @brief 重写销毁方法  
     */  
    @Override  
    public void destroy() {  
        super.destroy();  
        System.out.println("ServletLifeCycle obj has been destroyed.");  
    }  
}
```

### 8.2 Servlet的生命周期及其控制

#### 8.2.1 Servlet默认情况下的生命周期

编译并执行，会发现<font color="#c00000">在默认情况下</font>：
1. 实例化和初始化会在该服务第一次被请求时调用，顺序是先构造后初始化。
2. `service` 方法会在每一次被请求时调用。
3. `destory` 方法仅会在Tomcat退出时调用。

同时，Servlet为了能够同时响应和服务多个客户端，<span style="background:#fff88f"><font color="#c00000">Servlet将被存放于堆中</font></span>，而非各个线程的栈中。<span style="background:#fff88f"><font color="#c00000">而</font></span> `service` <span style="background:#fff88f"><font color="#c00000">方法会在每个线程的栈中执行</font></span>。

<span style="background:#fff88f"><font color="#c00000">因此类的成员变量会被多个线程和客户共享</font></span>，<span style="background:#fff88f"><font color="#c00000">而</font></span> `service` <span style="background:#fff88f"><font color="#c00000">方法中的变量则只会被每个线程或客户独占</font></span>。因此Servlet的类内对象应当注意并发控制，<u><span style="background:#fff88f"><font color="#c00000">同时强烈不建议使用可写变量(即仅使用只读变量)</font></span></u>。

#### 8.2.2 将Servlet配置为Tomcat启动时即实例化

在上一章节中提到，Servlet在默认情况下会在该服务第一次被请求时实例化。而若需要在Tomcat启动时就实例化则需要按照如下方式配置：

##### 8.2.2.1 在web.xml中配置

`web.xml` 配置方式：在 `servlet` 块中添加 `load-on-startup` 属性，并将该属性配置为一个正整数即可(默认值为 `-1` ，意味着延迟加载)。

```xml
<servlet>  
    <servlet-name>userServlet</servlet-name>  
    <servlet-class>indi.h13.servlet.UserServlet</servlet-class>  
	<!-- 配置启动时实例化，1表示第一个被实例化 -->
	<load-on-startup>1</load-on-startup>
</servlet>  

<servlet-mapping>  
    <servlet-name>userServlet</servlet-name>  
    <url-pattern>/isRoot/</url-pattern>  
</servlet-mapping>
```

##### 8.2.2.2 注解方式配置

在 `@WebServlet()` 中添加 `loadOnStartup` 属性，即：

```Java
// 基础配置
@WebServlet(loadOnStartup = 1);

// 多属性配置
@WebServlet(value="/isRoot", loadOnStartup = 1);
```

##### 8.2.2.3 关于load-on-startup的取值

关于 `load-on-startup` 的取值：
1. `load-on-startup` 的默认值为 `-1` ，意味着延迟加载。即第一次被调用时加载。
2. <span style="background:#fff88f"><font color="#c00000">该正整数是在Servlet中实例化的顺序</font></span>。
3. 当出现相同整数的类，则Servlet会自动协调被实例化的顺序。
4. 该正整数不需要连续，例如该属性只有1、2、4、6，则也会被正常按顺序执行(本质是sort)。
5. Tomcat中已经被占用的值有：
	- 1
	- 3
	- 4(可选)
	- 5(可选)
	<font color="#c00000">因此建议自定义序号时，应当从大于5的值开始</font>(不过一般不会出现问题)。

## 9 DefaultServlet

查看Tomcat根目录下的 `\conf\web.xml` ，可以看到一个名为default的servlet的相关配置：

```xml
    <servlet>
        <servlet-name>default</servlet-name>
        <servlet-class>org.apache.catalina.servlets.DefaultServlet</servlet-class>
        <init-param>
            <param-name>debug</param-name>
            <param-value>0</param-value>
        </init-param>
        <init-param>
            <param-name>listings</param-name>
            <param-value>false</param-value>
        </init-param>
        <load-on-startup>1</load-on-startup>
    </servlet>

    <!-- The mapping for the default servlet -->
    <servlet-mapping>
        <servlet-name>default</servlet-name>
        <url-pattern>/</url-pattern>
    </servlet-mapping>
```

其 `url-pattern` 可以匹配所有非 `*.jsp` 路径。
当请求发生时，其工作逻辑为：
1. Tomcat会将各请求路径与所有已实现的 `servlet-mapping` 进行匹配并转发。
2. 若没有能够相应该请求的servlet，则 `DefaultServlet` 会去查找该Servlet App下的静态资源路径并转发。

需要注意的是，当后续使用 `SpringMVC` 进行开发时，该 `DefaultServlet` 不再生效。如果有需求需要重新配置并使能 `DefaultServlet` (往往会在非前后端分离的项目中出现该需求)。

## 10 Servlet的继承结构

### 10.1 Servlet的大致继承结构

Tomcat的Servlet提供的若干开发接口有如下的继承结构：
- 抽象类 `HttpServlet` 拓展了 `GenericServlet` ：
	- 抽象类 `GenericServlet` 实现了 `Servlet` 、 `ServletConfig` 、 `Serializable` 等接口。
		- `Servlet` 接口定义了如下的方法：
			- `void init(ServletConfig var1) throws ServletException;`
				- 初始化方法
				- 在Tomcat构造完成后由Tomcat调用，传入的参数是 `ServletConfig` 对象。详见[[Servlet 简介#11 ServletConfig]]
			- `ServletConfig getServletConfig();`
				- 获取 `ServletConfig` 对象的方法。
				- 详见[[Servlet 简介#11 ServletConfig]]
			- `void service(ServletRequest var1, ServletResponse var2) throws ServletException, IOException;`
				- 接收用户请求并提供服务的方法。
			- `String getServletInfo();`
				- 返回Servlet字符串形式的描述信息的方法。
			- `void destroy();`
				- 销毁方法。
				- 在 `Servlet` 对象被回收前，由Tomcat调用。用于做资源的释放工作。
		- `ServletConfig` 接口定义了如下的方法：
			- `String getServletName();`
			- `String getServletName();`
			- `String getInitParameter(String var1);`
			- `Enumeration<String> getInitParameterNames();`
		- `Serializable` 接口为序列化接口，其没有任何方法或者字段，只是用于标识可序列化的语义。<font color="#c00000">序列化是将对象状态转换为可保持或传输的格式的过程</font>。与序列化相对的是反序列化，它将流转换为对象。<font color="#c00000">这两个过程结合起来，可以轻松地存储和传输数据</font>。
在开发Servlet App时，可以选择直接继承 `HttpServlet` ，也可以选择直接实现 `Servlet` 接口。不过当选择后者时，需要手动实现 `Servlet` 接口中的每一个方法1。所以通常选择继承 `HttpServlet` 或 `GenericServlet` 。

其继承关系图解如下图所示：

![[0001.png]]

### 10.2 GenericServlet的实现详解

如上一章节所述，抽象类 `GenericServlet` 实现了 `Servlet` 、 `ServletConfig` 、 `Serializable` 等接口的<font color="#c00000">大部分</font>方法(除了 `service` 方法)。<font color="#c00000">本类侧重于除了Service方法以外的方法的处理</font>。
该抽象类的参考代码如下：

```Java
public abstract class GenericServlet implements Servlet, ServletConfig, Serializable {  
    private static final long serialVersionUID = 1L;  
    private transient ServletConfig config;  
  
    public GenericServlet() {  
    }  
  
    public void destroy() {  
    }  
  
    public String getInitParameter(String name) {  
        return this.getServletConfig().getInitParameter(name);  
    }  
  
    public Enumeration<String> getInitParameterNames() {  
        return this.getServletConfig().getInitParameterNames();  
    }  
  
    public ServletConfig getServletConfig() {  
        return this.config;  
    }  
  
    public ServletContext getServletContext() {  
        return this.getServletConfig().getServletContext();  
    }  
  
    public String getServletInfo() {  
        return "";  
    }  
  
    public void init(ServletConfig config) throws ServletException {  
        this.config = config;  
        this.init();  
    }  
  
    public void init() throws ServletException {  
    }  
  
    public void log(String message) {  
        ServletContext var10000 = this.getServletContext();  
        String var10001 = this.getServletName();  
        var10000.log(var10001 + ": " + message);  
    }  
  
    public void log(String message, Throwable t) {  
        this.getServletContext().log(this.getServletName() + ": " + message, t);  
    }  
  
    public abstract void service(ServletRequest var1, ServletResponse var2) throws ServletException, IOException;  
  
    public String getServletName() {  
        return this.config.getServletName();  
    }  
}
```

在上述代码中：
- `public void destroy()`
- `public void init()`
方法<font color="#c00000">将对应接口定义的方法实现为了一个空方法</font>，<font color="#c00000">这种实现方式叫做平庸实现</font>。
并且在上述代码中有两个 `init` 实现：

```Java
public void init(ServletConfig config) throws ServletException {  
    this.config = config;  
    this.init();  
}  

public void init() throws ServletException {  
}  
```

而含参的 `public void init(ServletConfig config)` 的本质就是转存参数，然后调用无参版本初始化(即 `public void init()` )。

<span style="background:#fff88f"><font color="#c00000">需要注意的是，当开发者通过GenericServlet实现Servlet时，应当优先考虑重写无参版本的初始化方法</font></span>。因为：
0. 含参版本的初始化通常由Tomcat调用，在Tomcat初始化该类时会将配置文件中设置的参数传递进去。
1. 而 `GenericServlet` 实现的含参初始化已经完成参数拷贝的工作(存入 `this.config` )，随后并调用无参的初始化。
2. 若用户选择重写含参初始化时，需要手动完成存入 `this.config` 的工作，而后续或从前的版本是否仍使用的是 `this.config` 这个变量并无强制性规定，可能随版本而发生改变。

此外， `GenericServlet` 仍未具体实现 `service` 方法，因此该类本质也是一个抽象类。

### 10.3 HttpServlet的实现详解

虽然在 `GenericServlet` 中只剩 `service` 方法就已经完全实现 `Servlet` 接口中所有的方法，但是 `HttpServlet` <font color="#c00000">依旧是一个抽象类</font>，在该类中侧重于 `service` 方法的处理。

查看源码可以看到 `HttpServlet` 中共计实现了如下两个名为 `service` 的方法：

```Java
protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {  
    String method = req.getMethod();  
    long lastModified;  
    if (method.equals("GET")) {  
        lastModified = this.getLastModified(req);  
        if (lastModified == -1L) {  
            this.doGet(req, resp);  
        } else {  
            long ifModifiedSince;  
            try {  
                ifModifiedSince = req.getDateHeader("If-Modified-Since");  
            } catch (IllegalArgumentException var9) {  
                ifModifiedSince = -1L;  
            }  
  
            if (ifModifiedSince < lastModified / 1000L * 1000L) {  
                this.maybeSetLastModified(resp, lastModified);  
                this.doGet(req, resp);  
            } else {  
                resp.setStatus(304);  
            }  
        }  
    } else if (method.equals("HEAD")) {  
        lastModified = this.getLastModified(req);  
        this.maybeSetLastModified(resp, lastModified);  
        this.doHead(req, resp);  
    } else if (method.equals("POST")) {  
        this.doPost(req, resp);  
    } else if (method.equals("PUT")) {  
        this.doPut(req, resp);  
    } else if (method.equals("DELETE")) {  
        this.doDelete(req, resp);  
    } else if (method.equals("OPTIONS")) {  
        this.doOptions(req, resp);  
    } else if (method.equals("TRACE")) {  
        this.doTrace(req, resp);  
    } else {  
        String errMsg = lStrings.getString("http.method_not_implemented");  
        Object[] errArgs = new Object[]{method};  
        errMsg = MessageFormat.format(errMsg, errArgs);  
        resp.sendError(501, errMsg);  
    }  
  
}

public void service(ServletRequest req, ServletResponse res) throws ServletException, IOException {  
    HttpServletRequest request;  
    HttpServletResponse response;  
    try {  
        request = (HttpServletRequest)req;  
        response = (HttpServletResponse)res;  
    } catch (ClassCastException var6) {  
        throw new ServletException(lStrings.getString("http.non_http"));  
    }  
  
    this.service(request, response);  
}
```

需要注意的是：
- <font color="#c00000">第一个</font>属性为protected的service方法的参数类型为<font color="#c00000">HttpServletRequest</font>和<font color="#c00000">HttpServletResponse</font>；而<font color="#c00000">第二个</font>属性为public的service方法的参数类型为<font color="#c00000">ServletRequest</font>和<font color="#c00000">ServletResponse</font>。
- 其调用逻辑为：
	1. Servlet被Tomcat调用 `public void service(ServletRequest req, ServletResponse res)` 方法。
	2. 在该方法中会将 `ServletRequest` 和 `ServletResponse` 分别<font color="#c00000">强制转换</font>为 `HttpServletRequest` 和 `HttpServletResponse` 类型(<font color="#c00000">因为前者是后者的父类</font>)。
	3. 随后调用 `protected void service(HttpServletRequest req, HttpServletResponse resp)` 方法。
- 关于 `protected void service(HttpServletRequest req, HttpServletResponse resp)` 方法：
	- <font color="#c00000">前文Demo中基于HttpServlet开发Servlet时，需要重载的方法就是该方法</font>。
	- 因此HttpServlet自带的service方法在某种意义上算是一个Demo或一个default方法。

因此若需要基于 `HttpServlet` 进行开发时，<span style="background:#fff88f"><font color="#c00000">通常有两种选择</font></span>：
1. 重写 `service` 方法
2. 重写 `doGet` 、 `doPost` ...方法。

## 11 ServletConfig

### 11.1 使用web.xml配置Servlet初始化参数

在使用 `web.xml` 配置初始化参数时，应当将参数填写到 `servlet` 块中，示例如下：

```xml
<!--  
1. 配置Servlet类，其配置项及其含义为：  
        servlet-name: 用于关联请求的映射路径  
        servlet-class: 完成该请求所需要实例化的Servlet类  
-->  
<servlet>  
    <servlet-name>userServlet</servlet-name>  
    <servlet-class>indi.h13.servlet.UserServlet</servlet-class>  
	<!-- -->
	<init-param>
		<param-name>key</param-name>
		<param-value>value</param-value>
	</init-param>
</servlet>  
  
<!--  
2. 配置和完成请求路径和servlet-name之间的映射。  
-->  
<servlet-mapping>  
    <servlet-name>userServlet</servlet-name>  
    <url-pattern>/isRoot</url-pattern>  
</servlet-mapping>

```
