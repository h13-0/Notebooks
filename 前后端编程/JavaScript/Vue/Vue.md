#Vue #前端

## 目录

```toc
```

## Vue

Vue是JavaScript的一个开发框架，

其主要风格有：
- 选项式(Vue2的风格)
- 组合式(Vue3主推)

### Vue应用形式

在本章节中主要<span style="background:#fff88f"><font color="#c00000">介绍</font></span>如下两种使用Vue的方法，在章节[[Vue#单文件组件开发 vue]]之前将先试用在HTML中加载Vue的方式进行学习。

#### 在普通HTML网页文件中加载Vue

普通的HTML模板应当为：

```html
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Document</title>
</head>
<body>
</body>
</html>
```

随后应当在 `body` 中创建一个控件，设定id，并将Vue通过id挂载到该控件上。

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <div id="app">
        
    </div>

    <script type="module">
        import {createApp} from "https://unpkg.com/vue@3/dist/vue.esm-browser.js"
        createApp({
            setup(){
                })

                return {
                }

            }
        }).mount("#app")
    </script>
</body>
</html>
```

随后即可在代码段加入JavaScript代码或在id为 `app` 的 `div` 中加入控件。
该方式的主要优点是方便理解。
使用该方式的开发源码应当保存为 `.html` 格式。

#### 使用单文件组件开发vue应用

通常在IDE或编辑工具中会内置一个如下的Vue模板：

```JavaScript
<template>

</template>

<script>
export default {

}
</script>

<style>

</style>
```

向：
- `template` 中编写原先HTML中的 `<div id="app">` 的控件
- `script` 中编写原先 `setup` 中的代码
- 

随后使用 `npm run dev` 即可进行运行。

在本章中主要是介绍"存在使用Vue模板进行创建Vue应用"的开发方式，<span style="background:#fff88f"><font color="#c00000">具体方式可见章节</font></span>[[Vue#单文件组件开发 vue]]。
使用该方式开发的源码应当保存为 `.vue` 格式。

### View控件




#### 事件监听(@event、v-on:event)

可以通过在控件中设置监听函数的方法来监听控件的事件，例如下列代码中：
```html
<!DOCTYPE html>
<!-- ... -->
<body>
	<div id="app">
		{{ text }}
		<input type="text" v-on:keydown.enter="enter(true)" @keyup.enter="enter(false)">
	</div>
</body>
</html>
```

在上述代码中，将：
- <font color="#c00000">按键按下</font>( `keydown` )且按键为 `enter` 时执行 `enter(true)` 
- <font color="#c00000">按键松开</font>( `keyup` ) 且按键为 `enter` 时执行 `enter(false)` 
且 `v-on:event` 与 `@event` 等效。
类似的，可以用：
- `v-on:keyup.ctrl.enter` 监听<span style="background:#fff88f"><font color="#c00000">同时松开</font></span><font color="#c00000">ctrl和enter</font>的事件。<font color="#c00000">监听非tab按键尽量用on事件</font>。
- `@keydown.tab` <font color="#c00000">监听按下tab的事件</font>。<font color="#c00000">监听tab事件要用down事件，因为会切换焦点</font>。

```javascript
import {createApp, reactive, ref} from "https://unpkg.com/vue@3/dist/vue.esm-browser.js"
createApp({
	setup(){
		const text = ref("ready")
		
		const enter_down = () => {
			text.value = "enter"
		}
		
		const enter = (pressed) => {
			if(pressed) {
				text.value = "enter"
			} else {
				text.value = "release"
			}
		}

		return {
			text,
			enter
		}
	}
}).mount("#app")
```

就创建了一端正文和一个文本框，并在文本框中按下 `enter` 键时文本框显示为 `enter` ，松开时显示为 `release` 。

#### 控件隐藏()



#### 控件条件渲染(v-if、v-else-if、v-else)

可以在控件中设置条件渲染属性来控制该控件是否被渲染，例如：
```html
<p v-if="web.user < 1000">当前用户量小于1000</p>
<p v-else-if="web.user == 1000">当前用户量等于1000</p>
<p v-else="web.user > 1000">当前用户量大于1000</p>
```

注意：
- <font color="#c00000">条件渲染会修改DOM树</font>而<font color="#c00000">控件隐藏不会</font>，因此不适合频繁切换元素显示状态的场景

#### 动态属性绑定(v-bind、:)

动态属性绑定是指将空间的属性绑定到一个变量上，当变量发生变化时其属性值也会跟着改变。如果不使用动态绑定，则属性无法成功设置，例如：
```html
<button v-on:click="img1">img1</button>
<button @click="img2">img2</button>
<!--尝试将变量web.url设置为img的src属性-->
<img src=web.url></img>
```

```JavaScript
import {createApp, reactive, ref} from "https://unpkg.com/vue@3/dist/vue.esm-browser.js"
createApp({
	setup(){
		const web = reactive({
			title:"Sharing Space",
				url:"https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg"
		})
		
		const img1 = () => {
			web.url = "https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg"
		}

		const img2 = () => {
			web.url = "https://fuss10.elemecdn.com/8/27/f01c15bb73e1ef3793e64e6b7bbccjpeg.jpeg"
		}
		return {
			web,
			img1,
			img2
		}

	}
}).mount("#app")
```

则此时无法成功绑定：
	![[chrome_S7wiFEHML1.png]]
浏览器中的html代码为：
	![[chrome_87TbOgybv4.png]]

因此此时需要使用动态属性绑定才可以将变量值绑定到控件属性上，有以下两种写法：
- 在前面加上 `v-bind:` ，即： `<img v-bind:src=web.url></img>`
- 直接加 `:` ，即： `<img :src=web.url></img>`

随后即可正常显示：
	![[chrome_H8Xfks2sWn.png]]

#### 控件遍历(v-for)

当有遍历数组或遍历对象的需求时，可以先建立一个容器(通常使用 `div` 标签)，然后在该容器中使用 `v-for` 进行元素的遍历与创建，例如：

```html
<div v-for="src in imgs.url">
	<img :src="src"></img>
