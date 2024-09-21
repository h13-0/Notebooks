---
number headings: auto, first-level 2, max 6, 1.1
---
#后端 #Java 

## 1 目录

```toc
```

## 2 Tomcat简介





### 2.1 Tomcat WebAPP结构

打开Tomcat的安装目录下的 `webapps/examples` 文件夹，可以看到目录结构如下：
![[explorer_tz7cgDnjEk.png]]
除了上述目录之外，常见目录<font color="#c00000">及其子目录</font>的用途为：
- `jsp`：
- `META-INF`：
- `servlets`：
- `static`：\[非必要目录\]，存放静态资源的目录，例如 `*.jpg` 、 `*.css` 等。
- `WEB-INF`：\[<font color="#c00000">必要目录</font>\]，受保护的资源目录，即浏览器通过url无法访问的目录。
	- `classes`：\[常见目录\]，src下源代码、配置文件，编译后会出现在该目录下。如果该web项目不包含Java代码则不会出现该目录。
	- `lib`：\[常见目录\]，项目依赖的jar编译后会出现在该目录。如果web项目不依赖任何jar则不会出现该目录。
	- `web.xml`：\[常见文件\]，Web项目的配置文件。在较新版本中不存在该文件。
- `websocket`：
- `index.html`：\[非必要文件\]，
