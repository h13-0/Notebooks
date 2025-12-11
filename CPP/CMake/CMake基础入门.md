---
number headings: auto, first-level 1, max 6, 1.1
---
#CMake 

# 1 目录

```toc
```

# 2 变量

CMake按变量的提供者可以分为：
1. CMake中预先提供的变量
2. 通过 `set` 等方式用户自行定义的变量

而在CMake中，<span style="background:#fff88f"><font color="#c00000">其底层有且仅有一种类型</font></span>，<font color="#c00000">那就是字符串</font>。而在字符串之上，其通过如下的方式实现了不同的类型用途：
- 字符串类型


CMake中的变量区分大小写，其使用方式为 `${变量名}` 

### 2.1.1 set&unset