</div>
```

```JavaScript
const imgs = reactive({
	num: 4,
	url: [
		"https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg",
		"https://fuss10.elemecdn.com/8/27/f01c15bb73e1ef3793e64e6b7bbccjpeg.jpeg",
		"https://cube.elemecdn.com/6/94/4d3ea53c084bad6931a56d5158a48jpeg.jpeg",
		"https://fuss10.elemecdn.com/3/28/bbf893f792f03a54408b3b7a7ebf0jpeg.jpeg"
	]
})
	return {
		imgs
	}
```

随后即可在 `div` 容器中遍历 `imgs.url` 数组并创建4个图像。
当然也可以在取数组元素的同时获取该数组的 `index` ，即：

```html
<div v-for="(src, index) in imgs.url">
	<img :src="src"></img>
</div>
```

或者读取类的键值对：

```html
<ul v-for="(value, key, index) in data.class1">
	<li>index: {{index}}, key: {{key}}, value: {{value}}</li>
</ul>
```

```JavaScript
const data = reactive({
	class1:{
		key1:"value1",
		key2:"value2"
	}
})
```

或者直接读取类：

```html
<ul v-for="(value, index) in data.list">
	<li>
		index: {{index}}, id: {{value.id}}, text:{{value.text}}
	</li>
</ul>
```

```JavaScript
const data = reactive({
	list:[
		{ id:10010, text:"中国电信"},
		{ id:10016, text:"中国联通"},
		{ id:10086, text:"中国移动"}
	]
})
```

当然也可以结合条件渲染进行条件显示：
```html
<ul v-for="(value, key, index) in data.class1">
	<li v-if="index == 0">
		index: {{index}}, key: {{key}}, value: {{value}}
	</li>
