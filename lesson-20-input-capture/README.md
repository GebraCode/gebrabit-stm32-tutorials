# Lesson20 — timestamp both edges

Connect PA6 (TIM3_CH1 PWM output) to PA0 (TIM2_CH1 input) on the same GB100ST V2.0 board. PA6 is LQFP48 pin16; PA0 is pin10. These are MCU package numbers, not header positions. Same-board GND is already common. This lesson uses3.3V logic; an external source must respect the pin electrical limits and share GND. PA0 also supports analog functions: do not assume unrestricted5V tolerance.

## First experiment

Build the project with `cmake --preset Debug` then `cmake --build --preset Debug`. Flash with your suitable SWD setup. Watch `capture_period_ticks`, `capture_high_ticks`, `measured_frequency_millihz`, `measured_duty_permille` and `signal_present`. Expected nominal values are1000,250,1000000,250,1 for the supplied1kHz25% PWM. Debugger stops disrupt capture: inspect counters after free running, and compare with a scope. No hardware execution, IDE GUI or scope measurement was performed in preparing these files.

TIM2 free runs at1MHz: timer72MHz / (PSC71+1), ARR4294967295. Generated CubeMX channel1 captures rising edges from PA0/TI1, AF1, pulldown, ICF0 and ICPSC DIV1. User code in main.c USER CODE2 configures channel2 as indirect TI1, falling edge, same filter/prescaler; this extra channel setup is user code, not generated code. Both interrupts use TIM2 IRQ priority5. TIM3 on PA6 uses PSC71/ARR999/CCR250, PWM1/HIGH, ARPE+OC1PE. Core72MHz / APB136MHz / APB272MHz / Flash2WS matches the course clock.

At each rising edge the callback checks the previous rising/falling pair and publishes period/width. Unsigned subtraction handles one counter wrap, provided the elapsed interval is strictly shorter than one complete wrap. No update-overflow counting is implemented. Width must be strictly between0 and period: constantLOW/HIGH, missing edges and malformed frames are rejected rather than reported as0%/100%.

Disconnect the wire: the main loop continues without waiting for an edge. If more than250 HAL ticks pass after the last callback, signal_present becomes0 and computed fields become0. These zero display values mean invalid/no signal, not a measured0Hz. Previous raw sample values remain available but are stale when signal_present=0. Tick comparison and copying the multi-field sample use a short saved-PRIMASK critical section; original masking state is restored.

## Overcapture and limits

HAL_TIM_IRQHandler snapshots flags, clears CCxIF, sets active channel and calls the callback; it does not report CCxOF through a dedicated error callback. Our USER CODE hook at TIM2_IRQn0 inspects OF flags before HAL handling. It discards pending captures on overcapture or when both edge flags are pending, because HAL channel order would not establish chronological order. A second OF check occurs after reading CCR in the callback. Counters record detected overruns and conservative backlog drops. This is not a guarantee to detect every possible lost physical edge; service must finish before subsequent relevant edges, and interrupt masking or debugger halts can invalidate captures. No arbitrary maximum usable input frequency is promised.

Firmware accepts periods2..200000 ticks and width1..period-1. Thus the configured valid-period lower frequency is5Hz, much higher than the pure32-bit wrap lower bound of about0.000232831Hz. The1us tick gives one-tick relative period quantization about0.1% at1kHz and1% at10kHz; these figures exclude clock accuracy, input synchronization, signal quality and ISR throughput. Minimum mathematical period2ticks is not a usable500kHz claim. The default requires2000 edge interrupts per second; actual sustainable ISR rate remains to be measured. ICPSC DIV1 keeps every selected edge; a non-unit input divider changes capture cadence and must be included in frequency arithmetic. Digital filter0 provides no glitch filtering.

The alternative polarity-switch method and PWM Input/Slave Reset method are discussed in the article, but are not implemented by this free-running dual-channel project. No raw reset-mode period formula is applied to its timestamps. Both source and receiver share HSE: loopback ratio testing does not prove external frequency accuracy because common clock error cancels in the ratio.

## Validation and references

Actual clean GCC13.2.1 Debug -O0 -g3 -Wall -Werror build passed with zero warnings. Flash16092B, RAM region1792B. Full report, exact flags/source/artifact hashes, ELF/MAP and Python logical model are included. CubeMX6.14.0 DB6.0.140, CubeF3V1.11.6, package663d2baae3604244f90ed80d0d757df17e36ada9, HAL953955afe65f89e60e556bbcdba752597f5da65d. A build is not a board test. The model is not a capture log.

Nearest inspected official example: `Projects/STM32303C_EVAL/Examples/TIM/TIM_InputCapture`, CubeF3V1.11.6. Its TIM1/PE11,16-bit arithmetic and APB2 assumptions differ. We use its HAL call pattern, not its board mapping. RM0316 TIM2/TIM3/TIM4 input capture, DS9118 AF/pin tables, ES0204, AN4013 and AN4776 supply the device background. Actual driver behavior is documented in primary-source-evidence.md. Complete hardware-worksheet.csv yourself after testing. Upstream license files remain in Drivers.

## Original educational diagrams

Six original diagrams/models and editable draw_figures.py are included. These are not GUI/scope captures or physical measurements. Image metadata records sources, assumptions, captions and alt text. Python3/Pillow with system Segoe UI regenerates the drawings; font files are not redistributed.

## Download the complete package

[All lesson20 files](lesson-20-resources.zip)

Source/IOC, ELF/MAP, build reports, calculation model, worksheet, third-party licenses and six editable diagrams are INSIDE the ZIP. Hardware validation is pending.
