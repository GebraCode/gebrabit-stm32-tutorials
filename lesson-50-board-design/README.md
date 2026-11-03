# GebraBit STM32 lesson 50 — custom board design

The main deliverable is schematic-review-checklist.csv. It is a blank review aid, not a certified PCB design. Target STM32F303CBT6 LQFP48; case study GebraBit GB100ST V2.0. Official schematic is linked in source-index.json; the copyrighted drawing is not redistributed.

## What was actually verified
The real minimal companion firmware was clean-built locally with Arm GNU Toolchain13.2.rel1 GCC13.2.1, CMake3.31.10 and Ninja1.11.1. All20 C translation units use -O0 -g3 -Wall -Werror, no warnings. ELF mainSRAM32KiB/CCM8KiB/Flash128KiB, no private workstation paths. No board was fabricated, powered or measured; no ERC/DRC/EMC/ESD qualification was performed. No exact crystal or regulator vendor qualification is claimed.

## Firmware provenance and deliberate clock choice
The actual CubeMX6.14.0 DB6.0.140 / CubeF3V1.11.6 generated lesson05 hardware baseline is reused and renamed. The only functional addition is a volatile heartbeat in USER CODE PV/3. This task did not regenerate that baseline. HSI8MHz and PLL off deliberately allow first bringup without trusting the external crystal. This is not the course72MHz peripheral configuration. No RTOS or board LED dependency. g_bringup_heartbeat increments once before each HAL_Delay(500U); expected around4counts in2seconds while running, not a measured guarantee or independent clock validation. Pause/resume and breakpoints affect this observation.

## Rebuild
Extract this bundle. Put Arm GNU toolchain, CMake and Ninja bin directories on PATH. From project/ run `cmake --preset Debug` then `cmake --build --preset Debug --clean-first`. Optional export: `arm-none-eabi-objcopy -O binary build/Debug/gebrabit_lesson50_bringup.elf bringup.bin`. Import the CMake project into compatible CubeIDE/CMake tools. The IOC is provided as actual generation provenance; regeneration requires preserving USER CODE additions and the manual warning/path flags, then rebuilding.

## Bringup sequence
Check power-off shorts, polarity, exact package pin1, all power pins, NRST/BOOT0 and the model-specific SWD connector first. Use a properly current-limited supply based on a real current budget. Measure VDD/VDDA/NRST before connecting the probe; target3.3V, VDDA must satisfy its sequencing constraint. Verify probe VTref/GND/SWDIO PA13/SWCLK PA14/NRST; VTref is not automatically a power output. Program and observe the heartbeat, then separately validate HSE/LSE and the intended peripherals. Record actual observations in bringup-measurements-blank.csv. Never deliberately short supplies or overvoltage analog pins as a teaching fault.

## Calculations and diagrams
Run `python calculations.py` for hypothetical crystal-load/LDO/RC calculations. CL8pF/Cs3pF ->10pF each is a teaching example, not the actual GB100ST crystal datasheet. Run `python draw_figures.py` with Pillow and an installed Segoe UI font to recreate6original educational figures; font files are not included. These are not instrument screenshots, CAD output or fabricated PCB evidence. Original figures and drawing code: CC BY4.0, GEBRA ENG. Original added heartbeat: MIT; retain ST/CMSIS component licenses and copyright notices. All remaining inherited source remains under its original license.
