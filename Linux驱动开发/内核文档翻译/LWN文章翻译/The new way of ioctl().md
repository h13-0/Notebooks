#文档翻译 #Linux驱动开发 #操作系统 

原文链接：[https://lwn.net/Articles/119652/](https://lwn.net/Articles/119652/)
发布时间：January 18, 2005

## 翻译

`ioctl()` 系统调用长期以来一直不受内核开发人员的欢迎，因为他们认为它是进入内核的一个完全不受控制的入口点。然而，由于有大量的应用程序期望 `ioctl()` 的出现，所以它不会很快消失。因此，确保 `ioctl()` 调用快速、正确地执行是值得的，而且保证它们不会不必要地影响系统的其他部分。

`ioctl()` 是内核中仍然运行在"<font color="#c00000">大内核锁</font>"(Big Kernel Lock，<font color="#c00000">BKL</font>)保护下的部分之一。过去，使用BKL使得运行时间长的 `ioctl()` 方法可能会为无关的进程创建较长的延迟。最近的更改使得BKL覆盖的代码可抢占，从而在一定程度上缓解了这个问题。即便如此，希望最终完全摆脱BKL的想法表明， `ioctl()` 应该脱离其保护。

然而，简单地在调用 `ioctl()` 方法之前移除 `lock_kernel()` 调用并不是一个可行的方法。首先必须对每一个方法进行审核，以确定其在BKL之外安全运行所需的其他锁。这是一个庞大的工作，很难在单一的一天内完成(原文是指很难在一个"flag day"中完成，"flag day"表示对系统进行大规模更改的一天)。因此，必须提供一个迁移路径。从2.6.11版本开始，这条路径将会存在。

在[Michael s. Tsirkin提交的Patch](https://lwn.net/Articles/119656/)中，向 `file_operations` 结构体中新添加了一个成员：

```C
long (*unlocked_ioctl) (struct file *filp, unsigned int cmd, 
                        unsigned long arg);
```