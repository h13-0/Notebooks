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

### 3.1 Flash写入的基本流程

STM32的Flash写入流程为：
1. [[STM32内置Flash读写#^9g3lah|解锁Flash]]
2. Flash写入操作，主要有：
	- [[STM32内置Flash读写#^s1wv62|烧写Flash]]
	- 
3. [[STM32内置Flash读写#^kujyx3|锁定Flash]]

#### 3.1.1 解锁Flash ^9g3lah

HAL库API为：

```C
#include <stm32xx_hal.h>
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

#### 3.1.3 烧写Flash ^s1wv62

```C
HAL_StatusTypeDef  HAL_FLASH_Program(uint32_t TypeProgram, uint32_t Address, uint64_t Data);
HAL_StatusTypeDef  HAL_FLASH_Program_IT(uint32_t TypeProgram, uint32_t Address, uint64_t Data);
```

