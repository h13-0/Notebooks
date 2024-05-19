

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

#### 动态属性绑定(v-bind)

动态属性绑定是指将空间的属性绑定到一个变量上，当变量发生变化时其属性值也会跟着改变。
例如对于非动态属性绑定
