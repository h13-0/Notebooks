#前端 #后端

## 目录

```toc
```

## Token

`Token` 是指 `JSON Web Token` ，即 `JWT` ，其被定义于[RFC 7519](https://www.rfc-editor.org/rfc/rfc7519)中。
其要解决的是




Token需要附加在由客户端发起的HTTP请求的请求头中，且token中通常会携带用户id等数据。
Token由服务器进行加密生成和解密验证，客户端请求头中携带的Token通过解密验证后会被授权访问。
