---
number headings: auto, first-level 2, max 6, 1.1
---

## 1 目录

```toc
```

## 2 Linux设备模型


## 3 总线



## 4 设备

### 4.1 平台设备

anchor ^wahyvw


平台设备的注册：

```C
/**
 * platform_device_register - add a platform-level device
 * @pdev: platform device we're adding
 *
 * NOTE: _Never_ directly free @pdev after calling this function, even if it
 * returned an error! Always use platform_device_put() to give up the
 * reference initialised in this function instead.
 */
int platform_device_register(struct platform_device *pdev);
```


