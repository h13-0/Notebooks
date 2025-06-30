---
number headings: auto, first-level 1, max 6, 1.1
---
#C-Language #CPP-Language

# 1 目录

```toc
```

# 2 新增基本特性

## 2.1 面向对象

### 2.1.1 面向对象基础

通用部分参见：[[面相对象的程序设计]]

#### 2.1.1.1 对象的构造

此外，需要额外说明的是在C++中规定：<span style="background:#fff88f"><font color="#c00000">任何可以被解析为函数声明的代码都会被解析为函数声明</font></span>。因此在类的定义中，有如下注意事项：

```CPP
// 正确：调用默认构造函数
ClassName obj;

// 错误：声明一个返回值为ClassName的函数，函数名为obj
ClassName obj();

// C++11及以后正确：使用花括号避免歧义
ClassName obj{};
```

### 2.1.2 重载运算符

#### 2.1.2.1 基本定义

在C++中，运算符重载是一种形式的多态，允许开发者为已有的运算符赋予自定义的行为。运算符重载的实质是函数重载。重载运算符可以是<font color="#c00000">成员函数</font><span style="background:#fff88f"><font color="#c00000">或</font></span><font color="#c00000">全局函数(友元函数)</font>，但必须至少有一个操作数是用户定义的类型。

#### 2.1.2.2 运算符重载规则

1. <span style="background:#fff88f"><font color="#c00000">不可定义新的运算符</font></span>。
2. <span style="background:#fff88f"><font color="#c00000">不可修改现有运算符的操作数数量</font></span>。
3. **不可改变操作数的求值顺序**。
4. <span style="background:#fff88f"><font color="#c00000">某些运算符不能被重载</font></span>，如 `.` 、 `::` 、 `?:` 和 `sizeof` 。
5. <span style="background:#fff88f"><font color="#c00000">大多数运算符可以被重载</font></span>，但有一些特例如赋值运算符 `=` ，应该通常作为类的成员函数来重载。
6. 定义后的运算符功能应与其原先目的相同或相似。

#### 2.1.2.3 运算符重载的定义方式

```CPP
ReturnType operator${符号}(params...)
{
	// Do sth...
	return ...;
}
```

`${符号}` 为需要重载的运算符，<font color="#c00000">前后可以加空格</font>。

#### 2.1.2.4 可重载和不可重载的运算符

<font color="#c00000">可以重载的</font>运算符有：

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

#### 2.1.2.5 重载运算符Demo

假设我们需要对如下的虚数类实现其加法运算：

```CPP
class Complex {
private:
	double real;
	double image;

public:
	Complex(double real, double image);
	std::string to_string(void);
};

Complex::Complex(double real, double image)
{
	this->real = real;
	this->image = image;
}

std::string Complex::to_string(void)
{
	using namespace std;

	string symbol = "";
	image >= 0 ? symbol = "+" : symbol = "-";

	string str = std::format("{}{}{}i\r\n", real, symbol, fabs(image));
	return str;
}
```

##### 2.1.2.5.1 友元函数实现

基于上述类，可以基于上述类和友元函数实现全局函数定义的运算符 `+` 的重载，Demo如下：

```CPP
class Complex {
private:
	double real;
	double image;

public:
	Complex(double real, double image);
	std::string to_string(void);
	friend Complex operator+(const Complex& comp1, const Complex& comp2);
};

Complex::Complex(double real, double image)
{
	this->real = real;
	this->image = image;
}

std::string Complex::to_string(void)
{
	using namespace std;

	string symbol = "";
	image >= 0 ? symbol = "+" : symbol = "-";

	string str = std::format("{}{}{}i\r\n", real, symbol, fabs(image));
	return str;
}

Complex operator+(const Complex& comp1, const Complex& comp2)
{
	return Complex(comp1.real + comp2.real, comp1.image + comp2.image);
}
```

##### 2.1.2.5.2 成员函数实现

