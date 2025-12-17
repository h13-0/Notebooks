---
number headings: auto, first-level 1, max 6, 1.1
---
#C-Language #CPP-Language

# 1 目录

```toc
```

# 2 Readme

出于必要性考虑，本笔记不再记录已经被废弃或即将被废弃的C++特性。
学习本笔记前应当完成[[../../面向对象的程序设计/面向对象的程序设计|面向对象的程序设计]]的学习。

# 3 新增基本特性(不含STL)

## 3.1 面向对象

在笔记[[../../面向对象的程序设计/面向对象的程序设计|面向对象的程序设计]]中已经给出若干面向对象的特性，其中学习本章节之前需要提前学习的有：
- 

### 3.1.1 对象的构造

在[[../../面向对象的程序设计/面向对象的程序设计|面向对象的程序设计]]中已经给出了C++对象的若干构造方法。

此外，需要额外说明的是在C++中规定：<span style="background:#fff88f"><font color="#c00000">任何可以被解析为函数声明的代码都会被解析为函数声明</font></span>。因此在类的定义中，有如下注意事项：

```CPP
// 正确：调用默认构造函数
ClassName obj;

// 错误：声明一个返回值为ClassName的函数，函数名为obj
ClassName obj();

// 正确：使用含参构造非法，无歧义
ClassName obj(123);

// C++11及以后正确：使用花括号避免歧义，本质为使用std::initializer_list
ClassName obj{};
```

### 3.1.2 struct与class ^of8se6

