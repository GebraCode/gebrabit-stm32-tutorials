# Lesson 15: circular UART DMA with explicit ownership and deadlines

Real STM32F303CBT6 LQFP48 / GB100ST V2.0 project. CubeMX6.14.0 DB6.0.140 CubeF3V1.11.6 HAL953955afe65f89e60e556bbcdba752597f5da65d and GCC13.2.1. HSE8MHz/PREDIV1/PLLx9, SYSCLK/HCLK72MHz, APB1=36MHz/APB2=72MHz/Flash2WS. USART1 kernel explicitly PCLK2=72MHz,1152008N1 oversampling16, AF7PA9TX/PA10RX. SWDPA13/14 retained; PB6 toggles only on accepted lines. Compatible3.3V crossedTX/RX and commonGND required; package pins30/31 are not board header numbers. No5VTTL orRS232 direct connection.

## Actual generated channels and IRQs

CubeMX generated USART1_TX DMA1Channel4 Normal/LOW priority and USART1_RX DMA1Channel5 Circular/HIGH priority; byte widths, memory increment enabled, peripheral increment disabled. __HAL_LINKDMA links both handles. MX_DMA_Init runs before MX_USART1_UART_Init. DMA1Channel4, DMA1Channel5 and USART1 IRQs all have the same preemption priority2 under GROUP4, so UART and DMA callbacks cannot preempt one another. This makes them a serialized single ring producer. Do not change their grouping/priority independently without redesigning synchronization. DMA hardware channel priority differs from NVIC preemption priority.

Main starts HAL_UARTEx_ReceiveToIdle_DMA on a64byte SRAM buffer. HT/TC callbacks remain enabled, and USART1IRQ is required forIDLE, errors and finalTXTC. No DMA-request remapping is enabled. Actual generated files, channel routing and real ELF buffers are verified by the accompanying script. DMA buffers are in mainSRAM0x20000000..0x20007FFF, not CCM; this F303 has no data cache needing maintenance.

## Size is a position; current NDTR is the drain cursor

HAL_UARTEx_RxEventCallback Size is the event's first-free position in1..64, not a count of newly received bytes. HT commonly reports32, TC64, IDLE a partial position. A callback can be late or duplicate another notification. Treating a staleHT Size32 after anIDLE position40 as a wrap would copy duplicates.

This project validates Size and records HT/TC/IDLE event counters, then samples CURRENT __HAL_DMA_GET_COUNTER. Current write position is `(64-NDTR)&63`;0 represents the modulo wrap. Data from dma_read_cursor up to that current position are copied once to the auxiliary512byte SPSC ring, with511usable slots. A DMB precedes CPU buffer reads. The producer publishes copied ring data before advancinghead; main alone advances tail. No zero-copy ownership claim is made: DMA-to-ring copying deliberately protects a separate software queue from later DMA reuse.

Stale event Size does not move the cursor backwards. Equal cursor means no inferable new bytes: it may be a duplicate, or an entire unobserved64byte revolution. Firmware does not invent64bytes on an equal-cursorTC. If IRQ service falls behind a complete revolution, modulo position cannot reconstruct or universally detect overwritten data. rx_no_progress_events includes duplicates/ambiguity and is not an overrun count. ring_drops detects only auxiliary-ring overflow, not every DMA overwrite.

HT/TC must be serviced before DMA overtakes the unread region. At nominal1152008N1,32bytes take2.77778ms,64bytes5.55556ms; actual safe latency also includes copy/interrupt timing and clock error. Avoid masking these IRQs for such intervals. A larger auxiliary queue cannot repair a missed DMA deadline.511bytes represent about44.358ms ideal queued data, a separate main-consumer budget. No finite buffer guarantees lossless arbitrary sender traffic.

## Parser and protocol

The bounded protocol is identical to lesson13: `S,<uint32 decimal sequence>,<0..32 payload bytes as hex>,<2hex sum8>CR/LF/CRLF`. Checksum is modulo256 sum of ASCII prefix before the final comma. Valid lines produce `A,<sequence>,<sum8>\r\n`. Sequence mismatches increment sequence_discontinuities; sum8 has collisions and is neither CRC nor security. Host expectedACKs expose missing/duplicate sequences but cannot prove all physical errors are detected.

Main parser uses96byte storage, maximum95characters+NUL. Nonprintable bytes and overlong lines are discarded toEOL; CRLF generates a single line. Auxiliary overflow triggers flushing queued data and partial line, then resynchronization atEOL. The same resynchronization occurs after UART/DMA recovery. This intentionally drops data and cannot be called lossless recovery.

## TX buffer belongs to DMA until UART finalTC

tx_buffer is a persistent32byte SRAM ACK buffer. Main parses only while tx_busy=0. After formatting an ACK it sets tx_busy before HAL_UART_Transmit_DMA and does not modify the buffer until completion or completed abort. In the pinned HAL, normal TX DMA completion clearsDMAT and enables UARTTCIE; the final UARTTC path invokes HAL_UART_TxCpltCallback. Only this application callback, or main after HAL_UART_AbortTransmit, clears ownership. DMA channelTC alone does not release the application buffer here. Main never writes a stack-local reply buffer for asynchronous DMA.

