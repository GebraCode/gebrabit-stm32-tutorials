# مدیریت Heap و Stack و تشخیص کمبود حافظه در FreeRTOS

فایل‌های همراه درس 44 جبرابیت. [دانلود بستهٔ کامل](lesson-44-resources.zip) شامل پروژه، خروجی ساخت، اسکریپت‌ها، برگهٔ آزمایش و 6 تصویر آموزشی است.

وضعیت: کامپایل واقعی بدون هشدار انجام شده؛ اجرای روی برد و اندازه‌گیری فیزیکی انجام نشده است.

# GebraBit STM32 lesson 44 memory laboratory

This project teaches FreeRTOS heap statistics, static task allocation and diagnostic hooks on the STM32F303CBT6, using the GebraBit GB100ST V2.0 board. It uses the native FreeRTOS API.

## What was validated

The normal Debug build and a separate opt-in overflow build were compiled locally with Arm GNU Toolchain 13.2.rel1 (GCC 13.2.1), CMake 3.31.10 and Ninja 1.11.1. Both clean builds compiled 31 C files with `-O0 -g3 -Wall -Werror`, without warnings. Each passed 13 ELF and source checks. `-Wextra` and `-Wpedantic` were not enabled.

The normal image occupies 23248 bytes of Flash and reserves 19216 bytes of main RAM. The overflow variant occupies 23364 bytes of Flash and reserves 19216 bytes of main RAM. Reserved RAM includes the FreeRTOS heap, static task buffers and linker reservations; do not add the heap size again.

Hardware execution, debugger GUI operation, timing measurements and runtime stack high-water measurements were **not performed**. Compilation does not establish runtime correctness. The supplied allocator model is a calculation based on the source and the normal ELF image, not a hardware log.

## Source and hardware baseline

The hardware files derive from the real CubeMX 6.14.0, DB 6.0.140, CubeF3 V1.11.6 project generated for lesson 37. The project and IOC were renamed for this lesson. No new GUI regeneration was performed. The application and native FreeRTOS integration are manual additions, rather than CubeMX-generated middleware.

FreeRTOS-Kernel V11.2.0 is pinned to commit `0adc196d4bd52a2d91102b525b0aafc1e14a2386`. The project links the `ARM_CM4F` port and only `heap_4.c`. MIT, ST and CMSIS license files are retained.

The MCU has 128 KiB Flash, 32 KiB main SRAM and a separate 8 KiB CCM region. This project places its data in main SRAM. HSE is 8 MHz; PLL multiplication is 9; SYSCLK is 72 MHz; APB1 and APB2 are 36 and 72 MHz; Flash latency is 2 wait states. HAL uses TIM6 for its 1 ms tick. FreeRTOS owns SysTick, PendSV and SVC, with a 1000 Hz kernel tick.

## Rebuild the normal version

Put the Arm compiler, CMake and Ninja on PATH. In the project directory, run:

```sh
cmake --preset Debug
cmake --build --preset Debug --clean-first
arm-none-eabi-objcopy -O binary build/Debug/gebrabit_lesson44_memory.elf build/Debug/gebrabit_lesson44_memory.bin
```

When regenerating hardware code, preserve `App/Rtos`, the manual kernel integration in CMake, `rtos_app.h` in the main.c USER Includes section, and `App_Start()` in USER CODE section 2. Preserve TIM6 as the HAL timebase and keep automatic generation of SVC, PendSV and SysTick handlers disabled. Rebuild after regeneration.

## Normal operation

The Monitor task uses 384 stack words and priority 2. Worker uses 256 words and priority 1. Idle uses 128 words and priority 0. The timer daemon uses 256 words and priority 3. In this port one stack word is 4 bytes. All four task buffers are static. The heartbeat timer object is static, and this kernel also selects a static command queue when static allocation is enabled. The queue length is 8.

Dynamic allocation remains enabled for the demonstration. `heap_4` has a 12288-byte array in BSS. Startup performs an 8-byte allocation and free to initialize the allocator, then compares heap availability before and after creating the two static application tasks. `g_static_create_heap_delta` is expected to remain 0, which does not mean those tasks consume no RAM.

