---
number headings: auto, first-level 1, max 6, 1.1
---
#数据结构算法 #应试笔记与八股 

# 1 目录

```toc
```

# 2 适合类型

在C++中，`set` 、`map` 均是<font color="#c00000">使用红黑树实现</font>，其：
- <font color="#c00000">内部元素有序</font>，<span style="background:#fff88f"><font color="#c00000">遍历时也有序</font></span>
- <font color="#c00000">查找复杂度为</font> $O(logn)$ (`set.find()` 、`map.find()`)
- <font color="#c00000">二分搜索</font>为 `set.lower_bound()` / `set.upper_bound()`

因此其适合一些成员为 `string` 、`vector<T>` 的这种<span style="background:#fff88f"><font color="#c00000">没有预定义顺序规则的二分搜索场景</font></span>，可以直接使用 `set` 和 `map` 完成，使用其默认的字典序，即可完成 $O(logn)$ 的搜索复杂度，不再需要依赖定义 `Compare` 函数。

例如：
- [[数据结构/数据结构算法/LeetCode/LeetCode题目汇总#208 前缀树|LeetCode 208]]：`String` 的二分查找

## 2.1 字符串的二分查找

[[数据结构/数据结构算法/LeetCode/LeetCode题目汇总#208 前缀树|LeetCode 208]]
![[数据结构/数据结构算法/LeetCode/LeetCode题目汇总#208 前缀树|LeetCode 208]]

```CPP
class Trie {
private:
    set<string> data;
public:
    Trie() {
        
    }
    
    void insert(string word) {
        data.insert(word);
    }
    
    bool search(string word) {
        return data.find(word) != data.end();
    }
    
    bool startsWith(string prefix) {
        set<string>::iterator pos = data.lower_bound(prefix);
        return 
        	pos != data.end() && 
        	pos->size() >= prefix.size() && 
        	!pos->compare(0, prefix.size(), prefix);
    }
};
```