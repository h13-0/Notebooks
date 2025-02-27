---
number headings: auto, first-level 2, max 6, 1.1
---
#STM32开发 #嵌入式 

## 1 目录

```toc
```

## 2 前置知识

前置知识：
- [[STM32内置Flash模型]]

## 3 基本操作

### 3.1 Flash写入的基本流程(仅对用户Flash区域进行操作)

STM32的Flash写入流程为：
1. [[STM32内置Flash读写#^9g3lah|解锁Flash]]
2. Flash写入操作，主要有：
	- [[STM32内置Flash读写#^d0nzgi|擦除Flash]]
	- [[STM32内置Flash读写#^s1wv62|烧写Flash]]
3. [[STM32内置Flash读写#^kujyx3|锁定Flash]]

#### 3.1.1 解锁Flash ^9g3lah

HAL库API为：

```C
#include <stm32xx_hal.h>
// 解锁Flash区域
HAL_StatusTypeDef HAL_FLASH_Unlock(void);
```

LL库并未提供对应API，需要手动操作寄存器。

#### 3.1.2 锁定Flash ^kujyx3

HAL库API为：

```C
#include <stm32xx_hal.h>
HAL_StatusTypeDef HAL_FLASH_Lock(void);
```

LL库并未提供对应API，需要手动操作寄存器。

#### 3.1.3 擦除flash ^d0nzgi

HAL库API为：

```C
#include <stm32xx_hal.h>
HAL_StatusTypeDef HAL_FLASHEx_Erase(FLASH_EraseInitTypeDef *pEraseInit, uint32_t *PageError);
```

#### 3.1.4 烧写Flash ^s1wv62

在STM32L4xx中，HAL库提供了如下的Flash烧写API：

```C
#include <stm32xx_hal.h>
HAL_StatusTypeDef  HAL_FLASH_Program(uint32_t TypeProgram, uint32_t Address, uint64_t Data);
HAL_StatusTypeDef  HAL_FLASH_Program_IT(uint32_t TypeProgram, uint32_t Address, uint64_t Data);
```

### 3.2 3.2操作选项字节区域(Option Bytes)

STM32的OB Flash区域的操作步骤如下：
1. [[STM32内置Flash读写#^9g3lah|解锁Flash]]
2. [[STM32内置Flash读写#^ktzr6h|解锁OB区域]]
3. Flash写入操作，主要有：
	- [[STM32内置Flash读写#^d0nzgi|擦除Flash]]
	- [[STM32内置Flash读写#^s1wv62|烧写Flash]]
4. [[STM32内置Flash读写#^mv62jz|锁定OB区域]]
5. [[STM32内置Flash读写#^kujyx3|锁定Flash]]
<font color="#c00000">注意需要严格遵守顺序!!!</font>

#### 3.2.1 解锁OB区域 ^ktzr6h

```C
#include <stm32xx_hal.h>
HAL_StatusTypeDef HAL_FLASH_OB_Unlock(void);
```

#### 3.2.2 锁定OB区域 ^mv62jz

```C
#include <stm32xx_hal.h>
HAL_StatusTypeDef HAL_FLASH_OB_Lock(void);
```