<span style="background:#fff88f"><font color="#c00000">与上述友元函数的运算符重载不同的是，成员函数实现的运算符重载不再需要额外传递一次自身。即成员函数实现的运算符重载会比友元函数少一个函数参数。</font></span>
<font color="#c00000">如果需要重载的运算符为双目运算符，则只需要设置一个参数作为右侧运算量。</font>
<font color="#c00000">如果需要重载的运算符为单目运算符，则不需要另外设置参数，使用自身进行运算即可。</font>

因此，可以基于上述类和成员函数实现运算符 `==` 的重载，Demo如下：

```CPP
class Complex {
private:
	double real;
	double image;

public:
	Complex(double real, double image);
	std::string to_string(void);
	bool operator==(const Complex& comp);
};

bool Complex::operator==(const Complex& comp)
{
	return (this->real == comp.real && this->image == comp.image);
}
```

#### 2.1.2.6 运算符的隐式和显式调用

直接使用对若干个对象进行运算就是运算符的隐式调用，例如：

```CPP
Complex comp1(1, -1);
Complex comp2(-2, 3);

Complex comp_sum = comp1 + comp2;
```

而除了显示调用以外，还有如下的隐式调用方式：

```CPP
Complex comp1(1, -1);
Complex comp2(-2, 3);

// 全局函数重载的显示调用方式：
Complex comp_sum = operator+(comp1, comp2);
// 成员函数重载的显示调用方式
comp1.operator==(comp2);
```

<span style="background:#fff88f"><font color="#c00000">需要注意的是，函数重载的方式不同，其对应的显示调用方式也不同。</font></span>

### 2.1.3 模板






## 2.2 新增基本类型(不含STL)

### 2.2.1 string类

#### 2.2.1.1 sizeof(string)

在x86架构下，`sizeof(std::string) = 28`；
在x86_64架构下，`sizeof(std::string) = 40`；
而 `sizeof(std::string)` 的值<u><font color="#c00000">不随字符串内容发生改变</font></u>。
#### 2.2.1.2 string作为struct的成员时

string可以作为struct的成员，其size计算符合内存对齐等要求。

#### 2.2.1.3 常用方法

| <center>方法</center>      | <center>含义</center>        | <center>备注</center> |
| ------------------------ | -------------------------- | ------------------- |
| `string(const char *s);` | 构造方法，用 `c_str` 初始化         |                     |
| `string(int n,char c);`  | 构造方法，构造一个含有 `n` 个 `c` 的字符串 |                     |
|                          |                            |                     |
|                          |                            |                     |

# 3 STL

STL全名为Standard Template Library，意为标准模板库或泛型库，是C++中的一个重要组件。其主要包含如下组件：
- 容器(Containers)
- 算法(Algorithms)
- 迭代器(iterators)
- 函数对象(Function Objects)
- 适配器(Adapters)

## 3.1 迭代器






## 3.2 容器

STL容器主要有如下三类：
1. 序列容器
	1. `std::array`
	2. `std::vector`
	3. `std::deque`
	4. `std::list`
2. 关联容器
	1. `std::set`
	2. `std::multiset`
	3. `std::map`
	4. `std::multimap`
3. 无序容器
	1. `std::unordered_set`
	2. `std::unordered_multiset`
	3. `std::unordered_map`
	4. `std::unordered_multimap`

### 3.2.1 array

### 3.2.2 vector

`std::vector` 是C++的动态大小的数组实现，其元素被顺序存储，因此其可以被迭代器和引索顺序访问。其会自动扩展其所需要的内存空间，并且通常其所占用的内存比同大小的静态数组要多。其空间的动态分配仅会发生在其所保留的额外空间耗尽时触发。

#### 3.2.2.1 常用操作的时间复杂度

<font color="#c00000">vector的常用操作的时间复杂度</font>：
- 随机访问：$O(1)$
- 在末尾插入或删除元素：平均$O(1)$
- 在末尾的倒数第n个位置插入或删除元素：$O(n)$

#### 3.2.2.2 模板类型

<font color="#c00000">vector中的模板类型需要满足如下要求</font>：
- 可以拷贝赋值
- 可以拷贝构造

但是需要注意<span style="background:#fff88f"><font color="#c00000">慎用bool类型作为vector的元素</font></span>，除非明确地要使用 `vector<bool>` 的特性。

