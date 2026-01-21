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

## 3.1 面向对象的基础特性

在笔记[[../../面向对象的程序设计/面向对象的程序设计|面向对象的程序设计]]中已经给出若干面向对象的特性，其中学习本章节之前需要提前学习的有：
- 

### 3.1.1 对象的构造

在[[../../面向对象的程序设计/面向对象的程序设计|面向对象的程序设计]]中已经给出了C++对象的若干构造方法。

此外，需要额外说明的有：
1. 当对象在构造过程中，<font color="#c00000">由于异常等构造失败时</font>，<span style="background:#fff88f"><font color="#c00000">析构函数不会被调用</font></span>，先前已经动态申请的对象也不会被释放(需要考虑RAII范式)
2. 在C++中规定：<span style="background:#fff88f"><font color="#c00000">任何可以被解析为函数声明的代码都会被解析为函数声明</font></span>。因此在类的定义中，有如下注意事项：
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

| <center>运算符类别</center> | <center>运算符</center>                                               |
| ---------------------- | ------------------------------------------------------------------ |
| 算数运算符                  | `+` 、 `-` 、 `*` 、 `/` 、 `%` 、`~`                                   |
| 关系运算符                  | `==` 、 `!=` 、 `<` 、 `>` 、 `<=` 、 `>=`                              |
| 逻辑运算符                  | `!` 、`&&` 、`\|\|`                                                  |
| 赋值运算符                  | `=` 、`+=` 、`-=` 、`*=` 、`/=` 、`%=` 、`&=` 、`\|=` 、`^=` 、`<<=` 、`>>=` |
| 位运算符                   |                                                                    |
| 单目运算符                  |                                                                    |
| 自增、自减运算符               | `++` 、`--`                                                         |
| 动态内存操作运算符              |                                                                    |
| 类型转换运算符                | `int`                                                              |
| 其他运算符                  |                                                                    |
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

本质上来讲，引用在C++中<font color="#c00000">也是一种类型</font>(复合类型)。只不过有一些特殊。

### 3.2.1 引用的基本特性

在C++中，引用：
- 在语法上可以简单的理解为给一个<span style="background:#fff88f"><font color="#c00000"><b><u>现有</u>变量</b></font></span>起一个别名。
- 在实际编译中：
	- 通常基于指针进行实现，但是<font color="#c00000"><u>可行时</u></font>会优化为<font color="#c00000">直接操作引用的对象</font>
	- 在<font color="#c00000">函数参数传递时</font>绝大多数编译器的处理方式和指针一致(取地址、传地址、解引用)

引用的基本特性与规定：
- <span style="background:#fff88f"><font color="#c00000"><b>引用的对象不能为空</n></font></span>：值引用时<font color="#c00000">必须指向一个具体的对象</font>，如下的引用是错误的：
	- `int& r;       // 错误!` 
	- `int& r = var; // 正确`
	- 也就是定义引用的同时<font color="#c00000">必须初始化</font>该引用，这也是为什么一开始说是给<span style="background:#fff88f"><font color="#c00000"><b><u>现有</u>变量</b></font></span>起别名
- **不可更改引用的指向**：引用一旦被定义绑定，该引用不可能重新绑定到别的变量上
- **不存在指向非法的引用**(尽管可以恶劣的构造出来)：引用必须指向合法的内存区域

引用相较于指针：
- 引用更加安全：不存在NULL，也不会有野指针
- 引用更加方便：不需要引用和解引用(`&`、`*`、` -> `)

