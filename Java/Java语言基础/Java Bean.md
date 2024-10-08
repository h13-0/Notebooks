---
number headings: auto, first-level 2, max 6, 1.1
---
#Java 


## 1 目录

```toc
```

## 2 Java Bean概念

Java，从logo来理解是一杯咖啡：
	![[Pasted image 20241008200221.png]]

而如果把 `Java` 译为 "咖啡"，那 `Java Bean` 就可以翻译为 "咖啡豆" 。这很好的体现了 `Java Bean` 和 `Java` 之间的关系。事实上， `Java Bean` 的含义就是 "Java组件"。

在语法上，Java Bean是一种特殊的对象，符合Java Bean要求的对象都可以称之为Java Bean。这些要求可以使得其在Java的各种框架之间有通用的数据传递、处理方式。

## 3 Java Bean要求

从语法上，任何符合Java Bean要求的对象都可以称之为Java Bean。而其本质只是Java的一个特殊的类的规范而已。

一个标准的Java Bean需要遵守如下规范：
1. 实现序列化( `Java.io.Serializable` 接口)。
2. 是一个公共类。
3. 类中必须实现一个无参构造函数。
4. 所有属性为 `private` ，并且使用 `getter` 和 `setter` 操作类中属性(并且命名符合标准)。

## 4 Java Bean特性






