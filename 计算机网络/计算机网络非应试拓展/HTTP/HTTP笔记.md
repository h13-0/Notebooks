#计算机网络 #HTTP

## 目录

```toc

```

## HTTP版本

HTTP目前有如下若干版本
- HTTP/0.9：
- HTTP/1.0：RFC1945
- HTTP/1.1：[RFC2616](https://www.rfc-editor.org/rfc/rfc2616)
- 

但是目前主要使用 `HTTP/1.1` 、 `HTTP/2` 以及 `HTTP/3` 三个版本。


## HTTP方法集

### 请求方法

请求方法共计如下种：
- OPTIONS
- GET
- HEAD
- POST
- PUT
- DELETE 
- TRACE
- CONNECT

#### OPTION方法


#### GET方法

`GET` 方法主要用于从服务器检索资源，这个资源可以是一个网页、图片或者是其他资源。通常来说，<font color="#c00000">HTTP的GET请求不会改变资源的状态</font>，即<span style="background:#fff88f"><font color="#c00000">通常来说</font></span><font color="#c00000">无论执行多少次都应该得到相同的结果</font>。其特性有：
- 幂等性： `GET` 请求应该是幂等的，这意味着无论执行多少次，都应该得到相同的结果，而不会改变服务器上的资源状态。
- 可缓存： `GET` 请求的响应通常可以被浏览器或者其他缓存机制缓存，以加快相同请求的响应速度。
- 用在数据检索： `GET` 方法适用于请求数据检索，而不是用于像提交表单这样的操作。如果需要在请求中发送数据来更改服务器上的状态，应该使用如 `POST` 或 `PUT` 这样的方法。
- 查询字符串：在 `GET` 请求中，发送给服务器的数据附加在URL后面，形式为查询字符串。例如，在URL `https://api.example.com/search?q=keyword` 中，查询参数`q`的值是`keyword`，用于向服务器查询关键字为"keyword"的搜索结果。

#### HEAD方法

与 `GET` 方法相似的是 `HEAD` 方法也用于请求，只是 `HEAD` 只请求头部(即资源信息)，不请求资源本身(<font color="#c00000">服务器也不得在响应中返回消息主体</font>)。例如<font color="#c00000">可以通过</font> `HEAD` <font color="#c00000">方法获取资源的大小、修改日期等</font>。
- 通过 `Content-Length` 获取资源大小
- 通过 `Content-Type` 获取资源类型
- 通过 `Last-Modified` 获取资源最后修改时间
当然并不是所有的 `HEAD` 响应都会携带上述信息。
例如可以通过 `HEAD` 指令获取google的logo信息：
	![[Postman_lizTFvGLdo.png]]




