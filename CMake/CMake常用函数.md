#CMake 

```toc

```


## 添加头文件路径(include_directories)

```CMake
include_directories()
```


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




