# ارتباط وقفه‌های STM32 با Task و استفاده از توابع FromISR

فایل‌های همراه درس 41 جبرابیت. [دانلود بستهٔ کامل](lesson-41-resources.zip) شامل پروژه، خروجی ساخت، اسکریپت‌ها، برگهٔ آزمایش و 6 تصویر آموزشی است.

وضعیت: کامپایل واقعی بدون هشدار انجام شده؛ اجرای روی برد و اندازه‌گیری فیزیکی انجام نشده است.

# GebraBit STM32 lesson 41

Target STM32F303CBT6 LQFP48 on GB100ST V2.0. Native FreeRTOS V11.2.0, pinned commit 0adc196d4bd52a2d91102b525b0aafc1e14a2386; ARM_CM4F port and heap_4 only. Main RAM32KiB, CCM8KiB, Flash128KiB. HSE8MHz PLL9, HCLK72MHz, APB1/2=36/72MHz, Flash2WS. HAL uses TIM6 at1ms; kernel owns SysTick at1000Hz.

## Validation
Actual local clean CMake Debug build with Arm GNU Toolchain13.2.rel1 GCC13.2.1, CMake3.31.10 and Ninja1.11.1. All C units use -O0 -g3 -Wall -Werror. No Wextra/Wpedantic. No warnings. ELF/BIN/HEX and interrupt vectors audited. Hardware run, GUI operation and timing measurements NOT PERFORMED. Compilation does not establish runtime behavior.

## Rebuild
Install the versions above and place their bin directories on PATH. From gebrabit_lesson41_fromisr run:

    cmake --preset Debug
    cmake --build --preset Debug --clean-first
    arm-none-eabi-objcopy -O binary build/Debug/gebrabit_lesson41_fromisr.elf build/Debug/gebrabit_lesson41_fromisr.bin

## Provenance and regeneration
hardware-baseline-cubemx.ioc is the genuine previously generated lesson37 hardware baseline, not a newly generated lesson41 project. Native FreeRTOS and application are manually integrated. App/Rtos is user-managed. main.c includes rtos_app.h in USER CODE Includes and calls App_Start in USER CODE2. Keep the kernel CMake sources/includes and only one heap implementation. CubeMX must not generate SVC/PendSV/SysTick handlers already owned by the kernel port aliases. Preserve TIM6 HAL timebase. Rebuild and repeat vector checks after regeneration.

For lesson41, usart.c/usart.h and UART HAL sources are copied from the genuine lesson13_v2 generated project; original uart-provenance-cubemx.ioc retained. USART1 priority was manually changed from2 to5. HAL_UART_MODULE_ENABLED, source entries and USER CODE interrupt delegate were manually integrated. The two IOCs describe provenance, not a single newly regenerated final configuration. If regenerating, merge USART1 PA9/PA10 AF7 1152008N1 and IRQ5 into the TIM6 hardware baseline, preserve App/Rtos and handler ownership. No CubeMX GUI regeneration was performed.

## Run and observe
USART1 PA9 TX/PA10 RX AF7 1152008N1, no flow control,3.3V logic. Queue length32 bytes. Processor priority2 stack384words starts HAL_UART_Receive_IT only after scheduler starts and queue exists. IRQ priority5/subpriority0. Handler delegatesHAL_UART_IRQHandler; complete callback saves byte, rejects it without rearm when HAL ErrorCode is nonzero (preserves ORE classification for subsequent HAL ErrorCallback); on error-free completion rearms one-byte receive, copies byte with xQueueSendFromISR, counts full-queue loss, then portYIELD_FROM_ISR with initialized pdFALSE flag. Processor counts bytes and newline events and toggles PB6 on LF; no UART TX/echo. Error callback counts errors and records HAL code before rearm; rearm only if RxStateREADY, respecting nonblocking error reception. g_consumer_delay_ms can deliberately slow consumption to expose finite-capacity queue loss; default0.

Send ASCII lines ending LF from3.3V USB-UART TX toPA10 and commonGND (PA9 optional unusedTX). Processor counts each received byte, g_lines increments per LF and PB6 toggles per line. No echo is expected. Queue overflow increments g_rx_dropped, distinct from UART peripheral ORE/FE/NE/PE counters. Raise g_consumer_delay_ms to10ms and send a burst to demonstrate loss; reset variable0 to restore normal processing. If rearm_failed increments, receiver may stop; stop input, inspect HALstate, reset target after fixing cause. No infinite receive-retry loop masks configuration faults.

Watch globals: g_rx_irq_bytes, g_rx_dropped, g_rx_rejected, g_rx_errors, g_rx_last_error, g_rx_rearm_failed, g_processed_bytes, g_lines, g_last_byte, g_consumer_delay_ms. Use SWD probe and reset before a new experiment. Keep BOOT0 in user Flash boot mode. PB6 onboard LED is active-high. PB7 is configured but unused; do not connect another output. g_app_error1 is assert,2 allocation failure,3 stack hook; hooks stop for debugger inspection and do not print. Stack-overflow hooks are not complete protection.

## Important interpretation
4 implemented NVIC bits. configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY5 is passed unshifted to HAL_NVIC_SetPriority. Encoded configMAX_SYSCALL_INTERRUPT_PRIORITY=5<<(8-4)=0x50. IRQ priorities5..15 may call FromISR;0..4 must not call kernel API. Not every FreeRTOS API has an ISR variant.

configASSERT in ARM_CM4F port checks IRQ priority/grouping when ISR queue API executes. It is not a full race detector. Do not deliberately set priority0 in production.

portYIELD_FROM_ISR pends PendSV if a higher-priority task was unblocked; actual task execution begins after IRQ exits and other masking/higher-priority activity permits.

When RXNE and error coincide HAL calls RxCplt before ErrorCallback. Rearming there would reset ErrorCode and hide the error; this application instead rejects that byte (g_rx_rejected), leaves ErrorCode intact, and lets ErrorCallback rearm READY reception.

One-byte interrupt reception has rearm gaps and no flow control, so high-rate lossless reception is not guaranteed; use DMA/ringbuffer design for sustained high load.

1152008N1 ideal character10bits takes86.8055556us;32byte queue represents2.7777778ms wire data only if initially empty, continuous ideal stream and no consumer. Not guaranteed allowable CPU stall.

HAL and FreeRTOS timebases remain separate TIM6/SysTick; task API must never block ISR.

Only one application task384words; Idle128words; heap4 is12288bytes.

## Source licenses
FreeRTOS MIT, ST HAL and CMSIS licenses are retained in project directories. See source-index.json and exact included source. User lesson source and authored calculation script are provided for educational reuse with attribution to GebraBit. No credentials, writer prompts or private notes are included.
