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

其中 `FLASH_EraseInitTypeDef` 的定义为：

```C
/**
  * @brief  FLASH Erase structure definition
  */
typedef struct
{
  uint32_t TypeErase;   /*!< Mass erase or page erase.
                             This parameter can be a value of @ref FLASH_Type_Erase */
  uint32_t Banks;       /*!< Select bank to erase.
                             This parameter must be a value of @ref FLASH_Banks
                             (FLASH_BANK_BOTH should be used only for mass erase) */
  uint32_t Page;        /*!< Initial Flash page to erase when page erase is disabled
                             This parameter must be a value between 0 and (max number of pages in the bank - 1)
                             (eg : 255 for 1MB dual bank) */
  uint32_t NbPages;     /*!< Number of pages to be erased.
                             This parameter must be a value between 1 and (max number of pages in the bank - value of initial page)*/
} FLASH_EraseInitTypeDef;
```

该结构体的参考定义方式为：

```C
FLASH_EraseInitTypeDef EraseInit;

EraseInit.TypeErase   = FLASH_TYPEERASE_PAGES;
EraseInit.Banks       = FLASH_BANK_1;         // 单Bank型号可忽略
EraseInit.Page        = 128;                  // 目标页号
EraseInit.NbPages     = 1;                    // 擦除1页
```

#### 3.1.4 烧写Flash ^s1wv62

在STM32L4xx中，HAL库提供了如下的Flash烧写API：

```C
#include <stm32xx_hal.h>
HAL_StatusTypeDef  HAL_FLASH_Program(uint32_t TypeProgram, uint32_t Address, uint64_t Data);
HAL_StatusTypeDef  HAL_FLASH_Program_IT(uint32_t TypeProgram, uint32_t Address, uint64_t Data);
```

在上述API中：
- `HAL_FLASH_Program` 为同步方法，该函数会一直等待直到烧写完成。
- `HAL_FLASH_Program_IT` 为异步方法，该函数会立即返回，操作完毕后使用中断( `Flash_IRQn` )通知结果。
- `TypeProgram` 可以选择烧录选项。具体 `TypeProgram` 如下：
	- `FLASH_TYPEPROGRAM_DOUBLEWORD` ：适用于单次写入，速度较慢
	- `FLASH_TYPEPROGRAM_FAST` ：适用于<span style="background:#fff88f"><font color="#c00000">连续写入64个32Bit</font></span>()，但是写入最后一次操作时应使用下方选项。参数为内存地址。
	- `FLASH_TYPEPROGRAM_FAST_AND_LAST` ：适用于<span style="background:#fff88f"><font color="#c00000">连续写入64个32Bit</font></span>，且为最后一次操作。参数为内存地址。
异步的优势及使用场景通常为：
1. 低功耗场景
2. 多任务实时系统等

### 3.2 操作选项字节区域(Option Bytes)

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


