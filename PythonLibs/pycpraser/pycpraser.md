
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
- 

在该文件的原文中：
```yaml
# Each entry is a Node sub-class name, listing the attributes
# and child nodes of the class:
#   <name>*     - a child node
#   <name>**    - a sequence of child nodes
#   <name>      - an attribute
```
是按照如下规则标记属性值的：
	格式为：
		`<name>* ` 的，是一个子节点
		`<name>**` 的，是子节点序列
		`<name>  ` 的，是一个属性值

#### ArrayDecl

数组声明，其拥有以下属性值：
- type
- dim
- dim_equals

**type**
是一个Node，TODO

**dim**
是一个Node，是维度，

```jupyter
print(1)
```


```
jupyter==1.0.0
jupyter-client==7.0.2
jupyter-console==6.4.0
jupyter-core==4.7.1
jupyterlab-pygments==0.1.2
jupyterlab-widgets==1.0.1
nbclient==0.5.4
nbconvert==6.1.0
nbformat==5.1.3
notebook=6.4.3
```

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