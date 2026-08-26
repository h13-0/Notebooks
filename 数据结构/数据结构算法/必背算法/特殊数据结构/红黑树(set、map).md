---
number headings: auto, first-level 1, max 6, 1.1
---
#数据结构算法 #应试笔记与八股 

# 1 目录

```toc
```

# 2 适合类型

例如LeetCode中，有一些成员为 `string` 、`vector<T>` 的这种<span style="background:#fff88f"><font color="#c00000">没有预定义顺序机制的二分搜索场景</font></span>，可以直接使用 `set` 和 `map` 完成，使用其默认的字典序，即可完成 $O(logn)$ 的搜索复杂度，不再需要依赖定义 `Compare` 函数。

例题：
- [[数据结构/数据结构算法/LeetCode/LeetCode题目汇总#208 前缀树|LeetCode 208]]：`String` 的二分查找

