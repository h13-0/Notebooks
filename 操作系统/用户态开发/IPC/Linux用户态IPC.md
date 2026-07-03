---
number headings: auto, first-level 1, max 6, 1.1
---
#Linux用户态开发

# 1 目录

```toc
```

# 2 概述

Linux用户态IPC的方式主要有如下几种：
1. 管道：通过内核缓冲区在进程间按字节流传递数据，常用于父子进程或通过FIFO用于无亲缘进程。
2. 信号：用于向进程异步通知某个事件，适合控制和通知，不适合传输大量数据。
3. 消息队列：以内核消息队列为中介，进程之间按消息为单位发送和接收数据。
4. 共享内存：多个进程映射同一块内存区域，直接读写共享数据，速度快但需要额外同步。
5. 信号量：主要用于进程间同步和互斥，常配合共享内存使用。
6. 套接字：通过 `socket` 在本机或网络上的进程之间进行通信，通用性强。
7. 文件系统：多个进程通过读写同一个文件交换数据，简单但效率较低。
8. 内存映射文件：通过 `mmap` 将文件映射到内存，多个进程可共享访问文件内容。

用户态常用IPC库有：
- [Remote Call Framework (RCF) - Delta V Software](https://www.deltavsoft.com/)

# 3 管道

机制：
- 管道是内核维护的一段缓冲区，一个进程写入，另一个进程读取(<font color="#c00000">单向传递</font>)

常见种类有：
- 匿名管道 `pipe` ，通常用于父子进程
- 命名管道 `FIFO` ，可以用于无亲缘关系的进程

Demo：

```C
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>

int main() {
    int fd[2];
    pipe(fd);

    pid_t pid = fork();

    if (pid == 0) {
        close(fd[1]);

        char buf[128] = {0};
        read(fd[0], buf, sizeof(buf));

        printf("child read: %s\n", buf);

        close(fd[0]);
    } else {
        close(fd[0]);

        const char *msg = "hello pipe";
        write(fd[1], msg, strlen(msg));

        close(fd[1]);
        wait(NULL);
    }

    return 0;
}
```

# 4 信号

机制：
- 一种异步通知机制，常见信号有：
	- `SIGINT`  Ctrl+C
	- `SIGKILL` 强制终止
	- `SIGTERM` 请求终止
	- `SIGCHLD` 子进程退出
	- `SIGUSR1` 用户自定义信号
	具体可见[[../信号/可监听的信号列表|可监听的信号列表]]

详细应用可见：[[操作系统/课外补充/IO模型/IO模型#^cnqe2i|信号驱动型IO]]

Demo:

```C
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>

void handler(int signo) {
    write(STDOUT_FILENO, "child received signal\n", 22);
}

int main() {
    pid_t pid = fork();

    if (pid == 0) {
        signal(SIGUSR1, handler);

        while (1) {
            pause();
        }
    } else {
        sleep(1);
        kill(pid, SIGUSR1);

        sleep(1);
        kill(pid, SIGKILL);

        wait(NULL);
    }

    return 0;
}
```

# 5 消息队列

机制：
- 由内核维护，进程可以往队列中发送消息，另一个进程从队列中读取消息
- 消息队列与管道之间的区别：
	- 管道：按字节流传输
	- 消息队列：按消息为单位传输
- Linux下通常有如下两类队列：
	- System V 消息队列
	- POSIX 消息队列

优点：
- 有消息边界；
- 支持按消息类型读取；
- 不要求两个进程同时在线。

缺点：
- 需要内核拷贝数据，性能不如共享内存；
- 消息大小和队列容量有限；
- 需要手动删除队列资源。

适用场景：
- 进程间传递结构化小消息，例如任务通知、命令分发、日志消息等。

Demo：

```C
#include <stdio.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <sys/wait.h>
#include <unistd.h>

struct msgbuf {
    long mtype;
    char mtext[64];
};

int main() {
    int msgid = msgget(IPC_PRIVATE, 0666 | IPC_CREAT);

    pid_t pid = fork();

    if (pid == 0) {
        struct msgbuf msg;

        msgrcv(msgid, &msg, sizeof(msg.mtext), 1, 0);

        printf("child received: %s\n", msg.mtext);
    } else {
        struct msgbuf msg;

        msg.mtype = 1;
        strcpy(msg.mtext, "hello message queue");

        msgsnd(msgid, &msg, sizeof(msg.mtext), 0);

        wait(NULL);

        msgctl(msgid, IPC_RMID, NULL);
    }

    return 0;
}
```

# 6 共享内存

机制：
- 把多个进程把**同一块物理内存**映射到自己的虚拟地址空间中

优点：
- 速度非常快，适合大量数据共享

缺点：
- 本身不提供同步机制
- 容易出现竞态条件

Demo：

```C
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/wait.h>

int main() {
    char *shm = mmap(NULL, 4096,
                     PROT_READ | PROT_WRITE,
                     MAP_SHARED | MAP_ANONYMOUS,
                     -1, 0);

    pid_t pid = fork();

    if (pid == 0) {
        sleep(1);
        printf("child read: %s\n", shm);
    } else {
        strcpy(shm, "hello shared memory");

        wait(NULL);
        munmap(shm, 4096);
    }

    return 0;
}
```