The Monitor task allocates blocks A, B and C with payloads of 256, 512 and 256 bytes. It then frees A and C, records the separated free regions, frees B, and records adjacent-block coalescing. `g_heap_samples[0..4]` stores free bytes, historical minimum, largest free block, free-block count and allocation counters. These remain available after `g_heap_stage` becomes 4. Normal monitoring repeats every 500 ticks.

The timer callback toggles the onboard active-high LED on PB6 once every 1000 ticks. A full LED cycle nominally takes 2 seconds. This is expected behavior, not a measured timing result. The callback does not allocate or block. No UART output is implemented.

Record actual board observations in `memory-observation.csv`; its result fields are intentionally blank. Compare them with `memory-model-output.json`, which explicitly contains model values. Stack high-water values are returned in words. Multiply by 4 for bytes, exercise rare paths, and retain a justified margin. A fill-pattern watermark cannot prove that every future path fits. Debugger halts also change timing.

## Failure experiments

Use the normal build for the first two experiments. Run normally before changing a command. Reset the target after each experiment.

1. Set `g_memory_command = 1` and resume. The requested allocation equals the whole configured heap and cannot include the required metadata. `vApplicationMallocFailedHook` is expected to increment `g_malloc_failures`, set `g_app_error = 2` and halt.
2. Set `g_memory_command = 2` and resume. The program changes `worker_stack[0]` inside its own static buffer and wakes Worker. At the next switch out of Worker, the kernel's method 2 check should enter `vApplicationStackOverflowHook`, set `g_app_error = 3`, and record the task handle and name. This is **controlled guard corruption**, not a real deep-stack overflow. It exercises the check path without deliberately moving SP outside the stack.

The hooks only record minimal diagnostic globals and halt. They do not print, allocate, block or attempt to repair corrupted state. Overflow checking is not memory protection: a large overflow can cause a Fault or corrupt the TCB before the hook runs.

## Separate actual overflow drill

The normal build rejects command 3 and increments `g_command_rejected`. To compile the deliberately unsafe laboratory variant, explicitly run:

```sh
cmake -S . -B build/UnsafeOverflow -G Ninja -DCMAKE_BUILD_TYPE=Debug -DAPP_ENABLE_UNSAFE_OVERFLOW=ON
cmake --build build/UnsafeOverflow --clean-first
```

Use only a resettable, isolated test board and deliberately select the `UnsafeOverflow` artifact. Under a debugger, set `g_memory_command = 3` and resume. The recursive function requests 25 frames, each containing a 64-byte volatile array, exceeding the Worker's 1024-byte stack. Memory corruption is expected. Either the hook or a Fault can occur; the hook is not guaranteed. This variant was compiled but **never executed** during preparation. It does not run the overflow automatically.

## newlib and allocation boundaries

The FreeRTOS heap and newlib's linker heap are different allocators. Pair `pvPortMalloc` with `vPortFree`, and `malloc` with `free`.

`configUSE_NEWLIB_REENTRANT = 1` provides per-task C library reentrancy state. It does not by itself lock the system-wide malloc pool. Newlib allocator locks and system stubs need their own review, including recursive locking requirements where applicable. This project uses `configUSE_NEWLIB_REENTRANT = 0`, calls no allocating libc functions, and its ELF contains no libc malloc implementation. Adding formatted I/O or other allocating libc calls requires a separate review and hardware test.

No unverified CubeMX menu path is claimed here. The native setting in this project is in `App/Rtos/FreeRTOSConfig.h`; inspect the actual generated macro if a different integration is used.

## References

- [Pinned FreeRTOS source](https://github.com/FreeRTOS/FreeRTOS-Kernel/tree/0adc196d4bd52a2d91102b525b0aafc1e14a2386)
- [newlib C library manual, allocator locking and reentrancy](https://sourceware.org/newlib/libc.html)

Application code and the numerical model were authored for GebraBit. All model outputs and physical observations are deliberately distinguished.
