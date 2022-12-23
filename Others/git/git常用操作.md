
```toc
title: 目录
max_depth: 2
```

## 增加submodule

```bash
git submodule add <url> <path>
```

## 删除submodule

### 逆初始化子模块
```bash
git submodule deinit -f ${path}
```

### 删除 `.gitmodules` 中的cache
```bash
git rm --cached ${path}
```

### 删除 `.git/modules` 下缓存

#### Linux
```bash
rm -rf .git/modules/${path}
```

#### Windows
```powershell
Remove-Item .git/modules/${path} -recurse -force
```

## 更新submodules

```bash
git submodule update --init
```



## 从远程获取代码库(git fetch)

通常用于在 `git checkout ${commit-id}` 后遇到报错：
```shell
error: pathspec '${commit-id}' did not match any file(s) known to git
```

执行：
```shell
git fetch
```

即可

## 屏蔽文件更改(.gitignore)

通常来说，在仓库根目录创建文件 `.gitignore` 即可屏蔽文件更改，其语法如下
```gitignore
floder/
file
file/regex*
```
注意 `git` 中所有路径尽量使用windows和linux通用的路径分隔符，即 `/`
但是当文件已经被追踪过时，上述更改不能生效，仍需追加：
```bash
git rm --cached file
git rm --cached -r folder
```
即可。

## 与Github联动

### commit同时关闭issue

只需要在提交的commit中包含以下内容之一即可：
```git
+ fix #24
+ fixes #24
+ fixed #24
+ close #24
+ closes #24
+ closed #24
+ resolve #24
+ resolves #24
+ resolved #24
```
