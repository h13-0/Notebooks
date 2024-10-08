---
number headings: auto, first-level 2, max 6, 1.1
---
#Java 


## 1 目录

```toc
```

## 2 Java Bean概念

Java Bean是一种特殊的对象，符合Bean要求的对象都可以称之为Java Bean。这些要求可以使得其在Java的各种框架之间有通用的数据传递、处理方式。

### 2.1 Java Bean要求

一个标准的Java Bean需要实现如下规范：
1. 实现序列化( `Java.io.Serializable` 接口)。
2. 是一个公共类。
3. 类中必须实现一个无参构造函数。
4. 所有属性为 `private` ，并且使用 `getter` 和 `setter` 操作类中属性(并且命名符合标准)。

### 2.2 Java Bean特性






