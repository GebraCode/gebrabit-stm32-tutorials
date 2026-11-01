# Lesson 11: physical EXTI3 with deferred debounce

STM32F303CBT6 / GB100ST V2.0. HSE8MHz PREDIV1 PLLx9 gives HCLK72MHz, APB1=36MHz, APB2=72MHz, Flash2WS. SWD PA13/PA14 retained. Real CubeMX6.14.0/DB6.0.140/F3V1.11.6 CMake project. Clean GCC13.2.1 Debug `-O0 -g3 -Wall -Werror` build passed with no warnings: Flash8608B, RAM region1600B including linker heap/stack reservations. No board execution or IDE GUI test was performed.

## Real board circuit and generated route

Onboard USER BUTTON is PA3, physical LQFP48pin13, activeLOW. R17=0Ohm series link, R2=10kOhm external pull-up to3V3, C2=100nF toGND. GPIO_NOPULL deliberately uses the external resistor; no extra button required. Nominal RC1ms is not proof that all bounce disappears. PB6physical42 drives the onboard NPN LED circuit, activeHIGH and initiallyLOW.

CubeMX actually generated PA3 GPIO_MODE_IT_RISING_FALLING, no pull, EXTI3 priority2 and NVIC enable. HAL_GPIO_Init configures the GPIOA selection in SYSCFG EXTICR for line3 and both EXTI trigger bits. Only one port can feed a given GPIO EXTI line: PA3 and PB3 cannot both independently map to EXTI3. EXTI3 has a dedicated IRQ; lines5..9 share EXTI9_5 and10..15 share EXTI15_10, which require servicing/checking each configured source. This project enables only EXTI3.

Generated EXTI3_IRQHandler calls HAL_GPIO_EXTI_IRQHandler(USER_BUTTON_Pin). The pinned HAL tests PR, clears its write-one-to-clear pending bit, then calls HAL_GPIO_EXTI_Callback. The strong user callback in USER CODE4 checks the pin, increments irq_callbacks and stores last_irq_tick=HAL_GetTick. It contains no delay, output formatting or LED toggle.

## Deferred20ms qualification

Main takes a very short saved/restored PRIMASK snapshot of GPIO level, tick and callback counters. New callbacks reset the quiet-time origin to the latest callback tick; a newly observed raw GPIO change resets it to the current sample tick. Only after20ms without those observed changes is stable_level updated. An acceptedLOW increments debounced_presses and toggles PB6. Qualified release changes stable state without toggling. Initial raw/stable levels come from the actual boot sample, so a held boot button does not generate a synthetic press; release and press again.

The main loop has no HAL_Delay and continuously polls to complete deferred qualification. It is not a sleep/event-only low-power design. IRQ timestamps have1ms nominal HAL resolution; no true continuous physical stability, exact latency or wall-clock precision is claimed. Unsigned subtraction handles ordinary uint32 tick rollover with timely processing. Callback-count comparison also crosses an ordinary count wrap; a whole unseen2^32 callbacks is outside the intended use.

irq_callbacks counts executed HAL callbacks, including press and release edges, not all physical contact transitions. EXTI PR is a pending bit, not a queue; several edges can coalesce while pending/masked. The board RC and GPIO thresholds also affect observed events. irq_callbacks-debounced_presses is not a bounce count. Use scope/logic capture for a real physical bounce investigation. volatile is not a substitute for the snapshot critical section and does not generally make compound updates atomic.

## Files and reproduction

Source project and genuine ELF/MAP are separate ZIPs. Full build report, exact toolchain/source hashes, actual generated handler and HAL source evidence are included. Preserve component licenses. With an ARM-GCC/CMake/Ninja installation run `cmake --preset Debug` then `cmake --build --preset Debug`, adapting compiler paths. Run `python verify_model.py` for10 synthetic checks covering bounced press/release, held boot, short pulse, delayed callback, tick wrap and callback counter wrap. This is arithmetic prediction, not hardware execution or a CPU simulator. Complete hardware-worksheet.csv after real board experiments.

No final resources ZIP is created before the article images are added. No live waveform, bench photograph, physical bounce count or CubeIDE GUI session is claimed.


## Inspected official STM32CubeF3 V1.11.6 examples
Projects/STM32F3-Discovery/Examples/GPIO/GPIO_EXTI/Src/main.c
https://github.com/STMicroelectronics/STM32CubeF3/blob/663d2baae3604244f90ed80d0d757df17e36ada9/Projects/STM32F3-Discovery/Examples/GPIO/GPIO_EXTI/Src/main.c
Projects/STM32F3-Discovery/Examples/GPIO/GPIO_EXTI/Src/stm32f3xx_it.c
https://github.com/STMicroelectronics/STM32CubeF3/blob/663d2baae3604244f90ed80d0d757df17e36ada9/Projects/STM32F3-Discovery/Examples/GPIO/GPIO_EXTI/Src/stm32f3xx_it.c
Relevant source snippets were actually inspected. The official GPIO example uses Discovery PA0 with a rising edge and a busy-loop debounce. This lesson adapts the HAL IRQ/callback route to the onboard PA3 active-LOW button, both edges and deferred20ms main-loop qualification. Board-specific BSP mappings and the original blocking callback were not copied.

## Educational figures

Six original illustrative/model PNGs accompany this lesson; not GUI screenshots, photographs or scope/terminal captures. image-metadata.json records captions/basis. draw_figures.py regenerates them with Python3 + Pillow and installed Segoe UI; font files are not redistributed. No physical execution or measurement was collected.

## Download all files

[Download lesson11 resources ZIP](lesson-11-resources.zip)

Sources, .ioc, actual reports, ELF/MAP, scripts and figures are INSIDE the ZIP.
