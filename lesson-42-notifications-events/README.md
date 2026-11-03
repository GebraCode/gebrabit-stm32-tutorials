# Task Notification و Event Group و زمان انتخاب هرکدام

فایل‌های همراه درس 42 جبرابیت. [دانلود بستهٔ کامل](lesson-42-resources.zip) شامل پروژه، خروجی ساخت، اسکریپت‌ها، برگهٔ آزمایش و 6 تصویر آموزشی است.

وضعیت: کامپایل واقعی بدون هشدار انجام شده؛ اجرای روی برد و اندازه‌گیری فیزیکی انجام نشده است.

# GebraBit STM32 lesson 42

Target: STM32F303CBT6 LQFP48 / GebraBit GB100ST V2.0.

## Validation and limits

Actual local Windows clean CMake Debug compilation -O0 -g3 -Wall -Werror and ELF/BIN/HEX/kernel source audit passed. No -Wextra/-Wpedantic; no physical board execution, SWV capture, GUI execution, DWT/timing measurement or runtime heap measurement performed.

Build variants and exact sizes are in build-*.json. These are static linker reservations, not runtime heap consumption. No hardware measurement values are supplied. Fill measurement-worksheet.csv after your own continuous run.

## Rebuild

Install Arm GNU Toolchain13.2.rel1 (GCC13.2.1), CMake3.31.10 and Ninja1.11.1; put their bin directories on PATH. Extract project-and-build.zip and enter gebrabit_lesson42_notifications:

```sh
cmake --preset Debug
cmake --build --preset Debug --clean-first
arm-none-eabi-objcopy -O binary build/Debug/gebrabit_lesson42_notifications.elf build/Debug/gebrabit_lesson42_notifications.bin
```

For the comparison binary semaphore firmware, use the independent Semaphore preset:

```sh
cmake --preset Semaphore
cmake --build --preset Semaphore --clean-first
```

Program the ELF from build/Semaphore, and reset. Debug uses notifications. Never mix binaries or measurements from the two modes.

## Provenance and regeneration

Real CubeMX 6.14.0 DB6.0.140 hardware baseline lesson37, CubeF3 V1.11.6. Copied hardware sources and renamed IOC/project; app and native kernel integration are manually authored, not CubeMX-generated middleware. No new CubeMX generation or GUI test for42/43.

FreeRTOS-Kernel V11.2.0 commit 0adc196d4bd52a2d91102b525b0aafc1e14a2386. Native FreeRTOS, no CMSIS-RTOS wrapper. Only heap_4.c is linked. Native kernel sources and application are user-managed. Preserve main.c USER includes and App_Start() in USER2; preserve custom CMake integration and the port aliases for SVC/PendSV/SysTick. Do not regenerate conflicting handlers. HAL timebase remains TIM6. Regeneration was not performed for this derived project, so recheck and rebuild after any CubeMX changes.

HSE8MHz/PREDIV1/PLL9/SYSCLK72MHz/AHBdiv1/APB1div2=36MHz/APB2div1=72MHz/FLASH2WS.

HAL 1ms from generated TIM6 (timer72MHz PSC71 ARR999). Kernel SysTick1000Hz. Port aliases own SVC/PendSV/SysTick; no duplicate generated handler.

Flash128KiB; main SRAM32KiB; CCM8KiB separate, not used for DMA. heap_4 static arena12288bytes; application stacks256words=1024bytes; Idle128words=512bytes; StackType_t32bits. Stack high-water results require real execution.

## Run and observe

Only PB6 onboard active-high userLED is used. No additional wires are required. SWD and proper board power required to run; no UART output in42/43.

Synthetic Producer priority1 sends uint8 sequence into8-element byte_queue every100ticks with xTaskDelayUntil. Notification-mode default uses xTaskNotifyGive(receiver_handle); Receiver priority2 waits ulTaskNotifyTake(pdTRUE,portMAX_DELAY), drainsQueue without waiting and togglesPB6 perbyte. Semaphore build uses initially-empty binarysemaphore as doorbell, same Queue and tasks. EventObserver priority1 waits BIT_PRODUCED|BIT_CONSUMED with clearOnExit=pdTRUE, waitAll=pdTRUE. All3 stacks256words. No ISR or actual UART in this demonstration.

Expected, NOT MEASURED: Under light load receiverdrainsQueue every100ms, so sent/received approximately10persecond, g_queue_full=0andg_signal_failures=0 expected. PB6toggles perreceivedbyte idealfullcycle200ms. Eventpaircounter is flagsynchronization count, notproof everybyteprocessed or exacteventcount. Onlyg_received countsbytes. No numericalruntimeclaimverified.

Watch globals: g_sent, g_received, g_queue_full, g_last_byte, g_event_pairs, g_signal_failures, g_notification_mode, g_api_last_cycles, g_api_max_cycles, g_timing_available, g_signal_heap_bytes.

g_app_error=1 assert;2 malloc failure;3 stack overflow hook. Hooks halt without printf, logging or allocations.

## Doorbell, memory and timing comparison

Word42 says replace semaphore41, but Word41 explicitly requires UART IRQ->Queue->Task. Keep byte Queue; notification can replace an extra event semaphore/doorbell, not arbitrary Queue payload storage. Here the two builds compare doorbells with synthetic input. To extend lesson41, keep its UART byteQueue and error counters and use vTaskNotifyGiveFromISR, not task-context xTaskNotifyGive, plus portYIELD_FROM_ISR and NVIC rules.

Target DWT CYCCNT around ONLY the giveAPI while taskENTER_CRITICAL masks kernel-aware IRQs/PendSV. Context switch occurs after critical exit, outside measuredinterval. Higher-urgency interrupts may perturb; buildO0, conditionsreceiverblocked/queue/nestedIRQ affect cycles. Reset eachmode, run without breakpoints, recordmany samples. g_timing_available must1. At72MHz time_us=cycles/72. No measurement numbers exist. Do not claim universal45percentfaster.

Expected separate semaphore allocation88bytes vs notification0extra in thisconfiguration. Bothbuilds already include notifications inTCB and samefixed12KiBheap; do not infer88bytes lower ELF RAMreservation. ActualELFmetrics are separatelyreported.

## Source and licenses

https://github.com/FreeRTOS/FreeRTOS-Kernel/tree/0adc196d4bd52a2d91102b525b0aafc1e14a2386

FreeRTOS MIT license and ST/CMSIS licenses retained; instructional application MIT.

The download includes generated hardware source, IOC, manually integrated pinned kernel, application, CMake source, ELF/BIN/HEX/MAP and compiler reports. Temporary cache/object files, local login data and internal writing prompts are excluded. MAP report paths are normalized; executable bytes are the compiled files.

## Portable helper scripts

After extracting project-and-build.zip beside rebuild.py, run `python rebuild.py` with the toolchain, CMake and Ninja on PATH. This rebuilds all reviewed presets and writes local reports.

`python reproduce-layout-model.py` compiles type sizes and reproduces the heap_4 extra-allocation model without running a board. The DWT and runtime heap worksheet still require target execution.
