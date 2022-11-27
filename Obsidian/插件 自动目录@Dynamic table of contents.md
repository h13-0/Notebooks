项目地址： https://github.com/aidurber/obsidian-plugin-dynamic-toc

# 目录
```toc

```

## 使用

使用代码块
` ```toc
` ```
即可生成代码块，在其中加入yaml配置即可进行配置
如：
` ```toc
` style: bullet
` min_depth: 4
` ```

## 配置

配置使用yaml进行配置

### style

可选项有:
```toc
min_depth: 4
max_depth: 4
```

#### bullet
竖向排列，如下
```toc
style: bullet
```

#### number
编号排列，如下：
```toc
style: number
```

#### inline
将只显示深度值为[min_depth]()(默认为2)的标题并横向排列，如下
```toc
style: inline
```

### 深度(depth)

#### min_depth
设置自动生成的目录的最低深度，例如：
最低深度为3时：
```toc
min_depth: 3
```
最低深度为4时：
```toc
min_depth: 4
```

#### max_depth
设置自动生成目录的最大深度，例如
最大深度为3时：
```toc
max_depth: 3
```

最大深度为4时：
```toc
max_depth: 4
```

### 标题(title)

即设置目录的title
```toc
title: 自动目录插件
```


### 允许深度不一致(allow_inconsistent_headings)

遇到缺失的深度时将自动前移，例如下文中的level 2 -> level 4：
```markdown
## Level 2

#### Level 4

##### Level 5

## Level 2

### Level 3
```
效果：
allow_inconsistent_headings: false(default)
![[Obsidian_qcYn5k3ZYU.png]]
allow_inconsistent_headings: true
![[Obsidian_SDeLdlStNw.png]]