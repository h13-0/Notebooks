
仓库地址：
	https://github.com/eliben/pycparser


## 目录

```toc

```

### 抽象语法树(c_ast)

pycparser的语法树节点可由[\_c_ast.cfg](https://github.com/eliben/pycparser/blob/master/pycparser/_c_ast.cfg)配置并生成，默认情况下其提供了以下节点：
- ArrayDecl
- ArrayRef
- Assignment
- BinaryOp
- Break
- Case
- Cast
- Compound
- CompoundLiteral
- Constant
- Continue
- Decl
- DeclList
- Default
- DoWhile
- EllipsisParam
- EmptyStatement
- Enum
- Enumerator
- EnumeratorList
- ExprList
- FileAST
- For
- FuncCall
- FuncDecl
- FuncDef
- Goto
- ID
- IdentifierType
- If
- InitList
- Label
- NamedInitializer
- ParamList
- PtrDecl
- Return
- StaticAssert
- Struct
- StructRef
- Switch
- TernaryOp
- TypeDecl
- Typedef
- Typename
- UnaryOp
- Union
- While
- Pragma

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

#### ArrayDecl

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

#### ArrayRef

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

#### Assignment

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

#### Alignas

字节对齐，即C11中的

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


#### BinaryOp

#### Break

#### Case

#### Cast(强制类型转换)

#### Compound

[[C标准笔记#6 8 2 Compound statement 复合语句，即'块'，block]]
![[C标准笔记#6 8 2 Compound statement 复合语句，即'块'，block]]


#### Decl
`storage`为C语言的储存类型说明符，详见：[[C标准笔记#6.7.1 储存类型说明符]]
`funcspec`为C语言的函数说明符，详见：[[C标准笔记#6.7.4 函数说明符]]







#### FileAST

FileAST作为AST的顶部，表示经过预处理后的单个C文件，也是C语言标准中的术语 #翻译单元 ，其包含外部声明列表("external-declaration"s)，即声明(Decl)、Typedef或函数定义(FuncDef)。

其拥有属性值：
- ext**

##### ext
是子节点序列，元素即为上述的"external-declaration"s



