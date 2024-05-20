#Vue #前端

## 目录

```toc
```

## Vue

Vue是JavaScript的一个开发框架，

其主要风格有：
- 选项式(Vue2的风格)
- 组合式(Vue3主推)

### Vue应用

TODO



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

当然也可以结合条件渲染进行条件显示：
```html
<ul v-for="(value, key, index) in data.class1">
	<li v-if="index == 0">
		index: {{index}}, key: {{key}}, value: {{value}}
	</li>
</ul>
```



