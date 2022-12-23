#CMake 

```toc

```


## 添加头文件路径(include_directories)

是作用最大，影响全局,且向下传递的添加头文件路径的命令，一旦使用，对后续的所有命令均生效。
一般写在最外层以影响全局。

命令定义：
```CMake
include_directories([AFTER|BEFORE] [SYSTEM] dir1 [dir2 ...])
```

官网命令解释：
> 将给定的目录添加到编译器用来搜索头文件的目录中。相对路径被解释为相对于当前源目录。
> 
> 头目录被添加到当前CMakeLists文件的INCLUDE_DIRECTORIES目录属性中。它们还被添加到当前CMakeLists文件中每个目标的INCLUDE_DIRECTORIES目标属性中。目标属性值是生成器使用的属性值。
> 
> 默认情况下，指定的目录会附加到当前目录列表中。这个默认行为可以通过设置cmake_include_directores_before为ON来改变。通过显式地使用AFTER或BEFORE，您可以在追加和前缀之间进行选择，而不依赖于默认值。
> 
> 如果给出了SYSTEM选项，编译器将被告知在某些平台上，这些目录意味着系统包含目录。信号这个设置可能会达到一些效果，比如编译器跳过警告，或者这些固定安装的系统文件在依赖计算中不被考虑——参见编译器文档。


## 添加头文件路径(target_include_directories)

只会影响到当前项目

官网命令解释：
> **指定编译给定目标时要使用的include目录**。名为< target >的必须由add_executable()或add_library()等命令创建的，并且不能是ALIAS目标。
> 
> 通过显式地使用AFTER或BEFORE，您可以在追加和前缀之间进行选择，而不依赖于默认值。
> 
> **INTERFACE、PUBLIC和PRIVATE关键字用于（指定target_include_directories的影响范围）**

### 权限修饰符

关于权限修饰符，假设现在我们有如下依赖：
![[依赖图1.canvas]]



## 文件操作命令(file)

官方文档：
	https://cmake.org/cmake/help/latest/command/file.html

支持的操作包括搜索，写入，摘要等，具体如下：

### Reading

```CMake
  file([READ](https://cmake.org/cmake/help/latest/command/file.html#read) <filename> <out-var> [...])
  file([STRINGS](https://cmake.org/cmake/help/latest/command/file.html#strings) <filename> <out-var> [...])
  file([<HASH>](https://cmake.org/cmake/help/latest/command/file.html#hash) <filename> <out-var>)
  file([TIMESTAMP](https://cmake.org/cmake/help/latest/command/file.html#timestamp) <filename> <out-var> [...])
  file([GET_RUNTIME_DEPENDENCIES](https://cmake.org/cmake/help/latest/command/file.html#get-runtime-dependencies) [...])
```

### Writing


### FileSystem

```CMake
file(GLOB <variable>
     [LIST_DIRECTORIES true|false] [RELATIVE <path>] [CONFIGURE_DEPENDS]
     [<globbing-expressions>...])
file(GLOB_RECURSE <variable> [FOLLOW_SYMLINKS]
     [LIST_DIRECTORIES true|false] [RELATIVE <path>] [CONFIGURE_DEPENDS]
     [<globbing-expressions>...])
```

`GLOB` 只会搜索文件夹
`GLOB_RECURSE` 会遍历文件夹




