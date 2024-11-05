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

`config` 选项的<font color="#c00000">基本</font>格式如下：

```Kconfig
config ${name}
	${type} ${title}
	[${default}]
	[${depends or select}]
	[help]
		[${tips}]
```

其中：
- `${name}` <font color="#c00000">为必须项</font>，<font color="#c00000">用于生成.config文件中的配置项</font>，生成结果为 `CONFIG_${name}` 。
- `${type}` <font color="#c00000">为必须项</font>，可选类型包含 `bool` 、 `tristate` 、 `string` 、 `hex` 、 `int`。其中 `tristate` 为三态，用于表示内核模块的编译配置，值有 `y` 、 `m` 、 `n` 三种。
- `${title}` <font color="#c00000">为必须项</font>，<font color="#c00000">是该选项在menuconfig界面中的选项名</font>。
- `${default}` ，可选项，默认值。
- `${depends or select}` ，可选项，[[Kconfig基础语法#2 3 1 依赖关系 depends on、select|依赖关系]]。
- `help` 为帮助标签，可选项。
- `${tips}` 为帮助提示，配合 `help` 使用。当聚焦于目标选项时，按下 `h` 键即可查看帮助信息。

#### 2.3.1 依赖关系(depends on、select)

依赖关系分为正向依赖关系( `depends on` )和反向依赖关系( `select` )两种：
- 正向依赖关系是指声明了该依赖关系的选项只有当依赖的选项被选中后<font color="#c00000">才会出现</font>。
- 反向依赖关系是指当声明了该关系的选项被选中后，其 `select` 的选项也会被<font color="#c00000">强制选中</font>。

例如：

```Kconfig
CONFIG BASE_FUNC1
	bool "base function1"

CONFIG ADVANCED_FUNC1
	bool "advanced function1"
	depends on BASE_FUNC1
```

则会当选中 `"base function1"` 后，`"advanced function1"` 选项才会出现。

而例如：

```Kconfig
CONFIG BASE_FUNC2
	bool "base function2"

CONFIG ADVANCED_FUNC2
	bool "advanced function2"
	select BASE_FUNC2
```

则 `"advanced function2"` 会一直出现，并且若 `"advanced function2"` 被选中，则 `"base function2"` 无法被取消选中。

### 2.4 choice/endchoice 单选项

`choice` 可以把若干个config选项组合成一个单选项目。例如下方代码：

```Kconfig
#  
# Select the backing stores to be supported  
#  
choice  
    prompt "RomFS backing stores"  
    depends on ROMFS_FS  
    default ROMFS_BACKED_BY_BLOCK  
    help  
      Select the backing stores to be supported.  
  
config ROMFS_BACKED_BY_BLOCK  
    bool "Block device-backed ROM file system support"  
    depends on BLOCK  
    help  
      This permits ROMFS to use block devices buffered through the page  
      cache as the medium from which to retrieve data.  It does not allow  
      direct mapping of the medium.  
  
      If unsure, answer Y.  
  
config ROMFS_BACKED_BY_MTD  
    bool "MTD-backed ROM file system support"  
    depends on MTD=y || (ROMFS_FS=m && MTD)  
    help  
      This permits ROMFS to use MTD based devices directly, without the  
      intercession of the block layer (which may have been disabled).  It  
      also allows direct mapping of MTD devices through romfs files under  
      NOMMU conditions if the underlying device is directly addressable by  
      the CPU.  
  
      If unsure, answer Y.  
  
config ROMFS_BACKED_BY_BOTH  
    bool "Both the above"  
    depends on BLOCK && (MTD=y || (ROMFS_FS=m && MTD))  
endchoice
```

将三个选项组合成了一个单选项目，这一组中只有一个选择框可以被选中：
![[MobaXterm_n1CHLv2Nx0.png]]
![[MobaXterm_LbWbzHA5LI.png]]

### 2.5 comment 选项注释


