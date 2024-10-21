---
number headings: auto, first-level 2, max 6, 1.1
---
#后端 #Java #SSM框架

## 1 目录

```toc
```

## 2 MyBatis简介

MyBatis是基于JDBC的一个对象关系映射(ORM，Object-Relational Mapping)的一个框架，其主要是通过使用描述对象和数据库之间映射的元数据，将程序中的对象自动持久化到关系数据库中。
其主要用于把一个类和一个表一一对应，类的每个实例对应表中的一条记录，类的每个属性对应表中的每个字段。

通常的代码结构为：
1. 定义一个普通Java对象(POJO，Plain Old Java Object)，在其中定义属性，每个属性对应数据库中表格的一个列，例如下方代码所示。该类通常存放于 `xx.xx.xx.pojos` 包下：
```Java
package indi.h13.ssserver.pojos;  

public class User {  
    private Integer uid;  
    private String name;  
    private String userName;  
    private String passwordHash;  
    private String phoneNumber;  
    private String email;  
    private String faceFeature;  
    private Integer avatarId;  
}
```
2. 


## 3 




