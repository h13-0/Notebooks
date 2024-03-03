#C-Language #编译原理 

	Standards are paper. I use paper to wipe my butt every day. 
	That's how much that paper is worth. —— Linus Torvalds.

## 目录
```toc
min_depth: 1
```

## 笔记部分



## 原文翻译部分

### 5 环境

#### 5.1 概念模型

##### 5.1.1 翻译环境

###### 5.1.1.1 程序结构

储存有程序代码的文本被称为源文件(或预处理文件)，一个源文件和他使用`#include`包含的所有其他源文件和头文件被统一称作一个 `预处理单元` ，预处理之后的单元叫做 `翻译单元` 。
程序的独立翻译单元之间可以使用以下方式进行通信：
1. 调用具有外部链接标识符的函数
2. 操作具有外部链接标识符的对象
3. 操作文件

各个翻译单元之间可以独立翻译，然后最后链接到一起。

##### 5.1.1.2 翻译阶段

TODO: 检查空字符 `\0` 和空格字符` ` 是否有理解错误

翻译阶段的顺序如下：
1. 如果需要，物理源文件将会在行位添加一个新的换行符。???
2. 删除紧跟着换行符的反斜杠字符 `\` ，将物理源行拼成逻辑源行。只有物理源行的最后一个 `\` 才有资格被这样处理。任何非空的源文件应以换行符结尾，否则其前不应紧跟反斜杠字符 `\`
3. 源文件被分解为预处理`token`和空白字符序列(如注释)，源文件不得以不完整的预处理标记或注释结尾，每一个注释会被一个空格取代(**所以反斜杠后面不能接注释**)，换行字符会被保留。TODO:Whether each nonempty sequence of white-space characters other than new-line is retained or replaced by one space character is implementation-defined
4. 执行预处理指令，展开宏调用，并且执行`_Pragama`一元运算符表达式。如果在`token`连接中生成了与通用字符名语法匹配的字符序列，则其行为是未定义的，如[[#6.10.3.3]]中的`##`运算符。使用`#include`预处理指令会递归的处理步骤1到4。
5. 每一个设置了字符和转义字符串的字符常量和字符串会被计算或拼接为正确的值，若没有对应的成员则将会被转移成空字符????
6. 连接相邻的字符串标记，如 `"ab" "cd"` -> `"abcd"`
7. 此时空白字符不再有效，每一个预处理`token`都讲被转化为一个`token`，生成的`tokens`将会被用于语法和语义分析，并作为翻译单元进行翻译
8. 解析所有的外部对象和函数引用，并链接成一个文件


##### 5.1.1.3

##### 5.1.2 运行环境

运行环境有以下两种：
- 独立环境(freestanding)
- 托管环境(hosted)

无论在哪种环境下，C程序都会被环境调用。在C程序启动之前，所有的静态储存类型[^1]都会被初始化[^2]并设定为初始值。这种初始化的方式和时间均未具体规定，程序终止后控制权将返回到运行环境。