引用与非引用实体之间的赋值：
- 将实体赋值给引用，<font color="#c00000">则引用会指向该实体</font>
- 将引用赋值给实体，<font color="#c00000">则引用的值会</font><span style="background:#fff88f"><font color="#c00000">拷贝</font></span><font color="#c00000">到该实体</font>，常见场景：
	- 返回值类型为引用的函数，赋值给了实体([[CPP/C2CPP/C2CPP#^8eltqy|引用的链式调用]]中，返回值需要规定为引用)

### 3.2.2 引用的特殊特性

除了上述的基本特性以外，引用还有如下复合直觉的特性：
1. 使用类型判定时，引用和原始类型不是同一个类型：
	- `std::is_same<int, int&>` -> `false`
2. 可以使用 `using` 、`typedef` 为引用设置类别别名

<font color="#c00000">但是引用还有如下的反直觉特性</font>：
- 穿透性：
	- 引用在表达式中会"隐身"：
		- 即使是在 `sizeof(Type&)` 时，<font color="#c00000">其获取到的是</font> `Type` <font color="#c00000">的大小</font>，<font color="#c00000">而非指针的大小</font>
	- 获取 `typeid` 时也会"隐身"：
		- `typeid(ref).name()` 时，获取到的是原始类型的名称
- <span style="background:#fff88f"><font color="#c00000">C++中没有二级引用!!!</font></span> 
	- `Type&` 是左值引用
	- `Type&&` <span style="background:#fff88f"><font color="#c00000">是右值引用!!!</font></span> ^ymcr6z
- <font color="#c00000">引用折叠特性</font>：
	- <font color="#c00000">无论间接地套了多少次引用(即引用的引用)</font>，<span style="background:#fff88f"><font color="#c00000">其最终都会折叠为单级引用</font></span>：
		- 即使在类型判定(`std::is_same`)中也是如此
		- 间接引用主要依靠 `typedef` 、`using` 等类型别名的方式间接堆叠

### 3.2.3 引用的链式调用特性 ^8eltqy

在其他语言中通常有链式调用特性，例如：

```Python
result = (
	Query(users)
	.where(lambda u: u.city == "Shanghai")
	.where(lambda u: u.age >= 26)
	.order_by(lambda u: u.age, reverse=True)
	.take(2)
	.to_list()
)
```

而在C++中，可以通过将返回值改为该类别的引用形式实现链式调用：

```CPP
class Person {
public:
	Person& name(std::string name) { 
		m_name = std::move(name);
		return *this;
	};
	Person& age(int age) { 
		m_age = age;	
		return *this;
	};
	Person& gender(Gender g) {
		m_gender = g;
		return *this;
	};
}

// 调用：
void func() {
	auto person = Person().name("张三").age(35).gender(Gender::Male);
}
```

注：
1. 链式调用必须使用引用形式的返回值，因为返回实体类型时，会重新拷贝构造一次

### 3.2.4 const与引用






## 3.3 左值与右值







## 3.4 新增基本类型(不含STL)

### 3.4.1 智能指针

智能指针是C++中一类指针的统称，其包含：
- `std::unique_ptr` 独占指针
- `std::shared_ptr` 共享指针
- `std::weak_ptr` 弱引用指针
智能指针严格来说不属于STL。
智能指针使用头文件 `<memory>` 。

#### 3.4.1.1 独占指针(unique_ptr) ^t86e16

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

其通用API可见章节[[CPP/C2CPP/C2CPP#^sh4a28|独占、共享指针的通用方法]]，专用API见子章节。

##### 3.4.1.1.1 类型定义与指定Deleter

`std::unique_ptr` 在构造时可在模板中传递Deleter，从而在指针生命周期结束时自动释放资源。<font color="#c00000">其</font><span style="background:#fff88f"><font color="#c00000"><u>类型定义</u></font></span><font color="#c00000">如下</font>：

```CPP
// 使用默认Deleter
template<
    class T,
    class Deleter = std::default_delete<T>
> class unique_ptr;

// 指定自定义Deleter
template <
    class T,
    class Deleter
> class unique_ptr<T[], Deleter>;
```

需要注意：
- <font color="#c00000">Deleter不同</font>，<font color="#c00000">则对应的</font> `std::unique_ptr` <font color="#c00000">类型不同</font>。
- 当需要构造<font color="#c00000">指向类型</font> `A` <font color="#c00000">的智能指针时</font>，则上述<font color="#c00000">模板参数</font> `T` <font color="#c00000">应当为类型</font> `A` <span style="background:#fff88f"><font color="#c00000">本身而非</font></span> `A*`

#### 3.4.1.2 共享指针(shared_ptr)

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
void test_shared()
{
	// 通过 `std::make_shared` 创建，此时计数器为1
    std::shared_ptr<int> sp1 = std::make_shared<int>(100);
    
    {
    	// 两指针共用一个 int
        std::shared_ptr<int> sp2 = sp1; // 允许拷贝，计数 = 2
    } // sp2 析构，计数 = 1，内存未释放
    
} // sp1 析构，计数 = 0 -> 释放内存
```

其通用API可见章节[[CPP/C2CPP/C2CPP#^sh4a28|独占、共享指针的通用方法]]，专用API见子章节。

##### 3.4.1.2.1 构造函数构造与指定Deleter

对于 `unique_ptr` 和 `shared_ptr` 这两个智能指针，都可以为其指定析构器 `Deleter` ，从而实现自定义释放资源的方法。不过：
- `unique_ptr` 是在<font color="#c00000">类型模板中传递</font>，<font color="#c00000">会改变其类型定义</font>，会在编译期完成指定
- `shared_ptr` 是在构造函数中传递，<font color="#c00000">不会改变类型定义</font>，会在运行时完成指定

`std::shared_ptr` 的<span style="background:#fff88f"><font color="#c00000"><u>类型定义</u></font></span><font color="#c00000">如下</font>：

```CPP
template< class T > class shared_ptr;
```

其常用<span style="background:#fff88f"><font color="#c00000"><u>构造函数</u></font></span><font color="#c00000">定义如下</font>：

```CPP
// 使用类的默认删除器 std::default_delete<Y>
template< class Y >  
explicit shared_ptr( Y* ptr );

// 使用自定义Deleter
template< class Y, class Deleter >
shared_ptr( Y* ptr, Deleter d );
```

明显地，<font color="#c00000">其类型定义中使用的是类型</font> `T` ，<font color="#c00000">而构造函数中统一使用类型</font> `A` ，<span style="background:#fff88f"><font color="#c00000">这是两个不同的类</font></span>。其这样设计的目的有：
1. 允许使用基类指针指向派生类对象(多态)：
```C
std::shared_ptr<Base> p(new Derived());
```
2. 支持别名构造(Aliasing Constructor)： ^2eap77
```CPP
struct Car {
    Engine engine;
};

// 创建变量 `std::shared_ptr<Car> car` ，此时计数器为 1
std::shared_ptr<Car> car = std::make_shared<Car>();

// 使用别名构造方法创建变量 `std::shared_ptr<Engine> engine`
// 但是其计数器用的是变量 `car` 的计数器，此时计数器为 2
std::shared_ptr<Engine> engine(car, &car->engine);
```
3. 使用 `void` 指针持有任何对象(类型擦除、资源保活)：
```CPP
class DataTypeA {
public:
	uint8_t data[1024] = { 0 };
}

class DataTypeB {
public:
	uint8_t *data[2048] = { 0 };
}

// DataContainer 用于统一存储 DataTypeA 和 DataTypeB
class DataContainer {
	// 构造函数负责寄存
	DataContainer(uint8_t *data, std::shared_ptr<void> owner)
		: data(data), owner(owner) { }
	
	uint8_t *get_data() { return data; }
private:
	uint8_t *data;
	// 用于持有对真实数据持有者的引用计数
	std::shared_ptr<void> owner;
}

DataContainer func() {
	// 获取要寄存的数据
	// 需要注意，必须是动态分配在堆内存的对象才可以交给 shared_ptr 
	// 不然可能会导致双重释放
	DataTypeA *data_a = new DataTypeA;
	
	// 此时DataContainer引用了data_a
	return DataContainer(data_a->data, std::shared_ptr<DataTypeA>(data_a));
}

int main()
{
	DataContainer container = func();
	uint8_t *data = container.get_data();
	return 0;
}
```

<font color="#c00000">需要注意</font>：
- `Y*` <span style="background:#fff88f"><font color="#c00000">必须可以隐式转换为</font></span> `T*`
- `T` & `Y` ：
	- 类型 `T` 决定了 `shared_ptr.get()` 获取到的指针的类型
	- 类型 `Y` 决定了 `shared_ptr` 析构时的Deleter

#### 3.4.1.3 独占、共享指针的通用方法 ^sh4a28

##### 3.4.1.3.1 构造方法(std::make_unique、std::make_shared)(C++14) ^fb89wj

`make_unique` 和 `make_shared` 是专门用于构造对应的两种指针的构造方法。除了提供了一些性能优化和简化写法以外，其主要可以<font color="#c00000">在如下情况提供更安全的内存保护</font>，具体如下：
1. 在C++17之前，<font color="#c00000">函数参数的求值顺序是不确定的</font>(<font color="#c00000">甚至函数参数的参数求值顺序也不固定</font>)，例如：
```CPP
void process(std::unique_ptr<MyClass> ptr, int priority);
int getPriority(); // 这个函数可能会抛出异常
	
// 调用代码：
process(std::unique_ptr<MyClass>(new MyClass()), getPriority());
```
2. 则上述调用必须执行如下三件事，<font color="#c00000">但是其顺序不固定</font>：
	1. 执行 `new MyClass()` 
	2. 执行 `std::unique_ptr` 的构造函数
	3. 调用 `getPriority()`
3. 那么如果先执行了 `new MyClass()` ，随后在 `getPriority()` 时触发异常，则会导致 `new` 出来的内存没人去释放，从而导致内存泄露。
因此，上述代码可以改用 `make_unique` 进行实现：

```CPP
void process(std::unique_ptr<MyClass> ptr, int priority);
int getPriority(); // 这个函数可能会抛出异常

// 调用代码：
process(std::make_unique<MyClass>(), getPriority());
```

其解决的根本原理是<span style="background:#fff88f"><font color="#c00000">把资源申请的步骤放到了工厂函数中!!!</font></span>

不过需要注意：
1. <span style="background:#fff88f"><font color="#c00000">当设置了Deleter之后</font></span><font color="#c00000">两种指针均无法使用此方法构造</font>。
子章节中列出了常用的构造方法，更多构造方法自行参考cppreference。

###### 3.4.1.3.1.1 构造独占指针并传递参数

```CPP
template< class T, class... Args >
constexpr unique_ptr<T> make_unique( Args&&... args );
```

其中：
- 参数 `args` 被传递给 `T` 的构造函数

###### 3.4.1.3.1.2 为独占指针构造指定大小的数组

```CPP
template< class T >
constexpr unique_ptr<T> make_unique( std::size_t size );
```

其中：
- 模板 `T` <span style="background:#fff88f"><font color="#c00000">为目标类型的数组类型</font></span>

###### 3.4.1.3.1.3 构造共享指针并传递参数

```CPP
template< class T, class... Args >
shared_ptr<T> make_shared( Args&&... args );
```

其中：
- 参数 `args` 被传递给 `T` 的构造函数

###### 3.4.1.3.1.4 为共享指针构造指定大小的数组

```CPP
template< class T >
shared_ptr<T> make_shared( std::size_t N );
```

其中：
- 模板 `T` <span style="background:#fff88f"><font color="#c00000">为目标类型的数组类型</font></span>

##### 3.4.1.3.2 自定义工厂函数的方法 ^oji6gb

在[[CPP/C2CPP/C2CPP#^fb89wj|上述章节]]中提到了一种由于C++20之前，参数求值顺序不确定导致的内存泄露风险，在一般情况下我们可以通过使用工厂函数 `std::make_unique` 和 `std::make_shared` 进行规避。但是其问题是当我们自定义 `Deleter` 时，就无法使用上述两个函数。

此时的解决方案是定义自己的工厂函数












##### 3.4.1.3.3 解引用(operator->、operator*)

和普通裸指针一样使用即可。

```CPP
typename std::add_lvalue_reference<T>::type operator*() const
    noexcept(noexcept(*std::declval<pointer>()));
```

```CPP
pointer operator->() const noexcept;
```

##### 3.4.1.3.4 访问数组元素(operator\[\])




##### 3.4.1.3.5 获取原始裸指针(get)

当调用普通C语言API，或者调用未使用智能指针的API时，则可以使用 `get` 方法获取其持有的裸指针。

```CPP
pointer get() const noexcept;
```

##### 3.4.1.3.6 交换(swap)



#### 3.4.1.4 弱引用指针(weak_ptr)

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

弱引用指针无法使用解引用


##### 3.4.1.4.1 获取访问权并升格为共享指针(lock)

```CPP

```



#### 3.4.1.5 拓展用法

##### 3.4.1.5.1 资源自动释放(RAII) ^9cldls

在C语言中，资源的申请均需要申请者手动进行释放，没有C++中的析构函数的自动释放方式。这样一旦遇到复杂的错误路径处理就很麻烦，例如：

```C
int init() 
{
	int ret = 0;
	
	// 初始化资源a
	ResourceA a = {};
	ret = init_a(&a);
	if(ret)
		return ret;
	
	// 初始化资源b
	ResourceB b = {};
	ret = init_b(&b);
	if(ret) {
		free_a(&a);
		return ret;
	}
	
	// 初始化资源c
	ResourceC c = {};
	if(ret) {
		free_b(&b);
		free_a(&a);
		return ret;
	}
	
	// 越来越长...
	...
}
```

即使上述资源可以像指针一样简单判断是否需要释放，或者有一个鲁棒的释放函数，然后再配合 `goto` ，其错误处理依旧是十分复杂繁琐的：

```C
int init() 
{
	int ret = 0;
	
	// 初始化资源a
	ResourceA *a = NULL;
	ret = init_a(&a);
	if(ret)
		goto cleanup;
	
	// 初始化资源b
	ResourceB b = {};
	ret = init_b(&b);
	if(ret)
		goto cleanup;
	
	// 初始化资源c
	ResourceC c = {};
	if(ret)
		goto cleanup;
	
	...
cleanup:
	// 如果是指针类型，或者可以判断是否需要free
	if(a) free_a(a);
	if(is_inited(&b)) free_b(&b);
	// 或者说可以释放函数设计的很鲁棒，可以随意调用
	free(&c);
	
	return ret;
}
```

而使用智能指针可以解决这个问题，只需要为每个对象都：
1. 实现一个 `Deleter`
2. 使用绑定了 `Deleter` 的智能指针(通常是别名用法)
即可，并且智能指针可以使用 `.get()` 方法，从而兼容C语言调用，例如：

```CPP
// ResourcePtr.hpp
// 构造Deleter
Struct ResourceADeleter {
	void operator()(ResourceA* a) const {
		if(a) free_a(a);
	}
}

Struct ResourceBDeleter {
	void operator()(ResourceB* b) const {
		if(b) free_b(b);
	}
}

Struct ResourceBDeleter {
	void operator()(ResourceC* c) const {
		if(c) free_c(c);
	}
}

// 使用别名
Using ResourceAPtr = std::unique_ptr<ResourceA, ResourceADeleter>;
Using ResourceBPtr = std::unique_ptr<ResourceB, ResourceBDeleter>;
Using ResourceCPtr = std::unique_ptr<ResourceC, ResourceCDeleter>;
```

随后调用时可以：

```CPP
// 调用时可以：
int init() 
{
	int ret = 0;
	
	// 初始化资源a

}


```

#TODO

上述设计方法或思想即为RAII(资源获取即初始化)，简单理解即<span style="background:#fff88f"><font color="#c00000">把资源的声明周期绑定到对象的生命周期上</font></span>。

### 3.4.2 强类型枚举(enum class)

### 3.4.3 原子变量(std::atomic)(C++11)

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

#### 3.4.3.1 构造函数




#### 3.4.3.2 成员函数

C++的原子变量支持如子章节所示的成员函数。

##### 3.4.3.2.1 检查对象是否无锁

```CPP
bool is_lock_free() const noexcept;
```

其返回值为是否有锁。

##### 3.4.3.2.2 赋值运算符(operator=)

```CPP
T operator=(T desired) noexcept;
```

其功能为将非原子变量的值存入原子变量，等价于调用 `store` 函数。
参数：
- `T desired` ：要存入的非原子变量类型的值
返回值：
- 等于 `desired`

##### 3.4.3.2.3 原子地存值(store)

```CPP
void store(T desired, std::memory_order order =
            std::memory_order_seq_cst ) noexcept;
```

其功能为将非原子变量的值存入原子变量。
参数：
- `T desired` ：要存入的非原子变量类型的值
- `std::memory_order order` ：要强制执行的内存顺序约束

##### 3.4.3.2.4 取值运算符(operator T)

```CPP
operator T() const noexcept;
```

其功能为原子地加载并返回原子变量的当前值，等价于调用 `load` 函数。

##### 3.4.3.2.5 原子地取值(load)

```CPP
T load(std::memory_order order = std::memory_order_seq_cst) const noexcept;
```


##### 3.4.3.2.6 赋予新值并取出旧值(exchange)

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

##### 3.4.3.2.7 条件睡眠(wait)(C++20)

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

##### 3.4.3.2.8 唤醒一个睡眠线程(notify_one)(C++20)




##### 3.4.3.2.9 唤醒所有睡眠线程(notify_all)(C++20)




### 3.4.4 标准线程(std::thread、std::jthread)

C++中提供了两种线程对象：
- `std::thread` ：普通线程
- `std::jthread` ：自带收尾机制、在某些情况下可以被取消/停止的线程
上述两种对象均使用头文件 `<thread>`

#### 3.4.4.1 std::thread(C++11)

与其他语言/框架一致的是，其有如下的基本特性：
- 创建线程后会立即执行
- 若线程句柄被析构时，线程仍在运行且句柄未分离(即 `joinable` 为 `true` )，则会触发异常。对应的处理方式为：
	- 调用 `join` 可以等待子线程退出，退出后可析构线程句柄
	- 调用 `detach` 可以分离其与父线程之间的关联，此时析构线程句柄是安全的

##### 3.4.4.1.1 构造函数

###### 3.4.4.1.1.1 创建一个不表示任何线程的thread对象

```CPP
thread() noexcept;
```

###### 3.4.4.1.1.2 移动构造函数

```CPP
thread( thread&& other ) noexcept;
```

###### 3.4.4.1.1.3 创建线程并传递参数

```CPP
template< class F, class... Args >
explicit thread( F&& f, Args&&... args );
```

##### 3.4.4.1.2 阻塞等待指定线程执行完毕(join)

```CPP
void join();
```

调用前需要确保该线程可被 `join`，否则会抛出异常。
`join` 后其 `joinable` 为 `false` (即只能被 `join` 一次)。

##### 3.4.4.1.3 分离指定线程(detach)

```CPP
void detach();
```

分离指定线程，分离后其 `joinable` 为 `false` 。

#### 3.4.4.2 std::jthread(C++20)

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

##### 3.4.4.2.1 构造函数

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

### 3.4.5 错误码(std::error_code)(C++11) ^i8qvar

在C++11之前，标准提供的错误机制主要有如下两种：
1. 全局的 `errno` ，是全局变量，线程不安全
2. `exception` 机制，性能开销大，部分环境禁用

因此C++11引入了轻量化的错误码机制，相较于 `int` 类型错误码，其有如下的额外特性：
1. `int` 类型错误码不具有统一的语义，例如同样是 `-1` ，其在不同的库中含义不同
2. `std::error_code` 可以携带错误信息字符串
3. `std::error_code` 可以携带域信息，标明错误是源自操作系统、HTTP库或者其他的库

#### 3.4.5.1 发送者构造方法

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

#### 3.4.5.2 接收者使用方法

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

### 3.4.6 std::optional(C++17) ^fatdl4

`std::optional` 使用头文件 `<optional>`

#### 3.4.6.1 基本使用

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
需要注意：
- `std::optional<T>` <font color="#c00000">默认只是一个空容器</font>，<span style="background:#fff88f"><font color="#c00000"><u>需要先创建该对象</u></font></span>，<font color="#c00000">随后才能进行赋值和操作</font>。
	- 构造时可以：
		- 使用[[CPP/C2CPP/C2CPP#^r5zfr4|emplace]]原地构造
		- 也可以使用赋值操作
	- 作为struct成员时更应注意

在使用时，可以使用如下的方法校验其是否包含值：

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

#### 3.4.6.2 内存分配

`std::optional` 是静态分配的内存，位于栈上。

#### 3.4.6.3 常用成员函数

##### 3.4.6.3.1 原地构造(emplace) ^r5zfr4

`emplace` 函数会就地构造该值，如果调用时已包含该值，则会先销毁原值再构造新值。

其有如下两个重载：
1. 通过直接初始化构造包含值，相当于执行了 `T(args)` ：
```CPP
template< class... Args >
T& emplace( Args&&... args );
```
- 其中：
	- `args` 为传递给构造函数的参数

2. 通过调用聚合初始化方法构造，相当于执行了 `T({u1, u2, ...}, args...)`：
```CPP
template< class U, class... Args >
T& emplace( std::initializer_list<U> ilist, Args&&... args );
```
- 其中：
	- `ilist` 为要传递给构造函数的初始化列表
	- `args` 为传递给构造函数的参数

### 3.4.7 预期对象(std::expected) ^qh6jjo


### 3.4.8 文件系统(std::filesystem)

C++的文件系统中提供了大量的新类型与新机制，具体统一见章节[[CPP/C2CPP/C2CPP#^alqala|文件系统]]。

### 3.4.9 RAII的互斥体封装器(std::lock_guard)(C++11)

明显地，在进行互斥量开发时，需要针对函数的异常与错误分支进行解锁：
- 在C语言中，其依赖复杂的错误处理逻辑进行解锁
- 在C#、Python等语言中依赖 `with(mutex)` 的方式实现自动解锁
而C++中提供了依赖于RAII的互斥体解锁方式：
- 在加锁时，其通过创建 `std::lock_guard<T>(mutex)` 对象进行加锁
- 当代码块遇到错误或自然退出时，`std::lock_guard` 对象会自动析构，析构时自动执行解锁

demo如下：

```CPP
void func() {
    // 相当于 with(mutex)
    {
        std::lock_guard<std::mutex> guard(mtx); 
        // 只有这里被锁保护
        shared_resource++;
    } 
    // 后续处理，此时锁已释放
	...
}
```










### 3.4.10 std::basic_string_view(C++17) ^2d6kyg

本章节应当在学习完章节[[CPP/C2CPP/C2CPP#^33a2f1|basic_string]]后学习。
其与 `std::basic_string` 的区别如下表所示：

| <center>特性</center> | <center>std::string</center>               | <center>std::string_view</center>    |
| ------------------- | ------------------------------------------ | ------------------------------------ |
| 本质                  | <font color="#c00000">字符串的拥有者</font>(RAII) | <font color="#c00000">字符串的观察者</font> |
| 内存所有权               | 拥有内存(Owner)                                | 不拥有(Non-owning)                      |
| 引入版本                | C++98                                      | C++17                                |
| 拷贝代价                | 高(深拷贝，可能涉及 `new`/`malloc`)                 | 极低(仅拷贝指针+长度)                         |
| 数据位置                | 通常在堆上，短字符串优化(SSO)除外                        | 指向任意位置(栈、堆、静态区)                      |
| 可变性                 | 可修改                                        | <font color="#c00000">只读</font>      |
| 空结尾                 | 保证以 `\0` 结尾                                | 不保证以 `\0` 结尾                         |
| 主要用途                | 存储数据，作为返回值，需要修改字符串                         | 函数参数，解析字符串，切片等                       |

#### 3.4.10.1 常用构造方式

##### 3.4.10.1.1 默认构造(空视图)

```CPP
constexpr basic_string_view ( ) noexcept;
```

使用时直接构造即可，<font color="#c00000">构造后</font>`sv.data` <font color="#c00000">指向</font> `nullptr`

```CPP
std::string_view sv; 
// sv.data() == nullptr
// sv.size() == 0
```

##### 3.4.10.1.2 从basic_string隐式转换

需要注意，本方法并非使用构造函数，而是使用转换运算符 `operator string_view()` 

```CPP
std::string s = "Hello world!";
std::string_view sv = s; // 自动调用 s.operator string_view()
```

复杂度：
- 时间复杂度：$O(1)$

##### 3.4.10.1.3 从C风格字符串构造

构造函数定义：

```CPP
constexpr basic_string_view ( const CharT * s ) ;
```

其使用时可以：

```CPP
const char* c_str = "Hello World";

// 调用构造函数
std::string_view sv(c_str);

// 或者使用赋值形式(但是触发的是构造函数，而非类型转换运算符)
std::string_view sv = c_str;
```

复杂度：
- 时间复杂度：$O(n)$ ，其会遍历数组直到找到 `\0`

##### 3.4.10.1.4 由C风格字符串+长度构造

构造函数定义：

```CPP
constexpr basic_string_view ( const CharT * s, size_type count ) ;
```

复杂度：
- 时间复杂度：$O(1)$

##### 3.4.10.1.5 字面量+sv后缀构造

```CPP
using namespace std::literals; // 必须引入命名空间
auto sv = "Hello World"sv;     // 类型直接推导为 std::string_view
```

复杂度：
- 时间复杂度：$O(0)$ (编译期求值)

##### 3.4.10.1.6 迭代器构造






## 3.5 新增函数

### 3.5.1 字符串格式化函数(std::format)(C++20)

`std::format` 是类似于 `printf` 的字符串格式化函数，其格式字符串 `fmt` 有如下的替换规则：
- 除 `{` 和 `}` 的字符串会被原样复制输出
- `{{` 和 `}}` 被用作转义序列，表达 `{` 和 `}` 
- 形如下方的替换字段被用作格式化参数：
	- `{}` ：参数占位符
	- `{arg-id}` ：指定 `args` 中用于格式化的参数的索引，如果省略，则按顺序使用参数。
	- `{arg-id: format-spec}` ：<font color="#c00000">指定格式化规范</font>，并指定索引。
`std::format` 使用头文件 `<format>`

`std::format` 主要分为如下几类：
1. 使用标准格式方法格式化普通字符串和宽字符串：
```CPP
// 格式化普通字符串
template< class... Args >
std::string format( std::format_string<Args...> fmt, Args&&... args );
// 格式化宽字符串
template< class... Args >
std::wstring format( std::wformat_string<Args...> fmt, Args&&... args );
```
2. 使用与地区习惯相符的方式(尤其指日期、小数等)格式化普通字符串和宽字符串：
```CPP
template< class... Args >
std::string format( const std::locale& loc,
                    std::format_string<Args...> fmt, Args&&... args );
template< class... Args >
std::wstring format( const std::locale& loc,
                     std::wformat_string<Args...> fmt, Args&&... args );
```

demo如下：
```CPP


```

### 3.5.2 强制类型转换

注意：
- 下方四个子章节仅涉及普通<font color="#c00000"><u>裸指针</u></font>的类型转换，智能指针的对应版本为： ^4pmbef
	- `std::shared_ptr` 对应关系：
		- 静态转换：`std::static_pointer_cast`
		- 动态转换：`std::dynamic_pointer_cast`
		- 去常转换：`std::const_pointer_cast`
		- 重新解释转换：`std::reinterpret_pointer_cast`
	- `std::unique_ptr` 对应关系：
		- 静态转换：
			- 子转父：自动
			- 父转子：不支持
		- 剩余其他三种也均不支持

#### 3.5.2.1 静态转换(static_cast)

```CPP
static_cast<目标类型 ﻿>(表达式 ﻿)
```

静态转换会<font color="#c00000">在编译器进行检查</font>，<font color="#c00000">是最常用的转换方式</font>，也是C语言中隐式转换的替代品。

其常用方法为：
1. 数据类型转换：`int` 和 `double` 互转等
2. 父子类型转换：
	1. 上行转换：子类<font color="#c00000"><u>裸指针</u></font>转父类<font color="#c00000"><u>裸指针</u></font>，安全
	2. 下行转换：父类<font color="#c00000"><u>裸指针</u></font>转子类<font color="#c00000"><u>裸指针</u></font>，<font color="#c00000">不安全</font>：
		- 其只在编译时检查继承关系、计算指针偏移量
		- 没有运行时检查(dynamic_cast为该需求的安全版本)
3. `void*` 与其他指针的互转。

注意：
- 上述指针均为<font color="#c00000"><u>裸指针</u></font>类型，智能指针版本详见父章节开头[[CPP/C2CPP/C2CPP#^4pmbef|对应关系]]，后续子章节同。

#### 3.5.2.2 动态转换(dynamic_cast)

```CPP
dynamic_cast<目标类型>(表达式)
```

专门用于处理多态的转换，在运行时检查是否合法：
- 合法则返回目标指针或引用
- 非法则：
	- 指针返回 `nullptr` 
	- 引用抛出异常(`std::bad_cast`)

其使用要求如下：
1. <font color="#c00000">其目标类型必须为如下的一种</font>：
	- <u>裸指针</u>类型
	- 引用类型
	- `void*`
	<font color="#c00000">因此其不存在直接创造对象的方法</font>，即使是 `Base b = dynamic_cast<Base>(d);` 
	(<font color="#c00000">然而静态转换可以</font> `Base b = static_cast<Base>(d);` ) 
2. 操作的类型必须是多态的(含有RTTI表，<font color="#c00000">即基类必须有虚函数</font>)

其常用方法为：
- 下行转换：父类指针转子类指针，含有运行时检查，更为安全
- 侧向转换：在多重继承中，在兄弟类之间跳转

Demo及注意事项如下：
1. 正常使用方式如下：
```CPP
class Base {
	virtual ~Base() { };
}
class Derived : public Base {}

void func() {
	Derived d;
	
	// 这里静态动态均可
	Base *pb = dynamic_cast<Base *>(&d);
	Base &rb = static_cast<Base &>(d);
	
	// 1. 指针转换
	Derived *pd = dynamic_cast<Derived *>(pb);
	// 2. 引用转换
	Derived &rd = dynamic_cast<Derived &>(rb);
}
```
2. 不可混合使用指针和引用：
```CPP
// 错误：指针和引用不可混合使用
Derived *rd = dynamic_cast<Derived &>(rb);  // 编译错误
```
3. 空指针/抛异常Demo如下：
```CPP
void func() {
	Base b;
	
	// 空指针，返回nullptr
	Derived *pd = dynamic_cast<Derived *>(&b);
	// 抛异常
	Derived &rd = dynamic_cast<Derived &>(b); // std::bad_cast
}
```
4. 其基类必须有虚函数：
```CPP
class Base {}                     // 无法使用，Base必须包含虚函数
class Derived : public Base {}
```

#### 3.5.2.3 去常转换(const_cast)

去常转换主要用于去除变量的 `const` 修饰。

主要用途：
- 兼容旧的C语言库：
	- 若能确保C语言库中没有实际修改变量，则一定是安全的，可见[[CPP/C2CPP/C2CPP#^fxahzf|Demo1]]。
	- 若C语言库中修改了变量，<font color="#c00000">则要确保转换前的指针实际指向的是可修改的内存区域</font>(否则UB)，可见[[CPP/C2CPP/C2CPP#^tsx4l0|Demo2]]、[[CPP/C2CPP/C2CPP#^ytqx0t|Demo3]]。

其Demo如下：
1. 若实际上没有发生变量修改，则一定安全：^fxahzf
```CPP
// 旧接口，实际没有修改变量，但没写 const
void legacyFunc(int* p) { /* ... */ }

void wrapper(const int* p) {
    // legacyFunc(p);                // 编译错误
    legacyFunc(const_cast<int*>(p)); // 去掉 const 才能传进去
}
```
2. 若发生变量修改，且原内存区域<font color="#c00000">不允许</font>修改，则UB：^tsx4l0
```CPP
const int constant = 10;
int* p = const_cast<int*>(&constant);
*p = 20; // 错误!!! UB!!!
```
3. 若发生变量修改，且原内存区域<font color="#c00000">允许</font>修改，则合法：^ytqx0t
```CPP
int var = 10;
int const *const_p = &var;
int* p = const_cast<int*>(const_p);
*p = 20;  // 合法
```

#### 3.5.2.4 重新解释转换(reinterpret_cast)

```CPP
reinterpret_cast<目标类型>(表达式)
```

<font color="#c00000">对二进制底层重新解读从而实现转换</font>，需要用户了解底层内存布局。其用法类似于C语言中的指针等强制转换。

其常用方法为：
1. 指针强转(即使毫不相干)：`int*` 转 `std::vector*` 等
2. 类型强转：`long` 转 `struct xx` 等

#### 3.5.2.5 强制类型转换汇总与C语言风格转换

上述四种转换的汇总对比如下：

| 转换方式               | 检查时机 | <center>典型场景</center>        | <center>安全事项</center>                                |
| ------------------ | :--: | ---------------------------- | ---------------------------------------------------- |
| `static_cast`      | 编译期  | 类型转换<br>父子转换                 | <font color="#c00000">在下行转换时需要自行确保正确</font>          |
| `dynamic_cast`     | 运行时  | 多态互转，包含：<br>- 父子转换<br>- 兄弟互转 |                                                      |
| `const_cast`       | 编译期  | 对接C语言接口：<br>- 去除 `const` 修饰  | <font color="#c00000">需要确保指针指向的地址本身就非</font> `const` |
| `reinterpret_cast` | 编译期  | 二进制重读                        | <font color="#c00000">需要确保内存布局正确</font>              |

在C++中，C语言风格的强制类型转换会按照如下的顺序逐个尝试：
1. `const_cast`
2. `static_cast`
3. `reinterpret_cast`
4. `dynamic_cast`
因此不建议在C++中使用C语言风格的转换。

## 3.6 新增关键字

### 3.6.1 namespace

如其字面意思， `namespace` 主要用于划定命名空间，给其限定的函数、类、变量、枚举、模板等提供作用域，从而<font color="#c00000">避免命名冲突</font>。

#### 3.6.1.1 基本使用方式

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

#### 3.6.1.2 命名空间的导入与全局命名空间

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

#### 3.6.1.3 匿名命名空间

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

#### 3.6.1.4 内联命名空间

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

### 3.6.2 explicit 强制显式转换 ^6nhi9i

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

### 3.6.3 constexpr 编译期求值

`constexpr` 关键字用于指定<font color="#c00000">变量或函数</font>使其在<font color="#c00000">编译期完成求值</font>，其有如下特性：
- `constexpr` 修饰<font color="#c00000">常量</font>，<font color="#c00000">常量</font>在编译期完成求值
- `constexpr` 修饰函数，会<span style="background:#fff88f"><font color="#c00000">尝试</font></span>在编译期求值(也可能推迟到运行时)
- `constexpr` 修饰构造函数，会在编译期构造<font color="#c00000">常量</font>对象
需要注意：
- `constexpr` <span style="background:#fff88f"><font color="#c00000">仅</font></span><font color="#c00000">在修饰函数时</font>可能会延后到运行时求值，其他两种情况均<span style="background:#fff88f"><font color="#c00000">一定在编译期求值</font></span>。
- `constexpr` 修饰函数时，<span style="background:#fff88f"><font color="#c00000">必须在声明处使用</font></span>，不过通常推荐声明和定义写在一起。

#### 3.6.3.1 constexpr 常量

`constexpr` 会在编译期确定常量的值，其与 ` const ` 常量的区别：

```cpp
const int runtime_const = get_value(); // 运行时求值的常量
constexpr int compile_const = 42;      // 编译时求值的常量

int array1[runtime_const];             // 错误，C++不支持VLA
int array2[compile_const];             // 正确，编译期已经求值
```

#### 3.6.3.2 constexpr 函数

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

#### 3.6.3.3 constexpr 构造函数

`constexpr` 构造函数可以在编译期构造<font color="#c00000">常量</font>对象


### 3.6.4 consteval 

### 3.6.5 using

在C++中，`using` 主要有如下的用法：
1. 命名空间引入
2. 提供类别别名(现代版的 `typedef` )
3. 类继承中的成员引入
4. 使用枚举

#### 3.6.5.1 命名空间引入

using引入命名空间时，有如下两种的引入方式：
1. 引入整个命名空间(即 `using namespace std;` )
2. 引入特定成员，例如 `using namespace std::string` ，随后即可使用 `string`
通常来说更推荐第二种引入方式

#### 3.6.5.2 提供类别别名

```CPP
using xxCallback = std::function<void(const xx&)>;
```

#### 3.6.5.3 类继承中的成员引入

类继承中的成员引入可以用于<font color="#c00000">重写部分成员</font>和<font color="#c00000">修改成员权限</font>，具体可见章节[[CPP/C2CPP/C2CPP#^464qd9|成员引入]]与[[CPP/C2CPP/C2CPP#^cvt59v|成员权限修改]]：
![[CPP/C2CPP/C2CPP#3 1  3 4 成员引入 using 464qd9]]
![[CPP/C2CPP/C2CPP#3 1 3 5 成员权限修改 using cvt59v]]

#### 3.6.5.4 简化枚举类(C++20)

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

### 3.6.6 函数关键字汇总及要求

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

#### 3.6.6.1 前置关键字

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

#### 3.6.6.2 后置关键字

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

## 3.7 异常系统及设计(std::exception)

### 3.7.1 异常的基本原理

和其他语言一样，C++中的异常主要也分为尝试、抛出、捕获三部分：
- 尝试(`try`)：尝试可能抛出异常的代码块
- 抛出(`throw`)：当触发在当前上下文中无法处理的错误时，抛出异常
- 捕获(`catch`)：紧跟在 `try` 块之后，用于捕获特定类型的异常

异常传递机制：
1. 当异常被抛出后，程序会立即跳出当前作用域，<font color="#c00000">沿着调用栈逐级向上</font>，直到找到匹配的 `catch` 块
2. 在沿调用栈逐级向上寻找匹配的 `catch` 块的过程中，<font color="#c00000">被跳出的栈上的局部变量均会被自动调用析构函数</font>。

异常抛出与捕获机制：
1. 异常本身也是一个对象，在抛出时也<font color="#c00000">允许抛出任意对象</font>(如 `int` 、`char*` 等)，不过从规范上而言抛出的应当是标准异常类或其派生类。
2. 类别判定机制有如下的规则：
	1. 类别匹配规则：
		1. <span style="background:#fff88f"><font color="#c00000">派生类可以被基类捕获</font></span>
		2. <font color="#c00000">不支持隐式转换</font>(例如抛出 `int` ，则 `double` 无法捕获)
		3. <font color="#c00000">忽略</font> `const/volatile` <font color="#c00000">限定</font>：非 ` const ` 对象可以被 ` const ` 引用捕获
		4. 空指针可以捕获任意类型的指针
	2. <font color="#c00000">顺序匹配、首个即中</font>
3. 常用的异常类别有：
	1. `std::runtime_error` ：运行时错误

### 3.7.2 异常系统的设计

在使用异常系统之前，首先：
- <font color="#c00000">要考虑清楚到底用不用异常</font>，<font color="#c00000">对于整个项目而言风格要统一</font>。
- 对于一个好的设计而言，<span style="background:#fff88f"><font color="#c00000">同一个函数中错误码和异常一定不要混用</font></span>。不然又要 `try` 又要检查错误码。返回错误码或使用 `std::expected` 的函数一定是 `noexcept` 的。
此外，应当结合具体的环境进行考虑：
- 嵌入式和性能受限场景应当考虑使用错误码或 `std::expected` 。
- 对于现代应用开发，可以考虑使用异常系统。

在为一个项目设计异常时，应当： ^ut2ewj
1. 定义一个项目专属的异常基类，并继承自 `std::runtime_error` 或 `std::exception`
2. 每一个子模块派生自己的异常类
3. `try...catch` 防火墙应当只假设在<span style="background:#fff88f"><u>底层触发点</u></span>和<span style="background:#fff88f"><u>顶层触发点</u></span>：
	- 底层触发点：当项目调用其他库代码，接收到错误或异常时，详见[[CPP/C2CPP/C2CPP#^dmrijq|底层触发点设计原则]]
	- <font color="#c00000">顶层触发点</font>：当代码需要<font color="#c00000">被其他语言调用</font>、<font color="#c00000">或回调函数调用时</font>，<span style="background:#fff88f"><font color="#c00000">一定要捕获所有异常</font></span>
4. <span style="background:#fff88f"><font color="#c00000">每个线程的入口函数(Entry)必须包裹</font></span> `try...catch` ，否则当异常抛出时，<font color="#c00000">整个进程都会被终止</font>。
5. 一个优秀的异常对象应当包含：
	1. What：发生了什么错误
	2. Where：发生错误的文件名、函数名、行号
	3. Context：关键变量的值
	4. Cause：原始错误码

关于底层触发点的设计原则： ^dmrijq
1. 对于<font color="#c00000"><u>同时满足</u></font>以下条件的：
	- 只是简单包装了一个库、或者同属于同一个项目的异常
		- 正例：只是简单包装了调用者一定可以理解的库
		- 正例：一个项目下的两个不同模块之间互相调用，并发生异常
	- 不会暴露细节的
		- <font color="#c00000">反例</font>：例如现在使用的是SQL库，未来如果换成了Redis，则抛出的异常可能改变，从而导致上层调用全部需要改动
	可以不封装直接抛出
2. 此外<font color="#c00000">其他类型异常均应二次封装后再抛出</font>，二次封装可考虑使用[[CPP/C2CPP/C2CPP#^81jlmr|异常嵌套]]特性。

使用异常时需注意：
1. <font color="#c00000">绝对不要在析构函数中抛出异常</font>，原因：
	1. 若当一个异常已经被抛出，从而导致对象被析构，若此时再抛出异常，则会由于C++无法同时处理两个异常，从而导致程序被调用 `std::terminate` 而强行结束
2. 考虑安全与效率，应当：
	- 抛出时<font color="#c00000">按值抛出</font>
	- 捕获时<font color="#c00000">按引用捕获</font>(推荐用引用，也可以用指针)
3. 由于抛出异常时会立即退出当前作用栈，会导致栈中 `new` 的对象难以 `delete` ，因此使用异常时应当配合[[CPP/C2CPP/C2CPP#^9cldls|RAII范式]]。
4. 对派生类的拦截应当在基类前

### 3.7.3 异常嵌套(C++11) ^81jlmr

在C++中异常嵌套通常用于上文所述的二次封装。而<span style="background:#fff88f"><font color="#c00000">异常嵌套可以理解为"洋葱"</font></span>，<span style="background:#fff88f"><font color="#c00000">外层套着内层</font></span>：
- 在封装时调用 `std::throw_with_nested(e)` ，将现在上下文中正在处理的异常包装到新的异常 `e` 当中
- 在解封装时调用 `std::rethrow_if_nested(e)` ，<font color="#c00000">剥去最外一层异常</font>(从外到内剥)，<font color="#c00000">将内层重新抛出</font>(如果有)
具体用法如下：
1. 在 `catch` 块中使用 `std::throw_with_nested` <span style="background:#fff88f"><font color="#c00000">封装新的异常并抛出</font></span>：
```CPP
// 抛出原始异常 (最里层的娃娃)
void open_file() {
    throw std::runtime_error("File 'config.ini' not found");
}

void init() {
	try {
        openFile();
    } catch (...) {
        // 具体动作：
        // 1. catch块中捕获了 "File not found"
        // 2. 创建一个 "Init Failed" 异常
        // 3. 自动把 1 塞进 2 里面，然后抛出
        std::throw_with_nested(std::logic_error("Init Failed"));
    }
}
```
2. 当处理异常时，使用 `try` 配合 `std::rethrow_if_nested` 将里面的异常重新抛出并捕获：
```CPP
// 递归打印异常链的辅助函数
void print_exception_stack(const std::exception& e, int level = 0) {
    // 1. 打印当前这一层的错误信息
    std::cerr << std::string(...) << std::endl;
	
    try {
        // 2. 具体动作：尝试重新抛出“肚子里”的异常
        // 如果 e 里面没有嵌套异常，那么这句不会触发新的异常，结束 `try` 块
        // 如果 e 里面有，它就会把里面的异常 throw 出来
        std::rethrow_if_nested(e);
    } 
    catch (const std::exception& nested) {
        // 3. 捕获到了里面的异常，递归调用自己
        print_exception_stack(nested, level + 1);
    } 
    catch (...) {
        // 处理非 std::exception 类型的古怪异常
        std::cerr << "Unknown non-standard exception nested." << std::endl;
    }
}
```

应当说明的是：
1. 如果在 `catch` 块之外调用 `std::throw_with_nested` ，<font color="#c00000">则其中包裹的异常为</font> `nullptr`，<font color="#c00000">是一个无用且危险的行为</font>(当调用 `std::rethrow_if_nested` ，拆到 `nullptr` 时会直接触发 `std::terminate()` )
2. 调用 `std::rethrow_if_nested` 会从外到内的"拆洋葱"，如果当前异常还内嵌的有其他异常则会抛出，如果没有内嵌则不抛异常。
3. 对于普通业务场景，通常不需要"拆洋葱"，甚至不需要捕获异常
4. 对于日志等需求，<font color="#c00000">则应当</font><span style="background:#fff88f"><font color="#c00000">递归地</font></span><font color="#c00000">"拆洋葱"</font>，直到拆到没有新的异常(具体可见上方示例)

## 3.8 错误处理机制汇总


至此，我们已经学习了C++中如下的几种错误处理机制：
- C风格返回值：
	- 依赖机制：`int` 或 `enun` 等类型
	- 优缺点：
		- 优点：
			- 运行效率高、语言标准版本要求低
			- 可以传递预定义的错误原因
		- 缺点：
			- <font color="#c00000">占用返回值</font>，真正的运行结果需要通过引用方式传出(大多数情况下)
			- <font color="#c00000">无法获取字符串风格的错误原因</font>
			- 错误分支处理复杂、需要判定每个可能失败的操作
- 错误码：
	- 依赖机制：[[CPP/C2CPP/C2CPP#^i8qvar|std::error_code]]
	- 优缺点：
		- 优点：
			- 运行效率高
			- 可以传递字符串风格的错误原因
		- 缺点：
			- <font color="#c00000">占用返回值</font>，真正的运行结果需要通过引用方式传出
			- 错误分支处理复杂、需要判定每个可能失败的操作
- 异常 `throw` ：
	- 依赖机制：`try...catch` 
	- 优缺点：
		- 优点：
			- 可以一次性包裹一大块代码，<font color="#c00000">不用单独判定每个可能失败的操作</font>
			- <font color="#c00000">错误分支处理与错误传递极其方便</font>，<font color="#c00000">谁想负责谁去</font> `catch`
			- 可以配合RAII减轻资源回收复杂度
			- 不占用返回值
		- 缺点：
			- <font color="#c00000">性能开销大</font>
			- 部分开发环境中被禁用(嵌入式、游戏开发)
- 可选值：
	- 依赖机制：[[CPP/C2CPP/C2CPP#^fatdl4|std::optional]]
	- 优缺点：
		- 优点：
			- 不占用返回值
		- 缺点：
			- <font color="#c00000">无法传递任何错误信息</font>
- 预期对象：
	- 依赖机制：[[CPP/C2CPP/C2CPP#^qh6jjo|std::excepted]]
	- 优缺点：
		- 优点：
			- 可以强制调用者检查错误
		- 缺点：
			- 错误分支处理复杂、需要判定每个可能失败的操作
为规范性起见，<span style="background:#fff88f"><font color="#c00000">在单一函数中一定不可混用上述错误机制</font></span>：
- 使用了异常的不要使用其他错误机制
- 使用了其他错误机制的一定要用 `noexcept` 修饰该函数，其不止是为了编译器性能优化，<span style="background:#fff88f"><font color="#c00000">更是省去调用者对抛出异常导致其业务错误的担心</font></span>

在框架及系统设计中，<font color="#c00000">推荐使用如下设计原则</font>：
- 业务受限环境下不可使用异常
- 允许使用异常时：
	- 按照项目层级分：
		- 底层算法应当使用 `std::excepted` 或其简易实现
		- 业务逻辑应当使用 `throw` 机制，其原则可见[[CPP/C2CPP/C2CPP#^ut2ewj|异常设计原则]]
	- 按照错误性质分：
		- <span style="background:#fff88f"><font color="#c00000">不可恢复或不该发生</font></span>的错误使用 `throw` 抛出异常：
			- 例如：内存耗尽、严重初始化失败
		- 预期会发生的可以使用其他错误机制
		- <font color="#c00000">对外边界不应当</font>使用 `throw` 抛出异常：
			- 对外边界：公有API、线程入口、IPC句柄、插件回调等

## 3.9 C++不支持的C语言特性

### 3.9.1 VLA可变长数组

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

### 4.2.1 容器的常用成员函数及补充说明

<span style="background:#fff88f"><font color="#c00000">其常用成员函数有</font></span>：
- 元素增加：
	- `insert()` ：插入元素
	- `insert_range()` 
	- `emplace()` ：就地构造并插入
	- `emplace_back()` ：在末尾构造并插入
	- `append_range()` 
	- `push()` ：在顶部插入元素
	- `push_back()` ：在末尾添加
	- `push_front()` ：在前端添加
	- `push_range()` ：在顶部插入一个元素范围
- 元素删除：
	- `erase()` ：删除元素
		- 补充说明：[[CPP/C2CPP/C2CPP#^8t8324|遍历时安全删除元素]]
	- `pop_back()` ：删除末尾元素
	- `pop()` ：移除顶部元素
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
	- `assign()` ：为容器批量<font color="#c00000">赋值</font>(注意不是分配空间，区分于 `reserve` )
	- `assign_range()` 
- 容器容量：
	- `empty()` ：判断是否为空
	- `size()` ：返回元素成员数量
	- `max_size()` ：返回最大的可能成员数量
	- `reserve()` ：<font color="#c00000">预留存储空间</font>
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

#### 4.2.1.1 遍历时安全删除元素 ^8t8324

为避免遍历时删除中可能遇到的：
- 迭代器失效：通过 `erase(it)` 删除迭代器指向的元素后，迭代器 `it` 会失效，无法再 `it++` 等操作
- 逻辑错误：错误跳过某些元素
等问题，建议使用以下范式：

```CPP
for(auto it = container; it < container.end(); ) { // 注意这里不要使用 `it++`
	if(condition(it)) {
		it = container.erase(it);
	} else {
		it ++;
	}
}
```

注意：
1. <font color="#c00000">循环中并不是每次都执行</font> `it++` ，因此：
	1. 循环中不要每次执行 `it++`
	2. 未删除元素时别忘了 `it++`
2. 使用 `it = erase(it)` 在删除元素时更新迭代器

### 4.2.2 std::initializer_list

<font color="#9bbb59">初始化列表</font>( `initializer_list` )是一个轻量化的<span style="background:#fff88f"><font color="#c00000">只读容器</font></span>，<font color="#c00000">通常其只能通过特殊的构造函数构造</font>。
需注意的是，<font color="#9bbb59">初始化列表</font>和构造函数的<font color="#9bbb59">成员初始化列表</font>是不同的概念。

#### 4.2.2.1 模板定义

```CPP
template< class T >
class initializer_list;
```

#### 4.2.2.2 常用构造函数

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

#### 4.2.2.3 常用方法

##### 4.2.2.3.1 查询元素数量(size)

```CPP
size_type size() const noexcept;
```

其实际上返回的是表达式 `std::distance(begin(), end())` 的值，类型为 `std::size_t` 。

##### 4.2.2.3.2 迭代器(begin、end)

```CPP
const T* begin() const noexcept;
const T* end() const noexcept;
```

### 4.2.3 std::basic_string(C++98) ^33a2f1

`std::basic_string` 为C++为若干种字符串类型(`char` 、 `wchar_t` 、`char32_t` 等)提供的统一容器，用于适配不同的字符串及编码类型。

#### 4.2.3.1 模板定义

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

#### 4.2.3.2 常用方法

##### 4.2.3.2.1 插入字符(insert)

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

##### 4.2.3.2.2 删除字符(erase)

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

##### 4.2.3.2.3 查询/修改元素(operator\[\])

通过index获取字符：

```CPP
CharT& operator[]( size_type pos );
const CharT& operator[]( size_type pos ) const;
```

##### 4.2.3.2.4 访问指定位置的字符(at)

##### 4.2.3.2.5 查找字符串或字符(find)

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

##### 4.2.3.2.6 获取c语言字符串版本指针(c_str)

```CPP
const CharT* c_str() const;
```

其返回的指针：
1. 在 `[c_str(), c_str() + size()]` 的范围内有效
2. 在原字符串容量被修改前有效
3. <font color="#c00000">不可通过该指针写入数据</font>(UB)

##### 4.2.3.2.7 清空字符串(clear)



##### 4.2.3.2.8 替换子字符串(replace)

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




#### 4.2.3.3 基本特性

##### 4.2.3.3.1 sizeof(string)

在x86架构下，`sizeof(std::string) = 28`；
在x86_64架构下，`sizeof(std::string) = 40`；
而 `sizeof(std::string)` 的值<u><font color="#c00000">不随字符串内容发生改变</font></u>。
##### 4.2.3.3.2 string作为struct的成员时

string可以作为struct的成员，其size计算符合内存对齐等要求。

#### 4.2.3.4 basic_string_view

`std::basic_string_view` 是零拷贝观察字符串数据的一种方式，具体可见章节：
- [[CPP/C2CPP/C2CPP#^2d6kyg|std::basic_string_view]]

### 4.2.4 array(C++11)

#### 4.2.4.1 模板定义

```CPP
template<
    class T,
    std::size_t N
> struct array;
```

注意：
- `std::size_t N` <span style="background:#fff88f"><font color="#c00000">必须在编译器即可确定</font></span>，<font color="#c00000">即也不支持动态数组大小</font>

### 4.2.5 vector

`std::vector` 是C++的动态大小的数组实现，其元素被顺序存储，因此其可以被迭代器和引索顺序访问。其会自动扩展其所需要的内存空间，并且通常其所占用的内存比同大小的静态数组要多。其空间的动态分配仅会发生在其所保留的额外空间耗尽时触发。

#### 4.2.5.1 模板定义

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

#### 4.2.5.2 常用方法


##### 4.2.5.2.1 构造函数

###### 4.2.5.2.1.1 创建包含n个指定默认元素的vector

```CPP
explicit vector( size_type count,
                 const Allocator& alloc = Allocator() );
```

###### 4.2.5.2.1.2 创建包含n个指定值的vector

```CPP
vector( size_type count, const T& value,
        const Allocator& alloc = Allocator() );
```

###### 4.2.5.2.1.3 由输入迭代器构造vector

```C
template< class InputIt >
vector( InputIt first, InputIt last,
        const Allocator& alloc = Allocator() );
```




##### 4.2.5.2.2 迭代器

`vector` 返回的迭代器为随机访问迭代器，可通过 `.begin()` 、 `.end()` 获取。


### 4.2.6 queue ^vsyig3

[[CPP/C2CPP/C2CPP#^vsyig3|queue]]

### 4.2.7 deque ^xkoeis


[[CPP/C2CPP/C2CPP#^xkoeis]]



### 4.2.8 stack

`std::stack` 是STL提供的栈容器，数据结构特性略。

#### 4.2.8.1 模板定义

```CPP
template<
    class T,
    class Container = std::deque<T>
> class stack;
```

#### 4.2.8.2 常用方法











### 4.2.9 std::unordered_map

`std::unordered_map` <font color="#c00000">基于哈希表实现</font>，内部元素无序存储。

#### 4.2.9.1 模板定义

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

#### 4.2.9.2 常用方法

##### 4.2.9.2.1 构造函数

```CPP
unordered_map();
```

其定义了如下的成员：
- `key_type` ：即 `class Key` ，键类型
- `mapped_type` ：即 `class T` ，值类型
- `value_type` ：`std::pair<const Key, T>` ^o36e6j 

##### 4.2.9.2.2 清空容器(clear)

```CPP
void clear() noexcept;
```

##### 4.2.9.2.3 插入元素(insert)

###### 4.2.9.2.3.1 插入单个元素

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

###### 4.2.9.2.3.2 批量插入(通过初始化列表)

```CPP
void insert( std::initializer_list<value_type> ilist );
```

其：
- 参数类型为键值对构成的初始化列表( `{{key1, value1}, {key2, value2}, ...}` )
- 无返回值
- 特性/语义：
	- 若参数中有重复键，则只插入第一个
	- 不会修改已有键值

###### 4.2.9.2.3.3 批量插入(通过迭代器)

```C
template< class InputIt >
void insert( InputIt first, InputIt last );
```



###### 4.2.9.2.3.4 带位置提示的插入

##### 4.2.9.2.4 删除元素(erase)

###### 4.2.9.2.4.1 通过key值删除

```CPP
size_type erase( const Key& key );
```

其中：
- 参数为需要删除的键值对的键
- 返回值为被删除的元素数量，值为0或1

时间复杂度：
- 平均 $O(1)$
- 最坏 $O(size)$

###### 4.2.9.2.4.2 通过迭代器删除单个元素

```CPP
iterator erase( iterator pos );
```

其中：
- 参数:
	- `pos` 为要删除元素的迭代器，<span style="background:#fff88f"><font color="#c00000">且不能为</font></span> `end()` <span style="background:#fff88f"><font color="#c00000">!!!</font></span>
		- 因为<font color="#c00000">只要map不为空</font>，<font color="#c00000">其最后一个元素就不是</font> `end()` ，所以<font color="#c00000">非空时</font>删除最后一个元素应当使用 `map.erase(std::prev(map.end()))`
- 返回值为被删除元素之后元素的迭代器。如果删除的是最后一个元素，则返回 `end()` 。

###### 4.2.9.2.4.3 通过迭代器范围删除元素

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

##### 4.2.9.2.5 查询(at)

###### 4.2.9.2.5.1 普通查找

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

###### 4.2.9.2.5.2 异构查找(C++26)

在普通查找时，其参数只能为Key的类型，而不能是可以和Key透明比较的类型。例如：

```CPP
// C++11 传统方法：有性能损耗
// 创建临时 std::string 对象 → 内存分配 + 复制
int value1 = traditional_map.at("view"); 

// C++26 异构方法：零开销
// 直接使用 string_view 查找 → 无临时对象
int value2 = transparent_map.at(std::string_view("view"));
```

##### 4.2.9.2.6 查询/新增(operator\[\])

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

##### 4.2.9.2.7 查找(find)

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

##### 4.2.9.2.8 查找(count)

`count` 也可用于查找是否存在对应的元素，由于hash表特性，其值只能为0或1。

```CPP
size_type count( const Key& key ) const;
```

C++20开始的查找可等价比较的元素：

```CPP
template< class K >
size_type count( const K& x ) const;
```

##### 4.2.9.2.9 原地插入(emplace)


##### 4.2.9.2.10 迭代器

`unordered_map` 提供了 `.begin()` 和 `.end()` 两个获取迭代器的方法，返回的类型为前向迭代器。

##### 4.2.9.2.11 k, v遍历

```CPP
std::unordered_map<std::string, int> scores = {
    {"Alice", 90},
    {"Bob", 85},
    {"Charlie", 95}
};

// [key, val] 直接对应键和值
// 使用 const auto& 避免拷贝，提高效率
for (const auto& [name, score] : scores) {
    std::cout << "Key: " << name << ", Value: " << score << "\n";
}
```



### 4.2.10 std::map

`std::map` 内部通常基于红黑树实现，<font color="#c00000">元素始终按键的升序排序</font>。

## 4.3 算法

### 4.3.1 排序

#### 4.3.1.1 通用基础内容

##### 4.3.1.1.1 Compare要求 ^t2nyfa

Compare要求建立如下的严格弱序关系：
- <font color="#c00000">弱序时返回</font> `true` ：`compare(0, 1) == true`
- <span style="background:#fff88f"><font color="#c00000">相等时返回</font></span> `false` ： `compare(a, a) == false`
- 不可反转： `compare(a, b) == true` 则 `compare(b, a) == false`
- 可传递性：
	- 如果 `compare(a, b) == true` 且 `compare(b, c) == true` 
	- 则 `compare(a, c) == true` 
且其返回值要有如下特性：
- `BooleanTestable` (C++20前) 或 `boolean-testable` (C++20其)





#### 4.3.1.2 std::sort(混合排序)

`std::sort` 使用的排序方法会根据需要排序的元素数量动态切换排序方式，是<span style="background:#fff88f"><font color="#c00000">不稳定</font></span><font color="#c00000">排序</font>。其先使用快速排序对数据进行分段，
- 

##### 4.3.1.2.1 普通升序排序(串行)

```CPP
template< class RandomIt >
void sort( RandomIt first, RandomIt last );
```

##### 4.3.1.2.2 按指定策略升序排序

```CPP
template< class ExecutionPolicy, class RandomIt >
void sort( ExecutionPolicy&& policy,
           RandomIt first, RandomIt last );
```



##### 4.3.1.2.3 按自定义逻辑执行排序(串行)

```CPP
template< class RandomIt, class Compare >
void sort( RandomIt first, RandomIt last, Compare comp );
```

其中：
- `Compare comp` 应当满足[[CPP/C2CPP/C2CPP#^t2nyfa|Compare要求]]

##### 4.3.1.2.4 按自定义逻辑和指定策略执行排序

```CPP
template< class ExecutionPolicy, class RandomIt, class Compare >
void sort( ExecutionPolicy&& policy,
           RandomIt first, RandomIt last, Compare comp );
```

#### 4.3.1.3 二分搜索(C++20) ^1gb857

##### 4.3.1.3.1 搜索是否存在目标值(binary_search)

`std::binary_search` ：
- 头文件：`<algorithm>` 
- 函数功能：搜索 `[first, last)` 区间内是否存在目标值 `value` 
- 函数参数：
	- 使用默认 `Compare` 并搜索：`std::binary_search(first, last, value)`
	- 使用自定义[[CPP/C2CPP/C2CPP#^t2nyfa|Compare]]并搜索：`std::binary_search(first, last, value, comp)`
- 返回值：
	- `bool` ，表示范围内是否存在 `value`
- 注：
	- <font color="#c00000">容器中元素必须按</font> `Compare` <font color="#c00000">排序</font>，即：
		- 当<font color="#c00000">使用默认</font> `Compare` <font color="#c00000">时</font>，传入容器<span style="background:#fff88f"><font color="#c00000"><u>必须为升序容器</u></font></span>
		- 当传入降序容器时，必须指定自定义[[CPP/C2CPP/C2CPP#^t2nyfa|Compare]]

具体签名：
- 使用默认 `Compare` 并搜索：
```CPP
template< class ForwardIt, class T = typename std::iterator_traits
                                         <ForwardIt>::value_type >
constexpr bool binary_search( ForwardIt first, ForwardIt last,
                              const T& value );
```
- 使用自定义[[CPP/C2CPP/C2CPP#^t2nyfa|Compare]]并搜索：
```CPP
template< class ForwardIt, class T = typename std::iterator_traits
                                         <ForwardIt>::value_type,
          class Compare >
constexpr bool binary_search( ForwardIt first, ForwardIt last,
                              const T& value, Compare comp );
```

##### 4.3.1.3.2 搜索第一个大于等于目标值的位置(lower_bound)

`std::lower_bound` ：
- 头文件：`<algorithm>` 
- 函数功能：搜索 `[first, last)` 区间内的第一个<span style="background:#fff88f"><font color="#c00000">大于等于</font></span> `value` 的元素位置
- 函数参数：
	- 使用默认 `Compare` 并搜索：`std::lower_bound(first, last, value)`
	- 使用自定义[[CPP/C2CPP/C2CPP#^t2nyfa|Compare]]并搜索：`std::lower_bound(first, last, value, comp)`
- 返回值：
	- `iterator` ：
		- 当所有元素都比 `value` 大时，返回值等价 `.begin()`
		- 当所有元素都比 `value` 小时，返回值等价 `.end()`
- 注：
	- <font color="#c00000">容器中元素必须按</font> `Compare` <font color="#c00000">排序</font>，即：
		- 当<font color="#c00000">使用默认</font> `Compare` <font color="#c00000">时</font>，传入容器<span style="background:#fff88f"><font color="#c00000"><u>必须为升序容器</u></font></span>
		- 当传入降序容器时，必须指定自定义[[CPP/C2CPP/C2CPP#^t2nyfa|Compare]]

具体签名：
- 使用默认 `Compare` 并搜索：
```CPP
template< class ForwardIt, class T = typename std::iterator_traits
                                         <ForwardIt>::value_type >
constexpr ForwardIt lower_bound( ForwardIt first, ForwardIt last,
                                 const T& value );
```
- 使用自定义[[CPP/C2CPP/C2CPP#^t2nyfa|Compare]]并搜索：
```CPP
template< class ForwardIt, class T = typename std::iterator_traits
                                         <ForwardIt>::value_type,
          class Compare >
constexpr ForwardIt lower_bound( ForwardIt first, ForwardIt last,
                                 const T& value, Compare comp );
```

##### 4.3.1.3.3 搜索第一个大于目标值的位置(upper_bound)

`std::upper_bound` ：
- 函数功能：搜索 `[first, last)` 区间内的第一个<span style="background:#fff88f"><font color="#c00000">大于</font></span> `value` 的元素位置
- 函数参数：
	- 使用默认 `Compare` 并搜索：`std::upper_bound(first, last, value)`
	- 使用自定义[[CPP/C2CPP/C2CPP#^t2nyfa|Compare]]并搜索：`std::upper_bound(first, last, value, comp)`
- 返回值：
	- `iterator` ：
		- 当所有元素都比 `value` 大时，返回值等价 `.begin()`
		- 当所有元素都小于等于 `value` 时，返回值等价 `.end()`
- 注：
	- <font color="#c00000">容器中元素必须按</font> `Compare` <font color="#c00000">排序</font>，即：
		- 当<font color="#c00000">使用默认</font> `Compare` <font color="#c00000">时</font>，传入容器<span style="background:#fff88f"><font color="#c00000"><u>必须为升序容器</u></font></span>
		- 当传入降序容器时，必须指定自定义[[CPP/C2CPP/C2CPP#^t2nyfa|Compare]]

具体签名：
- 使用默认 `Compare` 并搜索：
```CPP
template< class ForwardIt, class T = typename std::iterator_traits
                                         <ForwardIt>::value_type >
constexpr ForwardIt upper_bound( ForwardIt first, ForwardIt last,
                                 const T& value );
```
- 使用自定义[[CPP/C2CPP/C2CPP#^t2nyfa|Compare]]并搜索：
```CPP
template< class ForwardIt, class T = typename std::iterator_traits
                                         <ForwardIt>::value_type,
          class Compare >
constexpr ForwardIt upper_bound( ForwardIt first, ForwardIt last,
                                 const T& value, Compare comp );
```

##### 4.3.1.3.4 搜索等于目标值的区间范围(equal_range)

`std::equal_range` ：
- 函数功能：找到 `[first, last)` 范围内所有与 `value` 等效的元素
- 函数参数：
	- 使用默认 `Compare` 并搜索：`std::equal_range(first, last, value);`
	- 使用自定义[[CPP/C2CPP/C2CPP#^t2nyfa|Compare]]并搜索：`std::equal_range(first, last, value, comp);`
- 返回值：
	- `std::pair<ForwardIt, ForwardIt>` ：
		- `pair.first` 指向 `[first, last)` 中第一个不小于 value 的元素的迭代器
		- `pair.second` 指向 `[first, last)` 中第一个大于 value 的元素的迭代器
	- 则有：
		1. 如果序列中所有元素大于 `value` ，则 `pair.first`、`pair.second`  指向 `.begin() `
		2. 如果序列中所有元素小于 `value` ，则 `pair.first`、`pair.second`  指向 `.end() `
		3. 如果序列中所有元素不等于 `value` ，则 `pair.second - pair.first = 0`
- 注：
	- <font color="#c00000">容器中元素必须按</font> `Compare` <font color="#c00000">排序</font>，即：
		- 当<font color="#c00000">使用默认</font> `Compare` <font color="#c00000">时</font>，传入容器<span style="background:#fff88f"><font color="#c00000"><u>必须为升序容器</u></font></span>
		- 当传入降序容器时，必须指定自定义[[CPP/C2CPP/C2CPP#^t2nyfa|Compare]]



### 4.3.2 替换

#### 4.3.2.1 std::replace

# 5 新增标准库

## 5.1 文件系统(std::filesystem)(C++17) ^alqala






# 6 现代C++

## 6.1 面向对象的高级特性

### 6.1.1 子类父类

#### 6.1.1.1 子类与父类之间的创建与转换



对于一个基类 `Base` 和一个派生类 `Derived` ：
- 当使用 `Base b = d;` 时，会发生截断
- 当使用 `Base &b = d;` 时，
- 当使用 `Base *b = &d;` 时，

#### 6.1.1.2 运行时类型信息(RTTI)




### 6.1.2 PImpl模式

在C++中，由于<font color="#c00000">不支持将一个对象或结构体分多个地方多次定义</font>，因此考虑如下的设计场景：
- 现在需要基于几个内部库实现一个对象，并且<font color="#c00000">不希望这个对象的调用者关心内部库的数据结构</font>以及这个对象的内部实现
- 但是这个对象中不可避免的需要几个由内部库定义的私有成员变量
例如：

```CPP
// FfmpegCapture.hpp

extern "C" {
	#include "libavutil/avutil.h"
	#include "libavformat/avformat.h"
	...
}

class FfmpegCapture : public ICapture {
public:
    // ... 接口 ...
private:
    // 若干FFmpeg定义的成员变量
    AVFormatContext* fmtctx;
    AVCodeID         codeid;
    AVCodecContext*  codecctx;
    ...
    
    // 若干内部实现
    std::vector<StreamInfo> probe_streams(AVFormatContext* fmtctx);
    ...
};
```

上述实现方式除了会被动暴露对象的私有成员变量、内部方法等实现细节，还会被动引入大量内部依赖库的头文件及数据结构定义、编译选项等。

解决此问题可以使用PImpl模式进行设计，其具体步骤为：
1. 在结构体的 `private` 中<span style="background:#fff88f"><font color="#c00000"><b><u>声明</u></b></font></span>一个 `struct Impl;` (<font color="#c00000">注意并非定义</font>)
2. 内部私有成员定义一个[[CPP/C2CPP/C2CPP#^t86e16|独占指针]]指向该结构体成员(`std::unique_ptr<Impl> _impl;`)
3. <span style="background:#fff88f"><font color="#c00000">在源文件中定义该结构体</font></span>
4. <span style="background:#fff88f"><font color="#c00000">在<u>头文件中声明</u>、<u>源文件中定义</u>构造函数、析构函数</font></span>(注意在哪声明、在哪定义)
5. 在上述构造函数中实例化该独占指针(通常是在初始化列表中实例化)
随后内部调用的时候使用 `_impl` 调用内部成员和方法即可。

Demo如下：

```CPP
// FfmpegCapture.hpp
class FfmpegCapture {
public:
	// 在头文件只声明，不实现构造和析构函数!!!
	// 因为此时还没有 Impl 的定义
	FfmpegCapture();
    ~FfmpegCapture(); 
    
    // ... 接口 ...
private:
    // 1. 声明 Impl 结构体
    struct Impl;
    // 2. 定义独占指针
    std::unique_ptr<Impl> _impl;
};
```

```CPP
// FfmpegCapture.cpp

#include "FfmpegCapture.hpp"
extern "C" {
	#include "libavutil/avutil.h"
	#include "libavformat/avformat.h"
	...
}

// 3. 在源文件定义内部成员和实现
struct FfmpegCapture::Impl {
	// 若干FFmpeg定义的成员变量
	AVFormatContext* fmtctx;
	AVCodeID         codeid;
	AVCodecContext*  codecctx;
	...
	
	// 若干内部实现
	std::vector<StreamInfo> probe_streams(AVFormatContext* fmtctx);
	...
};

// 4. [关键] 构造函数在 cpp 中实现
FfmpegCapture::FfmpegCapture() : _impl(std::make_unique<Impl>()) {}

// 4. [关键] 析构函数在 cpp 中实现
// 此时 Impl 已经是"完整类型"了，unique_ptr 知道怎么 delete 它了
FfmpegCapture::~FfmpegCapture() = default;
```

在上述情况下很好的解决了普通类的细节隐藏需求。
<font color="#c00000">但是需要注意</font>，<font color="#c00000">PImpl模式并不能很好的做到如下的场景</font>：
- 基类 `Base` 需要使用PImpl隐藏内部细节
- 派生类 `Dervide` 也需要使用PImpl隐藏内部细节
- 派生类需要访问基类的PImpl

在上述情况下其会面临如下的问题：
1. 如果派生类和基类的 `_impl` 使用不同的名称，则会：
	1. 带来极大的代码污染
	2. 构造派生类时，<font color="#c00000">会多次触发内存分配</font>(先构造基类的 `_impl` 随后构造派生类的)
2. 如果派生类和基类均使用 `_impl` ，则会：
	1. 引入命名遮蔽问题，派生类访问基类的 `_impl` 时需要使用 `Base::_impl`
	2. 构造派生类时，<font color="#c00000">会多次触发内存分配</font>(先构造基类的 `_impl` 随后构造派生类的)

对于此情况，则应当放弃对基类使用 `PImpl` ，将基类与派生类共用的成员塞入 `private` ，具体略。
