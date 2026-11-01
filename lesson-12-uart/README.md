# Lesson 12: USART1 polling echo and printf

Actual target STM32F303CBT6 LQFP48 on GB100ST V2.0. CubeMX6.14.0, DB6.0.140, STM32CubeF3V1.11.6, GCC13.2.1. HSE8MHz/PREDIV1/PLLx9; HCLK72MHz, APB1=36MHz, APB2=72MHz, Flash2WS. SWD PA13/PA14 retained. CSS off. The real generated project uses CMake; IDE GUI import or a target debugging session was not tested.

## Serial wiring

Board PA9 USART1_TX (LQFP48pin30) -> USB-serial adapter RX. Adapter TX -> board PA10 USART1_RX (LQFP48pin31). Connect a common GND. Use compatible3.3V UART logic, not directRS232 or5V TTL. The USB-serial adapter is separate from SWD; do not assume a virtualCOM port exists on a generic programmer. Power the board correctly and do not join different supply outputs just to obtain a serial link. Package pin numbers are not board header positions. Pins are verified against DS9118 and the boardV2.0 schematic.

Open the correct terminal at115200baud,8data bits,no parity,1stop bit,hardware flow control off. Local echo off avoids double characters. Reset the board after opening the terminal to see the startup banner; expected text is not a captured terminal log. The echo path relays each successfully received byte without line editing or CR/LF conversion.

## Actual generated UART settings

PA9/PA10 are AF7, push-pull, no pull, HIGH speed. USART1 clock mux is explicitly RCC_USART1CLKSOURCE_PCLK2, so its kernel clock is72MHz here. Do not assume every USART1 configuration always uses PCLK2; this chip has a kernel-clock mux. UART115200,8N1, TX/RX, noRTS/CTS, oversampling16 and one-bit-sampling disabled are generated in MX_USART1_UART_Init. UART interrupt andDMA are not enabled in this lesson.

For oversampling16, BRR=round(72000000/115200)=625=0x271. In the STM32F3 reference-manual notation for OVER8=0, USARTDIV=fCK/baud=625. The hexadecimal field can be decomposed into upper bits39 and lower bits1; the legacy39+1/16 representation must not be labeled USARTDIV in this F3 notation. Nominal baud is exactly115200:0% divider quantization error. This does not mean zero oscillator tolerance or serial-link error. Ideal bit time8.68056us and8N1frame time86.80556us are predictions. No physical baud or waveform was measured.

## Echo and error handling

Main calls HAL_UART_Receive for1byte with20ms timeout. A successful error-free byte is transmitted with another finite20ms timeout. Idle timeout is normal and increases uart_rx_timeouts. uart_rx_bytes counts accepted receive bytes; uart_tx_bytes also includes startup printf bytes. No delay or formatter runs inside an ISR.

The exact HAL behavior matters: UART_WaitOnFlagUntilTimeout can detectORE, set ErrorCode=HAL_UART_ERROR_ORE and returnHAL_ERROR; the enclosing HAL_UART_Receive translates any non-OK wait result intoHAL_TIMEOUT. Therefore main checks both returned status and HAL_UART_GetError, plus current ORE/FE/NE/PE flags. HAL_TIMEOUT with ErrorCode0 is ordinary idle timeout; HAL_TIMEOUT withORE follows the failure path. A returnedHAL_OK byte with a pending error flag is rejected conservatively.

On receive failure the code increments counters, records uart_last_error and invokes HAL_UART_AbortReceive. In this pinned F3 HAL the abort function clears the appropriate ICR error flags and issues RQR RXFRQ to discard stale receive data, then restoresRxState. This deliberately loses pending data to resume a simple experiment; it is not a lossless recovery protocol. No old-family SR-read/DR-read clearing sequence is introduced. If abort fails, generated Error_Handler stops. uart_last_error is the latest operation snapshot and can return to0 on a later idle loop, so use counters or a real debugger for persistent evidence.

