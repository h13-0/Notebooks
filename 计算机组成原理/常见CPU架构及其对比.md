---
number headings: first-level 2, max 6, 1.1
---
#计算机组成原理 

## 1 目录

```toc
```

## 2 常见CPU架构及其对应型号

常见的CPU架构有及其对应型号如下：
- 冯诺依曼架构：Intel、ARM7、MIPS
- 哈佛架构：AVR、ARM9-11、Arm Cortex A

## 3 主要区别

### 3.1 存储器及存储器总线设计区别

![[msedge_xQyvK1ZPQi.png]]

#### 3.1.1 冯诺依曼架构

1. 冯诺依曼架构的<font color="#c00000">指令存储器和数据存储器被合并到了一起</font>，因此程序<font color="#c00000">指令地址和程序数据地址指向同一个存储器的不同物理位置</font>。
2. 因为合并到了一起，因此程序和数据要通过同一条总线进行传输

#### 3.1.2 哈佛架构

1. 哈佛架构将<font color="#c00000">程序和数据存储器独立存储</font>，因此程序的<font color="#c00000">指令和数据可以有不同的数据宽度</font>。
2. <font color="#c00000">指令存储器</font>、<font color="#c00000">数据存储器</font>到CPU之间<font color="#c00000">均有一条独立的总线</font>，有较高的执行效率。
3. <span style="background:#fff88f"><font color="#c00000">改进的哈佛架构</font></span>：



