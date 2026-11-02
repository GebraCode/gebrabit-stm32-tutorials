# Lesson21 — read a potentiometer

Use a10kΩ potentiometer connected between board3.3V and GND, with its wiper connected to PA1 (ADC1_IN2, MCU LQFP48 pin11). This is an external proposed experiment, not an onboard potentiometer. Keep the analog input within0..VDDA;5V must not reach PA1. Share GND with the meter and measure the wiper voltage against GND.

## Run the simple experiment

1. Extract the project ZIP. From its root build using `cmake --preset Debug` and `cmake --build --preset Debug` with GCC13.2.1/CMake/Ninja on PATH. The IOC is for CubeMX6.14.0 and STM32CubeF3V1.11.6.
2. Program the ELF with your own suitable SWD setup. Watch adc_raw, adc_voltage_mv_estimate, adc_valid and adc_sample_count. SWD remains PA13/PA14.
3. Move the wiper slowly. Expect codes toward0 at GND and toward4095 near VDDA; real offset, saturation and noise can change endpoints. Compare the computed millivolts with a multimeter, and record actual results in hardware-worksheet.csv.

The application attempts one conversion every100 HAL ticks. It is not a fixed-rate waveform recorder. Actual generated ADC settings: ADC1, PA1/IN2, single-ended,12-bit/right-aligned, scan disabled, continuous disabled, software trigger, EOC_SINGLE_CONV, overrun data preserved. Synchronous clock is AHB72MHz/4=18MHz; sampling181.5cycles gives10.083us sampling plus12.5cycles SAR, nominal10.778us conversion before software overhead. Main USER CODE2 calibrates using the F3-specific HAL_ADCEx_Calibration_Start(&hadc1, ADC_SINGLE_ENDED) before first Start while ADC is disabled.

USER CODE3 calls Start, PollForConversion with10ms timeout, GetValue only on HAL_OK, and Stop, checking statuses and errors. adc_valid=0 means invalid; old displayed raw/voltage values are stale. A failed attempt increments adc_failures and later attempts can retry; initialization/calibration failure enters Error_Handler. Timeouts require a running HAL tick and are not an independent watchdog.

The display uses adc_raw*assumed_vdda_mv/4095, initially3300mV. This is an estimate assuming the supply, not a measurement of VDDA. Changing assumed_vdda_mv in the debugger changes the estimate only. It does not change or limit the physical input. The quantization bin size is VDDA/4096 for12bits;4095 is the maximum code and the endpoint-scaling denominator. Lesson22 adds VREFINT correction. Resolution is not accuracy, and software ADC calibration does not remove all external gain/noise/source-impedance errors.

HAL_ADC_GetValue returns a number, not a HAL status. The actual F303 implementations of Start/Poll/Get/Stop and Calibration are in stm32f3xx_hal_adc_ex.c; hal_adc.c contains weak shared stubs. In this version polling does not automatically diagnose every overrun. A single software-triggered conversion with no following conversion avoids a scan overwrite race in this project; do not generalize this loop to fast continuous scan.

## Validation and source details

Clean real Debug build: GCC13.2.1, -O0 -g3 -Wall -Werror, zero warnings; Flash14408B, RAM region1696B. CubeMX6.14.0 / DB6.0.140 / CubeF3V1.11.6 package663d2baae3604244f90ed80d0d757df17e36ada9 and HAL953955afe65f89e60e556bbcdba752597f5da65d. Core72MHz, APB1/2=36/72MHz, Flash2WS. CMake build performed; CubeIDE GUI, board flashing, meter/ADC accuracy, aliasing and noise measurements were not performed. Logs, hashes, source IOC and actual ELF/MAP are supplied. Run python verify_model.py for arithmetic illustrations, not synthetic measurement evidence.

Closest inspected official example: Projects/STM32303C_EVAL/Examples/ADC/ADC_RegularConversion_Polling. It uses another board, sampling19.5cycles and different overrun/DMA request settings. We checked the actual example code, not its contradictory extracted descriptive clock line. Primary references are DS9118, RM0316, ES0204 and the pinned HAL source; no unseen page number is asserted. Driver/CMSIS licenses remain in the source ZIP.

## Original educational diagrams

Six original diagrams/models and editable draw_figures.py are included. They are not GUI/scope captures or physical measurements. Metadata records sources, assumptions, captions and alt text. Python3/Pillow and the system Segoe UI font regenerate the drawings; font files are not redistributed.

## Download the complete package

[All lesson 21 files](lesson-21-resources.zip)

Source/IOC, ELF/MAP, build reports, calculation model, hardware worksheet, third-party licenses and six editable diagrams are INSIDE the ZIP. Hardware validation is pending.
