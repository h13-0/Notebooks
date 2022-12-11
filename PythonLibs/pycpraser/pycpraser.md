
仓库地址：
	https://github.com/eliben/pycparser




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
- type
- dim
- dim_equals

当其为一位数组时，该

**type**
是一个Node，TODO

**dim**
是一个Node，是维度，

Demo:
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

```jupyter
import pycparser as pyc

code = """
int length = 10;
int arr[5][length] = { 0 };
"""

parser = pyc.CParser()
ast = parser.parse(code)
print(ast)
```
例如上述代码，

#### ArrayRef


#### Assignment

#### BinaryOp

#### Break

#### Case

#### Cast(强制类型转换)



#### Decl
`storage`为C语言的储存类型说明符，详见：[[C标准笔记#6.7.1 储存类型说明符]]
`funcspec`为C语言的函数说明符，详见：[[C标准笔记#6.7.4 函数说明符]]

[[C标准笔记#6 8 2 Compound statement 复合语句，即'块'，block]]
![[C标准笔记#6 8 2 Compound statement 复合语句，即'块'，block]]