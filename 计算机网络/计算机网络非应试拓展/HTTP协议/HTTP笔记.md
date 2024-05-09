#计算机网络 #HTTP

## 目录

```toc

```

## HTTP版本

HTTP目前有如下若干版本
- HTTP/0.9：
- HTTP/1.0：RFC1945
- HTTP/1.1：HTTP/1.1最初与于1997年的RFC2068中发布，并于1999修订[RFC2616](https://www.rfc-editor.org/rfc/rfc2616)并成为HTTP/1.1规范。
- 

但是目前主要使用 `HTTP/1.1` 、 `HTTP/2` 以及 `HTTP/3` 三个版本。

## HTTP报文结构

![[第六章 应用层#^lppwjz]]

## HTTP(请求)方法集

请求方法共计如下种：
- OPTIONS
- GET
- HEAD
- POST
- PUT
- DELETE
- TRACE
- CONNECT
- PATCH(2010年加入HTTP/1.1)
<font color="#c00000">而服务器响应并没有上述概念，主要通过状态码来区分</font>，详见下一章节。
### OPTION方法

由于HTTP服务器不一定支持上述所有请求方法(甚至 `OPTION` 方法本身都不一定被支持)，因此需要实现一个 `OPTION` 方法查询服务器支持哪些请求方法。

### GET方法

`GET` 方法主要用于从服务器检索资源，这个资源可以是一个网页、图片或者是其他资源。通常来说，<font color="#c00000">HTTP的GET请求不会改变资源的状态</font>，即<span style="background:#fff88f"><font color="#c00000">通常来说</font></span><font color="#c00000">无论执行多少次都应该得到相同的结果</font>。其特性有：
- 幂等性： `GET` 请求应该是幂等的，这意味着无论执行多少次，都应该得到相同的结果，而不会改变服务器上的资源状态。
- 可缓存： `GET` 请求的响应通常可以被浏览器或者其他缓存机制缓存，以加快相同请求的响应速度。
- 用在数据检索： `GET` 方法适用于请求数据检索，而不是用于像提交表单这样的操作。如果需要在请求中发送数据来更改服务器上的状态，应该使用如 `POST` 或 `PUT` 这样的方法。
- 查询字符串：在 `GET` 请求中，发送给服务器的数据附加在URL后面，形式为查询字符串。例如，在URL `https://api.example.com/search?q=keyword` 中，查询参数`q`的值是`keyword`，用于向服务器查询关键字为"keyword"的搜索结果。
例如可以通过如下的命令发送 `GET` 请求：
```Shell
curl -X GET https://api.example.com
```

### HEAD方法

与 `GET` 方法相似的是 `HEAD` 方法也用于请求，只是 `HEAD` 只请求头部(即资源信息)，不请求资源本身(<font color="#c00000">服务器也不得在响应中返回消息主体</font>)。例如<font color="#c00000">可以通过</font> `HEAD` <font color="#c00000">方法获取资源的大小、修改日期等</font>。
- 通过 `Content-Length` 获取资源大小
- 通过 `Content-Type` 获取资源类型
- 通过 `Last-Modified` 获取资源最后修改时间
当然并不是所有的 `HEAD` 响应都会携带上述信息。
例如可以通过 `HEAD` 指令获取google logo的图片信息：
	![[Postman_lizTFvGLdo.png]]
例如可以通过如下的命令发送 `HEAD` 请求：
```Shell
curl -I https://api.example.com/image.png
curl --head https://api.example.com/image.png # -I或者--head均可
```

### POST方法

`POST` 方法主要用于提交数据，可以用于提交表单、文件等。其数据放置在请求的正文中。
其主要特性有：
- 非幂等性： `POST` 方法<font color="#c00000">通常不是幂等</font>的，这意味着同一个 `POST` 请求如果被多次发送，<font color="#c00000">可能会每次都产生或改变服务器上的资源状态</font>。
- 数据封装： <font color="#c00000">数据通过请求体发送</font>，而不是URL，这不仅<font color="#c00000">保护了数据的隐私性</font>，还<font color="#c00000">允许发送大量的数据</font>。
- 多功能性： `POST` 请求被广泛用于各种场景，包括表单提交、通过API上传文件、或者向服务器发送应用程序数据等。
例如可以通过如下的命令发送 `POST` 请求：
```Shell
curl -X POST https://api.example.com/data -H "Content-Type: application/json" -d '{"name": "Zhang San", "email": "example@example.com"}'
```

### PUT方法

和 `POST` 方法类似的是 `PUT` 方法也是客户端向服务器传输数据的一种方法，只是<font color="#c00000">其是幂等的方法</font>，主要用于更新或替换服务。
其特性主要有：
- 幂等性 如果多次执行同一个`PUT`请求，服务器上的资源状态应该和执行一次`PUT`请求时相同，这有助于防止由于网络问题导致的多次请求引发的问题。
- 更新和替换： `PUT`方法通常用于更新现有资源或替换资源内容。如果指定的资源不存在，根据服务器配置，`PUT`请求也可能创建一个新的资源。
例如可以使用如下的命令发送 `PUT` 请求：
```Shell
curl -X PUT https://api.example.com/users/123 -H "Content-Type: application/json" -d '{"name": "Zhang San", "age": 30}'
```

### DELETE方法

`DELETE` 方法用于删除指定服务器中的指定资源，<font color="#c00000">当删除操作成功时</font>应返回 `204 No Content` 或 `200 OK` 。
其特性主要有：
- 幂等性： `DELETE` 方法是幂等的，意味着无论请求执行多少次，结果都应保持一致。首次 `DELETE` 请求可能会删除资源，而后续的同样请求应返回同样的结果（比如 `404 Not Found`），因为资源已经不存在。
- 服务器控制： `DELETE` 请求的响应方式的实现取决于服务器。服务器可以直接删除资源，也可以标记为删除或移动到回收站。
例如可以使用如下的命令发送 `DELETE` 请求：
```Shell
curl -X DELETE https://api.example.com/users/123
```

### TRACE方法

`TRACE` 方法用于回显服务器收到的请求。<font color="#c00000">服务器回回显除了实体内容的精确副本</font>，但出于安全性考虑， `TRACE` 方法通常被禁用。
其特性主要有：
- 回显请求： 发送 `TRACE` 请求到服务器，服务器会在响应体中返回接收到的请求的精确副本（不包括实体的内容），这样客户端可以看到中间可能被代理或其他网络元素修改或添加的请求头部。
- 诊断工具： `TRACE` 方法可以帮助确定请求在传输过程中是否被修改或篡改，是网络安全和调试中的一个有用工具。
- <font color="#c00000">不安全</font>。
`TRACE` 的<font color="#c00000">安全性问题</font>：
- 例如某钓鱼网站在其内部的脚本中让浏览器TRACE一个关键网站，然后浏览器就会带着 `Cookie` 进行 `TRACE` ，并截获浏览器回显的 `Cookie` 。
- 在攻击者<font color="#c00000">已经可以篡改HTTP头部之后</font>，攻击者将头部中附加一些需要转义的附加JS代码，然后浏览器收到回显消息后会对JS代码转义并执行(反射性跨站脚本(XSS)攻击)。

### CONNECT方法

`CONNECT` 方法<font color="#c00000">建立的隧道通常都是</font> `Keep-alive` <font color="#c00000">性质的</font>，随后的 `GET` 、 `POST` 等方法通过该隧道传输。 `Close` 性质的隧道不常使用，使用 `Close` 可能是出于安全考虑。
在HTTPS中通常使用 `CONNECT` 建立一个隧道。
其特性通常有：
- 隧道建立： 使用 `CONNECT` 方法，客户端可以要求代理服务器为特定的服务器和端口号建立一个隧道。这个隧道允许客户端和目标服务器之间的直接通信，数据通过代理传输，但代理不会解读或修改这些数据。
- HTTPS 通过 HTTP 代理： 在 HTTPS 请求通过 HTTP 代理服务器的情况下，`CONNECT` 方法被用来建立到目标 HTTPS 服务器的隧道。一旦隧道建立成功，客户端和服务器之间的 SSL/TLS 握手可以开始，之后的通信将被加密。

### PATCH方法

该方法于2010年的RFC5789中被定义，并加入HTTP/1.1协议。
HTTP的 `PATCH` 方法用于对资源进行部分修改。与 `PUT` 方法不同的是， `PUT` 通常用于替换目标资源的完整内容，而 `PATCH` 则是<span style="background:#fff88f"><font color="#c00000">告知服务器</font></span><font color="#c00000">更新部分参数</font>，<font color="#c00000">而非全部参数</font>。在服务器程序设计中，PUT和PATCH会被不同的函数处理，PUT通常是全局覆盖，PATCH是不分更新，不过具体的实现还是取决于具体的服务器程序。

其特性主要有：
- 非幂等性： `PATCH`方法理论上可以是幂等的，但实际上是否幂等取决于其操作的性质和实现。如果多次应用相同的`PATCH`请求导致资源达到相同的状态，则这个`PATCH`请求是幂等的。然而，如果每次应用都会基于当前状态改变资源，则可能不是幂等的。
- 效率： 由于只需要传输需要改变的部分，而不是整个资源，PATCH请求通常比PUT请求更加高效。
- 灵活性： `PATCH` 方法允许开发者定义部分更新的操作，这可以是添加、删除或修改资源的某些部分。
例如可以使用如下的命令发送 `PATCH` 请求：
```Shell
curl -X PATCH https://api.example.com/users/123 -H "Content-Type: application/json" -d '{"email": "new.email@example.com"}' #告知服务器只更新email字段
```

## HTTP响应

HTTP响应均按照报文结构进行，其主要依靠状态码区分结果或类型。
状态码共计5类33种。