Per-byte polling echo has receive-service gaps during transmission, printf and other main work. Incoming bursts can overrun hardware; this is not a guaranteed continuous lossless115200 link. Lesson13 introduces interrupt reception and buffering. Finite HAL timeouts require a progressing HAL tick; the normal SysTick remains enabled. They are not independent of interrupt/timebase health.

## printf redirection

The generated syscalls.c _write is weak. A single strong `_write(int file,char *ptr,int len)` in main.c USER CODE4 overrides it; the generated file is not edited and no second strong definition is added. Actual ELF inspection confirms GLOBAL _write and a linked printf symbol. stdout is made unbuffered. The implementation acceptsstdout/stderr, validates inputs and transmits each byte with20ms timeout; it reports -1 on first failure or a partial count after prior success and sets errno. Printing is main-context only; no reentrancy or concurrent writer support is promised. Long output can block for a length-dependent duration. Floating-point formatting is not enabled or demonstrated. Never recursively printf from _write or its error path.

## Actual verification and resources

Clean Debug build `-O0 -g3 -Wall -Werror` passed with no warnings. GNU size reports text19996B+data104B=20100B; linker FLASH region consumption is20108B because of8B alignment/padding. RAM region2176B includes linker heap/stack reservations and is not measured live usage. Real source ZIP, ELF/MAP ZIP, build report, versions/source hashes, exact snippets and HAL evidence are included. Third-party component licenses are retained.

Rebuild with an ARM-GCC/CMake/Ninja environment using `cmake --preset Debug` then `cmake --build --preset Debug`; adapt compiler locations. Run `python verify_model.py` beside the artifact ZIP to reproduce baud/frame calculations, status/error classification and actual offline _write/printf symbol inspection. Complete the pending hardware worksheet with real terminal/scope observations. No board flash, physical echo test, terminal capture, baud measurement, ORE injection or IDE GUI test has been performed. The final resources ZIP awaits article images.


## Inspected official STM32CubeF3 V1.11.6 examples
Projects/STM32F3-Discovery/Examples/UART/UART_TwoBoards_ComPolling/Src/main.c
https://github.com/STMicroelectronics/STM32CubeF3/blob/663d2baae3604244f90ed80d0d757df17e36ada9/Projects/STM32F3-Discovery/Examples/UART/UART_TwoBoards_ComPolling/Src/main.c
Projects/STM32F3-Discovery/Examples/UART/UART_TwoBoards_ComPolling/Inc/main.h
https://github.com/STMicroelectronics/STM32CubeF3/blob/663d2baae3604244f90ed80d0d757df17e36ada9/Projects/STM32F3-Discovery/Examples/UART/UART_TwoBoards_ComPolling/Inc/main.h
Relevant source snippets were actually inspected. The official polling example uses USART2 onPD5/PD6 at9600baud between two boards. This lesson adapts the HAL polling transmit/receive approach to USART1 onPA9/PA10 at115200baud with20ms timeouts and explicit error recovery. Board-specific BSP mappings were not copied.

Additional inspected printf reference: Projects/STM32F303ZE-Nucleo/Examples/UART/UART_Printf/Src/main.c and Inc/main.h in STM32CubeF3V1.11.6:
https://github.com/STMicroelectronics/STM32CubeF3/blob/663d2baae3604244f90ed80d0d757df17e36ada9/Projects/STM32F303ZE-Nucleo/Examples/UART/UART_Printf/Src/main.c
Its USART3PD8/PD9,9600,7data+oddparity and compiler-dependent __io_putchar/fputc differ from this lesson8N1 USART1 and strongNewlib_write. Only the redirection concept is adopted; original unchecked0xFFFF transmit timeout is replaced by checked20ms calls.

## Educational figures

Six original illustrative/model PNGs accompany this lesson; not GUI screenshots, photographs or scope/terminal captures. image-metadata.json records captions/basis. draw_figures.py regenerates them with Python3 + Pillow and installed Segoe UI; font files are not redistributed. No physical execution or measurement was collected.

## Download all files

[Download lesson12 resources ZIP](lesson-12-resources.zip)

Sources, .ioc, actual reports, ELF/MAP, scripts and figures are INSIDE the ZIP.
