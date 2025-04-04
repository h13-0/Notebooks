#C-Language #编译原理 

	Standards are paper. I use paper to wipe my butt every day. 
	That's how much that paper is worth. —— Linus Torvalds.

## 目录

```toc
min_depth: 1
```

## 5. 环境

### 5.1 概念模型

#### 5.1.1 翻译环境

##### 5.1.1.1 程序结构

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

#### 5.1.2 运行环境

运行环境有以下两种：
- 独立环境(freestanding)
- 托管环境(hosted)

无论在哪种环境下，C程序都会被环境调用。在C程序启动之前，所有的静态储存类型[^1]都会被初始化[^2]并设定为初始值。这种初始化的方式和时间均未具体规定，程序终止后控制权将返回到运行环境。

**引用**
[^1]: 静态储存环境
	[[C标准学习笔记#6.7.1 储存类型说明符]]
[^2]: 初始化
	[[#6.7.9]]

##### 5.1.2.1 独立环境

##### 5.1.2.2 托管环境

###### 5.1.2.2.1 托管环境下的程序启动

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

###### 5.1.2.2.2 托管环境中的程序运行

在托管环境中，程序可以使用章节[[#7 库]]中的所有函数、宏、类型定义和对象。

5.1.2.2.3 托管环境中的程序终止

TODO

##### 5.1.2.3 程序执行

### 5.2 环境因素



## 6. 语言

### 6.2 概念

#### 6.2.1 标识符的范围
#### 6.2.2

#### 6.2.4

#### 6.2.5 类型

26. 限制说明符...TODO..包含 `const` 、 `volatile` 、 `restrict`  ^rbqfe0
27. 

### 6.3 转换

#### 6.3.1 算数操作数

##### 6.3.1.1 布尔、字符和整数

1. TODO
2. 
3. 整数类型提升会保留符号位。正如上述讨论，是否将普通的 `char` 视为 `signed char` 是实现定义的。

### 6.4 词法元素

#### 6.4.1 关键词(Keywords)

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

#### 6.4.2 标识符(Identifiers)

##### 6.4.2.1 普通标识符

**句法规则**
	TODO 没看懂什么意思，编译原理相关

**语义**
1. 标识符是一系列非数字字符（包括下划线 `_` 、小写和大写拉丁字母以及其他字符）和数字，用于指定[[C标准学习笔记#6 2 1 标识符的范围]]中所述的一个或多个实体。小写字母和大写字母是不同的。<font color="#c00000">标识的最大长度没有具体限制</font>。
2. 标识符中的每个通用字符名称应为在ISO/IEC 10646中的编码D.1.71中规定的范围中的一个字符。首字母字符不应是通用字符名称，该名称指定的字符的编码属于D.2中规定的范围之一。作为一种实现方式，可以允许不属于基本源字符集的多字节字符出现在标识符中；其实现定义了哪些字符及其与通用字符名的对应关系。
3. 当在翻译阶段7中将预处理token转换为token时，如果预处理token可以转换为关键字或标识符，则将其转换为关键字。

**实现限制**

##### 6.4.2.2 预定义标识符





#### 6.4.4 常量(Constants)

常量类型主要有
- 整数常数
- 浮点常数
- 枚举常数
- 还没看懂

**限制**
每一个常量类型都应具有类型，并且其值应在对应类型的可表示范围之内。

##### 6.4.4.1 整数

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


##### 6.4.4.3 枚举(enum)

对于枚举类型的常量，其标识符的类型为 `int`


##### 6.4.4.4 字符常量





### 6.5 表达式


#### 6.5.1

#### 6.5.2

##### 6.5.2.5 复合字面量(Compound literals)

##### 6.5.3.4 sizeof和_Alignof运算符

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


#### 6.5.5 乘法类操作符(*、\/、%)

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

#### 6.5.5 位移运算符

**语义**

**限制**
	每一个操作数都应当为整数类型。

**语义**
1. 位移运算会对每个操作数的类型进行提升，提升结果是运算符左侧操作数的类型。<span style="background:#fff88f"><font color="#c00000">如果右侧操作数的值是负值或超过了左侧操作数的宽度，则该行为是未定义行为</font></span>。
2. `E1 << E2` 的结果是 `E1` 左移 `E2` 位的位置，<font color="#c00000">空位用零填充</font>。如果 `E1` 是无符号类型，则结果的值为： $$E_1\times2^{E_2}$$，比结果类型中可表示的最大值多减少一个模。如果 `E1` 有符号类型的非负值，并且$$E_{1}\times 2^{E2}$$在结果类型中是可表示的，那么这就是结果值; 否则该行为<font color="#c00000">是未定义行为</font>。
3. `E1 >> E2` 的结果是 `E1` 右移 `E2` 位的位置，<font color="#c00000">空位用零填充</font>。如果 `E1` 是无符号类型，则结果的值为：$$E_{1}/2^{E_2}$$，如果 `E1` 是一个有符号类型的负值，则<font color="#c00000">结果是由实现来定义的</font>。

#### 6.5.17 逗号运算符

**句法**

**语义**
1. 逗号运算符的左操作数被当做 `void` 表达式进行计算(即不考虑返回值)；然后计算右操作数，并且将右操作数的值作为该表达式的值。
2. 如句法所示，逗号运算符不能出现在使用逗号分隔列表中的项的上下文中(例如函数的参数或初始值设定项列表)，例如：
```C
int a[] = { 1, 2, 3 }; //此处逗号不生效，仅当分隔符。
printf("This line is: %d\r\n", __LINE__); //此处逗号也不生效。
```
3. 逗号表达式可以在带括号的表达式中使用，也可以在条件运算符的第二表达式中使用。
```C
int a = 5;
func(a, (t=3, t+2), c);  //等价于 fuc(5, 5, c);

if(a, a+1 > 5)
{
    printf("value of `a, a+1` is 6\r\n");
}
```
4. 计算顺序为从左向右依次执行。

### 6.7 声明

#### 6.7.1 储存类型说明符

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

#### 6.7.2 变量类型说明符

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

#### 6.7.4 函数说明符

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


#### 6.7.5 字节对齐说明符

#### 6.7.6

##### 6.7.6.2 数组声明

#### 6.7.8


#### 6.7.9 初始化

### 6.8 语句和块

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

#### 6.8.1 Labeled statements

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

#### 6.8.2 Compound statement(复合语句，即'块'，block)

复合语句即由花括号及其包含的可选块序列 `{ block-item-list(opt) }` 构成，符合语句必须包含花括号。

**语义**
一个 `Compound statement` 就是一个块(`block`)。

### 6.10

#### 6.10.3
##### 6.10.3.3 

#### 6.10.6 Pragma指令
[\_Pragama with msvc](https://learn.microsoft.com/zh-cn/cpp/preprocessor/pragma-directives-and-the-pragma-keyword)


### 6.11 C语言未来的发展方向



## 7. 库


### 7.21 基本输入输出<stdio.h>

#### 7.21.5 文件访问函数

##### 7.21.5.1 fclose函数

**概要**
```C
#include <stdio.h>
int fclose(FILE *stream);
```

**描述**
1. 当 `fclose` 成功调用时，文件流会被flush并关闭，流中缓冲区的：
	1. 所有未写入到文件的数据将会被投送至宿主环境以写入到文件中。
	2. 所有未被程序接收但已被读出是数据会被丢弃。
2. 无论调用成功与否，文件和 `stream` 都将解除关联，由 `setbuf` 和 `setvbuf` 所设置的缓冲区也会和 `stream` 解除关联(如果是自动分配的缓冲区，则会自动的调用析构函数)。

**返回值**
1. 如果成功将返回 `0` ，不成功将返回 `EOF` 。

##### 7.21.5.2 fflush函数

**概要**
```C
#include <stdio.h>
int fflush(FILE *stream);
```

**描述**
1. 如果流指向一个输出流(例如 `stdout` )或更新流，其中最近的操作没有输入，则 `fflush` 函数将导致该流的任何未写数据被传送到主机环境，并写入文件；否则，行为是未定义的(例如操作只读流 `fflush(stdin)` )。
2. 如果 `stream` 的参数值为 `NULL` ，则 `fflush` 会刷新程序中定义的所有流。

**返回值**
1. 若 `fflush` 正常执行则会返回 `0` ，否则则会设置错误标识符并返回 `EOF` 。

##### 7.21.5.3 fopen函数

**概要**
```C
#include <stdio.h>  
FILE *fopen(const char * restrict filename,
	const char * restrict mode);
```

**描述**
1. `fopen` 函数打开名称(路径)为 `filename` 的文件，返回一个与该文件绑定的 `FILE*` 指针。
2. `mode` 参数应当是以下字符串之一，随后将以对应的模式打开文件。<span style="background:#fff88f"><font color="#c00000">若非以下字符串则行为未定义</font></span>。

| <center>mode</center> | <center>打开模式</center>                                                                                                                                                                                                                                                                                                               |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "r"                   | 以<font color="#c00000">字符读取</font>方式打开文件。                                                                                                                                                                                                                                                                                           |
| "w"                   | 以<font color="#c00000">字符读取</font>方式<font color="#c00000">覆盖</font>(即从0)<span style="background:#fff88f"><font color="#c00000">或</font></span>创建新文件。                                                                                                                                                                                |
| "wx"                  | 以<font color="#c00000">字符读取</font>方式创建新文件并写入<br>- <span style="background:#fff88f"><font color="#c00000">若已存在该文件则操作失败，并返回NULL</font></span><br>通常用此避免覆盖掉原来的文件("x"表示强制使用新文件，仅可配合"w"和"w+"使用)                                                                                                                                          |
| "a"                   | 以<font color="#c00000">字符读取</font>方式追加方式打开文件：<br>- 当文件存在时，<span style="background:#fff88f"><font color="#c00000">会从文件尾开始追加</font></span>(即 `EOF` 前)<br>- 当文件不存在时，<span style="background:#fff88f"><font color="#c00000">会创建该文件</font></span>。                                                                                       |
| "r+"                  | 以<font color="#c00000">字符读取</font>方式<span style="background:#fff88f"><font color="#c00000">读取或写入文件</font></span>：<br>- <span style="background:#fff88f"><font color="#c00000">此时指针置于文件头</font></span>，且不会截断文件(与下方"w+"的第一个区别)。<br>- <span style="background:#fff88f"><font color="#c00000">如果文件不存在则操作失败</font></span>(与下方"w+"的另一区别)。 |
| "w+"                  | 以<font color="#c00000">字符读取</font>方式<span style="background:#fff88f"><font color="#c00000">读取或写入文件</font></span>：<br>- <span style="background:#fff88f"><font color="#c00000">如果文件存在则会从文件头截断</font></span>(即覆盖，文件长度清零)。<br>- <span style="background:#fff88f"><font color="#c00000">如果文件不存在则会创建新文件</font></span>。                   |
| "w+x"                 | 以<font color="#c00000">字符读取</font>方式<span style="background:#fff88f"><font color="#c00000">读取或写入文件</font></span>：<br>- <span style="background:#fff88f"><font color="#c00000">如果文件存在则会从文件头截断</font></span>。<br>- <span style="background:#fff88f"><font color="#c00000">如果文件不存在则操作失败</font></span>。                                 |
| "a+"                  | 以<font color="#c00000">字符读取</font>方式<span style="background:#fff88f"><font color="#c00000">写入文件</font></span>，<span style="background:#fff88f"><font color="#c00000">此时指针置于文件头</font></span>。(不可读取)                                                                                                                                 |
|                       |                                                                                                                                                                                                                                                                                                                                     |
| "rb"                  | 以<font color="#c00000">二进制读取</font>方式打开文件。                                                                                                                                                                                                                                                                                          |
| "wb"                  | 以<font color="#c00000">二进制读取</font>方式<font color="#c00000">覆盖</font>(即从0)<span style="background:#fff88f"><font color="#c00000">或</font></span>创建新文件                                                                                                                                                                                |
| "wbx"                 | 以<font color="#c00000">二进制读取</font>方式创建新文件并写入(<span style="background:#fff88f"><font color="#c00000">若已存在该文件则操作失败，并返回NULL</font></span>，通常用此避免覆盖掉原来的文件)                                                                                                                                                                             |
| "ab"                  | 以<font color="#c00000">二进制读取</font>方式追加方式打开文件，当文件存在时，会从 `EOF` 前开始追加；当文件不存在时，<span style="background:#fff88f"><font color="#c00000">会创建该文件</font></span>。                                                                                                                                                                            |
| "rb+" 或 "r+b"         | 以<font color="#c00000">二进制读取</font>方式<span style="background:#fff88f"><font color="#c00000">读取或写入文件</font></span>，<span style="background:#fff88f"><font color="#c00000">此时指针置于文件头</font></span>。                                                                                                                                   |
| "wb+" 或 "w+b"         |                                                                                                                                                                                                                                                                                                                                     |
| "wb+x" 或 "w+bx"       |                                                                                                                                                                                                                                                                                                                                     |
| "a+b" 或 "ab+"         |                                                                                                                                                                                                                                                                                                                                     |

简单来说，mode主要为以下关键字的组合：

| key | 作用和注意事项 |
| --- | ------- |
|     |         |

#### 7.21.6 格式化输入输出

##### 7.21.6.1 fprintf函数

**概要**
```C
#include <stdio.h>
int fprintf(FILE * restrict stream,
	const char * restrict format, ...);
```

**描述**
1. `fprintf` 函数会将字节流按照 `format` 所指字符串中所指定的输出格式输出到 `stream` 所指向的流中。
2. 如果给定的参数比 `format` 所需的参数少，<span style="background:#fff88f"><font color="#c00000">则行为未定义</font></span>。
3. 如果给定的参数比 `format` 所需的参数多，则多余的表达式<font color="#c00000">也会被计算</font>，<font color="#c00000">然后被忽略</font>。
4. `fprintf` 处理到 `format` 所指字符串的末尾字符 `\0` 后返回。
5. `format` 应为字符序列，普通的多字节流(除了 `%` 符)会原封不动的输出，每一个占位符都由 `%` 符引入，
TODO 补全翻译

#### 7.21.7 字符输入输出函数

##### 7.21.7.1 fgetc函数

概要：
```C
#include <stdio.h> 
int fgetc(FILE *stream);
```

描述：
1. 如果输入 `stream` 没有设置 `EOF` 指示符，并且存在下一个字符，`fgetc` 函数将获得该字符作为 `unsigned char` 转换为 `int` (本质还是 `char` ，只是类型变了)，并推进该流的相关文件位置指示符(如果已定义)。

返回值：
1. 如果设置了 `stream` 的 `EOF` 指示符且 `stream` 处于 `EOF` 位置， `fgetc` 函数将返回 `EOF` 。否则 `fgetc` 函数将返回由 `stream` 指向的输入流中的下一个字符。如果发生读取错误，则设置流的错误指示符，并返回 `EOF` 。其中，读到的 `EOF` 是由于文件到达末尾还是读取时发生错误可以使用 `feof` 或 `ferror` 函数区分。

##### 7.21.7.2 fgets函数

概要：
```C
#include <stdio.h>  
char *fgets(char * restrict s, int n, 
	FILE * restrict stream);
```

描述：
1. `fgets` 函数从流中读取至多 `n - 1` 个字符并存入 `s` 所指字符串中。在新行(可能是 `\n` )字符之后或文件结束之后不会读取任何其他字符(其中新行字符会被保留)。并会在字符串末尾立即添加一个 `\0` 字符(哪怕结尾是换行符)。

返回值：
1. 如果读取成功， `fgets` 函数将返回 `s` 。如果遇到 `EOF` 并且数组中没有读入任何字符，则数组的内容保持不变并返回空指针。如果在操作期间发生读取错误，则数组内容是不确定的，并返回空指针。

##### 7.21.7.3 fputc函数







##### 7.21.7.5 getc函数

概要：
```C
#include <stdio.h>  
int getc(FILE *stream);
```

描述：
1. `getc` 函数等价于 `fgetc` ，是 `fgetc` 的通过宏的实现。但是如果它被当做宏来调用时，它可能不止一次操作 `stream` ，因此参数绝不应该是带有<font color="#c00000">副操作</font>的表达式。

<font color="#c00000">副操作</font>例如：
```C
#include <stdio.h>
#define MACRO_SQRT(x) x*x 

int func_sqrt(int x) 
{
	return x*x;
} 

int main() {
	int x = 10,y = 10;
	int xx,yy;
	xx = func_sqrt(++x);
	printf("xx = %d, x = %d\n",xx,x);  //xx = 121, x = 11
	yy = MACRO_SQRT(++y);
	printf("yy = %d, y = %d\n",yy,y);  //yy = (++y)*(++y) => UB, y = 12; ++y就是副操作。
	return 0;
}
```
而 `getc` 和 `fgetc` 之间的关系就类似于上方程序中 `MACRO_SQRT` 和 `func_sqrt` 的关系，当出现类似于如下操作就可能出现问题：
```C
FILE streams[] = { ... };
int index = 0;
while(index < n)
	getc(&streams[index++]); //不要这样做，因为执行一次getc可能会触发多次index++
```

返回值：
1. `getc` 函数返回由流指向的输入流中的下一个字符。如果流处于文件结束位置，则设置流的文件结束指示符，并且 `getc` 返回 `EOF`。如果发生读取错误，则设置流的错误指示符，并且 `getc` 返回 `EOF` 。

##### 7.21.7.6 getchar函数

概要：
```C
#include <stdio.h>  
int getchar(void);
```

描述：
1. `getchar()` 函数等价于 `getc(stdin)` 。

返回值：
1. `getchar` 函数返回 `stdin` 指向的输入流中的下一个字符。如果流处于文件结束位置，则设置流的文件结束指示符，并且 `getchar` 返回 `EOF` 。如果发生读取错误，则设置流的错误指示符，并且 `getchar` 返回 `EOF` 。

##### 7.21.7.7 putc函数

**概要**
```C
#include <stdio.h>  
int putc(int c, FILE *stream);
```

**描述**
1. 与getc函数([[C标准学习笔记#7 21 7 5 getc函数]])相似，`putc` 函数等价于 `fputc` ，是 `fputc` 的通过宏的实现。因此参数绝不应该是带有<font color="#c00000">副操作</font>的表达式(副操作见getc章节)。

**返回值**
1. `putc` 函数返回写入的字符。如果发生写入错误，则设置流的错误指示符，随后返回 `EOF` 。

##### 7.21.7.8 putchar函数

**概要**
```C
#include <stdio.h>  
int putchar(int c);
```

**描述**
1. `putchar` 函数等价于 `putc` 函数的第二个参数为 `stdout` 的情况。

**返回值**
1. 与 `putc` 函数的第二个参数为 `stdout` 的情况相同。

##### 7.21.7.9 puts函数

**概要**
```C
#include <stdio.h>
int puts(const char *s);
```

**描述**
1. `puts` 函数将 `s` 指向的字符串写入 `stdout` 指向的流，<span style="background:#fff88f"><font color="#c00000">并将一个新行字符附加到输出</font></span>，<span style="background:#fff88f"><font color="#c00000">且不写入终止空字符</font></span> `\0` 。

**返回值**
1. 如果发生写错误，`puts` 函数返回 `EOF` ；否则返回非负值。

笔记注：
1. 一般的 `txt` 文件中也不用 `\0` 分割句子，一般 `txt` 文件是指可直接阅读的文件，而 `\0` 通常不可阅读。

##### 7.21.7.10

#### 7.21.9 文件定位函数









### 7.24 字符串库<string.h>

#### 7.24.2 拷贝函数

##### 7.24.2.1 memcpy函数

**概要**
```C
#include <string.h>  
void *memcpy(void * restrict s1,  
	const void * restrict s2, 
	size_t n);
```
**描述**
1. `memcpy` 函数将 `s2` 指向的内存的 `n` 个字符复制到 `s1` 指向的内存中。<font color="#c00000">如果复制发生在重叠的对象之间，则行为是未定义的</font>。

**返回值**
1. `memcpy` 函数将返回 `s1` 指针。

##### 7.24.2.2 memmove函数

**概要**
```C
#include <string.h>  
void *memmove(void *s1, const void *s2, size_t n);
```
**描述**
1. `memmove` 函数将 `s2` 指向的内存的 `n` 个字符复制到 `s1` 指向的内存中。复制的过程就像是将 `s2` 指向的对象中的 `n` 个字符首先复制到一个 `n` 个字符的临时数组中，这个临时数组不会与 `s1` 和 `s2` 指向的内存重叠，然后将临时数组中的 `n` 个字符复制到 `s1` 指向的内存中。

**返回值**
1. `memmove` 函数将返回 `s1` 指针。

笔记注：
1. 在Windows的C运行库中(`msvcrt`)， `memcpy` 实质上就是 `memmove` ，虽然微软在MSDN中依旧是按照C语言标准进行描述。
2. 在OpenBSD系统中，如果 `memcpy` 的内存区域重叠会导致崩溃。
3. 效率上， `memcpy` 比 `memmove` 仅少了一个分支。
4. [Linus对这两个函数的评价](https://bugzilla.redhat.com/show_bug.cgi?id=638477#c129)(由于Adobe错误使用了 `memcpy` 从而导致在一次 `glibc` 升级后触发了一些bug)

##### 7.24.2.3 strcpy函数

**概要**
```C
#include <string.h>  
char *strcpy(char * restrict s1,  
	const char * restrict s2);
```

**描述**
	`strcpy` 函数将 `s2` 指向的字符串(包括终止空字符)复制到 `s1` 指向的数组中。<font color="#c00000">如果复制发生在重叠的对象之间，则行为是未定义的</font>。

**返回值**
	`strcpy` 函数将返回 `s1` 指针。

笔记注：
1. `strcpy` 函数操作的字符串要以 `\0` 结尾。
2. 库函数并不会检查目标的内存边界，因此<font color="#c00000">可能会导致溢出</font>。

##### 7.24.2.4 strncpy函数

**概要**
```C
#include <string.h>  
char *strncpy(char * restrict s1, 
	const char * restrict s2, 
	size_t n);
```

**描述**
1. `strncpy` 函数将不超过 `n` 个字符(空字符后面的字符不复制)从 `s2` 指向的数组复制到 `s1` 指向的数组。<font color="#c00000">如果复制发生在重叠的对象之间，则行为是未定义的</font>。
2. 如果 `s2` 指向的数组是一个比 `n` 个字符短的字符串，则空字符将附加到 `s1` 指向的数组中的副本，直到所有字符中的 `n` 个字符都写入(即后尾全为 `\0` )。

**返回值**
	`strncpy` 函数将返回 `s1` 指针。

笔记注：
1. 库函数并不会检查目标的内存边界，因此<font color="#c00000">可能会导致溢出</font>。

#### 7.24.3 连接函数(concatenation function)

##### 7.24.3.1 strcat函数

**概要**
```C
#include <string.h>  
char *strcat(char * restrict s1, 
	const char * restrict s2);
```

**描述**
1. `strcat` 函数将 `s2` 指向的字符串的副本(包括终止空字符)附加到 `s1` 指向的字符串的末尾。 `s2` 的初始字符覆盖 `s1` 末尾的 `null` 字符。<font color="#c00000">如果复制发生在重叠的对象之间，则行为是未定义的</font>。

**返回值**
	`strcat` 函数将返回 `s1` 指针。

注：
1. 库函数并不会检查目标的内存边界，因此<font color="#c00000">可能会导致溢出</font>。

##### 7.24.3.2 strncat函数

**概要**
```C
#include <string.h>  
char *strncat(char * restrict s1, 
	const char * restrict s2, 
	size_t n);
```

**描述**
1. `strncat` 函数从 `s2` 指向的数组到 `s1` 指向的字符串的末尾追加不超过 `n` 个字符(空字符和跟随它的字符不被追加)。 `s2` 的初始字符覆盖 `s1` 末尾的 `null` 字符。结果总是附加一个终止空字符(因此，最终可以出现在 `s1` 指向的数组中的字符数的最大值是 `strlen (s1) + n + 1` )。<font color="#c00000">如果复制发生在重叠的对象之间，则行为是未定义的</font>。

**返回值**
	`strcat` 函数将返回 `s1` 指针。

笔记注：
1. 库函数并不会检查目标的内存边界，因此<font color="#c00000">可能会导致溢出</font>。

#### 7.24.4 比较函数

##### 7.24.4.1 memcmp函数

**摘要**
```C
#include <string.h>  
int memcmp(const void *s1, const void *s2, size_t n);
```
**描述**
1. `memcmp` 函数将 `s1` 指向的对象的前 `n` 个字符与 `s2` 指向的对象的前 `n` 个字符进行比较。

**返回值**
1. `memcmp` 函数可能会返回大于、等于、或小于0的值，该函数将从 `s1` 和 `s2` 的第一个字节进行对比，直到遇见第一个不相等的字节，并返回 `s1` 的字节 减去 `s2` 的字节的值。若完全指向内容在前 `n` 字节完全相等，则返回0。

**标准注**
1. 需要注意结构体中为了内存对齐而导致的 `holes` 。
2. 分配空间短于 `n` 的内存和 `s1` 和 `s2` 重合的内存可能会出现问题。

##### 7.24.4.2 strcoll函数

**摘要**
```C
#include <string.h>  
int strcoll(const char *s1, const char *s2);
```

**描述**
1. `strcoll` 函数会将 `s1` 指向的字符串与 `s2` 指向的字符串先根据语言环境(`LC_COLLATE`变量)进行重新解释，然后再进行比较。主要用于unicode环境。

**返回值**
1. 同 `strcmp` 。

笔记注：
1. `strcoll` 和 `strcmp` 的区别可见讨论[https://stackoverflow.com/questions/14087062/](https://stackoverflow.com/questions/14087062/)。
2. 执行速度自然不如 `strncmp` 。

##### 7.24.4.3


#### 7.24.5 搜索函数

##### 7.24.5.1 memchr函数

**摘要**
```C
#include <string.h>
void *memchr(const void *s, int c, size_t n);
```

**描述**
1. `memchr` 函数从 `s` 指向的内存的前 `n` 个字符(每个字符都被解释为 `unsigned char` ，实际上也就是前 n Byte)中定位第一个值 `c` 的内存地址( `c` 也会被解释为 `unsigned char` )。
2. 此函数类似于从指定长度的字符串中找到第一个指定字符。

**返回值**
1. 如果找到匹配的指定字符 `c` ，则将返回 `c` 第一次出现的地址，若没有找到指定字符，则返回 `NULL` 。

笔记注：
1. 关于为什么 `memchr` 会将 `int c` 解释为 `unsigned char` ，而 `strchr` 会将 `int c` 解释为 `char` 的讨论可见如下内容：
	![[CPP/应试笔记与八股#2 48 为什么在C语言中，一定要用unsigned char表示byte而非signed char或char]]

##### 7.24.5.2 strchr函数

**摘要**
```C
#include <string.h>
char *strchr(const char *s, int c);
```

**描述**
1. `strchr` 函数将从 `s` 所指字符串中找出第一个字符 `c` 出现的位置。字符串 `s` 遇到 `\0` 自动截止，字符 `c` 会被转换为 `char` 。

**返回值**
1. 如果在字符串中找到指定字符 `c` ，则返回该字符第一次出现的地址，若没有找到指定字符，则返回 `NULL` 。

##### 7.24.5.3 strcspn函数

**摘要**
```C
#include <string.h>
size_t strcspn(const char *s1, const char *s2);
```

**描述**
1. `strcspn` 函数将计算从字符串 `s1` 的第一个字符开始，最大连续不包含字符串 `s2` 中任意字符的数量(此时 `s2` 被看做一个字符集合而非字符串)。
2. 可以把该函数理解为从 `s1` 中查找字符集 `s2` 中的字符，返回值为<font color="#c00000">第一次出现字符集中字符的字符号-1</font>。可见下方笔记示例。

**返回值**
1. `strcspn` 函数将返回从 `s1` 头部开始最大的不包含字符集合 `s2` 中任意字符的数量。

笔记示例：
```C
int func()
{
	const char str1[] = "ABCDEF4960910";
	const char str2[] = "013";           // 字符集合 { '0', '1', '3' }
	int len = strcspn(str1, str2);       // 从str1的开头开始统计有多少不在集合中的字符
	printf("len = %d\r\n", len);         // len = 9，"ABCDEF496"长度为9
	
	// 另一种理解
	if(len == strlen(str1))
	{
		printf("No characters found in the character set str2 in str1\r\n");
	} else {
		printf("The first character in the character set str2 in str1 is %c, locate at %d\r\n", str[len], len + 1);
	}
	return 0;
}
```

##### 7.24.5.4

##### 7.24.5.5

##### 7.24.5.6

##### 7.24.5.7 strstr函数

**摘要**
```C
#include <string.h>
char *strstr(const char *s1, const char *s2);
```

**描述**
1. `strstr` 函数会从 `s1` 所指字符串中寻找 `s2` 字符串所指子串第一次出现的位置。上述字符串均以 `\0` 为截断。

**返回值**
1. `strstr` 函数将返回 `s1` 中第一次出现子串 `s2` 位置的指针，如果 `s1` 中没有子串 `s2` ，则返回 `NULL` 。
2. 如果 `s2` 为零长度字符串(即 `{ '\0' }` )，则返回值为 `s1` 。

##### 7.24.5.8 strtok函数

**摘要**

```C
#include <string.h>
char *strtok(char * restrict s1,
	const char * restrict s2);
```

**描述**

1. `strtok` 函数通常会被一系列的调用：在首次调用时其会在 `s1` 字符串中搜索 `s2` <span style="background:#fff88f"><font color="#c00000">中的所有字符</font></span>， `s2` <font color="#c00000">字符中的</font><span style="background:#fff88f"><font color="#c00000">任意一个字符都是单独的分隔符</font></span>。在后续搜索原 `s1` 字符串时，参数 `s1` 需要保持为 `NULL` 。
2. 该函数搜索出的字符字串不包含 `s2` <span style="background:#fff88f"><font color="#c00000">字符串中的任意一个字符</font></span>，当有搜索结果时会返回原 `s1` 字符串内存区域内的指向下一字串的指针，当无更多子串时返回 `NULL` 。
3. `strtok` 函数会保存指向后续字符的指针，从而实现后续 `s1` 参数为 `NULL` 的搜索。
4. <font color="#c00000">该函数并没有考虑竞态问题</font>，<span style="background:#fff88f"><font color="#c00000">因此应当避免和其他函数同时使用</font></span>(<span style="background:#fff88f"><font color="#c00000">竞态时应当使用</font></span> `strtok_s` )。

**返回值**

1. `strtok` 函数返回 `s1` 内存区域内的被 `s2` 字符串中所有字符集合作为分隔符的第一个字串的指针。如果 `s1` 不包含 `s2` 字符串中的所有字符集合，则返回 `NULL` 。
2. 示例：
```C
#include <string.h>

static char str[] = "?a???b,,,#c";
char *t;

// 1. 在 "?a???b,,,#c" 中搜索字符集合 { '?' }, 
//    并将 '\0' 插入到第一个被分割字串的结尾。
//    此时 str="\0a\0??b,,,#c", t 所表示的字符串为 "a"
t = strtok(str, "?");

// 2. 在 "??b,,,#c" 中搜索字符集合 { ',' }, 
//    并将 '\0' 插入到第一个被分割字串的结尾。
//    此时 str="\0a\0??b\0,,#c", t 所表示的字符串为 "??b"
t = strtok(NULL, ",");

// 3. 在 ",,#c" 中搜索字符集合 { '#', ',' }, 
//    并将 '\0' 插入到第一个被分割字串的结尾。
//    此时 str="\0a\0??b\0\0\0\0c", t 所表示的字符串为 "c"
t = strtok(NULL, "#,");

// 4. 此时 t = NULL
t = strtok(NULL, "?");
```

笔记注：
1. <span style="background:#fff88f"><font color="#c00000">该函数会修改输入的s1字符串</font></span>，会将 `\0` <font color="#c00000">插入到后续字符串中</font><span style="background:#fff88f"><font color="#c00000">第一个被分隔子串的结束位置</font></span><font color="#c00000">用于分割字串</font>，具体可见上方示例。

## 附录K 边界检查接口


#### K.3.5.4 字符输入输出函数
##### K.3.5.4.1 gets_s函数

**摘要**
```C
#define __STDC_WANT_LIB_EXT1__ 1  
#include <stdio.h>  
char *gets_s(char *s, rsize_t n);
```

**运行时限制**
1. `s` 不应当为空指针
2. TODO

**描述**
1. `gets_s` 函数从 `stdin` 指向的流中读入最多比 `n` 少一个的字符并且存储到 `s` 指向的数组中，在新行字符(该新行字符会被丢弃)或文件结束后不会读入任何其他字符。
2. 被丢弃的新行字符不计入读取的字符数。
3. 在将最后一个字符读入数组后立即写入空字符。


笔记注：
1. C11标准正式移除 `get_s` 函数。


## 先前版本(已被删除或修改)

## 7. 库


### 7.21 基本输入输出<stdio.h>


#### 7.21.7 字符输入输出函数


#### gets函数

**摘要**
```C
#include <stdio.h>
char *gets(char *s);
```




