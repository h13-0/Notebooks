---
number headings: auto, first-level 2, max 6, 1.1
---
#Java 

## 1 目录

```toc
```

## 2 Mevan简介

Mevan是一个Java的项目构建与管理工具，可以自动化安装依赖，构建、打包和发布项目。

## 3 使用Mevan创建并管理项目

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

### 3.2 使用Mevan构建Java EE工程



### 3.3 使用Mevan构建Java SE工程








