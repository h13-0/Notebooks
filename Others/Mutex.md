互斥锁，用于保护临界区，其类型主要有：
```toc
```


## 互斥锁

一个互斥锁只能同时加锁一次，加锁后需要主动解锁，若程序先后加锁，则后加锁的指令会被阻塞，直到该锁被其他线程解锁。

### pthread
```C
pthread_mutex_t mutex;
pthread_mutex_init(&mutex, NULL);
```
#### 额外配置

## 递归锁
### pthread
```C

```


## 自旋锁

## 读写锁