#### 3.2.2.3 常用方法





### 3.2.3 std::initializer_list

<font color="#9bbb59">初始化列表</font>( `initializer_list` )是一个轻量化的<span style="background:#fff88f"><font color="#c00000">只读容器</font></span>，<font color="#c00000">通常其只能通过特殊的构造函数构造</font>。
需注意的是，<font color="#9bbb59">初始化列表</font>和构造函数的<font color="#9bbb59">成员初始化列表</font>是不同的概念。

#### 3.2.3.1 模板定义

```CPP
template< class T >
class initializer_list;
```

#### 3.2.3.2 常用构造函数

```CPP
initializer_list() noexcept;
```

正如章节开头所述， `initializer_list` <font color="#c00000">是一个只读容器</font>，因此其必须在构造时赋值。而上述的默认构造函数明显无法完成该需求。所以C++和编译器就为其提供了独有的构造方式：

```CPP
std::initializer_list<int> list{1, 2, 3};
```

而在上述步骤中，编译器执行了如下的工作步骤：
1. 创建对应的临时常量数组 `const int __temp_array[5] = {1, 2, 3, 4, 5};`
2. 调用如下的私有构造函数：

```C
private:
	constexpr initializer_list(const E* first, size_t count) 
		: begin_(first), size_(count) {}
```

#### 3.2.3.3 常用方法

##### 3.2.3.3.1 查询元素数量(size)

```CPP
size_type size() const noexcept;
```

其实际上返回的是表达式 `std::distance(begin(), end())` 的值，类型为 `std::size_t` 。

##### 3.2.3.3.2 迭代器(begin、end)

```CPP
const T* begin() const noexcept;
const T* end() const noexcept;
```

### 3.2.4 std::unordered_map

`std::unordered_map` <font color="#c00000">基于哈希表实现</font>，内部元素无序存储。

#### 3.2.4.1 模板定义

```CPP
template<
  class Key,
  class T,
  class Hash = std::hash<Key>,
  class KeyEqual = std::equal_to<Key>,
  class Allocator = std::allocator<std::pair<const Key, T>>
> class unordered_map;
```

上述模板中：
- `class Key` 为键类型
- `class T` 为值类型
- `class Hash` 为哈希函数对象类型
- `class KeyEqual` 为键值比较函数对象类型
- `class Allocator` 为内存分配器类型

#### 3.2.4.2 常用构造函数

```CPP
unordered_map();
```

其定义了如下的成员：
- `key_type` ：即 `class Key` ，键类型
- `mapped_type` ：即 `class T` ，值类型
- `value_type` ：`std::pair<const Key, T>` ^o36e6j 

#### 3.2.4.3 常用方法

##### 3.2.4.3.1 清空容器(clear)

```CPP
void clear() noexcept;
```

##### 3.2.4.3.2 插入元素(insert)

###### 3.2.4.3.2.1 插入单个元素

```CPP
std::pair<iterator, bool> insert( const value_type& value ); 
std::pair<iterator, bool> insert( value_type&& value );
```

