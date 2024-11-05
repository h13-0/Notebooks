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

`menu` 会创建一个子菜单，并且在该子菜单中
