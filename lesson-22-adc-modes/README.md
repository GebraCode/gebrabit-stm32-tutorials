# Lesson22 — ordered channels and continuous conversion

Two actual projects are supplied. Start with gebrabit_lesson22_adc_scan: connect one external10kΩ potentiometer between3.3V/GND with wiper to PA1, and another different known voltage within0..VDDA to PA2. A second10kΩ pot is convenient. PA1/ADC1_IN2 is MCU pin11; PA2/ADC1_IN3 is pin12. These are LQFP48 package numbers, not connector positions. Never apply5V to these analog inputs. Measure each voltage and VDDA against common GND with a multimeter.

## Read the three ranks

Build with `cmake --preset Debug` then `cmake --build --preset Debug`, using GCC13.2.1/CMake/Ninja, or regenerate the IOC with CubeMX6.14.0/CubeF3V1.11.6. Program using your suitable SWD setup. Watch adc_raw_channels[0..2], adc_voltage_mv[0..1], adc_voltage_assumed_mv[0..1], measured_vdda_mv, adc_valid and adc_sequences. These are not printed to UART.

Generated rank order is PA1/IN2, PA2/IN3, then internal VREFINT/channel18. Every channel uses single-ended12-bit right-aligned conversion and sampling181.5cycles. The synchronous ADC clock is AHB72MHz/4=18MHz. Scan is enabled, continuous disabled, discontinuous enabled with one rank per software trigger, EOC_SINGLE_CONV, no DMA and preserved overrun data. Three successive HAL_ADC_Start calls each advance one rank, with Poll10ms/GetValue between them; the results are sequential, never simultaneous. Normal sequence completion returns to rank1 for the next sequence. The three analog conversion times total32.333us nominal, but software gaps add time; this is not a measured scan duration.

HAL ConfigChannel enables VREFEN while configuring rank3. Before first conversion main waits HAL_Delay(1U), longer than the12us stabilization constant, and calibrates the disabled ADC with ADC_SINGLE_ENDED. Factory VREFINT calibration is read as uint16 at the header-defined0x1FFFF7BA address, for calibration VDDA3300mV. LL header is included for constants only; peripheral control remains HAL.

For each valid sequence VDDA_estimate=3300*factory_code/VREFINT_raw, then external_mV=external_raw*VDDA_estimate/4095. Comparison values using3300 are also exposed. Factory0 or a value above4095 causes initialization failure; VREFINT raw0, invalid raw codes or a computed VDDA outside2000..3600mV reject the sequence. The range is a sanity check for this device, not a promise of analog performance across the entire range. Treat the corrected value as an estimate: calibration tolerance, temperature drift, ADC errors, noise and reference settling remain.

The scan loop explicitly checks OVR before each Start and after Poll. This matters because Start clears flags/ErrorCode and Poll does not itself test OVR in the pinned F303 implementation. It captures status/errors, stops the ADC and clears OVR. Any scan failure increments adc_failures and enters Error_Handler: a partially completed failed sequence is not silently retried with an assumed rank order. Stop failure also halts. adc_valid=0 marks invalid/stale values; do not use stale raw or voltage as fresh measurements. Poll timeouts need the HAL tick to run.

## Continuous single-channel comparison

gebrabit_lesson22_adc_continuous uses only PA1/IN2. Scan is disabled, continuous enabled, AutoWait enabled, sampling181.5cycles/18MHz. Main calibrates first, then attempts a batch every100 HAL ticks. One Start begins conversion;32 Poll/GetValue operations copy results to adc_cont_samples. AutoWait holds off the next conversion until DR is read; HAL polling preserves EOC when AutoWait is enabled. Reading DR releases the next conversion. Main then stops ADC; a conversion already started after the final read may be aborted and discarded. No DMA or conversion IRQ is used.

Watch adc_cont_valid, adc_cont_batches, adc_cont_errors and the last status/error. Only a valid completed batch is indicated as valid; a failed batch may contain partially updated/stale array entries. This continuous example is paced by CPU reads and software gaps, not a fixed-rate sample stream. Its32 nominal analog conversions sum344.889us before gaps/AutoWait delays. The code still checks OVR and finite10ms Poll timeouts. Stopping failure enters Error_Handler. No lossless or maximum-throughput guarantee is inferred from compilation.

| Channels | Once | Continuous |
|---|---|---|
|Single|One result per trigger; lesson21|Automatic repeat; supplied continuous AutoWait project|
|Scan|Ordered ranks per sequence; supplied discontinuous scan is paced one rank/trigger|Sequences repeat automatically; fast polling can overwrite DR, use appropriately designed DMA in lesson23|

Discontinuous pacing is an additional scan choice, not synonymous with scan. CONT and discontinuous cannot both be enabled. An unpaced scan must transfer each result before the next conversion overwrites or overruns DR; our one-rank-per-trigger project avoids that race by not launching the next rank until after reading the previous result. Choosing EOS alone does not save all earlier channel data. Low sampling time with a high-impedance source can bias the reading even when all HAL statuses are OK; change the sampling setting in the IOC and rebuild for the deliberate short/long comparison experiment.

## Validation and sources

Both real clean Debug builds passed with -O0 -g3 -Wall -Werror, zero warnings. Scan Flash15204B/RAM1720B; continuous Flash13636B/RAM1752B. Toolchain GCC13.2.1, CubeMX6.14.0/DB6.0.140, CubeF3V1.11.6 package663d2baae3604244f90ed80d0d757df17e36ada9, HAL953955afe65f89e60e556bbcdba752597f5da65d. Core72MHz/APB1=36MHz/APB2=72MHz/Flash2WS. Full exact build reports, source/artifact hashes and actual ELF/MAP are included. Neither project was flashed/tested on a board or in CubeIDE GUI. Meter readings, VDDA correction accuracy and noise/source-impedance effects are PENDING in hardware-worksheet.csv. Python models use explicitly synthetic arithmetic inputs, never measured data.

Nearest inspected official sequencer example: Projects/STM32F303RE-Nucleo/Examples/ADC/ADC_Sequencer. It demonstrates three-rank software-triggered discontinuous sequencing but uses DMA, a temperature-sensor rank, DAC stimulus and another board. Its code also contains illustrative comments/macros that must not be treated as this device's measured voltage calibration. Single-poll reference: Projects/STM32303C_EVAL/Examples/ADC/ADC_RegularConversion_Polling. RM0316 section15.3.20/15.3.17 and the actual source establish sequence/stop behavior; DS9118 establishes pin and analog limits, AN4195 F3 modes and AN2834 accuracy/background, ES0204 silicon limitations. Driver/CMSIS licenses remain in each project.

## Original educational diagrams

Six original diagrams/models and editable draw_figures.py are included. They are not GUI/scope captures or physical measurements. Metadata records sources, assumptions, captions and alt text. Python3/Pillow and the system Segoe UI font regenerate the drawings; font files are not redistributed.

## Download the complete package

[All lesson 22 files](lesson-22-resources.zip)

Source/IOC, ELF/MAP, build reports, calculation model, hardware worksheet, third-party licenses and six editable diagrams are INSIDE the ZIP. Hardware validation is pending.
