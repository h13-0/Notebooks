---
number headings: auto, first-level 2, max 6, 1.1
---
#C-Language #CPP-Language


## 1 目录

```toc
```



## 2 新增基本特性

### 2.1 面向对象

#### 2.1.1 面向对象基础

参见：[[面相对象的程序设计]]

#### 2.1.2 重载运算符

在C++中，运算符重载是一种形式的多态，允许开发者为已有的运算符赋予自定义的行为。运算符重载的实质是函数重载。重载运算符可以是成员函数或全局函数，但必须至少有一个操作数是用户定义的类型。
重载运算符的规则：
1. <span style="background:#fff88f"><font color="#c00000">不可定义新的运算符</font></span>。
2. <span style="background:#fff88f"><font color="#c00000">不可修改现有运算符的操作数数量</font></span>。
3. **不可改变操作数的求值顺序**。
4. <span style="background:#fff88f"><font color="#c00000">某些运算符不能被重载</font></span>，如 `.` 、 `::` 、 `?:` 和 `sizeof` 。
5. <span style="background:#fff88f"><font color="#c00000">大多数运算符可以被重载</font></span>，但有一些特例如赋值运算符 `=` ，应该通常作为类的成员函数来重载。
6. 


函数重载的定义方式：

```CPP
ReturnType operator ${符号} (params...)
{
	// Do sth...
	return ...;
}
```

`${符号}` 为需要重载的运算符。<font color="#c00000">可以重载的</font>运算符有：

| <center>运算符类别</center> | <center>运算符</center>                  |
| ---------------------- | ------------------------------------- |
| 算数运算符                  | `+` 、 `-` 、 `*` 、 `/` 、 `%`           |
| 关系运算符                  | `==` 、 `!=` 、 `<` 、 `>` 、 `<=` 、 `>=` |
| 逻辑运算符                  |                                       |
| 赋值运算符                  |                                       |
| 位运算符                   |                                       |
| 单目运算符                  |                                       |
| 自增、自减运算符               |                                       |
| 动态内存操作运算符              |                                       |
| 其他运算符                  |                                       |
<span style="background:#fff88f"><font color="#c00000">不可重载的运算符有</font></span>：
1. 成员访问运算符： `.`
2. 成员指针访问运算符： `->`
3. 域操作运算符： `::`
4. 条件运算符： `? :`
5. 空间计算运算符： `sizeof`




## 3 新增基本类型

### 3.1 string类

#### 3.1.1 sizeof(string)

在x86架构下，`sizeof(std::string) = 28`；
在x86_64架构下，`sizeof(std::string) = 40`；
而 `sizeof(std::string)` 的值<u><font color="#c00000">不随字符串内容发生改变</font></u>。
#### 3.1.2 string作为struct的成员时

string可以作为struct的成员，其size计算符合内存对齐等要求。

#### 3.1.3 常用方法

| <center>方法</center>      | <center>含义</center>        | <center>备注</center> |
| ------------------------ | -------------------------- | ------------------- |
| `string(const char *s);` | 构造方法，用 `c_str` 初始化         |                     |
| `string(int n,char c);`  | 构造方法，构造一个含有 `n` 个 `c` 的字符串 |                     |
|                          |                            |                     |
|                          |                            |                     |



