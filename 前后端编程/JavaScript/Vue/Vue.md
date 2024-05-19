

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
```vue
<body>
    <div id="app">
		<input type="text" v-on:keydown.enter="enter_down" @keyup.enter="enter_up">
	</div>
	<script type="module"
        import {createApp, reactive, ref} from "https://unpkg.com/vue@3/dist/vue.esm-browser.js"
        createApp({
			setup(){
				const text = ref("ready")
				
				const enter_down = () => {
					text.value = "enter"
				}
				
				const enter_up = () => {
						text.value = "release"
					}
				}

				return {
					text,
					enter_down,
					enter_up
				}
			}
		}).mount("#app")
	</script>
</body>
</html>
```
就创建了一个文本输入框，并在 `enter` 键按下时