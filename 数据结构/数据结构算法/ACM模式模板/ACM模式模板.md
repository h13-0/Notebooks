---
number headings: auto, first-level 1, max 6, 1.1
---
#数据结构算法 #应试笔记与八股 

# 1 目录

```toc
```

# 2 C++

## 2.1 基础输入输出方式

### 2.1.1 cin

cin的分隔符为：
- 空格、tab、换行符
- 从第一个非空字符开始读取，直到换行符结束

### 2.1.2 getline




## 2.2 读入数组

给定长度数组，例如：
- 第一行输入一个正整数 $n$，代表数组的大小。
- 第二行输入 $n$ 个正整数 $a_i$，代表数组的元素。
```text
5
2 1 2 3 1
```

则可以：

```CPP
int len = 0;
cin >> len;

vector<int> nums(len, 0);
for(int i = 0; i < len; i++) {
	cin >> nums[i];
}
```



