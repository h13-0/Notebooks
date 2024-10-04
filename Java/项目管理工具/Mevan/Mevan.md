---
number headings: auto, first-level 2, max 6, 1.1
---
#Java #Mevan

## 1 目录

```toc
```

## 2 Mevan简介

Mevan是一个Java的项目构建与管理工具，可以自动化安装依赖，构建、打包和发布项目。

## 3 使用Mevan创建项目

### 3.1 项目名及项目版本管理

Mevan相比于普通的工程项目，其还需要额外配置一组属性，这组属性被称为 `GAVP` 属性，其具体为：
- `GroupID` ：<span style="background:#fff88f"><font color="#c00000">组织标识</font></span>，通常最多不超过四级，格式为 `${组织属性}.${组织名}.${业务线}.[${子业务线}]`
	- 组织属性通常有如下可选选项：
		- `indi` ：个体项目，指个人发起，但非自己独自完成的项目，可公开或私有项目，copyright主要属于发起者。
		- `pers` ：个人项目，指个人发起，独自完成，可分享的项目，copyright主要属于个人。
		- `priv` ：私有项目，指个人发起，独自完成，非公开的私人使用的项目，copyright属于个人。
		- `onem` ：同 `indi` ，并且推荐使用 `indi` 。
		- `team` ：团队项目，指由团队发起，并由该团队开发的项目，copyright属于该团队所有。
		- `com` ：公司项目，copyright由项目发起的公司所有。
	- 子业务线为可选字段。
- `ArtifactID` ：一般为项目名或模块名，或者 `${项目名}-${模块名}` ，命名前可以去仓库中心搜索一下避免重复。
- `Version` ：版本号，<u>推荐</u>格式为 `${主版本号}.${次版本号}.${Patch号}` 。
- `Packaging` ：<font color="#c00000">可选属性</font>，拥有默认值。其含义为Mevan工程的打包方式，其值只有如下三种：
	- `jar` ：<font color="#c00000">默认值</font>，打包为 `*.jar` 文件
	- `war` ：打包为JavaWeb工程
	- `pom` ：标识不会打包，通常用于当成做继承的父工程

### 3.2 使用Mevan构建Java SE工程

在IDE中创建新工程(或者Module)时选择使用Mevan构建即可，注意需要指定 `GroupID` 和 `ArtifactID` 即可：

![[idea64_On9moKqDbO.png]]

随后该项目下会出现：
1. 一个 `src` 文件夹用于存放Java代码
2. 一个 `pom.xml` 存放Mevan配置信息。

`pom.xml` 的默认配置信息如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>  
<project xmlns="http://maven.apache.org/POM/4.0.0"  
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">  
    <modelVersion>4.0.0</modelVersion>  
  
    <groupId>indi.h13</groupId>  
    <artifactId>maven-javase-project-01</artifactId>  
    <version>1.0-SNAPSHOT</version>  
  
    <properties> 
	    <maven.compiler.source>22</maven.compiler.source>  
        <maven.compiler.target>22</maven.compiler.target>  
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>  
    </properties>  
</project>
```

可以在上述配置文件中修改 `GroupID` 、 `ArtifactID` 和 `Version` 等项目信息。而在上述的默认配置中，并未提供 `Packaging` 信息，因此 `pom.xml` 中的项目信息可以做如下修改：

```xml
    <groupId>indi.h13</groupId>  
    <artifactId>maven-javase-project-01</artifactId>  
    <version>1.0.0</version>  
    <packaging>jar</packaging>
```

### 3.3 使用Mevan构建Java EE工程

正如[[Java语言基础#2 1 Java SE、EE、ME的区别和联系]]所述，Java EE是基于Java SE的拓展，因此使用Mevan构建Java EE工程有两种方式：
1. 直接使用IDE创建Java EE工程
2. 手动基于Java SE补全工程

#### 3.3.1 直接使用IDE创建Java EE工程

直接使用IDE创建Java EE工程的具体方式取决于具体的IDE，其中，在IDEA下的操作步骤如下：
1. 安装插件 `JBLJavaToWeb` 。
	![[idea64_hdyM53TwBe.png]]
2. 先创建普通Java SE工程。
3. 在该工程右键选择 `JBLJavaToWeb` 即可。
	![[sEShHZ6AGM.png]]

#### 3.3.2 手动基于Java SE补全工程

手动基于Java SE补全工程只需要补全对应文件即可，例如若需要使用Java EE创建WebApp(Servlet)，则只需要：
1. 在 `src/main` 文件夹下补充 `webapp/WEB-INF` 目录并补充 `web.xml` 文件。
2. 在 `pom.xml` 中将打包方式改为 `war` 。
3. 重新加载Mevan即可。

## 4 使用Mevan进行项目依赖管理

### 4.1 添加依赖

在完成章节[[Mevan#3 2 使用Mevan构建Java SE工程]]的配置后，所形成的 `pom.xml` 代码如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>  
<project xmlns="http://maven.apache.org/POM/4.0.0"  
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">  
    <modelVersion>4.0.0</modelVersion>  
  
    <groupId>indi.h13</groupId>  
    <artifactId>maven-javase-project-01</artifactId>  
    <version>1.0-SNAPSHOT</version>  
    <packaging>jar</packaging>
  
    <properties> 
	    <maven.compiler.source>22</maven.compiler.source>  
        <maven.compiler.target>22</maven.compiler.target>  
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>  
    </properties>  
</project>
```

