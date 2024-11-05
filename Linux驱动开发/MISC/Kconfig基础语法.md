---
number headings: auto, first-level 2, max 6, 1.1
---
#嵌入式 #Linux驱动开发 

## 1 目录

```toc
```

## 2 语法特性

### 2.1 mainmenu 主菜单标题

`mainmenu` 用于指定主菜单的标题，简单的示例如下：

```Kconfig
mainmenu "Linux/$(ARCH) $(KERNELVERSION) Kernel Configuration"
```

随后即可指定如红框内的标题：

![[MobaXterm_MkA9yoZ1ys.png]]

### 2.2 menu/endmenu 子菜单

menu子菜单的特性如下：
1. `menu` 会创建一个子菜单，菜单名跟随 `menu` 定义，即：
```Kconfig
menu "title"
# ...
endmenu
```
2. 在该子菜单中还可以再创建子菜单。
3. 该子菜单用 `endmenu` 进行结束。在结束前，其中所有选项或子菜单均隶属于该子菜单。
4. 父级菜单只会显示子菜单的名称和入口。

例如：
- 顶层Kconfig：
```Kconfig
mainmenu "mainmenu"

source "module_a/Kconfig"
source "module_b/Kconfig"

```
- `module_a/Kconfig` ：
```dts
menu "module A"

config BOOL_OPTION  
    bool  

menu "submodule"

source "module_a/submodule/Kconfig"

endmenu

endmenu
```
- `module_b/Kconfig` ：
```dts
menu "module B"

menu "submodule"

source "module_b/submodule/Kconfig"

endmenu

endmenu
```
则上述主菜单中只会出现如下的两个子菜单选项：
- `module A  --->`
- `module B  --->`
而其子选项则需要进入子菜单才可以配置。

### 2.3 config 选项