**引用**
[^1]: 静态储存环境
	[[C标准学习笔记#6.7.1 储存类型说明符]]
[^2]: 初始化
	[[#6.7.9]]

###### 5.1.2.1 独立环境

###### 5.1.2.2 托管环境

5.1.2.2.1 托管环境下的程序启动

程序启动时所被调用的函数为`main`，其声明可以是：
```C
int main(void)
```
或：
```C
int main(int argc, char *argv[])
```
或上一形式的等效形式：
```C
int main(int argc, char **argv)
```
或其他类型的由托管环境锁指定的声明。
参数的名字并不重要，但为了方便起见以上述命名进行表述：

当这些参数被声明后，这些参数有如下的限制：
1. `argc`的值应为非负
2. `argv[argc]`的值应为空指针`NULL`
3. 如果`argc`的值不为零，则`argv[0]`到`argv[argc - 1]`的值都应指向字符串。这些字符串由托管环境所指定，其目的是获取或传递信息。如果主机环境无法提供大写形式的字符串，则`main`程序在接收的时候应确保其能接收小写形式的字符串。
4. 如果`argc`的值大于0，则`argc[0]`指向的字符串应表示程序名。若托管环境无法提供该功能，则`argc[0][0]`应为空字符`\0`。若`argc`的值大于一，则`argv[1]`到`argv[argc - 1]`的值应表示程序参数。
5. `argc`和`argv`及其指向的字符串应可由程序修改，并在程序生命周期中一直保存其储存的值。

5.1.2.2.2 托管环境中的程序运行

在托管环境中，程序可以使用章节[[#7 库]]中的所有函数、宏、类型定义和对象。

5.1.2.2.3 托管环境中的程序终止

TODO

###### 5.1.2.3 程序执行

### 5.2 环境因素



### 6 语言

#### 6.2 概念

##### 6.2.1 标识符的范围
##### 6.2.2

##### 6.2.4

##### 6.2.5 类型

26. 限制说明符...TODO..包含 `const` 、 `volatile` 、 `restrict`  ^rbqfe0
27. 

#### 6.4 词法元素

##### 6.4.1 关键词(Keywords)

C11标准中的关键词如下：
- auto
- break
- case
- char
- const
- continue
- default
- do
- double
- else
- enum
- extern
- float
- for
- goto
- if
- inline
- int
- long
- register
- restrict
- return
- short
- signed
- sizeof
- static
- struct
- typedef
- union
- unsigned
- void
- volatile
- while
- \_Alignas
- \_Alignof
- \_Atomic
- \_Bool
- \_Complex
- \_Generic
- \_Imaginary
- \_Noreturn
- \_Static_assert
- \_Thread_local

以上标记在翻译阶段7和8被预留为关键词(区分大小写)，不得用作其他行为。关键词 `_Imaginary` 用作指定为虚数类型。

##### 6.4.2 标识符(Identifiers)

###### 6.4.2.1 普通标识符

**句法规则**
	TODO 没看懂什么意思，编译原理相关

**语义**
1. 标识符是一系列非数字字符（包括下划线 `_` 、小写和大写拉丁字母以及其他字符）和数字，用于指定[[C标准学习笔记#6 2 1 标识符的范围]]中所述的一个或多个实体。小写字母和大写字母是不同的。<font color="#c00000">标识的最大长度没有具体限制</font>。
2. 标识符中的每个通用字符名称应为在ISO/IEC 10646中的编码D.1.71中规定的范围中的一个字符。首字母字符不应是通用字符名称，该名称指定的字符的编码属于D.2中规定的范围之一。作为一种实现方式，可以允许不属于基本源字符集的多字节字符出现在标识符中；其实现定义了哪些字符及其与通用字符名的对应关系。
3. 当在翻译阶段7中将预处理token转换为token时，如果预处理token可以转换为关键字或标识符，则将其转换为关键字。

**实现限制**

###### 6.4.2.2 预定义标识符





##### 6.4.4 常量(Constants)

常量类型主要有
- 整数常数
- 浮点常数
- 枚举常数
- 还没看懂

**限制**
每一个常量类型都应具有类型，并且其值应在对应类型的可表示范围之内。

###### 6.4.4.1 整数

注意本文所述均为整数常量的定义、而非整数变量的运算。

对于整形常量、可以用前缀定义其进制，后缀定义其类型。

整数常量主要有以下几种类型：
- 十进制(decimal)
- 八进制(octal)
- 十六进制(hexadecimal)

十进制常量整数类型直接定义即可

八进制常量整数类型定义时应带前缀`0`，例如：
```C
int dec = 10;  //等于十进制的10
int oct = 010; //等于十进制的8
```

十六进制常量整数类型定义时应带前缀`0x`，例如：
```C
int hex = 0x10; //等于10进制的16
```

整数常量类型的修饰后缀：
- unsigned后缀
- long后缀
- long-long后缀

unsigned后缀可以为：
\	`u` 或者 `U`

long后缀可以为：
\	`l` 或者 `L`

long-long后缀可以为：
\	`ll` 或者 `LL`


###### 6.4.4.3 枚举(enum)

对于枚举类型的常量，其标识符的类型为 `int`

#### 6.5 表达式


##### 6.5.1

##### 6.5.2

###### 6.5.2.5 复合字面量(Compound literals)

###### 6.5.3.4 sizeof和_Alignof运算符

**限制**
`sizeof` 运算符不能用于函数类型(参数不可为函数名)或不完备的变量类型，或用括号包裹的变量类型，或含有位域的成员表达式。
`_Alignof` 运算符不能用于函数类型(参数不可为函数名)或不完备的变量类型。
如：
```C
#include <stdio.h>

typedef struct {
	int a : 2;
	int b : 2;
} typea_t;

typedef struct {
	int a;
	int b;
} typeb_t;

int main()
{
	typea_t typea;
	typeb_t typeb;
	
	printf("testa_t: %lld\r\n", sizeof(typea_t));  //4
	
	//printf("testa_t: %lld\r\n", sizeof((typea_t)));//参数不可为含括号的类型
	
	//printf("testa_t: %lld\r\n", sizeof(typea.a));  //参数不可为含位域的成员
	
	printf("testa_t: %lld\r\n", sizeof(typeb.a));  //4
	
	//printf("testa_t: %lld\r\n", sizeof(main));     //参数不可为函数名
	
	return 0;
}
```
**语义**
1. `sizeof` 运算符生成其操作数的大小(以字节为单位)，操作数可以是表达式或类型的括号名称。大小由操作数的类型决定。结果是一个整数。如果操作数的类型是可变长度数组类型，则计算该操作数<font color="#c00000">(此时不可再简单理解为宏，是运行时求值)</font>; 否则，不计算该操作数，结果为整数常量。
```C
#include <stdlib.h>

size_t vla_test(int size)
{
	int array[size];
	return sizeof(array);
}

int main()
{
    printf("%lld", vla_test(89)); //356
    return 0;
}
```
2. TODO...


##### 6.5.5 乘法类操作符(*、\/、%)

**限制**
1. 每一个操作数都应当具有算数类型。
2. 取余运算符(`%`)的操作数都应当是整数类型。

**语义**
1. 通常的算数转换是在操作数上执行的。
2. 二元运算符 `*` 的结果是两个操作数的乘积。
3. 运算符 `/` 的结果是第一个操作数除以第二个操作数的商； `%` 运算符的结果是取余数。在这两个操作中，如果第二个操作数的值为零，则<font color="#c00000">行为是未定义的</font>。
4. 当整数被分割时， `/` 运算符的结果是<font color="#c00000">丢弃所有小数部分的代数商</font>(通常被称为"向零截断")。如果商 `a/b` 是可表示的，表达式 `(a/b) * b + a%b` 应等于 `a` ; 否则，`a/b` 和 `a%b` 的行为都是未定义的。
向零截断：
```C
#include <stdio.h>
int main() {
	printf("%d\r\n", 5/3);  // 5/3=1.6667  => 1
	printf("%d\r\n", -5/3); // -5/3=-1.667 => -1
	printf("%d\r\n", -1/3); // -1/3=-0.333 => 0
}
```
5. <span style="background:#fff88f"><font color="#c00000">整数除法的结果是整数</font></span>，而非先算出小数再转整数。




#### 6.7 声明

##### 6.7.1 储存类型说明符

**语义**
储存类型说明符主要有以下几种：
- typedef
- extern
- static
- \_Thread_local
- auto
- register

**限制**
1. 除了之外 `_Thread_local` 可以和 `static` 、 `extern` 联合使用以外，一个变量最多使用一个储存类型说明符。 ^9zuwzp
2. 在具有块(block)范围的对象的声明中，如果使用了 `_Thread_local` 则他还应包含 `static` 或 `extern` 。TODO: If `_Thread_local` appears in any declaration of an object, it shall be present in every declaration of that object.
3. `_Thread_local` 不应该出现在函数声明中的说明符中。
4. `typedef`被称为储存类型说明符只是为了语法方便，这一特性在章节[[#6.7.8]]中有所讨论，TODO:且在[[#6.2.2]]和[[#6.2.4]]中讨论了各种联系以及储存周期的含义。
5. 带有`register`的说明符建议使用在需要尽可能快的访问对象的地方。当然编译器可以不听你的。
6. 具有块作用域的函数声明中不应具有除`extern`以外的显示的储存类型说明符。
7. 如果使用`typedef`以外的储存类型说明符来说明`struct`和`union`对象，则储存说明符所产生的属性也将作用于除链接(TODO:linkage?)以外的成员。

##### 6.7.2 变量类型说明符

**语义**
变量类型说明符主要有以下几种：
- void
- char
- short
- int
- long
- float
- double
- signed
- unsigned
- \_Bool
- \_Complex
- 原子类型说明符
- `struct`或`union`所定义的说明符
- `enum`所定义的说明符
- `typedef`所定义的说明符

##### 6.7.4 函数说明符

**语义**
函数说明符主要有以下两种：
- `inline`
- `_Noreturn_`

**限制**
1. 函数说明符只能用于函数的声明中(而非定义)。
2. TODO
3. 在托管(TODO:host?)环境中，任何函数说明符不应出现在`main`函数中。
4. 一个函数可以使用多个函数说明符，且说明符之间的行为不受影响。
5. `inline`修饰符建议编译器将其编译为内联干啥，主要用于尽可能快的调用该函数。当然编译器可以不听你的。
6. 内联函数有以下限制：
	1. 如果使用`inline`修饰一个函数的声明，则其应被定义在同一个翻译单元中(也就是源文件必须include其头文件，且由于该特性，内联函数可以多次被定义???)
	2. 如果inline...看不懂了TODO
7. 使用了`_Noreturn_`的函数不能返回调用者，若未写明`return`而导致函数执行完毕退出的，其结果是未定义行为，如下例中 `i <= 0` 的情况：
```C
_Noreturn_ void func(int i)
{
	if(i > 0)
	{
		abort();  //OK
	}
	// UB.
}
```


##### 6.7.5 字节对齐说明符



##### 6.7.8


##### 6.7.9 初始化

#### 6.8 语句和块

语句主要有以下几种：
- Labeled statement
- compound statement
- expression statement
- selection statement
- iteration statement
- jump statement

**语义**
1. 一个语句(statement)就是一个要执行的操作，在未说明的情况下，这些语句会按照顺序执行。
2. 块(block)允许将一组声明(如变量)和语句分组为一个语法单元。TODO


##### 6.8.1 Labeled statements

Labeled statements主要包含以下几种：
- `identifier` : statement (即普通label)
- case `constant-expression` : statement (即case+常量表达式)
- default : statement

**限制**
1. `case` 和 `default` 标签应只能在 `switch` 中出现，更多的约束将在 `switch` 语句下进行讨论。
2. `Label` 同一个**函数内**(而不是块)不能同名，标签作用域是整个函数，即可以如下：
```C
#include <stdio.h>

int main(int argc, char** argv)
{
    if(5 > 3)
    {
main :
        printf("jumped to label: \"main\"\r\n");
        goto end;
    }

    goto main;
    
end :
    return 0;
}

```

##### 6.8.2 Compound statement(复合语句，即'块'，block)

复合语句即由花括号及其包含的可选块序列 `{ block-item-list(opt) }` 构成，符合语句必须包含花括号。

**语义**
一个 `Compound statement` 就是一个块(`block`)。

#### 6.10

##### 6.10.3
###### 6.10.3.3 

##### 6.10.6 Pragma指令
[\_Pragama with msvc](https://learn.microsoft.com/zh-cn/cpp/preprocessor/pragma-directives-and-the-pragma-keyword)


#### 6.11 C语言未来的发展方向



### 7 库


#### 7.21 基本输入输出<stdio.h>

##### 7.21.6 格式化输入输出



#### 7.24 字符串库<string.h>

##### 7.24.2 拷贝函数

###### 7.24.2.1 memcpy函数

概要：
```C
#include <string.h>  
void *memcpy(void * restrict s1,  
	const void * restrict s2, 
	size_t n);
```
描述：
	`memcpy` 函数将 `s2` 指向的内存的 `n` 个字符复制到 `s1` 指向的内存中。<font color="#c00000">如果复制发生在重叠的对象之间，则行为是未定义的</font>。

返回值：
	`memcpy` 函数将返回 `s1` 指针。

###### 7.24.2.2 memmove函数

概要：
```C
#include <string.h>  
void *memmove(void *s1, const void *s2, size_t n);
```
描述：
	`memmove` 函数将 `s2` 指向的内存的 `n` 个字符复制到 `s1` 指向的内存中。复制的过程就像是将 `s2` 指向的对象中的 `n` 个字符首先复制到一个 `n` 个字符的临时数组中，这个临时数组不会与 `s1` 和 `s2` 指向的内存重叠，然后将临时数组中的 `n` 个字符复制到 `s1` 指向的内存中。

返回值：
	`memmove` 函数将返回 `s1` 指针。

注：
1. 在Windows的C运行库中(`msvcrt`)， `memcpy` 实质上就是 `memmove` ，虽然微软在MSDN中依旧是按照C语言标准进行描述。
2. 在OpenBSD系统中，如果 `memcpy` 的内存区域重叠会导致崩溃。
3. 效率上， `memcpy` 比 `memmove` 仅少了一个分支。
4. [Linus对这两个函数的评价](https://bugzilla.redhat.com/show_bug.cgi?id=638477#c129)(由于Adobe错误使用了 `memcpy` 从而导致在一次 `glibc` 升级后触发了一些bug)

###### 7.24.2.3 strcpy函数

概要：
```C
#include <string.h>  
char *strcpy(char * restrict s1,  
	const char * restrict s2);
```

描述：
	`strcpy` 函数将 `s2` 指向的字符串(包括终止空字符)复制到 `s1` 指向的数组中。<font color="#c00000">如果复制发生在重叠的对象之间，则行为是未定义的</font>。

返回值：
	`strcpy` 函数将返回 `s1` 指针。

注：
1. `strcpy` 函数操作的字符串要以 `\0` 结尾。
2. 库函数并不会检查目标的内存边界，因此<font color="#c00000">可能会导致溢出</font>。

###### 7.24.4 strncpy函数

概要：
```C
#include <string.h>  
char *strncpy(char * restrict s1, 
	const char * restrict s2, 
	size_t n);
```

描述：
1. `strncpy` 函数将不超过 `n` 个字符(空字符后面的字符不复制)从 `s2` 指向的数组复制到 `s1` 指向的数组。<font color="#c00000">如果复制发生在重叠的对象之间，则行为是未定义的</font>。
2. 如果 `s2` 指向的数组是一个比 `n` 个字符短的字符串，则空字符将附加到 `s1` 指向的数组中的副本，直到所有字符中的 `n` 个字符都写入(即后尾全为 `\0` )。

返回值：
	`strncpy` 函数将返回 `s1` 指针。

注：
1. 库函数并不会检查目标的内存边界，因此<font color="#c00000">可能会导致溢出</font>。

##### 7.24.3 连接函数(concatenation function)

###### 7.24.3.1 strcat函数

概要：
```C
#include <string.h>  
char *strcat(char * restrict s1, 
	const char * restrict s2);
```

描述：
1. `strcat` 函数将 `s2` 指向的字符串的副本(包括终止空字符)附加到 `s1` 指向的字符串的末尾。 `s2` 的初始字符覆盖 `s1` 末尾的 `null` 字符。<font color="#c00000">如果复制发生在重叠的对象之间，则行为是未定义的</font>。

返回值：
	`strcat` 函数将返回 `s1` 指针。

注：
1. 库函数并不会检查目标的内存边界，因此<font color="#c00000">可能会导致溢出</font>。

###### 7.24.3.2 strncat函数

概要：
```C
#include <string.h>  
char *strncat(char * restrict s1, 
	const char * restrict s2, 
	size_t n);
```

描述：
1. `strncat` 函数从 `s2` 指向的数组到 `s1` 指向的字符串的末尾追加不超过 `n` 个字符(空字符和跟随它的字符不被追加)。 `s2` 的初始字符覆盖 `s1` 末尾的 `null` 字符。结果总是附加一个终止空字符(因此，最终可以出现在 `s1` 指向的数组中的字符数的最大值是 `strlen (s1) + n + 1` )。<font color="#c00000">如果复制发生在重叠的对象之间，则行为是未定义的</font>。

返回值：
	`strcat` 函数将返回 `s1` 指针。

注：
1. 库函数并不会检查目标的内存边界，因此<font color="#c00000">可能会导致溢出</font>。

##### 7.24.4 比较函数

###### 7.24.4.1 memcmp函数