而当需要使用Mevan管理依赖时则需要在 `project` 块中添加并形成如下内容：

```xml
<?xml version="1.0" encoding="UTF-8"?>  
<project xmlns="http://maven.apache.org/POM/4.0.0"  
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">  
    <modelVersion>4.0.0</modelVersion>  
  
    <groupId>indi.h13</groupId>  
    <artifactId>maven-javase-project-01</artifactId>  
    <version>1.0-SNAPSHOT</version>  
    <packaging>jar</packaging>
  
    <properties> 
	    <maven.compiler.source>22</maven.compiler.source>  
        <maven.compiler.target>22</maven.compiler.target>  
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>  
    </properties>  

<dependencies>  

	<!-- https://mvnrepository.com/artifact/com.fasterxml.jackson.core/jackson-core -->
	<dependency>
	    <groupId>com.fasterxml.jackson.core</groupId>
	    <artifactId>jackson-core</artifactId>
	    <version>2.18.0</version>
	</dependency>

	<!-- https://mvnrepository.com/artifact/com.fasterxml.jackson.core/jackson-databind -->
	<dependency>
	    <groupId>com.fasterxml.jackson.core</groupId>
	    <artifactId>jackson-databind</artifactId>
	</dependency>
	
</dependencies>

</project>
```

正如上文配置，每一个依赖均需要 `GAVP` 属性，但是 `version` 属性可以省略(<span style="background:#fff88f"><font color="#c00000">不推荐</font></span>)、使用特殊值(<span style="background:#fff88f"><font color="#c00000">不推荐</font></span>)、引用版本变量(<span style="background:#fff88f"><font color="#c00000">常用</font></span>)、使用版本区间等。详见下一章节。

而每个依赖所需要的 `GAVP` 属性可以去mevan仓库官网 https://mvnrepository.com 搜索。也可以使用 `mevan-search` 插件进行搜索和复制配置信息。
在完成 `pom.xml` 的修改之后刷新mevan即可。

### 4.2 依赖的版本管理

正如上一章节所述，版本信息的配置方式有如下几种：
- 省略
- 特殊值，特殊值有：
	- `LATEST` ：表示最新的版本，包括开发中的快照(snapshot)版本。
	- `RELEASE` ：表示最新的稳定版本，但是不包括快照版本。
	(从Maven2.1开始，`LATEST` 和 `RELEASE` <font color="#c00000">已经被标记为不推荐使用</font>，并在Maven3中<span style="background:#fff88f"><font color="#c00000">强烈不推荐使用</font></span>，<span style="background:#fff88f"><font color="#c00000">并且会在未来版本中移除</font></span>)。
- 使用版本区间：
	例如 `<version>[3.0,3.9]</version>` 表示支持使用3.0到3.9版本中的任意一个(不过该特性也需要谨慎使用)。
- 引用版本变量：
	例如可以直接在 `pom.xml` 中的 `properties` 块中定义依赖的版本变量，例如：
	```xml
	<properties> 
		<maven.compiler.source>22</maven.compiler.source>  
	    <maven.compiler.target>22</maven.compiler.target>  
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding> 
		<!-- 声明jackson版本变量 -->
		<!-- 命名的标签建议使用两层及以上 -->
		<jackson.version>2.18.0</jackson.version>
    </properties>  
	```
	随后在定义 `dependency` 时使用该变量即可：
	```xml
		<!-- https://mvnrepository.com/artifact/com.fasterxml.jackson.core/jackson-core -->
	<dependency>
	    <groupId>com.fasterxml.jackson.core</groupId>
	    <artifactId>jackson-core</artifactId>
	    <version>${jackson.version}</version>
	</dependency>

	<!-- https://mvnrepository.com/artifact/com.fasterxml.jackson.core/jackson-databind -->
	<dependency>
	    <groupId>com.fasterxml.jackson.core</groupId>
	    <artifactId>jackson-databind</artifactId>
	    <version>${jackson.version}</version>
	</dependency>
	```

### 4.3 依赖的作用域管理

在 `dependency` 块中可以添加一个 `scope` 属性用于限定依赖的作用域，其可选项有：
- `compile` ：<font color="#c00000">默认值</font>，在编辑、打包和运行时都会被生效。
- `main` ：仅在主程序中使用。
- `test` ：仅在测试中生效。
- `runtime` ：仅在运行时有效，在打包和运行时使用，例如 `mysql` 的驱动。
- `provided` ：仅在 `main` 和 `test` 中会被使用，打包和运行时不会使用(与上一项相反)，例如 `servlet` ，Tomcat本身提供了 `servlet` ，因此打包时不会将该依赖打包进去。

### 4.4 依赖传递和依赖冲突

例如工程有如下的项目依赖：

```mermaid
flowchart LR
    A[当前项目] --> B[依赖库A]
    A[当前项目] --> C[依赖库B]
    B --> D[依赖库C，版本1.0.0]
    C --> E[依赖库C，版本1.5.1]
```

则当前项目会自动







