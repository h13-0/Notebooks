---
number headings: auto, first-level 2, max 6, 1.1
---
#C-Language #CPP-Language


## 1 目录

```toc
```


## 2 新增基本类型

### 2.1 string类

#### 2.1.1 sizeof(string)

在x86架构下，`sizeof(std::string) = 28`；
在x86_64架构下，`sizeof(std::string) = 40`；
而 `sizeof(std::string)` 的值<u><font color="#c00000">不随字符串内容发生改变</font></u>。
#### 2.1.2 string作为struct的成员时

string可以作为struct的成员，其size计算符合内存对齐等要求。

#### 2.1.3 常用方法

| <center>方法</center>      | <center>含义</center>        | <center>备注</center> |
| ------------------------ | -------------------------- | ------------------- |
| `string(const char *s);` | 构造方法，用 `c_str` 初始化         |                     |
| `string(int n,char c);`  | 构造方法，构造一个含有 `n` 个 `c` 的字符串 |                     |
|                          |                            |                     |
|                          |                            |                     |



## 3 新增基本语法