</ul>
```

#### 双向数据绑定(v-model)

前文的动态属性绑定只能动态同步由 `JavaScript` 代码中导致的变量变化导致的控件属性值变化，无法将由控件属性值的变化同步到 `JavaScript` 代码中的变量变化。而双相数据绑定就解决了该问题。

```html
<input type="text" v-model="text">
{{text}}
```

```JavaScript
const text = ref("")
```

此外， `v-model` <span style="background:#fff88f"><font color="#c00000">可以设置同步条件或其他操作</font></span>，例如：
- `v-model.lazy` 在控件失去焦点后同步数据
- `v-model.number` 将输入框的值转化为数字类型
- `v-model.trim` 去除首尾空格

#### 渲染数据(v-html、v-text)

使用该功能可以将变量中的字符串按照html渲染或者渲染为text，不过按照html渲染之后无法再使用vue特性。(TODO 待深入理解)

```html
<p v-html="html"></p>
```

```JavaScript
const html = ref("<button>btn1</button>")
```

随后即可正常生成一个
注意：
- <font color="#c00000">由于将变量渲染为html了，因此尽量避免XSS跨站攻击</font>
- 可以用于设定css布局等

#### 计算属性(computed)

计算属性相较于普通函数，其提供了一种<font color="#c00000">使用缓存避免相同数据重复计算</font>的一种方法。
需要注意 `comp_add` 是属性而非方法，<font color="#c00000">不需要使用括号</font>：

```html
x:<input type="number" v-model.lazy="x"><br>
y:<input type="number" v-model.lazy="y"><br>
<button :click="comp_add">calc</button><br>
Result: {{ comp_add }}
```

计算属性 `computed` 需要在模块化加载Vue时手动导入，即：

```JavaScript
import {createApp, ref, computed} from "https://unpkg.com/vue@3/dist/vue.esm-browser.js"
```

随后即可使用 `computed` 特性，其参数应当为一个函数：

```JavaScript
const x = ref(10)
const y = ref(20)
const comp_add = computed(() => {
	console.log("Run computed func.")
	return x.value + y.value
})
```

打开本页面及调试窗口，可以看到日志区有一条日志输出
	![[chrome_ZISCvbsvld.png]]
反复按动 `calc` 按钮，数字保持不变，且日志区无新增日志输出，该数据不会被反复计算。
修改x或y的数值后，日志区会新增对应日志输出，如下图所示：
	![[chrome_DWKLIR5ecq.png]]
但是直到该值下一次变化之前，均不会有新的日志出现，函数不会被重复计算。
<font color="#c00000">注意</font>：
1. 被计算的参数应当是 `ref` 或 `reactive` 等数据格式

#### 监听器(watch)

监听器提供了一种监听变量变化的方法，当变量发生变化时，该监听器构造时填入的监听函数会被调用。可以配合双相数据绑定使用。

```html
<input type="text" v-model.lazy="text">
```

监听器在模块化引入时，同样需要单独导入：

```JavaScript
import {createApp, ref, watch} from "https://unpkg.com/vue@3/dist/vue.esm-browser.js"
```

```JavaScript
const text = ref("")
watch(text, (new_text, old_text) => {
	console.log("text edited, new text: " + new_text)
})
```

随后当文本框失去焦点，触发数据同步后，该监听函数也会被执行：
	![[chrome_tMbCDWaYIr.png]]

#### 自动监听器(watchEffect)

上一章节的监听器需要手动设置被监听的变量，自动监听器则会在其使用的<font color="#c00000">任意</font>变量发生变动时，自动执行对应函数。

```html
<input type="text" v-model.lazy="userName"><br>
<select v-model="gender">
	<option value="">请选择</option>
	<option value="male">male</option>
	<option value="female">female</option>
	<option value="武装直升机">武装直升机</option>
</select>
```

同样在模块化加载Vue时，需要加载 `watchEffect` 模块，此处省略。

```JavaScript
const userName = ref("")
const gender = ref("")

watchEffect(() => {
	console.log("userName: " + userName.value)
	console.log("gender: " + gender.value)
})
```

进行操作时，只要自动监听器中的变量发生变化，则自动监听器会被自动触发：
	![[chrome_bxpCUczA7f.png]]
<font color="#c00000">注意</font>：
1. <font color="#c00000">在自动监听器中</font>， `ref` 类型<font color="#c00000">需要用</font> `value` <font color="#c00000">取值</font>，<font color="#c00000">但是监听器中不需要</font>。

### 单文件组件开发(.vue)

在html开发方式的基础之上，Vue提供了直接使用Vue框架进行开发的方式，其所支持的特性更多，也在一定程度上减少了在html开发中的重复性的不必要的工作。其具体开发方式可见下方的[[Vue#使用Vue]]章节。

#### 使用单文件组件开发

使用单文件组件进行开发时，应当将代码保存到后缀名为 `.vue` 的文件中，且其默认模板如下：

```JavaScript
<template>

</template>

<script>
export default {

}
</script>

<style>

</style>
```

在上述模板中，其主要有如下几个块：
- `<template>` ：每个 `.vue` 文件<font color="#c00000">至多只能包含一个template块</font>，其所包含的控件会被预编译为JavaScript渲染函数。
- `<script>` ：<font color="#c00000">除了</font> `<script setup>` <font color="#c00000">外</font>，每个 `.vue` 文件<font color="#c00000">至多只能包含一个script块</font>，该块中的脚本代码将被作为ES模块执行
- `<style>` ：每个 `.vue` 文件<font color="#c00000">可以包含多个style块</font>，用于封装组件的样式。
此外，还有几个常用的块：
- `<script setup>` ：<span style="background:#fff88f"><font color="#c00000">该块中的代码会被会被预处理为该组件的</font></span> `setup` <span style="background:#fff88f"><font color="#c00000">函数</font></span>。

使用单文件组件进行开发时，<font color="#c00000">不再需要手动导入vue源</font>。
TODO


#### 组件与导入组件

在网页开发中，其 `header` 和 `footer` 通常是相同且复用的，因此为了避免在不用的页面写重复的 `header` 和 `footer` ，可以考虑使用Vue的组件特性。














