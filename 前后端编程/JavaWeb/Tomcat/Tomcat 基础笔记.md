---
number headings: auto, first-level 2, max 6, 1.1
---
#后端 #Java 

## 1 目录

```toc
```

## 2 Tomcat

### 2.1 Tomcat 简介


### 2.2 Tomcat WebAPP结构

打开Tomcat的安装目录下的 `webapps/examples` 文件夹，可以看到目录结构如下：
![[explorer_tz7cgDnjEk.png]]
除了上述目录之外，常见目录<font color="#c00000">及其子目录</font>的用途为：
- `jsp`：
- `META-INF`：
- `servlets`：
- `static`：\[非必要目录\]，存放静态资源的目录，例如 `*.jpg` 、 `*.css` 等。
	- `img`
	- `js`
	- `css`
	- ...
- `WEB-INF`：\[<font color="#c00000">必要目录</font>\]，<span style="background:#fff88f"><font color="#c00000">受保护的资源目录，即浏览器通过url无法访问的目录</font></span>。
	- `classes`：\[常见目录\]，src下源代码、配置文件，编译后会出现在该目录下。如果该web项目<u>不包含Java代码则不会出现该目录</u>。
	- `lib`：\[常见目录\]，项目依赖的jar编译后会出现在该目录。如果web项目<u>不依赖任何jar则不会出现该目录</u>。
	- `web.xml`：\[常见文件\]，Web项目的配置文件。在较新版本中不存在该文件。
- `websocket`：
- `index.html`：\[非必要文件\]，通常为默认页面。默认液面也可以是 `index.htm` 、 `index.jsp` 等。

阅读上述内容可知，<font color="#c00000">一个Tomcat App不一定需要Java代码或者JavaScript代码</font>。因此，创建目录 `webapps/test` 并向 `webapps/test/index.html` 中填充如下代码：

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>test</title>
</head>
<body>
    Hello World.
</body>
</html>
```

即可完成一个最基础的静态Tomcat App，访问效果如下：

![[chrome_IJ4YQL8og4.png]]

### 2.3 Tomcat App打包与部署

#### 2.3.1 Tomcat Demo

Tomcat Demo见[[Servlet 简介|Servlet]]章节。

#### 2.3.2 部署到其他目录

进入Tomcat文件夹，进入 `conf/Catalina/localhost` 文件夹，创建 `${app_name}.xml` 文件(其中 `${app_name}` 为APP的名称)，并填写如下内容：

```xml
<!--
	path: 项目的上下文路径，即 `http://hostname/path` 的路径
	docBase: 项目在磁盘中的实际路径
-->
<Content path="/${app_name}" docBase="${path}" />
```

#### 2.3.3 打包为war包并部署

除了上述的直接部署以外，Tomcat还有打包为 `*.war` 包的形式进行部署。
在IDEA软件中进行简单配置即可将项目打包为war包，步骤如下：
1. `File` -> `Project Structure` -> `Project Settings` -> `Artifacts`
2. 添加 `Web Application: Archive` 并选定模块即可。
![[idea64_lN8sQgvqgG.png]]
3. 编译，即在 `out` 路径下会出现war包
![[idea64_KB8AYBflpV.png]]

随后将生成的war包保存到Tomcat的 `webapps/ROOT` 文件夹下，在 `conf/server.xml` 的 `Host` 块中添加如下代码即可部署：

```xml
<Context path="/${app_name}" docBase="${TomcatPath}/ROOT/xx.war" reloadable="true"></Context>
```

随后Tomcat在启动时会自动解压该war包。

### 2.4 Tomcat常用配置

#### 2.4.1 配置网页的访问账户和密码

例如直接访问Tomcat自带demo的 `http://localhost:8080/manager/html` 时，会有如下提示：

![[chrome_meFwaexx5d.png]]

在默认情况下，Tomcat并未预置访问 `manager/html` 所需要的用户，因此需要在 `conf/tomcat-users.xml` 中的 `tomcat-users` 区块内部配置如下内容：

```xml
  <role rolename="admin-gui"/>
  <role rolename="admin-script"/>
  <role rolename="manager-gui"/>
  <role rolename="manager-script"/>
  <role rolename="manager-jmx"/>
  <role rolename="manager-status"/>
  <user username="admin" password="admin" roles="admin-gui, admin-script, manager-gui, manager-script, manager-jmx, manager-status"/>
```

随后即可成功访问：

![[chrome_1XTies2qnt.png]]
