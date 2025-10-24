---
number headings: auto, first-level 1, max 6, 1.1
---

# 1 目录

```toc
```

# 2 TODO

# 3 CPU启动后流程

在ARM Cortex-M的CPU开始运行之后，其<span style="background:#fff88f"><font color="#c00000">CPU会自动</font></span>：
1. 从<font color="#9bbb59">向量表基地址</font><sup>注1</sup>装入<font color="#9bbb59">主堆栈指针MSP</font>
2. 再将向量表基地址的下一条地址(`+0x04`)装入PC
<font color="#c00000">再次强调</font>，<span style="background:#fff88f"><font color="#c00000">上述步骤由CPU硬件自动完成</font></span>。

注：
1. 对于非Cortex-M0的其他CM内核，其通常拥有<font color="#9bbb59">VTOR</font>(<font color="#9bbb59">向量表基地址寄存器</font>、Vector Table Offset Register)，该寄存器可以将向量表从 `0x00000000` 映射到别处。
	1. Cortex-M0通常没有该寄存器，M0+可选，其他CM内核通常拥有该寄存器