If transmit start fails or the100ms HALtick watchdog expires, main requests recovery and aborts before reuse. It never assumes HAL_BUSY means the previous buffer may be overwritten. A receive error can conservatively cancel a simultaneousTX ACK during full recovery; host must treat missingACK as a failed transaction. The100ms watchdog is a recovery bound under a progressing tick, not a queue-capacity guarantee; the auxiliary queue may fill earlier.

## Error handling and restart

The RX event callback checks HAL_UART_GetError before copying. ErrorCallback only aggregates uart_error_flags/counter and sets recovery_pending. In the actual F3 HAL, ORE/RTO in IT or any UARTerror duringDMA reception can abort RX; DMA abort callback ordering is part of the pinned source. This project conservatively recovers notified errors in main, not inside IRQ: under saved/restored PRIMASK it calls HAL_UART_AbortReceive and HAL_UART_AbortTransmit, clearsTXownership only after abort, resets drain cursor, flushes ring and partial line, enters discard-toEOL and restarts ReceiveToIdle_DMA. AbortReceive uses F3ICR clears and RQRflush, not another family's SR/DR sequence. If restart fails, pending recovery remains for another attempt; fatal abort errors reach Error_Handler. No byte preservation across errors is promised.

DMA continues writing while main parses orTXruns. The same-priority serialized callbacks and bounded copying assumption are necessary. PRIMASK sections are intentionally short control operations; fault injection, long interrupt masking and debugger stops can violate reception deadlines. No physical overrun/recovery test was performed.

## What was actually validated

CleanDebug `-O0 -g3 -Wall -Werror` compiled with no warnings. GNU text+data23516B; linker FLASH region23572B includes56B layout/alignment; RAMregion3096B includes reservations, not measured live usage. SourceIOC and genuine ELF/MAP are separateZIPs with hashes and pinned sources. The Python checks verify staleHT/TC duplicate handling, wrap,1000ordered synthetic bytes within service bounds, explicit full-revolution ambiguity,511slot capacity,100protocol frames, recovery/ownership decisions, actual ELF SRAM buffers and actual generated channel/IRQ mapping. These are models and offline artifact checks, not MCU execution.

Use `python host_verify_serial.py --self-test` without hardware; no serial port or pyserial installation is needed. For an operator-run bench test install pyserial separately and supply `--port COMx --count 100 --window 1`, then declare larger randomized burst windows and record missing/bad/duplicateACKs. Use the supplied seed and payload limits. No host serial run was done here.

## CPU-load comparison remains a bench task

At1152008N1 continuous input, byteIT can require about11520RXcompletion callbacks/s;64byte circularDMA yields about360HT/TCcallbacks/s before additionalIDLE/error/TX events. These are nominal event-rate calculations, not CPUload percentages. DMA callback still copies bytes; parser/checksum/TXsetup remain CPUwork. Main continuously polls queue/TXstate rather than sleeping, so this program does not demonstrate aggregateCPUidle or low-power improvement. Measure actual HALIRQ+callback+main service cycles under comparable traffic for polling12, byteIT13 and DMA15 before claiming load reduction. Record optimization/library/IRQsettings, VDD and sender conditions. CPU_load_percent is deliberatelynull in model results.

## References and reproduction

Official STM32CubeF3V1.11.6 example actually inspected: `Projects/STM32F3-Discovery/Examples/UART/UART_TwoBoards_ComDMA/Src/main.c`, `Inc/main.h`, `Src/stm32f3xx_it.c`. It uses USART2PD5/PD6, DMA1TX7/RX6 and fixed buffer transfers; this course adapts to USART1TX4/RX5 and adds original circular-IDLE cursor/parser/ownership code. Do not copy its board macros into GB100ST.

https://github.com/STMicroelectronics/STM32CubeF3/tree/663d2baae3604244f90ed80d0d757df17e36ada9/Projects/STM32F3-Discovery/Examples/UART/UART_TwoBoards_ComDMA

Pinned uart.c/uart_ex.c provide the actual ReceiveToIdle_DMA, callback and finalTC behavior. RM0316 fixed DMA request table and USART register semantics; DS9118Rev14 pin/electrical limits. Rebuild with ARM-GCC/CMake/Ninja using `cmake --preset Debug` and `cmake --build --preset Debug`, adapting tool paths. Component licenses retained. No board flash, terminal trace, CPU measurement, waveform, error injection or IDEGUI run was performed; final resources ZIP includes the article images.

## Educational figures

Six original educational diagrams/models with captions in image-metadata.json; no screenshots or physical measurements. draw_figures.py reproduces figures using Python3/Pillow and an installed Segoe UI font (not redistributed). Full-resolution files are included. The drawings represent configuration, reasoning and expected behavior, not actual board evidence.

## Download all files

[Download lesson15 resources ZIP](lesson-15-resources.zip)

Complete project sources/IOC, actual ELF/MAP and reports, scripts, worksheet and six editable diagrams are INSIDE this ZIP.