在C++中，<font color="#c00000">struct与class几乎完全一致</font>，其区别仅在于：
- class中默认成员访问权限和继承权限为 `private` ，struct中默认成员访问权限和继承权限为 `public` 
而使用 `struct` 可以很方便的实现[[../../面向对象的程序设计/面向对象的程序设计#^vuawz5|聚合初始化]]功能，而该功能又可以让struct像C语言中的struct一样被简单定义。

### 3.1.3 面向对象的其他基础特性

#### 3.1.3.1 this指针

众所周知，在C语言中，同名变量之间优先使用最近作用域的那个变量(可以近似理解为在当前代码可访问的作用域内，作用域越小的同名变量越优先被使用)。

而在遇到如下情况时：

```CPP
class demo {
	int var;
	void setVar(int var)
	{
		this->var = var;
	}
}
```

成员变量 `var` 的作用域是整个类，大于 `setVar` 方法中的参数 `var` ，因此此时则需要引入 `this` 指针来明确指定使用成员变量或成员方法。

简单来说，在类中的<font color="#c00000">非静态方法</font>均可访问 `this` 指针来指向当前对象，从而指向类中方法、属性或类本身等。

#### 3.1.3.2 指定使用默认的方法(=default)

使用默认方法 `=default` 可以用于指定部分函数按照其自动生成规则进行生成。具体如下。

在C++11中可以指定使用默认的方法有：
- 默认构造函数 `T()=default;`
- 析构函数 `~T()=default;`
- 拷贝构造函数 `T(const T&)=default;`
- 拷贝赋值函数 `T& operator=(const T&)=default;`
- 移动构造函数 `T(T&&)=default;`
- 移动赋值函数 `T& operator=(const T&&)=default;`
而在C++20起，还额外支持了：
- 比较运算函数 `bool operator==(const T&) const=default;`
- 三路比较函数 `auto operator<=>(const T&) const=default;`
<span style="background:#fff88f"><font color="#c00000">明显地，上述构造函数中</font></span>：
- <font color="#c00000">拷贝构造函数的参数均为</font> `const T&`
- <font color="#c00000">移动构造函数的参数均为</font> `T&&`
- <font color="#c00000">复制函数均为运算符重载</font> `operator=`
此外：
1. <font color="#c00000">若指定的函数不满足生成条件</font>，<span style="background:#fff88f"><font color="#c00000">则</font></span> `=default;` <span style="background:#fff88f"><font color="#c00000">会转化为</font></span> `=delete;` ，例如：
	- 若成员中包含不可拷贝类型，则<font color="#c00000"><u>拷贝构造函数</u></font>、<font color="#c00000"><u>拷贝赋值函数</u></font>会被转化为 `=delete;` 
	- 若成员中包含 `const` 成员或引用成员，且没有自定义赋值语句，则<font color="#c00000"><u>拷贝赋值函数</u></font>也会被删除
	- 若成员或基类没有默认构造且未提供成员初始化器，则<font color="#c00000"><u>默认构造函数</u></font>会被删除
	- 若该类已经声明了任意构造函数，则该类的<font color="#c00000"><u>默认构造函数</u></font>会被删除
	- 若基类或成员不可移动，则<font color="#c00000"><u>移动构造函数</u></font>、<font color="#c00000"><u>移动赋值函数</u></font>会被删除
	- 若某个基类或成员析构函数被删除，则该类<font color="#c00000"><u>析构函数</u></font>会被删除
	- 若某个基类或成员不可比较，则<font color="#c00000"><u>比较运算函数</u></font>、<font color="#c00000"><u>三路比较函数</u></font>会被删除
2. <font color="#c00000">当类声明了析构函数</font>(即使是 `~T()=default;` )，<font color="#c00000">则编译器不会再隐式生成移动构造或移动赋值函数</font>，除非再手动 `T(T&&)=default;` 等。
3. 使用 `=default;` 生成默认方法和直接使用一个空实现(例如 `T(){};` )的区别是自定义的空函数可能会失去trivial特性，例如 `noexcept` 、 `constexpr` 等特性。

#### 3.1.3.3 删除指定方法(=delete)

删除指定方法 `=delete` 可以用于删除不可支持或暂不支持的方法，例如当类中成员包含不可复制对象时(例如套接字等)可以显示禁用类的拷贝方法。

#### 3.1.3.4 成员引入(using) ^464qd9

当父类中某一个函数有多个重载，且子类<font color="#c00000">只</font><span style="background:#fff88f"><font color="#c00000">重新定义</font></span><font color="#c00000">了某一个时</font>，可以使用 `using` 把其他签名的函数引入到子类中，例如：

```CPP
class Base {
public:
    void func(int i) { ... }
    void func(double d) { ... }
};

class Derived : public Base {
public:
    // 子类定义了一个 func，这会导致 Base::func(int) 和 Base::func(double) 被隐藏
    void func(std::string s) { ... }
    
    // 补救：使用 using 把父类的 func 全家桶都拉进可见范围
    using Base::func; 
};

Derived d;
d.func(10); // 如果没有 using，这行会报错
```

同样的，若我只想重定义 `void func(int i) { ... }` ，那么则应当按照如下方式进行：

```CPP
class Base {
public:
    void func(int i) { ... }
    void func(double d) { ... }
};

class Derived : public Base {
public:
	// **提前**使用 using 把父类的 func 全家桶都拉进可见范围
	using Base::func; 
	
    // 子类重定义 func ，从而只覆盖 `void func(int i)`
    void func(int i) { ... }
};
```

注意：
1. <font color="#c00000">使用</font> `using` <font color="#c00000">引入基类成员</font>和<font color="#c00000">重新定义基类成员</font>是<span style="background:#fff88f"><font color="#c00000">两个<u>不同的</u>特性</font></span>：
	- 使用 `using` 则会<font color="#c00000">重新引入对应的成员</font>，<font color="#c00000">不会创建新的副本</font>
	- 重新定义基类成员会重新分配一个成员，并按变量遮蔽规则进行使用，即：
		- 父类中<font color="#c00000">只能使用</font>父类定义的成员
		- 子类中<font color="#c00000">优先使用</font>子类定义的成员

#### 3.1.3.5 成员权限修改(using) ^cvt59v

在C++的语法上，允许子类通过<font color="#c00000">使用</font> `using` <font color="#c00000">的方式来修改某个属性和方法的权限</font>，例如：

```CPP
class Base {
protected:
    void func() { /* ... */ } // 父类是 public
};

class Derived : public Base {
public:
    // 将父类的 func 在子类中强制降级为 private
    using Base::func;
};
```

当然，从语法上也允许子类将 `public` 的方法降级为 `private` ，不过其依旧可以通过多态将子类降级为父类从而实现访问。因此：
- 将成员<font color="#c00000">提权</font>是<span style="background:#fff88f"><font color="#c00000">可行且常用的</font></span>
- 将成员<font color="#c00000">降级</font>是可行但<font color="#c00000">有漏洞的</font>(没必要)

注意：
1. 只能通过 `using` 的方式实现上述操作
2. <font color="#c00000">若使用重新定义的方式</font>，<span style="background:#fff88f"><font color="#c00000">则会触发命名遮蔽特性</font></span>。<font color="#c00000">此时会创建两个副本</font>，<font color="#c00000">父类中只能看到父类的副本</font>，<font color="#c00000">子类则优先看到子类的副本</font>(与上一章节相同)。

### 3.1.4 重载运算符

#### 3.1.4.1 基本定义

在C++中，运算符重载是一种形式的多态，允许开发者为已有的运算符赋予自定义的行为。运算符重载的实质是函数重载。重载运算符可以是<font color="#c00000">成员函数</font><span style="background:#fff88f"><font color="#c00000">或</font></span><font color="#c00000">全局函数(友元函数)</font>，但必须至少有一个操作数是用户定义的类型。

#### 3.1.4.2 运算符重载规则

1. <span style="background:#fff88f"><font color="#c00000">不可定义新的运算符</font></span>。
2. <span style="background:#fff88f"><font color="#c00000">不可修改现有运算符的操作数数量</font></span>。
3. **不可改变操作数的求值顺序**。
4. <span style="background:#fff88f"><font color="#c00000">某些运算符不能被重载</font></span>，如 `.` 、 `::` 、 `?:` 和 `sizeof` 。
5. <span style="background:#fff88f"><font color="#c00000">大多数运算符可以被重载</font></span>，但有一些特例如赋值运算符 `=` ，应该通常作为类的成员函数来重载。
6. 定义后的运算符功能应与其原先目的相同或相似。

#### 3.1.4.3 运算符重载的定义方式

```CPP
ReturnType operator${符号}(params...)
{
	// Do sth...
	return ...;
}
```

`${符号}` 为需要重载的运算符，<font color="#c00000">前后可以加空格</font>。

#### 3.1.4.4 可重载和不可重载的运算符

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

#### 3.1.4.5 重载运算符Demo

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

##### 3.1.4.5.1 友元函数实现

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

##### 3.1.4.5.2 成员函数实现

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

#### 3.1.4.6 运算符的隐式和显式调用

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

### 3.1.5 模板


### 3.1.6 虚函数与纯虚函数

[[面向对象的程序设计/面向对象的程序设计#^gcn6sq|虚函数与纯虚函数]]

### 3.1.7 最终继承、绝育类

[[面向对象的程序设计/面向对象的程序设计#^dq3ggj|最终继承、绝育类]]



## 3.2 引用


## 3.3 新增基本类型(不含STL)

### 3.3.1 智能指针

智能指针是C++中一类指针的统称，其包含：
- `std::unique_ptr` 独占指针
- `std::shared_ptr` 共享指针
- `std::weak_ptr` 弱引用指针
智能指针严格来说不属于STL。
智能指针使用头文件 `<memory>` 。

#### 3.3.1.1 独占指针(unique_ptr)

独占指针是现在C++中<font color="#c00000">最常用</font>、<font color="#c00000">最推荐</font>的智能指针，其特性如下：
1. 独占特性：
	1. 同一时刻<font color="#c00000">有且只能有一个</font> `unique_ptr` 指向该对象
	2. 禁止拷贝：赋值会报错
	3. 允许移动：把所有权通过 `std::move` 转让给别人
2. 零开销特性：其大小和普通指针一样大，运行时也几乎没有额外开销
3. 自动内存管理：指针声明周期结束时会自动释放对应内存

其特性与demo为：

```CPP
void test_unique() {
    // 通过 `std::make_unique` 创建
    std::unique_ptr<int> ptr1 = std::make_unique<int>(10);
    
    // std::unique_ptr<int> ptr2 = ptr1; // 编译报错！禁止拷贝
    
    // 移动 (所有权转移)
    std::unique_ptr<int> ptr2 = std::move(ptr1); 
    // 此时 ptr1 变为空 (nullptr)，ptr2 拥有那个 int
} // 函数结束，ptr2 析构，自动 delete 内存
```

#### 3.3.1.2 共享指针(shared_ptr)

共享指针用于多个指针指向同一个对象的情况，其特性如下：
1. <font color="#c00000">引用计数特性</font>：
	- 每多一个指针则引用计数器 `+1` ，每少一个指针则计数器 `-1` 
	- 计数器归零时自动释放内存
2. 有性能开销：
	1. <font color="#c00000">其大小是普通指针的二倍</font>(一个指向对象，一个指向计数器)
	2. 计数器的加减涉及原子操作，新增/释放指针时比普通指针慢
3. 允许拷贝

其特性与demo为：

```CPP
void test_shared() {
	// 通过 `std::make_shared` 创建，此时计数器为1
    std::shared_ptr<int> sp1 = std::make_shared<int>(100);
    
    {
    	// 两指针共用一个 int
        std::shared_ptr<int> sp2 = sp1; // 允许拷贝，计数 = 2
    } // sp2 析构，计数 = 1，内存未释放
    
} // sp1 析构，计数 = 0 -> 释放内存
```

#### 3.3.1.3 弱引用指针(weak_ptr)

弱引用指针是为解决共享指针循环引用问题而设计的工具，<font color="#c00000">需要配合共享指针使用</font>。

考虑如下的循环引用场景：

```CPP
struct B;
struct A {
    std::shared_ptr<B> b_ptr;
};
struct B {
    std::shared_ptr<A> a_ptr; 
};

void test_cycle() {
    auto a = std::make_shared<A>();
    auto b = std::make_shared<B>();
    a->b_ptr = b;  // b的引用计数 -> 2
    b->a_ptr = a;  // a的引用计数 -> 2
} // a, b均减一，但不为0，内存泄露
```

那么此时则需要为其中一个结构体设计一个不增加引用计数器的指针，即 `weak_ptr` ，其特性如下：
1. <font color="#c00000">不增加共享指针的引用计数</font>
2. 其没有解引用操作符(`*` 、 `->`)，需要调用 `.lock()` 升级为 `std::shared_ptr` 后才可以使用
其改进demo如下：

```CPP
struct B;
struct A {
    std::shared_ptr<B> b_ptr;
};
struct B {
    // 如果这里是 shared_ptr<A>，就会循环引用，内存永远泄露
    std::weak_ptr<A> a_ptr; 
};

void test_cycle() {
    auto a = std::make_shared<A>();
    auto b = std::make_shared<B>();
    a->b_ptr = b;
    b->a_ptr = a; // weak_ptr 不增加计数
    
    // 解引用需要升级为 shared_ptr
    auto shared = b->a_ptr.lock();
    if(shared)
    	do_sth(*shared);
    
} // 正常释放
```

### 3.3.2 强类型枚举(enum class)

### 3.3.3 原子变量(std::atomic)(C++11)

正如其名，对原子类型的操作是原子的，即在多线程环境下任何对原子变量的访问都是完整的。因此使用原子变量可以有效避免数据竞争。

在C++中，原子变量是一个模板类，其支持如下的类型：
- 整数类型：`int` 、`loog` 、`unsigned int`、`uintxx_t` 等
- bool类型：
- 指针类型：
- 用户自定义的满足要求的，满足如下要求的类型(Struct/Class)：
	- 目标类型必须是可平凡拷贝的(可以用 `memcpy` 进行拷贝)

需要注意：
1. 对于小对象，编译器通常会直接生成无锁指令，<font color="#c00000">是硬件级的原子操作</font>
2. 对于大对象，编译器<font color="#c00000">可能通过</font><span style="background:#fff88f"><font color="#c00000">内置互斥锁</font></span>实现"原子操作"：
	- 通常来说，界限为8字节或16字节
	- <font color="#c00000">可以使用</font> `obj.is_lock_free()` <font color="#c00000">来检测当前类型是否无锁</font>

#### 3.3.3.1 构造函数




#### 3.3.3.2 成员函数

C++的原子变量支持如子章节所示的成员函数。

##### 3.3.3.2.1 检查对象是否无锁

```CPP
bool is_lock_free() const noexcept;
```

其返回值为是否有锁。

##### 3.3.3.2.2 赋值运算符(operator=)

```CPP
T operator=(T desired) noexcept;
```

其功能为将非原子变量的值存入原子变量，等价于调用 `store` 函数。
参数：
- `T desired` ：要存入的非原子变量类型的值
返回值：
- 等于 `desired`

##### 3.3.3.2.3 原子地存值(store)

```CPP
void store(T desired, std::memory_order order =
            std::memory_order_seq_cst ) noexcept;
```

其功能为将非原子变量的值存入原子变量。
参数：
- `T desired` ：要存入的非原子变量类型的值
- `std::memory_order order` ：要强制执行的内存顺序约束

##### 3.3.3.2.4 取值运算符(operator T)

```CPP
operator T() const noexcept;
```

其功能为原子地加载并返回原子变量的当前值，等价于调用 `load` 函数。

##### 3.3.3.2.5 原子地取值(load)

```CPP
T load(std::memory_order order = std::memory_order_seq_cst) const noexcept;
```


##### 3.3.3.2.6 赋予新值并取出旧值(exchange)

```CPP
T exchange(T desired, std::memory_order order =
                           std::memory_order_seq_cst) noexcept;
T exchange(T desired, std::memory_order order =
                           std::memory_order_seq_cst) volatile noexcept;
```

该函数会给原子变量赋予新值并取出旧值
其参数：
- `T desired` ：要存入的非原子变量类型的值
- `std::memory_order order` ：要强制执行的内存顺序约束
返回值：
- 调用前原子变量的值

##### 3.3.3.2.7 条件睡眠(wait)(C++20)

```CPP
void wait(T old, std::memory_order order =
                      std::memory_order_seq_cst) const noexcept;
void wait(T old,
           std::memory_order order =
               std::memory_order_seq_cst) const volatile noexcept;
```

该函数会阻塞，并当满足条件或被唤醒时解除睡眠
其参数：
- `T old` ：要比较的参数。
	- 当条件变量当前值与 `old` <font color="#c00000">相等时则睡眠</font>，<font color="#c00000">否则</font><span style="background:#fff88f"><font color="#c00000">直接结束</font></span>
	- <font color="#c00000">其比较是按位进行的</font>，类似于 `memcmp` 
- `std::memory_order order` ：要强制执行的内存顺序约束

##### 3.3.3.2.8 唤醒一个睡眠线程(notify_one)(C++20)




##### 3.3.3.2.9 唤醒所有睡眠线程(notify_all)(C++20)




### 3.3.4 标准线程(std::thread、std::jthread)

C++中提供了两种线程对象：
- `std::thread` ：普通线程
- `std::jthread` ：自带收尾机制、在某些情况下可以被取消/停止的线程
上述两种对象均使用头文件 `<thread>`

#### 3.3.4.1 std::thread(C++11)

与其他语言/框架一致的是，其有如下的基本特性：
- 创建线程后会立即执行
- 若线程句柄被析构时，线程仍在运行且句柄未分离(即 `joinable` 为 `true` )，则会触发异常。对应的处理方式为：
	- 调用 `join` 可以等待子线程退出，退出后可析构线程句柄
	- 调用 `detach` 可以分离其与父线程之间的关联，此时析构线程句柄是安全的

##### 3.3.4.1.1 构造函数

###### 3.3.4.1.1.1 创建一个不表示任何线程的thread对象

```CPP
thread() noexcept;
```

###### 3.3.4.1.1.2 移动构造函数

```CPP
thread( thread&& other ) noexcept;
```

###### 3.3.4.1.1.3 创建线程并传递参数

```CPP
template< class F, class... Args >
explicit thread( F&& f, Args&&... args );
```

##### 3.3.4.1.2 阻塞等待指定线程执行完毕(join)

```CPP
void join();
```

调用前需要确保该线程可被 `join`，否则会抛出异常。
`join` 后其 `joinable` 为 `false` (即只能被 `join` 一次)。

##### 3.3.4.1.3 分离指定线程(detach)

```CPP
void detach();
```

分离指定线程，分离后其 `joinable` 为 `false` 。

#### 3.3.4.2 std::jthread(C++20)

考虑如下的场景：
- 主线程中实现UI交互，并创建若干子线程执行子任务
- 主线程会响应来自UI的退出程序命令，主线程需要：
	1. 通过条件变量或原子变量通知子任务结束
	2. 等待所有子任务结束后才能安全退出程序

因此 `std::jthread` 就提供了如下的停止机制：
- `std::jthread` <font color="#c00000">可通过其提供的</font> `std::stop_token` <font color="#c00000">检测是否请求退出</font>
- 在线程句柄被析构时，线程仍在运行且句柄未分离(即 `joinable` 为 `true` )，则：
	- `std::thread` 会直接 `std::terminate()` 并触发异常
	- `std::jthread` 会先 `request_stop()` ，随后自动 `join()`

应当注意：
1. <font color="#c00000">线程函数</font><span style="background:#fff88f"><font color="#c00000">应当</font></span><font color="#c00000">检测</font> `std::stop_token` ，<font color="#c00000">否则在</font> `jthread` <font color="#c00000">析构时可能死锁</font>

其相较于 `std::thread` 多出的特性如子章节所示。

##### 3.3.4.2.1 构造函数

`std::jthread` 的构造函数定义与 `std::thread` 定义一致，但是<font color="#c00000">只要当线程函数的第一个参数为</font> `std::stop_token` ， `std::jthread` <font color="#c00000">就会自动把内部的</font> `token` <font color="#c00000">注入进去</font>。

demo：
1. 如果第一个参数为 `std::stop_token` 就会自动注入：
```CPP
void func(std::stop_token st, int x);
jthread t(func, 10);                  // 自动注入token
```
2. 不为 `std::stop_token` 时也正常传参即可：
```CPP
void func(int x);
jthread t(func, 10);                  // 不会注入token
```
3. 线程函数中可直接判断 `std::stop_token` 并退出：
```CPP
void func(std::stop_token stoken, int id) 
{ 
	while (!stoken.stop_requested())
	{
		// do sth.
	}
}
```

### 3.3.5 错误码(std::error_code)(C++11)

在C++11之前，标准提供的错误机制主要有如下两种：
1. 全局的 `errno` ，是全局变量，线程不安全
2. `exception` 机制，性能开销大，部分环境禁用

因此C++11引入了轻量化的错误码机制，相较于 `int` 类型错误码，其有如下的额外特性：
1. `int` 类型错误码不具有统一的语义，例如同样是 `-1` ，其在不同的库中含义不同
2. `std::error_code` 可以携带错误信息字符串
3. `std::error_code` 可以携带域信息，标明错误是源自操作系统、HTTP库或者其他的库

#### 3.3.5.1 发送者构造方法

对于错误发送者，可直接使用构造函数构造并返回，但其要求<font color="#c00000">已拥有</font>或<font color="#c00000">已完成</font>：
1. 错误类别(域信息)的构造
2. 错误枚举及错误信息的构造
随后即可使用构造函数进行构造：

```CPP
error_code() noexcept;
error_code(int ec, const error_category& ecat) noexcept;
template<class ErrorCodeEnum> error_code(ErrorCodeEnum e) noexcept;
error_code(const error_code& other) = default;
error_code(error_code&& other) = default;
```

其中：
- `error_category` 为错误类别对象，其要继承自 `std::error_category`
- `ErrorCodeEnum` 为可转换为 `std::error_code` 的错误码

而错误类别、错误枚举及错误信息的构造步骤为：
1. 定义错误枚举：
```CPP
// capture_errors.hpp
enum class CaptureError {
    Success = 0,
    DeviceBusy,
    CameraDisconnected,
    DecodeFailed
};
```
2. 向STL告知 `CaptureError` 可以转换为 `std::error_code`
```CPP
// capture_errors.hpp
namespace std {
    template <>
    struct is_error_code_enum<CaptureError> : true_type {};
}
```
3. 定义错误类别，继承自 `std::error_category` ，并设置错误信息
```CPP
// capture_errors.hpp
class CaptureCategory : public std::error_category {
public:
    const char* name() const noexcept override {
        return "MasqueCapture"; // 错误类别的名字
    }

    std::string message(int ev) const override {
        switch (static_cast<CaptureError>(ev)) {
            case CaptureError::Success: return "Success";
            case CaptureError::DeviceBusy: return "Device is busy";
            case CaptureError::CameraDisconnected: return "Camera disconnected";
            case CaptureError::DecodeFailed: return "Frame decode failed";
            default: return "Unknown capture error";
        }
    }
};


```
4. 为错误类别构造全局单例
```CPP
// capture_errors.hpp
// 全局单例，保证 Category 地址唯一
const std::error_category& capture_category() {
    static CaptureCategory instance;
    return instance;
}
```
5. (可选)重载 `make_error_code` 方便使用
```CPP
// capture_errors.hpp
inline std::error_code make_error_code(CaptureError e) {
    return std::error_code(static_cast<int>(e), capture_category());
}
```

#### 3.3.5.2 接收者使用方法

对于错误接收者，其基本用法有：
1. 判断是否有错：
```CPP
// 直接使用重载的 bool 转换
if (ec) { ... }
```
2. 直接获取错误信息：
```CPP
cout << ec.message()
```
3. 比较是不是特定错误：
```CPP
// 判断是不是标准错误码中的参数错误
if(ec == std::errc::invalid_argument) ...
```
4. 获取错误码值和其所属类别：
```CPP
cout << "Value: " << ec.value() << ", Category: " << ec.category().name()
```

## 3.4 新增关键字

### 3.4.1 namespace

如其字面意思， `namespace` 主要用于划定命名空间，给其限定的函数、类、变量、枚举、模板等提供作用域，从而<font color="#c00000">避免命名冲突</font>。

#### 3.4.1.1 基本使用方式

`namespace` 可以用于限定函数、类等特性，其基本使用方式为：

```cpp
namespace mylib {
void log(const char*);
}

int main(int argc, char **argv)
{
	mylib::log("hello, world");
	return 0;
}
```

其有如下的拓展特性：
1. 可合并特性：在多处使用同一个 `namespace` 划分的同名空间会被自动合并。

```C
// foo.h
namespace proj {
struct Image {};
void process(Image&);
}

// foo.cpp
namespace proj {
void process(Image&) { /* ... */ }
}
```

2. 可嵌套特性：

```cpp
// 基础写法
namespace api {
namespace v2 {
void foo();
}

namespace v1 {
void foo();
}
}

// C++17之后还可以简写为
namespace api::v2 {
void foo();
}

// 使用时逐级引用即可
api::v2::foo();
```

3. 命名空间别名：

```cpp
namespace fs = std::filesystem; // 简化长路径
```

#### 3.4.1.2 命名空间的导入与全局命名空间

命名空间的导入可直接参考如下方式：

```cpp
// 导入整个命名空间
using namespace std;

// 导入部分命名空间
// 当导入子命名空间时，后续调用仍然需要 sub_namespace::func1()
using proj::sub_namespace;
// 不可以省略子命名空间
func1();             // 错误，仍然需要 sub_namespace::func1()

// 当导入的是命名空间成员时，可以直接调用对应成员
using proj::func2;
// 可以直接调用func
func2();             // 正确
```

需要注意：
1. <span style="background:#fff88f"><font color="#c00000">禁止在头文件中直接使用</font></span> `using namespace xxx;` <span style="background:#fff88f"><font color="#c00000">导入命名空间</font></span>，头文件在编译时会直接或间接的包含到众多的源文件中，从而污染命名空间。

而对于没有添加命名空间的对象，<span style="background:#fff88f"><font color="#c00000">其默认位于全局命名空间中</font></span>。
<font color="#c00000">当发生命名空间冲突时</font>(例如全局命名空间和 `std` 均有函数 `abs` )，<font color="#c00000">可使用</font> `::target` <font color="#c00000">来指定使用全局命名空间</font>

```cpp
void func()
{
	using namespace std;
	
	abs(-11);   // 直接使用 abs() 则默认调用 std::abs()
	::abs(-11); // 指定使用全局命名空间的 abs()
}
```

#### 3.4.1.3 匿名命名空间

其主要用于替代C语言里面的 `static` 写法。
当使用不包含名称的 `namespace` 时，该命名空间会被视作匿名命名空间，其作用是<span style="background:#fff88f"><font color="#c00000">当前作用域内可见</font></span>。

1. 若匿名命名空间直接位于 `curr.cpp` 文件中：

```cpp
namespace {
void func() { } // 则仅当前 curr.cpp可见，相当于直接定义 static void func(){ }
}
```

2. 若匿名命名空间位于父 `namespace` 中：

```cpp
namespace api {
namespace {
void helper() { } // 则整个namespace api中可见
}
}
```

注意：
1. <font color="#c00000">匿名命名空间不可放于头文件中</font>，<span style="background:#fff88f"><font color="#c00000">否则每个包含该头文件的源文件均会生成一份实体</font></span>。(类似于 `static` )。

#### 3.4.1.4 内联命名空间

内联命名空间可将子命名空间自动提升为外层可见，方便用于版本管理和ABI过渡：

```cpp
namespace api {
inline namespace v2 {  // 外部可见为 api::*
void foo();          // 等价于 api::foo()
}

namespace v1 {
void foo();
}
}

api::foo();            // 自动调用api::v2::foo();
```

### 3.4.2 explicit 强制显式转换 ^6nhi9i

对于没有使用 `explicit` 修饰的类，若其存在<font color="#c00000">只有一个</font><span style="background:#fff88f"><font color="#c00000">非</font></span><font color="#c00000">默认参数</font>的构造函数时，那么该类就允许<font color="#c00000">由一个非默认参数的变量隐式转换为该类</font>。

<font color="#c00000">该关键字只在声明处使用</font>。

例如：

```CPP
class MyClass {
public:
	// 允许隐式转换
    MyClass(int value)
    {
        // 构造函数实现
        ...
    }
};

void process(MyClass obj) {
    // 处理对象
}

int main()
{
	// 隐式转换: int -> MyClass
    MyClass obj1 = 42;
    // 在函数参数传递中也可以隐式转换
    process(42);
    // 当然也可以使用显式转换
    // MyClass obj2(42); // 合法但不建议
    MyClass obj2{ 42 };  // 建议使用初始化列表方式避免起义
}
```

当使用 `explicit` 修饰后：

```CPP
class MyClass {
public:
	// 不允许隐式转换
    explicit MyClass(int value)
    {
        // 构造函数实现
        ...
    }
};

void process(MyClass obj) {
    // 处理对象
}

int main()
{
	// 非法，编译时报错
    MyClass obj1 = 42;
    // 非法，编译时报错
    process(42);
    // 此时只可使用显式转换
    // MyClass obj2(42); // 合法但不建议
    MyClass obj2{ 42 };  // 建议使用初始化列表方式避免起义
}
```

### 3.4.3 constexpr 编译期求值

`constexpr` 关键字用于指定<font color="#c00000">变量或函数</font>使其在<font color="#c00000">编译期完成求值</font>，其有如下特性：
- `constexpr` 修饰<font color="#c00000">常量</font>，<font color="#c00000">常量</font>在编译期完成求值
- `constexpr` 修饰函数，会<span style="background:#fff88f"><font color="#c00000">尝试</font></span>在编译期求值(也可能推迟到运行时)
- `constexpr` 修饰构造函数，会在编译期构造<font color="#c00000">常量</font>对象
需要注意：
- `constexpr` <span style="background:#fff88f"><font color="#c00000">仅</font></span><font color="#c00000">在修饰函数时</font>可能会延后到运行时求值，其他两种情况均<span style="background:#fff88f"><font color="#c00000">一定在编译期求值</font></span>。
- `constexpr` 修饰函数时，<span style="background:#fff88f"><font color="#c00000">必须在声明处使用</font></span>，不过通常推荐声明和定义写在一起。

#### 3.4.3.1 constexpr 常量

`constexpr` 会在编译期确定常量的值，其与 ` const ` 常量的区别：

```cpp
const int runtime_const = get_value(); // 运行时求值的常量
constexpr int compile_const = 42;      // 编译时求值的常量

int array1[runtime_const];             // 错误，C++不支持VLA
int array2[compile_const];             // 正确，编译期已经求值
```

#### 3.4.3.2 constexpr 函数

`constexpr` 修饰函数后，编译器会<span style="background:#fff88f"><font color="#c00000">尝试</font></span>对该函数在编译期求值：
- 若输入的参数为常量，则编译期会完成求值
- 若输入的参数是运行时变量，则求值会被推迟到运行时
因此，`constexpr` 函数的返回值在编译期可求值时具有 `constexpr` 常量的特性，但当不可求值时，会回退到普通函数。

```cpp
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}

// 输出常量时
int array[factorial(5)];              // 正确：编译时已知大小
// 输入运行时变量时
int array[factorial(var)];            // 错误：编译期无法完成求值
```

此外，在C++11中，限制函数只能有一个 `return` 语句；而在C++14后放宽了该限制。

```cpp
// C++11 约束较多
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);  // 只能有一条return语句
}

// C++14 放宽限制
constexpr int fibonacci(int n) {
    if (n <= 1) return n;
    
    int a = 0, b = 1;
    for (int i = 2; i <= n; ++i) {
        int next = a + b;
        a = b;
        b = next;
    }
    return b;
}

constexpr int fact_5 = factorial(5);  // 编译时计算：120
constexpr int fib_10 = fibonacci(10); // 编译时计算：55
```

#### 3.4.3.3 constexpr 构造函数

`constexpr` 构造函数可以在编译期构造<font color="#c00000">常量</font>对象


### 3.4.4 consteval 

### 3.4.5 using

在C++中，`using` 主要有如下的用法：
1. 命名空间引入
2. 提供类别别名(现代版的 `typedef` )
3. 类继承中的成员引入
4. 使用枚举

#### 3.4.5.1 命名空间引入

using引入命名空间时，有如下两种的引入方式：
1. 引入整个命名空间(即 `using namespace std;` )
2. 引入特定成员，例如 `using namespace std::string` ，随后即可使用 `string`
通常来说更推荐第二种引入方式

#### 3.4.5.2 提供类别别名

```CPP
using xxCallback = std::function<void(const xx&)>;
```

#### 3.4.5.3 类继承中的成员引入

类继承中的成员引入可以用于<font color="#c00000">重写部分成员</font>和<font color="#c00000">修改成员权限</font>，具体可见章节[[CPP/C2CPP/C2CPP#^464qd9|成员引入]]与[[CPP/C2CPP/C2CPP#^cvt59v|成员权限修改]]：
![[CPP/C2CPP/C2CPP#3 1  3 4 成员引入 using 464qd9]]
![[CPP/C2CPP/C2CPP#3 1 3 5 成员权限修改 using cvt59v]]

#### 3.4.5.4 简化枚举类(C++20)

在C++20之前，当使用枚举类时(`enum class`)，必须为预定义的枚举添加类名：

```CPP
enum class Color { Red, Green, Blue };

void paint() {
    // 在C++20之前，必须为预定义的枚举 `Red` 前添加类名 `Color`
    Color c = Color::Red;
    
    // C++20之后，可以使用using enum来简化枚举类的使用
    using enum Color;
    Color c = Red; // 可以直接写 Red
}
```

### 3.4.6 函数关键字汇总及要求

在C++中，函数关键字主要可以分为前置关键字和后置关键字。

$$
\underbrace{\text{template <...>}}_{\text{声明定义皆有}} 
\quad
\underbrace{\text{static/virtual/explicit}}_{\text{仅声明}} 
\quad
\text{ReturnType} 
\quad
\text{FuncName}(\text{Params}) 
\quad
\underbrace{\text{const}}_{\text{声明定义皆有}} 
\quad
\underbrace{\text{volatile}}_{\text{声明定义皆有}} 
\quad
\underbrace{\&/\&\&}_{\text{声明定义皆有}} 
\quad
\underbrace{\text{noexcept}}_{\text{声明定义皆有}} 
\quad
\underbrace{\text{override/final}}_{\text{仅声明}} 
\quad
\underbrace{=0}_{\text{仅声明}}
$$

#### 3.4.6.1 前置关键字

前置关键字需要放到函数的返回值类型之前，<font color="#c00000">用于修饰函数本身的性质</font>(储存方式、链接属性、构造规则等)

| 关键字         | 作用分类   |  必须写在哪里？   | <center>核心含义</center>              |
| ----------- | ------ | :--------: | ---------------------------------- |
| `static`    | 存储/作用域 |    只在声明    | **静态成员**：函数属于类，不属于对象(无 `this` 指针)。 |
| `virtual`   | 多态     |    只在声明    | **虚函数**：开启动态绑定，允许子类覆盖。             |
| `explicit`  | 构造规则   |    只在声明    | **显式**：禁止构造函数或转换运算符发生隐式类型转换。       |
| `friend`    | 权限     |    只在声明    | **友元**：这不是成员函数，但允许它访问类的私有成员。       |
| `inline`    | 编译建议   |   建议两边都写   | **内联**：建议编译器把函数体展开，通常定义在头文件中。      |
| `constexpr` | 编译期计算  | 声明+定义(头文件) | **常量表达式**：函数可以在编译期执行。              |
| `consteval` | 编译期计算  | 声明+定义(头文件) | **强制编译期**：C++20引入，函数**必须**在编译期执行。  |
| `template`  | 泛型     | 声明+定义(头文件) | **模板**：定义泛型函数。                     |

#### 3.4.6.2 后置关键字

后置关键字放置于函数的参数列表 `(...)` 之后，通常用于：
- 修饰隐含的 `this` 指针
- 修饰函数的异常行为
- 修饰继承关系

| 关键字        | 作用分类      |              必须写在哪里？               | <center>核心含义</center>                       |
| ---------- | --------- | :--------------------------------: | ------------------------------------------- |
| `const`    | `this` 指针 | <font color="#c00000">声明+定义</font> | **只读**：承诺函数内部不会修改成员变量。`this` 变成 `const T*`。 |
| `override` | 继承检查      |                只在声明                | **覆盖**：检查父类是否有对应的虚函数。                       |
| `final`    | 继承控制      |                只在声明                | **绝育**：禁止子类继续重写该虚函数。                        |
| `noexcept` | 异常        | <font color="#c00000">声明+定义</font> | **不抛异常**：函数签名的一部分，承诺不抛出异常。                  |
| `volatile` | `this` 指针 | <font color="#c00000">声明+定义</font> | **易变**：极少用。允许 `volatile` 对象调用此函数。           |
| `&` / `&&` | 引用限定符     | <font color="#c00000">声明+定义</font> | **C++11新特性**：限制函数只能被左值对象(`&`)或右值对象(`&&`)调用。 |
| `= 0`      | 纯虚函数      |                只在声明                | **纯虚**：没有实现，类变为抽象类。                         |

## 3.5 C++不支持的C语言特性

### 3.5.1 VLA可变长数组

在C99之后，C语言就支持了可变长数组，但是无论哪个C++标准均不支持可变长数组。




# 4 STL

STL全名为Standard Template Library，意为标准模板库或泛型库，是C++中的一个重要组件。其主要包含如下组件：
- 容器(Containers)
- 算法(Algorithms)
- 迭代器(iterators)
- 函数对象(Function Objects)
- 适配器(Adapters)

## 4.1 迭代器

迭代器是C++用于统一迭代(遍历)访问容器的一种对象，通过该对象可以让用户访问容器而不关心内部实现。

其被定义为模板结构体：

```CPP
template<
    class Category,
    class T,
    class Distance = std::ptrdiff_t,
    class Pointer = T*,
    class Reference = T&
> struct iterator;
```

其中：
- `Category` ：为[[C2CPP#^jhkiyp|迭代器类别]]，定义了迭代器拥有的基本特性。
- `T` ：为可以通过解引用获得的值的类型
- `Distance` ：用于标识迭代器距离的类型，通常是有符号的整数类型，如 `long` 或 `long long` 。
	- 两个迭代器相减，其返回值类型为 `Distance` 
	- C++17中已弃用。
- `Pointer` ：定义指向元素的指针的类型，默认填充为 `T*`
- `Reference` ：定义指向元素的引用的类型，默认填充为 `T&`

### 4.1.1 从容器中获取迭代器

通常来说容器都会提供如下几个迭代器：
- `.begin()` ：返回指向首元素的迭代器
- `.end()` ：返回指向尾元素<font color="#c00000">下一个位置</font>的迭代器
- 
	![[Pasted image 20250722135056.png]]

那么明显的有如下特性：
1. 容器元素数量： `x.end() - x.begin()`


### 4.1.2 迭代器类别 ^jhkiyp

标准库定义了如下的迭代器类别：
- `input_iterator_tag` ：输入迭代器
- `output_iterator_tag` ：输出迭代器
- `forward_iterator_tag` ：前向迭代器
- `bidirectional_iterator_tag` ：双向迭代器
- `random_access_iterator_tag` ：随机访问迭代器
- `contiguous_iterator_tag` ：连续迭代器(C++20起)

### 4.1.3 迭代器的基本操作

|        操作         | 输入  | 输出  | 前向  | 双向  | 随机访问 | 连续  |
| :---------------: | :-: | :-: | :-: | :-: | :--: | :-: |
|       默认构造        |  是  |  是  |  是  |  是  |  是   |  是  |
|   拷贝构造、拷贝赋值和析构    |  是  |  是  |  是  |  是  |  是   |  是  |
|    `it == it2`    |  是  |     |  是  |  是  |  是   |  是  |
|    `it != it2`    |  是  |     |  是  |  是  |  是   |  是  |
|     `*it` (读)     |  是  |     |  是  |  是  |  是   |  是  |
| `*it = value` (写) |     |  是  |  是  |  是  |  是   |  是  |
|   `it->member`    |  是  |     |  是  |  是  |  是   |  是  |
|    `++it` （前置）    |  是  |  是  |  是  |  是  |  是   |  是  |
|    `it++` （后置）    |  是  |  是  |  是  |  是  |  是   |  是  |
|    `--it` （前置）    |     |     |     |  是  |  是   |  是  |
|    `it--` （后置）    |     |     |     |  是  |  是   |  是  |
|     `it + n`      |     |     |     |     |  是   |  是  |
|     `n + it`      |     |     |     |     |  是   |  是  |
|     `it - n`      |     |     |     |     |  是   |  是  |
|     `it += n`     |     |     |     |     |  是   |  是  |
|     `it -= n`     |     |     |     |     |  是   |  是  |
| `it - it2` (返回距离) |     |     |     |     |  是   |  是  |
|      `it[n]`      |     |     |     |     |  是   |  是  |
|    `it < it2`     |     |     |     |     |  是   |  是  |
|    `it <= it2`    |     |     |     |     |  是   |  是  |
|    `it > it2`     |     |     |     |     |  是   |  是  |
|    `it >= it2`    |     |     |     |     |  是   |  是  |

## 4.2 容器

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

<span style="background:#fff88f"><font color="#c00000">其常用成员函数有</font></span>：
- 元素增加：
	- `insert()` ：插入元素
	- `insert_range()` 
	- `emplace()` ：就地构造并插入
	- `push_back()` ：在末尾添加
	- `emplace_back()` ：在末尾构造并插入
	- `append_range()` 
	- 
- 元素删除：
	- `erase()` ：删除元素
	- `pop_back()` ：删除末尾元素
- 元素修改：
	- `operator[]` ：访问指定元素
- 元素访问：
	- `at()` ：访问指定元素，带边界检查
	- `operator[]` ：访问指定元素
	- `find()` ：查找指定元素(通常返回元素的迭代器)
	- `front()` ：访问第一个元素
	- `back()` ：访问最后一个元素
	- `count()` ：统计指定元素数量
- 容器修改：
	- `clear()` ：清空容器
	- `resize()` ：修改容器大小
		- 若元素数量大于目标容器大小，则删除后续元素并缩小
		- 若元素数量小于目标容器大小，则填充默认值或指定值
	- `swap()` 
	- `operator=` ：容器赋值
	- `assign()` ：为容器批量赋值
	- `assign_range()` 
	- 
- 容器容量：
	- `empty()` ：判断是否为空
	- `size()` ：返回元素成员数量
	- `max_size()` ：返回最大的可能成员数量
	- `reserve()` ：预留存储空间
	- `capacity()` ：返回当前已分配空间中可以容纳的元素数量
	- `shrink_to_fit()` ：通过释放未使用的内存来减少内存占用
- 容器访问：
	- `data()` ：直接访问底层的数据存储的连续区域
- operators：
	- `operator[]` ：访问指定元素
	- 
- 迭代器：
	- `begin()` ：获取指向开始的迭代器
	- `end()` ：获取指向末尾的下一个元素的迭代器
- 


### 4.2.1 std::initializer_list

<font color="#9bbb59">初始化列表</font>( `initializer_list` )是一个轻量化的<span style="background:#fff88f"><font color="#c00000">只读容器</font></span>，<font color="#c00000">通常其只能通过特殊的构造函数构造</font>。
需注意的是，<font color="#9bbb59">初始化列表</font>和构造函数的<font color="#9bbb59">成员初始化列表</font>是不同的概念。

#### 4.2.1.1 模板定义

```CPP
template< class T >
class initializer_list;
```

#### 4.2.1.2 常用构造函数

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

#### 4.2.1.3 常用方法

##### 4.2.1.3.1 查询元素数量(size)

```CPP
size_type size() const noexcept;
```

其实际上返回的是表达式 `std::distance(begin(), end())` 的值，类型为 `std::size_t` 。

##### 4.2.1.3.2 迭代器(begin、end)

```CPP
const T* begin() const noexcept;
const T* end() const noexcept;
```

### 4.2.2 std::basic_string

`std::basic_string` 为C++为若干种字符串类型(`char` 、 `wchar_t` 、`char32_t` 等)提供的统一容器，用于适配不同的字符串及编码类型。

#### 4.2.2.1 模板定义

```CPP
template<
    class CharT,
    class Traits = std::char_traits<CharT>,
    class Allocator = std::allocator<CharT>
> class basic_string;
```

基于上述模板，各字符串类型及类定义如下：

| 字符串类型            | <center>类定义</center>          |
| ---------------- | ----------------------------- |
| `std::string`    | `std::basic_string<char>`     |
| `std::u8string`  | `std::basic_string<char8_t>`  |
| `std::u16string` | `std::basic_string<char16_t>` |
| `std::u32string` | `std::basic_string<char32_t>` |
| `std::wstring`   | `std::basic_string<wchar_t>`  |

#### 4.2.2.2 常用方法

##### 4.2.2.2.1 插入字符(insert)

插入多个指定字符：

```CPP
basic_string& insert( size_type index, size_type count, CharT ch );
```

插入字符串：
```CPP
// 插入的指针指向的字符串必须以结束符结尾
basic_string& insert( size_type index, const CharT* s );
// 插入指向字符串的至多count个字符
basic_string& insert( size_type index, const CharT* s, size_type count );
// 插入字符串对象
basic_string& insert( size_type index, const basic_string& str );
```

插入字符串的字串：

```CPP
basic_string& insert( size_type index, const basic_string& str,
                      size_type s_index, size_type count = npos );
```

在迭代器前插入字符：

```CPP
iterator insert( const_iterator pos, CharT ch );
```

在迭代器前插入若干个指定字符：

```CPP
iterator insert( const_iterator pos, size_type count, CharT ch );
```

通过迭代器插入字符：

```CPP
template< class InputIt >
iterator insert( const_iterator pos, InputIt first, InputIt last );
```

在迭代器前插入由初始化列表构成的字符：

```CPP
iterator insert( const_iterator pos, std::initializer_list<CharT> ilist );
```

插入并转换为字符串视图(`StringViewLike`)：

```CPP
template< class StringViewLike >
basic_string& insert( size_type index, const StringViewLike& t );

template< class StringViewLike >
basic_string& insert( size_type index, const StringViewLike& t,
                      size_type t_index, size_type count = npos );
```

##### 4.2.2.2.2 删除字符(erase)

从指定引索开始删除至多指定数量的字符：

```CPP
basic_string& erase( size_type index = 0, size_type count = npos );
```

移除迭代器指向的字符：

```CPP
// 如果 `position` 非可解引用的迭代器，则行为未定义
iterator erase( const_iterator position );
```

删除两个迭代器范围内的字符(不含 `last` )：

```CPP
// 删除[first, last)范围内的字符，若区间无效则行为未定义
iterator erase( const_iterator first, const_iterator last );
```

##### 4.2.2.2.3 查询/修改元素(operator\[\])

通过index获取字符：

```CPP
CharT& operator[]( size_type pos );
const CharT& operator[]( size_type pos ) const;
```

##### 4.2.2.2.4 访问指定位置的字符(at)

##### 4.2.2.2.5 查找字符串或字符(find)

从指定位置开始查找子字符串：

```CPP
// 从pos开始搜索子字符串
size_type find( const basic_string& str, size_type pos = 0 ) const;

// 查找C类型指针字符串
size_type find( const CharT* s, size_type pos, size_type count ) const;
size_type find( const CharT* s, size_type pos = 0 ) const;
```

查找字符：

```CPP
size_type find( CharT ch, size_type pos = 0 ) const;
```

查找字符串视图：

```CPP
template< class StringViewLike >
size_type find( const StringViewLike& t,
                size_type pos = 0 ) const noexcept(/* see below */);
```

##### 4.2.2.2.6 获取c语言字符串版本指针(c_str)

```CPP
const CharT* c_str() const;
```

其返回的指针：
1. 在 `[c_str(), c_str() + size()]` 的范围内有效
2. 在原字符串容量被修改前有效
3. <font color="#c00000">不可通过该指针写入数据</font>(UB)

##### 4.2.2.2.7 清空字符串(clear)



##### 4.2.2.2.8 替换子字符串(replace)

需要注意，`replace` 是用于将字符串的指定区间替换为另一个字符串，而非字符或子字符串的匹配替换(该方法为 `std::replace` )。

下列所有函数可以理解为：
- 位置引索版本将原字符串拆为：
	- `[0, pos)` 
	- `[pos, pos + count)`
	- `[pos + count, size())` 
	三部分，
- 迭代器版本将字符串拆分为：
	- `[begin(), first)`
	- `[first, last)`
	- `[last, end())`
<font color="#c00000">然后将第一部分、目标字符串、第三部分按顺序拼接为新串</font>(<font color="#c00000">第二部分被丢弃</font>)。也就是说无论 `size()` 或 `last - first` 与 `str.size()` 的关系，其都会如此拼接。
上述区间均为左闭右开。

```CPP
// 替换为指定字符串
basic_string& replace( size_type pos, size_type count,
                       const basic_string& str );
basic_string& replace( const_iterator first, const_iterator last,
                       const basic_string& str );                     

// 替换为指定字符串的指定区域(左闭右开)
basic_string& replace( size_type pos, size_type count,
                       const basic_string& str,
                       size_type pos2, size_type count2 = npos );

// 替换为C语言风格的指针形式字符串
basic_string& replace( size_type pos, size_type count,
                       const CharT* cstr, size_type count2 );
basic_string& replace( const_iterator first, const_iterator last,
                       const CharT* cstr, size_type count2 );
basic_string& replace( size_type pos, size_type count,
                       const CharT* cstr );
basic_string& replace( const_iterator first, const_iterator last,
                       const CharT* cstr );

// 替换为 `count2` 个 `ch` 字符副本构成的字符串
basic_string& replace( size_type pos, size_type count,
                       size_type count2, CharT ch );                      
basic_string& replace( const_iterator first, const_iterator last,
                       size_type count2, CharT ch );

// 替换为迭代器中指向的字符串
template< class InputIt >
basic_string& replace( const_iterator first, const_iterator last,
                       InputIt first2, InputIt last2 );

// 替换为初始化列表中的字符
basic_string& replace( const_iterator first, const_iterator last,
                       std::initializer_list<CharT> ilist );

// 替换为字符串视图中的字符串
template< class StringViewLike >
basic_string& replace( size_type pos, size_type count,
                       const StringViewLike& t );
template< class StringViewLike >
basic_string& replace( const_iterator first, const_iterator last,
                       const StringViewLike& t );
template< class StringViewLike >
basic_string& replace( size_type pos, size_type count,
                       const StringViewLike& t,
                       size_type pos2, size_type count2 = npos );
```




#### 4.2.2.3 基本特性

##### 4.2.2.3.1 sizeof(string)

在x86架构下，`sizeof(std::string) = 28`；
在x86_64架构下，`sizeof(std::string) = 40`；
而 `sizeof(std::string)` 的值<u><font color="#c00000">不随字符串内容发生改变</font></u>。
##### 4.2.2.3.2 string作为struct的成员时

string可以作为struct的成员，其size计算符合内存对齐等要求。


### 4.2.3 array

### 4.2.4 vector

`std::vector` 是C++的动态大小的数组实现，其元素被顺序存储，因此其可以被迭代器和引索顺序访问。其会自动扩展其所需要的内存空间，并且通常其所占用的内存比同大小的静态数组要多。其空间的动态分配仅会发生在其所保留的额外空间耗尽时触发。

#### 4.2.4.1 模板定义

```CPP
template<
    class T,
    class Allocator = std::allocator<T>
> class vector;
```


<font color="#c00000">vector中的模板类型需要满足如下要求</font>：
- 可以拷贝赋值
- 可以拷贝构造

但是需要注意<span style="background:#fff88f"><font color="#c00000">慎用bool类型作为vector的元素</font></span>，除非明确地要使用 `vector<bool>` 的特性。

#### 4.2.4.2 常用方法


##### 4.2.4.2.1 构造函数

###### 4.2.4.2.1.1 创建包含n个指定默认元素的vector

```CPP
explicit vector( size_type count,
                 const Allocator& alloc = Allocator() );
```

###### 4.2.4.2.1.2 创建包含n个指定值的vector

```CPP
vector( size_type count, const T& value,
        const Allocator& alloc = Allocator() );
```

###### 4.2.4.2.1.3 由输入迭代器构造vector

```C
template< class InputIt >
vector( InputIt first, InputIt last,
        const Allocator& alloc = Allocator() );
```




##### 4.2.4.2.2 迭代器

`vector` 返回的迭代器为随机访问迭代器，可通过 `.begin()` 、 `.end()` 获取。

### 4.2.5 std::unordered_map

`std::unordered_map` <font color="#c00000">基于哈希表实现</font>，内部元素无序存储。

#### 4.2.5.1 模板定义

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

#### 4.2.5.2 常用方法

##### 4.2.5.2.1 构造函数

```CPP
unordered_map();
```

其定义了如下的成员：
- `key_type` ：即 `class Key` ，键类型
- `mapped_type` ：即 `class T` ，值类型
- `value_type` ：`std::pair<const Key, T>` ^o36e6j 

##### 4.2.5.2.2 清空容器(clear)

```CPP
void clear() noexcept;
```

##### 4.2.5.2.3 插入元素(insert)

###### 4.2.5.2.3.1 插入单个元素

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

###### 4.2.5.2.3.2 批量插入(通过初始化列表)

```CPP
void insert( std::initializer_list<value_type> ilist );
```

其：
- 参数类型为键值对构成的初始化列表( `{{key1, value1}, {key2, value2}, ...}` )
- 无返回值
- 特性/语义：
	- 若参数中有重复键，则只插入第一个
	- 不会修改已有键值

###### 4.2.5.2.3.3 批量插入(通过迭代器)

```C
template< class InputIt >
void insert( InputIt first, InputIt last );
```



###### 4.2.5.2.3.4 带位置提示的插入

##### 4.2.5.2.4 删除元素(erase)

###### 4.2.5.2.4.1 通过key值删除

```CPP
size_type erase( const Key& key );
```

其中：
- 参数为需要删除的键值对的键
- 返回值为被删除的元素数量，值为0或1

时间复杂度：
- 平均 $O(1)$
- 最坏 $O(size)$

###### 4.2.5.2.4.2 通过迭代器删除单个元素

```CPP
iterator erase( iterator pos );
```

其中：
- 参数:
	- `pos` 为要删除元素的迭代器，<span style="background:#fff88f"><font color="#c00000">且不能为</font></span> `end()` <span style="background:#fff88f"><font color="#c00000">!!!</font></span>
		- 因为<font color="#c00000">只要map不为空</font>，<font color="#c00000">其最后一个元素就不是</font> `end()` ，所以<font color="#c00000">非空时</font>删除最后一个元素应当使用 `map.erase(std::prev(map.end()))`
- 返回值为被删除元素之后元素的迭代器。如果删除的是最后一个元素，则返回 `end()` 。

###### 4.2.5.2.4.3 通过迭代器范围删除元素

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

##### 4.2.5.2.5 查询(at)

###### 4.2.5.2.5.1 普通查找

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

###### 4.2.5.2.5.2 异构查找(C++26)

在普通查找时，其参数只能为Key的类型，而不能是可以和Key透明比较的类型。例如：

```CPP
// C++11 传统方法：有性能损耗
// 创建临时 std::string 对象 → 内存分配 + 复制
int value1 = traditional_map.at("view"); 

// C++26 异构方法：零开销
// 直接使用 string_view 查找 → 无临时对象
int value2 = transparent_map.at(std::string_view("view"));
```

##### 4.2.5.2.6 查询/新增(operator\[\])

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

##### 4.2.5.2.7 查找(find)

`find` 用于查找是否包含对应的键值：

```CPP
iterator find( const Key& key );
const_iterator find( const Key& key ) const;
```

此外C++20开始还有查找可等价比较的元素：

```CPP
template< class K >  
iterator find( const K& x );
template< class K >  
const_iterator find( const K& x ) const;
```

该函数的返回值为指向键值对应的元素的迭代器，若没有该元素则返回 `end()` 迭代器

##### 4.2.5.2.8 查找(count)

`count` 也可用于查找是否存在对应的元素，由于hash表特性，其值只能为0或1。

```CPP
size_type count( const Key& key ) const;
```

C++20开始的查找可等价比较的元素：

```CPP
template< class K >
size_type count( const K& x ) const;
```

##### 4.2.5.2.9 原地插入(emplace)


##### 4.2.5.2.10 迭代器

`unordered_map` 提供了 `.begin()` 和 `.end()` 两个获取迭代器的方法，返回的类型为前向迭代器。

### 4.2.6 std::map

`std::map` 内部通常基于红黑树实现，<font color="#c00000">元素始终按键的升序排序</font>。

### 4.2.7 std::optional(C++17)

`std::optional` 使用头文件 `<optional>`

#### 4.2.7.1 基本使用

`std::optional` 表示是<span style="background:#fff88f"><font color="#c00000">一个可能存在，也可能不存在的值</font></span>。其可以用于如下用途：
1. 函数返回值：表示可能无法返回有效结果的返回值
```CPP
// 当不使用 `std::optional` 时，必须同时从参数和返回值接收查询结果
bool find_item(const Container &c, Item &i) { ... }

// 而使用 `std::optional` 后，可以不再从参数接收结果
std::optional<Item> find_item(const Container &c) { 
	if(success)
		return Item();
	else
		return std::nullopt;
}
```
2. struct成员：表示struct的可选字段
```CPP
struct UserInfo {
    std::string name;           // 必填
    int age;                    // 必填
    std::optional<std::string> nickname; // 选填：用户可能没有昵称
    std::optional<std::string> phone;    // 选填：用户可能没填电话
};
```
3. 延迟初始化：例如有些对象的构造代价可能很大，因此可以先使用 `std::optional` 进行占位

而在使用时，可以使用如下的方法校验其是否包含值：

```CPP
// 使用 `has_value` 方法
if(opt.has_value()) { ... }

// 使用重载的 bool 转换
if(opt) { ... }
```

获取值也有如下的几种方法：
1. (<font color="#c00000">推荐</font>)使用 `opt.value_or(default_val)` ，当没有值时会使用默认值
2. 使用 `opt.value()` ，<font color="#c00000">当没有值时会抛出异常</font>
3. 直接解引用 `value = *opt` ，<font color="#c00000">没有值时行为未定义</font>，但是速度最快

#### 4.2.7.2 内存分配

`std::optional` 是静态分配的内存，位于栈上。

## 4.3 算法

### 4.3.1 排序

#### 4.3.1.1 std::sort(混合排序)

`std::sort` 使用的排序方法会根据需要排序的元素数量动态切换排序方式，是<span style="background:#fff88f"><font color="#c00000">不稳定</font></span><font color="#c00000">排序</font>。其先使用快速排序对数据进行分段，
- 

### 4.3.2 替换

#### 4.3.2.1 std::replace


