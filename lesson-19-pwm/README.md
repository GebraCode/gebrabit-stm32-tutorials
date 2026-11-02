# Lesson19 — hardware PWM on TIM3

This project targets STM32F303CBT6, LQFP48, on GB100ST V2.0. It produces hardware PWM on PA6 / TIM3_CH1 / AF2. PA6 is MCU package pin16, not a statement about connector positions. The board LED on PB6 is a different signal. Use a compatible scope on PA6 with common GND; never connect a motor directly to this GPIO.

## Start with the default experiment

1. Extract `lesson-19-projects.zip`. Open the IOC in CubeMX6.14.0 using STM32CubeF3V1.11.6, or build the supplied CMake project with GCC13.2.1, CMake and Ninja available on PATH.
2. For command-line build: `cmake --preset Debug`, then `cmake --build --preset Debug` from the project root. Use an independent build directory if your machine has an existing cache. The delivered sources were built remotely using these actual CMake files; CubeIDE GUI and hardware flashing were not performed.
3. Flash the ELF with your own suitable SWD setup. The supplied ELF/MAP are actual build outputs. SWD PA13/PA14 remains reserved. Power and probe voltage must match the board.
4. Expect nominal1kHz PWM. Default duty steps are25%,50%,75%, each held by a `HAL_Delay(1000U)` call. This is a step demonstration, not a fade. The delay includes HAL tick behavior and execution latency; no exact software dwell duration was measured.

Clock: HSE8MHz, PLLx9, SYSCLK/HCLK72MHz, APB1 divide2 gives PCLK1=36MHz and TIM3 kernel72MHz; APB2=72MHz, Flash latency2. TIM3 upcount, PSC71, ARR999, initial CCR1=250, PWM1, HIGH polarity, ARPE enabled. HAL PWM channel configuration enables OC1PE. Counter tick is nominal1us, period1000 ticks.

## Optional debugger controls

Change these volatile variables only with awareness that pausing the debugger disrupts the experiment. Mode changes are read at the next outer loop; default mode may first finish its three delays.

| lesson_mode | Behavior |
|---|---|
|0|Default25/50/75% steps|
|1|CCR750 established across an update boundary, then CCR250 written after polling CNT>=500 with OC1PE enabled|
|2|Same trial but OC1PE disabled immediately before waiting for CNT>=500|
|3|Stop PWM, preload PA6 ODR LOW, configure PA6 as push-pull GPIO LOW|
|4|Use lesson_duty_permille in range0..1000 as CCR1, because ARR is fixed999|

Mode4 supports0,250,500,750,1000 for0%,25%,50%,75%,100%. It is not a generic function for a different ARR. Invalid values stop the output LOW and enter Error_Handler. Other invalid modes enter Error_Handler. The actual partial pulse in mode2 depends on software timing: the ideal model writes exactly at CNT500, while compiled firmware polls >=500 and then executes a write. No scope trace is supplied. Continuous PWM with OC1PE disabled is a deliberately discouraged comparison experiment, not a production configuration. The comparator-only model's500-tick partial pulse is illustrative and is not a guaranteed hardware result.

Each phase polling wait has a20ms HAL tick deadline (checked with >20). Timeout sets lesson_hal_error5, requests GPIO LOW, then stops in Error_Handler. This protection requires a running HAL tick; it is not an independent watchdog and does not protect against a halted debugger or masked tick interrupt. With only this simple main loop, polling normally spans many timer cycles before this timeout, but that is not a measured scheduling guarantee.

Returning from mode3 restores AF2 while the timer is stopped, writes CCR250/CNT0, issues UG, clears UIF and restarts PWM. UG is deliberately issued while stopped in this helper; no live-period UG trial is implemented. Do not claim a guaranteed glitch-free pin handover. HAL_TIM_PWM_Stop alone does not guarantee a physical LOW pin, which is why mode3 explicitly reconfigures the pin.

## What was checked

Actual clean CMake Debug GCC13.2.1 build: -O0 -g3 -Wall -Werror, zero warnings. text12652B, data16B, bss1656B; Flash12668B and RAM region1672B. These are build figures, not runtime stack high-water measurements. Exact flags, source hashes, ELF/MAP hashes and report are included. CubeMX6.14.0 / DB6.0.140 / STM32CubeF3V1.11.6. Firmware selection is pinned with LastFirmware=false and user edits stay in USER CODE blocks. The generated main/SystemClock_Config/tim.c remain distinct from user code in the source project.

Run `python verify_model.py` for arithmetic and discrete-time model checks. Predicted nominal1kHz, TON0.25/0.5/0.75ms and ideal average0.825/1.65/2.475V are calculations, not measurements. Actual HSE accuracy, VOH/VOL, load, transitions, probe effects and scope readings remain pending. Complete hardware-worksheet.csv after actual testing.

TIM3 registers are16-bit: PSC0/ARR71999 is invalid. At1kHz, PSC1/ARR35999 gives the largest exact period count36000; at20kHz, PSC0/ARR3599 gives3600. At ARR65535, CCR65536 cannot be represented; CCR65535 is slightly below100% in PWM1/HIGH upcount. PWM2 and polarity LOW invert the physical HIGH duty relationship. Center-aligned mode has a different timing formula and is not configured here. ARPE controls ARR buffering, OC1PE controls CCR1 buffering, and PSC is buffered independently.

The nearest inspected official example is STM32CubeF3 `Projects/STM32303C_EVAL/Examples/TIM/TIM_PWMOutput`: it demonstrates HAL_PWM_Init, ConfigChannel and Start on four channels. Its board/pins/prescaler and ARPE setting differ; it was used as a call-order reference, not claimed as this board's project. See primary-source-evidence.md for exact pinned references.

Original lesson user code and documentation are provided for educational reuse under MIT; upstream ST/CMSIS files retain their own licenses included in Drivers. No hardware, CubeIDE GUI, scope, fade, live UG, center-aligned or motor experiment has been executed by this package preparation.

## Original educational diagrams

Seven original diagrams/models and their editable draw_figures.py script are included. Metadata records assumptions, sources, alt text and captions. No diagram is a GUI/scope capture or physical measurement. In particular the OC1PE-off transient figure is an abstract comparator illustration, NOT guaranteed hardware behavior. Python3/Pillow and an installed Segoe UI font regenerate the drawings; the font is not redistributed.

## Download the complete lesson package

[Download all lesson19 files](lesson-19-resources.zip)

Sources/IOC, ELF/MAP, build reports, calculation model, worksheet, licenses and seven editable diagrams are INSIDE the ZIP. This is the revised student-oriented lesson19 package; earlier root-level lesson19 links remain unchanged.
