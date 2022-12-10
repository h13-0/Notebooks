
仓库地址：
	https://github.com/eliben/pycparser



`storage`为C语言的储存类型说明符，详见：[[C标准笔记#6.7.1 储存类型说明符]]
`funcspec`为C语言的函数说明符，详见：[[C标准笔记#6.7.4 函数说明符]]



### 抽象语法树(c_ast)

pycparser的语法树节点可由[\_c_ast.cfg](https://github.com/eliben/pycparser/blob/master/pycparser/_c_ast.cfg)配置并生成，默认情况下其提供了以下节点：

```toc
min_depth: 4
```

#### ArrayDecl




| NodeType | Meaning |
| -------- | ------- |
| ArrayDecl | 数组声明 |
| ArrayRef | 数组定义 |
| Assignment | 符号 |
| BinaryOp | 二进制运算符 |
| Break | `break` |
| Case | `case` |
| Cast | 

