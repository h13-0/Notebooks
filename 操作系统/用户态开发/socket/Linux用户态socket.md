---
number headings: auto, first-level 2, max 6, 1.1
---
#Linux用户态开发 

## 1 目录

```toc
```

## 2 socket概述


## 3 BIO socket

### 3.1 Server端Demo

单线程的server段的主要逻辑如下：

```mermaid
flowchart TB
	A[开始] --> B[创建socket<br><code>socket</code>]
	B --> C[配置可选项<br><code>setsockopt</code>]
	C --> D[将监听地址与socket绑定<br><code>bind</code>]
	D --> E[开始监听<br><code>listen</code>]
	E --> F{判定退出条件}
	F --> |继续|G[接受连接<br><code>accept</code>]
	G --> H[<code>recv</code> & <code>send</code>]
	H --> I[关闭连接<br><code>close</code>]
	I --> F
	F --> J[退出]
	K[退出] --> L[关闭socket<br><code>close</code>]
```


```CPP
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <iostream>

#define PORT 8888

int main() {
    using namespace std;

    int socket_fd = socket(AF_INET, SOCK_STREAM, 0);

    int opt = 1;
    setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(yes));

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(PORT);

    bind(socket_fd, (struct sockaddr*)&server_addr, sizeof(server_addr));

    cout << "Start listening 0.0.0.0:8888." << endl;
    listen(socket_fd, 10);

    while (1) {
        cout << "Waiting for connection." << endl;
        int conn_fd = accept(socket_fd, NULL, NULL);
        cout << "Connected." << endl;

        const string msg = "hello, world!";

        // 发送数据
        send(conn_fd, msg.c_str(), msg.length() + 1, 0);

        shutdown(conn_fd, SHUT_WR); // 关闭发送
        close(conn_fd); // 关闭连接
    }

	close(socket_fd);
	return 0;
}
```

### 3.2 Client端Demo

### 3.3 相关APIs

#### 3.3.1 数据结构 sockaddr_in 与 sockaddr



#### 3.3.2 setsockopt

##### 3.3.2.1 setsockopt概述

##### 3.3.2.2 setsockopt选项列表

![[setsockopt及其选项列表#3 setsockopt选项列表]]

#### 3.3.3 close与shutdown


## 4 NIO socket

### 4.1 相关APIs

#### 4.1.1 select

select函数是跨平台的函数，已验证支持的平台有：
- Linux
- Windows
- Mac OS
select底层使用的数据结构为线性表，默认的连接上限为1024个。
通常使用的函数为select和epoll。




#### 4.1.2 poll

poll函数底层使用的数据结构为线性表

#### 4.1.3 epoll

epoll函数底层使用的数据结构为红黑树

