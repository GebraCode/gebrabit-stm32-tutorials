# راهنمای پروژهٔ درس 14

این پروژه سه آرایهٔ جدا در SRAM دارد و برای مقایسهٔ memcpy با انتقال DMA آماده شده است. متغیرهای زمان فقط پس از اجرای واقعی روی برد معنا دارند؛ این بسته اندازه‌گیری سرعت ارائه نمی‌کند. مدل همراه چیدمان واقعی آرایه‌ها را در ELF بررسی می‌کند.

## جزئیات فنی و شواهد

# Lesson 14: real SRAM-to-SRAM DMA and pending timing comparison

STM32F303CBT6 LQFP48 / GB100ST V2.0; HSE8MHz PREDIV1 PLLx9, HCLK72MHz/APB1=36MHz/APB2=72MHz/Flash2WS. SWDPA13/14 retained, PB6safeLOW until successful checksum comparisons. Real CubeMX6.14.0 DB6.0.140 CubeF3V1.11.6 CMake project; GCC13.2.1 cleanDebug `-O0 -g3 -Wall -Werror` passes without warnings. Flash10832B, RAMregion4808B including linker reservations. No board run or GUItest is claimed.

## Actual generated DMA route

CubeMX generated hdma_memtomem_dma1_channel1 using DMA1_Channel1, DMA_MEMORY_TO_MEMORY, both PINC/MINC enabled, source/destination widthWORD32, DMA_NORMAL and HIGH channel priority. DMA1Channel1 IRQpriority2 is generated and calls HAL_DMA_IRQHandler. F303xB/C has DMA1with7channels and DMA2with5; this example uses onlyDMA1. Requests are fixed/channel-specific, not a modernDMAMUX. MEM2MEM is software-triggered and does not wait for a peripheral request; do not configure a competing ADC/peripheral request on the chosen channel.

MEM2MEM must not be combined withCircular on this hardware; RM0316 explicitly requires CIRC cleared. Circular peripheral streaming is explained separately, not demonstrated by this memory-copy configuration. In this direction the HAL maps source to CPAR and destination to CMAR; the wordsPeriph/Mem in the API register names do not mean a physical peripheral is used as source here. DataLength256 means256words, not256bytes. Alignment is4bytes.

## Buffer ownership and actual ELF proof

dma_source, cpu_destination and dma_destination are each256uint32 words=1024bytes. Actual offline ELF inspection verifies all3 symbols have size1024,4byte alignment and addresses inside0x20000000..0x20007FFF mainSRAM; none is in CCM0x10000000. DMA cannot access CCM on this device. Source remains unchanged during DMA; DMA destination is read/compared only after completion. DMB barriers order publication/readback. Cortex-M4F on this device has no data cache requiring maintenance; barriers are not a substitute for data-cache maintenance on another family.

The source pattern is `0x13570000 ^ (i*17)`. Main first calls memcpy into cpu_destination, then runs2actual DMA transfers into dma_destination. HT, TC andTE callbacks are registered with HAL_DMA_RegisterCallback before transfers. HAL_DMA_Start_IT enablesHT only because a half-complete callback exists; TC/TE also enabled. Short callbacks increment counters; TC records cycle elapsed in dma_elapsed_at_callback and separately sets the boolean dma_done flag. Zero elapsed is retained rather than replaced by a fabricated value. No HAL_Delay or formatting runs inside IRQ. HT/TC flags are status bits, not unbounded event queues; observed callback counts depend on servicing and must be recorded on the board.

## What the timing fields would measure

DWT CYCCNT is enabled via CMSIS CoreDebug/DWT. CPU memcpy records cpu_copy_cycles. Trial0 starts DMA then busy-waits with finite100ms HALtick timeout; trial1 starts DMA, performs1024LCG iterations as foreground work, then waits if needed. dma_start_cycles measures setup-to-return, dma_callback_cycles records start-to-TC-callback including IRQ latency, dma_total_wait_cycles records start-to-main continuation, and foreground_work_cycles covers the foreground work wallcycles including possible interrupts and contention. foreground_result prevents discarding the workload. Cycle counters use unsigned subtraction; the intended interval is far below a full32bit wrap.

All these counters are firmware instrumentation, not delivered measurements. Trial1 contains extra CPUwork, so its total walltime must not be directly advertised as a faster copy than memcpy. Busy-wait time is CPUoccupied; asynchronous copying creates an opportunity to do other work, not automatic zeroCPU cost. Bus contention, IRQoverhead, memory layout and library memcpy implementation affect results. Main is compiledO0; that does not imply the linked C-library memcpy was builtO0. For a fair bench report record repeated runs, optimization/toolchain, interrupts and array sizes; do not infer speedup from compile success.

After DMA completes, memcmp checks everyword and checksums are recorded; checksum equality alone is not used as complete data proof. benchmark_complete and LED are runtime outputs to inspect, not observed values supplied in this package. A DMA error or finite wait timeout reaches Error_Handler after abort attempt. Timeout requires progressing defaultHALtick; debugger halts can invalidate timing. No intentional TE injection was performed.

## Reproduce and validate

Extract source ZIP; use compatible ARM-GCC/CMake/Ninja and `cmake --preset Debug`, `cmake --build --preset Debug`, adapting tool paths. Separate ZIP contains actual ELF/MAP. python verify_model.py performs8 arithmetic/ELF placement checks; no cycle values are fabricated. Complete hardware-worksheet.csv on a real board before claiming DMA execution or timing. Code snippets and generated init are available with the article. Component licenses preserved; final resources ZIP includes lesson images.

Official inspected F3V1.11.6 reference: `Projects/STM32303C_EVAL/Examples/DMA/DMA_FLASHToRAM/Src/main.c` and its IRQ configuration. That example usesDMA2Channel1 andFlash-to-RAM; this lesson adapts Normal word/increment/callback configuration toDMA1Channel1 with both arrays inSRAM and adds original CPU/DMA timing instrumentation.

https://github.com/STMicroelectronics/STM32CubeF3/tree/663d2baae3604244f90ed80d0d757df17e36ada9/Projects/STM32303C_EVAL/Examples/DMA/DMA_FLASHToRAM

Hardware references: RM0316DMA/busmatrix, DS9118Rev14 (12channelDMA andCCM), PM0214DWT, pinnedHAL953955afe65f89e60e556bbcdba752597f5da65d. No simulated timing is represented as hardware performance.


Fresh v2 projects separately regenerated and clean-built2026-11-02. Old published resources unchanged. No GUI or board execution. New images and final resources bundle prepared separately.

Additional nominal calculations: `python calculate_clock.py`. Not board measurements.

[دانلود همهٔ منابع درس 14](lesson-14-resources-v2.zip)
