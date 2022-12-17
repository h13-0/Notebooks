
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

