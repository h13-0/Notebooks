#C-Language 

```toc

```

## attribute(param)相关


### weak

弱函数


## 语法糖

### case范围

gcc中支持case范围，其用法为：

```C
case low ... high:
```

例如下方代码：

```C
int c = 9;

switch(c) {
case 1: case 2: case 3: case 4: case 5:
    printf("c in [1, 5]");
    break;
case 6 ... 10:
    printf("c in [6, 10]");
    break;
default:
    break;
}
```

的 `case 6 ... 10:` 等价于 `case 6: case 7: case 8: case 9: case 10:` 。
但是注意不要写成 `case 6...10:` 。
