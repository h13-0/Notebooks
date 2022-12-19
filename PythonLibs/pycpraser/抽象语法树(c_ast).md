#pycpraser 

pycparser的语法树节点可由[\_c_ast.cfg](https://github.com/eliben/pycparser/blob/master/pycparser/_c_ast.cfg)配置并生成，默认情况下其提供了以下节点(Node)：
```toc
min_depth: 3
max_depth: 3
```

在该文件的原文中是按照如下规则标记属性值的：
```yaml
# Each entry is a Node sub-class name, listing the attributes
# and child nodes of the class:
#   <name>*     - a child node
#   <name>**    - a sequence of child nodes
#   <name>      - an attribute
```
即：
	`<name>* ` 的，是一个子节点
	`<name>**` 的，是子节点序列
	`<name>  ` 的，是一个属性值

### ArrayDecl

数组声明，其拥有以下属性值：
- type*
- dim**
- dim_equals

当其为一位数组时，该

**type**
是一个Node，TODO

**dim**
是一个Node，是维度，TODO

Demo
```C
int length = 10;
int arr[5][length] = { 0 };
```

```AST
FileAST(ext=[Decl(name='length',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='length',
                                quals=[
                                      ],
                                align=None,
                                type=IdentifierType(names=['int'
                                                          ]
                                                    )
                                ),
                  init=Constant(type='int',
                                value='10'
                                ),
                  bitsize=None
                  ),
             Decl(name='arr',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=ArrayDecl(type=ArrayDecl(type=TypeDecl(declname='arr',
                                                              quals=[
                                                                    ],
                                                              align=None,
                                                              type=IdentifierType(names=['int'
                                                                                        ]
                                                                                  )
                                                              ),
                                                dim=ID(name='length'
                                                       ),
                                                dim_quals=[
                                                          ]
                                                ),
                                 dim=Constant(type='int',
                                              value='5'
                                              ),
                                 dim_quals=[
                                           ]
                                 ),
                  init=InitList(exprs=[Constant(type='int',
                                                value='0'
                                                )
                                      ]
                                ),
                  bitsize=None
                  )
            ]
        )
```

### ArrayRef

数组值引用，其拥有以下属性值：
- name*
- subscript*

**name**


**subscript**



Demo
```C
int array[10] = { 0 };
int val = array[5];
```

```AST
FileAST(ext=[Decl(name='array',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=ArrayDecl(type=TypeDecl(declname='array',
                                               quals=[
                                                     ],
                                               align=None,
                                               type=IdentifierType(names=['int'
                                                                         ]
                                                                   )
                                               ),
                                 dim=Constant(type='int',
                                              value='10'
                                              ),
                                 dim_quals=[
                                           ]
                                 ),
                  init=InitList(exprs=[Constant(type='int',
                                                value='0'
                                                )
                                      ]
                                ),
                  bitsize=None
                  ),
             Decl(name='val',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='val',
                                quals=[
                                      ],
                                align=None,
                                type=IdentifierType(names=['int'
                                                          ]
                                                    )
                                ),
                  init=ArrayRef(name=ID(name='array'
                                        ),
                                subscript=Constant(type='int',
                                                   value='5'
                                                   )
                                ),
                  bitsize=None
                  )
            ]
        )
```

### Assignment

赋值操作符，有以下几种：
- `=`
- `*=`
- `/=`
- `%=`
- `+=`
- `-=`
- `<<=`
- `>>=`
- `&=`
- `|=`
- `^=`

其拥有以下属性值：
- op
- lvalue*
- rvalue*

**op**
类型为字符串，是上述操作符的字符串形式

**lvalue**
左值

**rvalue**
右值

Demo
```C
void func()
{
    int val = 0;
    val += 1;
}
```

```AST
FileAST(ext=[FuncDef(decl=Decl(name='func',
                               quals=[
                                     ],
                               align=[
                                     ],
                               storage=[
                                       ],
                               funcspec=[
                                        ],
                               type=FuncDecl(args=None,
                                             type=TypeDecl(declname='func',
                                                           quals=[
                                                                 ],
                                                           align=None,
                                                           type=IdentifierType(names=['void'
                                                                                     ]
                                                                               )
                                                           )
                                             ),
                               init=None,
                               bitsize=None
                               ),
                     param_decls=None,
                     body=Compound(block_items=[Decl(name='val',
                                                     quals=[
                                                           ],
                                                     align=[
                                                           ],
                                                     storage=[
                                                             ],
                                                     funcspec=[
                                                              ],
                                                     type=TypeDecl(declname='val',
                                                                   quals=[
                                                                         ],
                                                                   align=None,
                                                                   type=IdentifierType(names=['int'
                                                                                             ]
                                                                                       )
                                                                   ),
                                                     init=Constant(type='int',
                                                                   value='0'
                                                                   ),
                                                     bitsize=None
                                                     ),
                                                Assignment(op='+=',
                                                           lvalue=ID(name='val'
                                                                     ),
                                                           rvalue=Constant(type='int',
                                                                           value='1'
                                                                           )
                                                           )
                                               ]
                                   )
                     )
            ]
        )
```

### Alignas

字节对齐，即C11中的 `_Alignas` ，[[C标准笔记#6 7 5 字节对齐说明符]]，其拥有以下属性：
- alignment*

**alignment**
是一个Node，含义为对齐参数

Demo
```C
int _Alignas(8) a;
int b;
```

```AST
FileAST(ext=[Decl(name='a',
                  quals=[
                        ],
                  align=[Alignas(alignment=Constant(type='int',
                                                    value='8'
                                                    )
                                 )
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='a',
                                quals=[
                                      ],
                                align=None,
                                type=IdentifierType(names=['int'
                                                          ]
                                                    )
                                ),
                  init=None,
                  bitsize=None
                  ),
             Decl(name='b',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='b',
                                quals=[
                                      ],
                                align=None,
                                type=IdentifierType(names=['int'
                                                          ]
                                                    )
                                ),
                  init=None,
                  bitsize=None
                  )
            ]
        )
```

### BinaryOp

二进制运算符，有以下几种：
- `+`
- `-`
- `*`
- `/`
- `%`
- `|`
- `&`
- `~`
- `^`
- `<<`
- `>>`
- `||`
- `&&`
- `!`
- `<`
- `>`
- `<=`
- `>=`
- `==`
- `!=`

其拥有如下属性：
- op
- left*
- right*

**op**
类型为字符串，是上述操作符的字符串形式

TODO.

Demo
```C
int a = 1;
int b = a == 1;
```

```AST
FileAST(ext=[Decl(name='a',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='a',
                                quals=[
                                      ],
                                align=None,
                                type=IdentifierType(names=['int'
                                                          ]
                                                    )
                                ),
                  init=Constant(type='int',
                                value='1'
                                ),
                  bitsize=None
                  ),
             Decl(name='b',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='b',
                                quals=[
                                      ],
                                align=None,
                                type=IdentifierType(names=['int'
                                                          ]
                                                    )
                                ),
                  init=BinaryOp(op='==',
                                left=ID(name='a'
                                        ),
                                right=Constant(type='int',
                                               value='1'
                                               )
                                ),
                  bitsize=None
                  )
            ]
        )
```

### Break

Demo
```C
void func()
{
    while(1)
    {
        break;
    }
}
```

```AST
FileAST(ext=[FuncDef(decl=Decl(name='func',
                               quals=[
                                     ],
                               align=[
                                     ],
                               storage=[
                                       ],
                               funcspec=[
                                        ],
                               type=FuncDecl(args=None,
                                             type=TypeDecl(declname='func',
                                                           quals=[
                                                                 ],
                                                           align=None,
                                                           type=IdentifierType(names=['void'
                                                                                     ]
                                                                               )
                                                           )
                                             ),
                               init=None,
                               bitsize=None
                               ),
                     param_decls=None,
                     body=Compound(block_items=[While(cond=Constant(type='int',
                                                                    value='1'
                                                                    ),
                                                      stmt=Compound(block_items=[Break()
                                                                                ]
                                                                    )
                                                      )
                                               ]
                                   )
                     )
            ]
        )
```

### Case



### Cast(强制类型转换)

### Compound

[[C标准笔记#6 8 2 Compound statement 复合语句，即'块'，block]]
![[C标准笔记#6 8 2 Compound statement 复合语句，即'块'，block]]


### CompoundLiteral
[[C标准笔记#6.5.2.5 复合字面量(Compound literals)]]
![[C标准笔记#6.5.2.5 复合字面量(Compound literals)]]

Demo
```C
int *p = (int[]) { 1, 2, 3 };
```

```AST
FileAST(ext=[Decl(name='p',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=PtrDecl(quals=[
                                     ],
                               type=TypeDecl(declname='p',
                                             quals=[
                                                   ],
                                             align=None,
                                             type=IdentifierType(names=['int'
                                                                       ]
                                                                 )
                                             )
                               ),
                  init=CompoundLiteral(type=Typename(name=None,
                                                     quals=[
                                                           ],
                                                     align=None,
                                                     type=ArrayDecl(type=TypeDecl(declname=None,
                                                                                  quals=[
                                                                                        ],
                                                                                  align=None,
                                                                                  type=IdentifierType(names=['int'
                                                                                                            ]
                                                                                                      )
                                                                                  ),
                                                                    dim=None,
                                                                    dim_quals=[
                                                                              ]
                                                                    )
                                                     ),
                                       init=InitList(exprs=[Constant(type='int',
                                                                     value='1'
                                                                     ),
                                                            Constant(type='int',
                                                                     value='2'
                                                                     ),
                                                            Constant(type='int',
                                                                     value='3'
                                                                     )
                                                           ]
                                                     )
                                       ),
                  bitsize=None
                  )
            ]
        )
```

### Constant

即常量，其属性有：
- type
- value

**type**

**value**

Demo
```C
const int a = 1;
int b = 0;
```

```AST
FileAST(ext=[Decl(name='a',
                  quals=['const'
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='a', 
                                quals=['const'
                                      ],      
                                align=None,   
                                type=IdentifierType(names=['int'
                                                          ]
                                                    )
                                ),
                  init=Constant(type='int',
                                value='1'
                                ),
                  bitsize=None
                  ),
             Decl(name='b',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='b',
                                quals=[
                                      ],
                                align=None,
                                type=IdentifierType(names=['int'
                                                          ]
                                                    )
                                ),
                  init=Constant(type='int',
                                value='1'
                                ),
                  bitsize=None
                  )
            ]
        )
```

### Continue



### Decl



所有声明语句均为Decl，
其属性有：
- name
- quals
- align
- storage
- funcspec
- type*
- init*
- bitsize*

#### `name`
`name` 仅为声明对象的名字，类型为字符串

#### `quals`
`quals` 为对象的限定符，包含：

- \[[[C标准笔记#^rbqfe0|限制说明符]]\]
	- `const`
	- `volatile`
	- `restrict`

#### `align`



#### `storge`
storage` 为C语言的储存类型说明符，详见：[[C标准笔记#6.7.1 储存类型说明符]]
- \[[[C标准笔记#6 7 1 储存类型说明符|储存类型说明符]]\]
	- `typedef`
	- `extern`
	- `static`
	- `_Thread_local`
	- `auto`
	- `register`
当然，同笔记中所言：
![[C标准笔记#^9zuwzp]]


`funcspec` 为C语言的函数说明符，详见：[[C标准笔记#6.7.4 函数说明符]]

最小示例：


```C

```


### DeclList

```C
int a, b;
```

### Default

### DoWhile

### EllipsisParam

```C
int mprint(char* fmt, ...);
```

### EmptyStatement

```C
;
```


### Enum

Demo
```C
enum enum_type { a, b, c };
enum enum_type obj;
```
则其中的 `obj` 即为 `Enum` ， `a` 则为 `Enumerator` ， `{ a, b, c }` 则为 `EnumeratorList`

```AST
FileAST(ext=[Decl(name=None,
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=Enum(name='enum_type',
                            values=EnumeratorList(enumerators=[Enumerator(name='a',
                                                                          value=None
                                                                          ),
                                                               Enumerator(name='b',
                                                                          value=None
                                                                          ),
                                                               Enumerator(name='c',
                                                                          value=None
                                                                          )
                                                              ]
                                                  )
                            ),
                  init=None,
                  bitsize=None
                  ),
             Decl(name='obj',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='obj',
                                quals=[
                                      ],
                                align=None,
                                type=Enum(name='enum_type',
                                          values=None
                                          )
                                ),
                  init=None,
                  bitsize=None
                  )
            ]
        )
```

### Enumerator

Demo
```C
enum enum_type { a, b, c };
enum enum_type obj;
```
则其中的 `obj` 即为 `Enum` ， `a` 则为 `Enumerator` ， `{ a, b, c }` 则为 `EnumeratorList`

```AST
FileAST(ext=[Decl(name=None,
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=Enum(name='enum_type',
                            values=EnumeratorList(enumerators=[Enumerator(name='a',
                                                                          value=None
                                                                          ),
                                                               Enumerator(name='b',
                                                                          value=None
                                                                          ),
                                                               Enumerator(name='c',
                                                                          value=None
                                                                          )
                                                              ]
                                                  )
                            ),
                  init=None,
                  bitsize=None
                  ),
             Decl(name='obj',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='obj',
                                quals=[
                                      ],
                                align=None,
                                type=Enum(name='enum_type',
                                          values=None
                                          )
                                ),
                  init=None,
                  bitsize=None
                  )
            ]
        )
```

### EnumeratorList

Demo
```C
enum enum_type { a, b, c };
enum enum_type obj;
```
则其中的 `obj` 即为 `Enum` ， `a` 则为 `Enumerator` ， `{ a, b, c }` 则为 `EnumeratorList`

```AST
FileAST(ext=[Decl(name=None,
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=Enum(name='enum_type',
                            values=EnumeratorList(enumerators=[Enumerator(name='a',
                                                                          value=None
                                                                          ),
                                                               Enumerator(name='b',
                                                                          value=None
                                                                          ),
                                                               Enumerator(name='c',
                                                                          value=None
                                                                          )
                                                              ]
                                                  )
                            ),
                  init=None,
                  bitsize=None
                  ),
             Decl(name='obj',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='obj',
                                quals=[
                                      ],
                                align=None,
                                type=Enum(name='enum_type',
                                          values=None
                                          )
                                ),
                  init=None,
                  bitsize=None
                  )
            ]
        )
```

### ExprList

Demo
```C
int a, b, c = (a = 1, b = 2);
```
expression list以逗号为分隔，其表达式值为最后一个语句的值，此时的 `a` 、 `b` 、 `c` 分别为 `1` 、 `2` 、 `2` 。

```AST
FileAST(ext=[Decl(name='a',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='a',
                                quals=[
                                      ],
                                align=None,
                                type=IdentifierType(names=['int'
                                                          ]
                                                    )
                                ),
                  init=None,
                  bitsize=None
                  ),
             Decl(name='b',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='b',
                                quals=[
                                      ],
                                align=None,
                                type=IdentifierType(names=['int'
                                                          ]
                                                    )
                                ),
                  init=None,
                  bitsize=None
                  ),
             Decl(name='c',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='c',
                                quals=[
                                      ],
                                align=None,
                                type=IdentifierType(names=['int'
                                                          ]
                                                    )
                                ),
                  init=ExprList(exprs=[Assignment(op='=',
                                                  lvalue=ID(name='a'
                                                            ),
                                                  rvalue=Constant(type='int',
                                                                  value='1'
                                                                  )
                                                  ),
                                       Assignment(op='=',
                                                  lvalue=ID(name='b'
                                                            ),
                                                  rvalue=Constant(type='int',
                                                                  value='2'
                                                                  )
                                                  )
                                      ]
                                ),
                  bitsize=None
                  )
            ]
        )
```

### FileAST

FileAST作为AST的顶部，表示经过预处理后的单个C文件，也是C语言标准中的术语 #翻译单元 ，其包含外部声明列表("external-declaration"s)，即声明(Decl)、Typedef或函数定义(FuncDef)。

其拥有属性值：
- ext**

**ext**
是子节点序列，元素即为上述的"external-declaration"s


### For


### FuncCall

### FuncDecl

### FuncDef

### Goto

### IdentifierType

```C
int a;
```

```AST
FileAST(ext=[Decl(name='a',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='a',
                                quals=[
                                      ],
                                align=None,
                                type=IdentifierType(names=['int'
                                                          ]
                                                    )
                                ),
                  init=None,
                  bitsize=None
                  )
            ]
        )
```

### InitList

Demo

```C
int a[3] = { 1, 2, 3 };
```

```AST
FileAST(ext=[Decl(name='a',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=ArrayDecl(type=TypeDecl(declname='a',
                                               quals=[
                                                     ],
                                               align=None,
                                               type=IdentifierType(names=['int'
                                                                         ]
                                                                   )
                                               ),
                                 dim=Constant(type='int',
                                              value='3'
                                              ),
                                 dim_quals=[
                                           ]
                                 ),
                  init=InitList(exprs=[Constant(type='int',
                                                value='1'
                                                ),
                                       Constant(type='int',
                                                value='2'
                                                ),
                                       Constant(type='int',
                                                value='3'
                                                )
                                      ]
                                ),
                  bitsize=None
                  )
            ]
        )
```

### NamedInitializer

Demo
```C
struct { int a; int b; } obj = { .a = 1, .b = 2 };
```

```AST
FileAST(ext=[Decl(name='obj',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='obj',
                                quals=[
                                      ],
                                align=None,
                                type=Struct(name=None,
                                            decls=[Decl(name='a',
                                                        quals=[
                                                              ],
                                                        align=[
                                                              ],
                                                        storage=[
                                                                ],
                                                        funcspec=[
                                                                 ],
                                                        type=TypeDecl(declname='a',
                                                                      quals=[
                                                                            ],
                                                                      align=None,
                                                                      type=IdentifierType(names=['int'
                                                                                                ]
                                                                                          )
                                                                      ),
                                                        init=None,
                                                        bitsize=None
                                                        ),
                                                   Decl(name='b',
                                                        quals=[
                                                              ],
                                                        align=[
                                                              ],
                                                        storage=[
                                                                ],
                                                        funcspec=[
                                                                 ],
                                                        type=TypeDecl(declname='b',
                                                                      quals=[
                                                                            ],
                                                                      align=None,
                                                                      type=IdentifierType(names=['int'
                                                                                                ]
                                                                                          )
                                                                      ),
                                                        init=None,
                                                        bitsize=None
                                                        )
                                                  ]
                                            )
                                ),
                  init=InitList(exprs=[NamedInitializer(name=[ID(name='a'
                                                                 )
                                                             ],
                                                        expr=Constant(type='int',
                                                                      value='1'
                                                                      )
                                                        ),
                                       NamedInitializer(name=[ID(name='b'
                                                                 )
                                                             ],
                                                        expr=Constant(type='int',
                                                                      value='2'
                                                                      )
                                                        )
                                      ]
                                ),
                  bitsize=None
                  )
            ]
        )
```


### pragma

[[C标准笔记#6.10.6 Pragma指令]]
![[C标准笔记#6.10.6 Pragma指令]]

Demo
```C
#pragma once
```

```AST
FileAST(ext=[Pragma(string='once'
                    )
            ]
        )
```

### PtrDecl

Demo
```C
int *a;
```

```AST
FileAST(ext=[Decl(name='a',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=PtrDecl(quals=[
                                     ],
                               type=TypeDecl(declname='a',
                                             quals=[
                                                   ],
                                             align=None,
                                             type=IdentifierType(names=['int'
                                                                       ]
                                                                 )
                                             )
                               ),
                  init=None,
                  bitsize=None
                  )
            ]
        )
```


### Return


### Struct

### TernaryOp


### TypeDecl

### Typename



### UnaryOp

Demo
```C
char a = ! 0xf0;
```

```AST
FileAST(ext=[Decl(name='a',
                  quals=[
                        ],
                  align=[
                        ],
                  storage=[
                          ],
                  funcspec=[
                           ],
                  type=TypeDecl(declname='a',
                                quals=[
                                      ],
                                align=None,
                                type=IdentifierType(names=['char'
                                                          ]
                                                    )
                                ),
                  init=UnaryOp(op='!',
                               expr=Constant(type='int',
                                             value='0xf0'
                                             )
                               ),
                  bitsize=None
                  )
            ]
        )
```




### Union


### While