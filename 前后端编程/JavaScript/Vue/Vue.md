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
- 

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
- 在前面加上`v`，即：`<img v-bind:src=web.url></img>`
- 