其：
- 参数类型为[[C2CPP#^o36e6j|value_type]]，即键值对
- 返回值为 `std::pair<iterator, bool>` ：
	- 第一个参数为指向插入键的迭代器
	- 第二个参数为该键是否插入成功
- 特性/语义：
	- <font color="#c00000">若原容器中已有相同键值，则插入失败</font>

其示例为：

```CPP
std::unordered_map<int, std::string> map;
auto ret1 = map.insert({1, "one"});               // ret1.second == true
auto ret2 = map.insert(std::make_pair(1, "one")); // 此时ret2.second为false
```

###### 3.2.4.3.2.2 批量插入(通过初始化列表)

```CPP
void insert( std::initializer_list<value_type> ilist );
```

其：
- 参数类型为键值对构成的初始化列表( `{{key1, value1}, {key2, value2}, ...}` )
- 无返回值
- 特性/语义：
	- 若参数中有重复键，则只插入第一个
	- 不会修改已有键值

###### 3.2.4.3.2.3 批量插入(通过迭代器)

```C
template< class InputIt >
void insert( InputIt first, InputIt last );
```



###### 3.2.4.3.2.4 带位置提示的插入

##### 3.2.4.3.3 删除元素(erase)

###### 3.2.4.3.3.1 通过key值删除

```CPP
size_type erase( const Key& key );
```

其中：
- 参数为需要删除的键值对的键
- 返回值为被删除的元素数量，值为0或1

时间复杂度：
- 平均 $O(1)$
- 最坏 $O(size)$

###### 3.2.4.3.3.2 通过迭代器删除单个元素

```CPP
iterator erase( iterator pos );
```

其中：
- 参数:
	- `pos` 为要删除元素的迭代器，<span style="background:#fff88f"><font color="#c00000">且不能为</font></span> `end()` <span style="background:#fff88f"><font color="#c00000">!!!</font></span>
		- 因为<font color="#c00000">只要map不为空</font>，<font color="#c00000">其最后一个元素就不是</font> `end()` ，所以<font color="#c00000">非空时</font>删除最后一个元素应当使用 `map.erase(std::prev(map.end()))`
- 返回值为被删除元素之后元素的迭代器。如果删除的是最后一个元素，则返回 `end()` 。

###### 3.2.4.3.3.3 通过迭代器范围删除元素

```CPP
iterator erase( const_iterator first, const_iterator last );
```

其中：
- 参数：
	- `first` 为第一个要删除的元素
	- `last` 为删除范围后的一个元素(`last` <span style="background:#fff88f"><font color="#c00000">不会被删除</font></span>)
	- 其删除范围为 $[first, last)$ 
- 返回值：
	- 返回 `last` 迭代器指向的位置(即被删除的最后一个元素的下一个元素)。
	- 如果 `last` 是 `end()` ，则返回 `end()` 。

时间复杂度：
- 平均 $O(n)$
- 最坏 $O(n\times size)$

##### 3.2.4.3.4 查询(at)

###### 3.2.4.3.4.1 普通查找

普通查找有如下两个不同的成员函数：

```CPP
T& at( const Key& key );
const T& at( const Key& key ) const;
```

上述两个成员函数是由编译器根据被提取变量的常量性来自动选区的，例如：

```CPP
std::unordered_map<int, std::string> map;
// 存入常量(但是并不影响at使用哪个方法)
map.emplace(1, "Hello");

// 使用非const变量提取元素，自动使用非常量版本的at函数
std::string& ref = map.at(1);
// 使用const变量提取元素，自动使用常量版本的at函数
const std::string& cref = const_map.at(1);
```

###### 3.2.4.3.4.2 异构查找(C++26)

在普通查找时，其参数只能为Key的类型，而不能是可以和Key透明比较的类型。例如：

```CPP
// C++11 传统方法：有性能损耗
// 创建临时 std::string 对象 → 内存分配 + 复制
int value1 = traditional_map.at("view"); 

// C++26 异构方法：零开销
// 直接使用 string_view 查找 → 无临时对象
int value2 = transparent_map.at(std::string_view("view"));
```

##### 3.2.4.3.5 查询/新增(operator\[\])

其对应的运算符重载函数签名为：

```CPP
T& operator[]( const Key& key );
T& operator[]( Key&& key );
```

与at的对比：

| 特性     | `at()` | `operator[]` |
| ------ | ------ | ------------ |
| 键值不存在时 | 抛出异常   | 插入新元素        |
| 只读访问   | 可用     | 不可，会插入新元素    |

##### 3.2.4.3.6 原地插入(emplace)





### 3.2.5 std::map

`std::map` 内部通常基于红黑树实现，<font color="#c00000">元素始终按键的升序排序</font>。

## 3.3 算法

### 3.3.1 排序

#### 3.3.1.1 std::sort(混合排序)

`std::sort` 使用的排序方法会根据需要排序的元素数量动态切换排序方式，是<span style="background:#fff88f"><font color="#c00000">不稳定</font></span><font color="#c00000">排序</font>。其先使用快速排序对数据进行分段，
- 


