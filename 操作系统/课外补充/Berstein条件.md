#操作系统

## 目录

```toc
```

## 概述

Berstein条件是程序可并发执行的条件。
以 ${\rm R}(P_i)$ 计为进程或线程 $P_i$ 对某一互斥资源的读取操作，以 ${\rm W}(P_i)$ 计为进程或线程 $P_i$ 对某一互斥资源的写入操作。则在满足如下两个条件时，程序可以并发执行：
$${\rm Cond1}:\forall i,j<n, i\neq j, {\rm W}(P_i)\cap {\rm R}(P_j)=\varnothing$$
$${\rm Cond2}:\forall i,j<n, i\neq j, {\rm W}(P_i)\cap {\rm W}(P_j)=\varnothing$$
