# ارتباط و همگام‌سازی Taskها با Queue، Semaphore و Mutex

فایل‌های همراه درس 40 جبرابیت. [دانلود بستهٔ کامل](lesson-40-resources.zip) شامل پروژه، خروجی ساخت، اسکریپت‌ها، برگهٔ آزمایش و 6 تصویر آموزشی است.

وضعیت: کامپایل واقعی بدون هشدار انجام شده؛ اجرای روی برد و اندازه‌گیری فیزیکی انجام نشده است.

# GebraBit STM32 lesson 40

Target STM32F303CBT6 LQFP48 on GB100ST V2.0. Native FreeRTOS V11.2.0, pinned commit 0adc196d4bd52a2d91102b525b0aafc1e14a2386; ARM_CM4F port and heap_4 only. Main RAM32KiB, CCM8KiB, Flash128KiB. HSE8MHz PLL9, HCLK72MHz, APB1/2=36/72MHz, Flash2WS. HAL uses TIM6 at1ms; kernel owns SysTick at1000Hz.

## Validation
Actual local clean CMake Debug build with Arm GNU Toolchain13.2.rel1 GCC13.2.1, CMake3.31.10 and Ninja1.11.1. All C units use -O0 -g3 -Wall -Werror. No Wextra/Wpedantic. No warnings. ELF/BIN/HEX and interrupt vectors audited. Hardware run, GUI operation and timing measurements NOT PERFORMED. Compilation does not establish runtime behavior.

## Rebuild
Install the versions above and place their bin directories on PATH. From gebrabit_lesson40_sync run:

    cmake --preset Debug
    cmake --build --preset Debug --clean-first
    arm-none-eabi-objcopy -O binary build/Debug/gebrabit_lesson40_sync.elf build/Debug/gebrabit_lesson40_sync.bin

## Provenance and regeneration
hardware-baseline-cubemx.ioc is the genuine previously generated lesson37 hardware baseline, not a newly generated lesson40 project. Native FreeRTOS and application are manually integrated. App/Rtos is user-managed. main.c includes rtos_app.h in USER CODE Includes and calls App_Start in USER CODE2. Keep the kernel CMake sources/includes and only one heap implementation. CubeMX must not generate SVC/PendSV/SysTick handlers already owned by the kernel port aliases. Preserve TIM6 HAL timebase. Rebuild and repeat vector checks after regeneration.

No new CubeMX GUI regeneration was performed. No peripheral wiring beyond the existing PB6 board LED is needed for the synchronization demonstration.

## Run and observe
Queue producer sends Sample {uint32_t sequence,value} by value into length4 queue, up to50tick blocking; producer delays100ticks. Consumer priority2 receives indefinitely and toggles PB6. Concurrent finite inversion experiment phases: phase0 binary semaphore used as lock, phase1 mutex. Coordinator4,High3,Medium2,Low1; gates are binary semaphores, completion counter maximum3. Low acquires resource before Coordinator releases High/Medium. High blocks acquiring held resource; Medium executes2000000 NOP-loop iterations; Low executes300000. With binary semaphore no inheritance so Medium completes first; with mutex Low inherits3 and High acquires before Medium completes. Bounded CPU load is deliberate experiment code, not a production wait. Expected relative order, not measured durations. Coordinator then checks counting semaphore3 gives succeed and fourth fails, drains it, sets done and self-deletes; worker tasks remain blocked on gates. Queue producer/consumer continue.

After g_demo_done==1, g_phase==2; expected low priorities[1,3], medium-finished-at-high-acquire[1,0], counting_successes3/full_seen1. g_high_wait_ticks[0] is expected longer than[1], but no exact ratio/value asserted. Reset to repeat; do not halt until done. Both phases use the same loop counts. Tick quantization and measurement overhead matter. Priority inheritance reduces this inversion, does not prevent deadlock or arbitrary nested-lock problems.

Watch globals: g_produced, g_consumed, g_queue_timeouts, g_last_value, g_phase, g_demo_done, g_high_wait_ticks[2], g_low_effective_priority[2], g_medium_finished_at_high_acquire[2], g_counting_successes, g_counting_full_seen. Use SWD probe and reset before a new experiment. Keep BOOT0 in user Flash boot mode. PB6 onboard LED is active-high. PB7 is configured but unused; do not connect another output. g_app_error1 is assert,2 allocation failure,3 stack hook; hooks stop for debugger inspection and do not print. Stack-overflow hooks are not complete protection.

## Important interpretation
Queue copies8-byte structs; pointers would copy only pointer values and require explicit lifetime/ownership.

Binary semaphore used as lock is a comparison case, not recommended shared-resource protection; mutex must be taken/given by owner and is not ISR-safe.

Counting semaphore stores event/token count, not payload; binary semaphore coalesces repeated gives.

Avoid deadlock with global lock order, short ownership and bounded wait; never promise timeout alone proves correctness.

volatile debugger globals do not replace synchronization.

Six application tasks have256-word stacks each; Idle128words; heap4 is12288bytes.

## Source licenses
FreeRTOS MIT, ST HAL and CMSIS licenses are retained in project directories. See source-index.json and exact included source. User lesson source and authored calculation script are provided for educational reuse with attribution to GebraBit. No credentials, writer prompts or private notes are included.
