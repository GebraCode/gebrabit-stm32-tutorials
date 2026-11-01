# Lesson 10: NVIC software-pending experiment

Target: STM32F303CBT6, LQFP48, GebraBit GB100ST V2.0. Real CubeMX6.14.0 / DB6.0.140 / STM32CubeF3V1.11.6 projects; HSE crystal8MHz, PREDIV1, PLLx9, SYSCLK/HCLK72MHz, APB1=36MHz, APB2=72MHz, Flash2WS. SWD PA13/PA14 retained, CSS disabled. This is a CMake-generated project, not a claim of a tested CubeIDE GUI project.

## Two actual compiled projects

- `gebrabit_lesson10_nvic`: LESSON10_EQUAL_PREEMPT=0; GROUP4 has4 preemption bits and0 subpriority bits. EXTI0 logical priority2, EXTI1 logical priority1. Predicted RAM trace: `[1,2,3,4]`.
- `gebrabit_lesson10_equal`: only the macro default changes to1; GROUP3 has3 preemption bits and1 subpriority bit. Both preemption priorities1; EXTI0 subpriority1, EXTI1 subpriority0. Predicted trace: `[1,3,4,2]`. Subpriority cannot preempt an active handler of equal preemption priority.

Both projects were actually built clean with GCC13.2.1, `-O0 -g3 -Wall -Werror`, no warnings. Each uses Flash8956B and RAM region1632B. RAM includes linker reservations, not measured runtime stack usage. Source projects and genuine ELF/MAP pairs are separate ZIPs. Version/compile commands/source hashes/build reports are included. Original third-party licenses are retained.

## Software NVIC, not a physical EXTI input

No EXTI peripheral line, GPIO EXTI mux, edge detector or external interrupt wire is configured. EXTI0/EXTI1 vector names are deliberately reused as available software-pended NVIC IRQs. There is no EXTI pending flag to clear in this experiment. Do not add a physical EXTI source without adding correct peripheral servicing.

Strong handlers in main.c USER CODE4 override the startup weak aliases. The generated interrupt source does not also define these handlers. Offline inspection of each actual ELF verifies GLOBAL binding and the real vector slots: IRQ6 at exception22, IRQ7 at exception23. This proves linking, not handler execution.

Main starts a trial approximately every1s. It saves PRIMASK, disables configurable interrupts, disables/clears these NVIC lines, resets the RAM trace, re-enables the lines and restores the saved PRIMASK. It then pends EXTI0. The low handler writes PB6 HIGH, logs1, executes a short NOP loop, pends EXTI1, logs3 after the request and logs4 before returning PB6LOW. The high handler writes PB7HIGH, logs2 and returns PB7LOW. Short bounded NOP loops make pulses potentially observable; their duration and total exception latency are not measured or promised. HAL_Delay is used only in main, never inside an ISR. SysTick can continue between trials; main's1000ms request is not an exact measured repetition period.

`trace_events`, `trace_length`, `trace_overflow`, `low_active_seen` and `high_saw_low_active` are volatile debug variables. Default predicts high_saw_low_active=1; equal-preempt predicts0. These are predictions, not captured values. This controlled program requests the high IRQ only after the low handler's first trace write is complete; it is not a general concurrent multi-producer ring buffer. volatile preserves access visibility; it does not make arbitrary compound operations atomic.

## Wiring and safe observation

PB6 is LQFP48pin42 and drives the onboard active-HIGH transistor LED circuit. PB7 is LQFP48pin43 and is exposed as PB7 on the board. Connect suitable scope channels to board PB6/PB7 signals and a nearby common GND; no added LED or load is required on PB7. Do not confuse IC package numbers with board header positions. Use compatible3.3V signal probes and appropriate loading. Breakpoints change timing; use real scope capture for preemption pulse experiments.

## Priority and mask interpretation

The exact xC header defines __NVIC_PRIO_BITS=4. CMSIS logical priorities0..15 become the upper4 bits in an IPR byte. GROUP4 is encoded AIRCR.PRIGROUP3; GROUP3 is encoded PRIGROUP4. Lower numerical preemption priority is more urgent. Subpriority orders simultaneously eligible pending IRQs of equal preemption priority; it does not interrupt equal-preempt active work. NMI and HardFault have fixed priority and are not masked by PRIMASK. BASEPRI selectively masks configurable priorities at or below an encoded nonzero threshold; BASEPRI=0 disables that threshold. This project uses saved/restored PRIMASK for trace reset; it does not claim an executed BASEPRI experiment.

Tail-chaining and late arrival are architecture mechanisms, not cycle measurements from this project. No exact12-cycle entry/6-cycle chaining guarantee is inferred for this board with Flash/memory/bus/FPU effects. No physical ISR latency, scope waveform, target debug trace or board execution has been collected.

## Reproduce and verify

Extract the source ZIP. With a compatible ARM-GCC/CMake/Ninja environment run `cmake --preset Debug`, then `cmake --build --preset Debug`; adapt compiler locations to your installation. Run `python verify_model.py` beside the build-artifacts ZIP for priority arithmetic and actual ELF vector inspection. The script uses only Python3 standard library. Populate hardware-worksheet.csv with genuine observations before calling predictions hardware results.

Primary sources: ST PM0214 Rev10, exact CMSIS core_cm4.h/cmsis_gcc.h, generated startup_stm32f303xc.s, pinned HAL cortex driver, DS9118 Rev14 and official board V2.0 schematic. Exact references and source evidence are provided separately. 


## Inspected official STM32CubeF3 V1.11.6 examples
Projects/STM32F3-Discovery/Examples/GPIO/GPIO_EXTI/Src/main.c
https://github.com/STMicroelectronics/STM32CubeF3/blob/663d2baae3604244f90ed80d0d757df17e36ada9/Projects/STM32F3-Discovery/Examples/GPIO/GPIO_EXTI/Src/main.c
Projects/STM32303C_EVAL/Examples/Cortex/CORTEXM_SysTick/Src/main.c
https://github.com/STMicroelectronics/STM32CubeF3/blob/663d2baae3604244f90ed80d0d757df17e36ada9/Projects/STM32303C_EVAL/Examples/Cortex/CORTEXM_SysTick/Src/main.c
Relevant extracted source snippets were actually inspected. The NVIC software-pending two-vector exercise is original user code, not a verbatim ST example. GPIO example is PA0/rising and contains a busy-loop debounce; this course uses PA3/both edges and deferred main-loop debounce instead. UART example is USART2PD5/PD6 at9600, two boards; this course adapts toUSART1PA9/PA10 at115200 with20ms timeouts. Board-specific BSP pin mappings were not copied. Cortex SysTick example confirms the HSEPLL72 baseline but is not a two-IRQ preemption demo.

## Educational figures

Six original illustrative/model PNGs accompany this lesson; not GUI screenshots, photographs or scope/terminal captures. image-metadata.json records captions/basis. draw_figures.py regenerates them with Python3 + Pillow and installed Segoe UI; font files are not redistributed. No physical execution or measurement was collected.

## Download all files

[Download lesson10 resources ZIP](lesson-10-resources.zip)

Sources, .ioc, actual reports, ELF/MAP, scripts and figures are INSIDE the ZIP.
