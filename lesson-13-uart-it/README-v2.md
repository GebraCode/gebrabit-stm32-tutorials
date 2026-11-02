# راهنمای پروژهٔ درس 13

این پروژه دریافت وقفه‌ای UART را از پردازش خط در حلقهٔ اصلی جدا می‌کند. دو نسخهٔ تک‌بایتی و ReceiveToIdle_IT همراه‌اند. ابتدا مدل و self-test میزبان را اجرا کنید؛ برای ادعای دریافت بدون افت، آزمون واقعی با شرایط ثبت‌شده لازم است. ساخت‌ها موفق‌اند، اما پورت سریال و برد در این تحویل آزمایش نشده‌اند.

## جزئیات فنی و شواهد

# Lesson 13: interrupt UART, bounded stream and recovery

Actual target STM32F303CBT6 LQFP48 on GB100ST V2.0, CubeMX6.14.0/DB6.0.140/CubeF3V1.11.6/GCC13.2.1. HSE8MHz PREDIV1 PLLx9 gives SYSCLK/HCLK72MHz, APB1=36MHz, APB2=72MHz, Flash2WS. USART1 kernel clock explicitly PCLK2;1152008N1 oversampling16, PA9TX/PA10RX AF7. SWDPA13/PA14 retained, PB6 LED activeHIGH initiallyLOW. CSS off. Real CMake-generated projects, not a tested IDE GUI import.

## Two compiled alternatives

- `gebrabit_lesson13_uart_it_v2`: standard HAL_UART_Receive_IT for1byte, completion callback queues that byte and rearms.
- `gebrabit_lesson13_idle_it_v2`: LESSON13_IDLE_IT=1; HAL_UARTEx_ReceiveToIdle_IT receives up to32bytes and calls HAL_UARTEx_RxEventCallback on IDLE or full transfer. This IT API is actually present in the pinned F3 HAL. It still services received bytes by interrupts; it is not DMA. The batch stops and is rearmed after each event, so an inter-batch reception gap remains. IDLE is a hardware inactivity event, not an application packet delimiter.

Both actually built clean with `-O0 -g3 -Wall -Werror` and no warnings. Standard variant linker FLASH21948B (text+data21892B), IDLE variant FLASH21972B (text+data21916B). RAM region2600B each includes linker heap/stack reservations; runtime usage has not been measured. Component licenses and real source IOC/ELF/MAP are retained in separate ZIPs.

## ISR-to-main ownership

ISR is the sole ring producer; main is the sole consumer. The256byte ring has255usable positions. Aligned uint32 head/tail are volatile; DMB publishes data before head and completes reads before tail. This is a Cortex-M4 single-core SPSC design, not a general multiple-producer queue or a claim that volatile makes arbitrary operations atomic. Main resets/flushed shared state only under saved/restored PRIMASK. No transmit, printf or line parser runs inside ISR. RX completion copies1byte, or at most32bytes in the IDLE variant, and rearms unless recovery is pending.

When the ring fills, new bytes are dropped, ring_drops and loss_epoch increase. Main detects loss, discards all queued bytes, resets the partial line and ignores input until the next line delimiter. discarded_on_resync counts those additionally flushed queued bytes. This intentionally sacrifices data to regain framing; it is not lossless behavior. Bounded96byte line storage accepts at most95characters plusNUL. Too-long or nonprintable input is discarded untilEOL. CR, LF andCRLF are normalized soCRLF produces one line.

## Re-arm error ordering matters

The actual F3 HAL IRQ error branch can call RxISR/completion before it saves the final ErrorCode for the outer blocking-error decision. Starting a new receive clears ErrorCode. Therefore both completion callbacks first read HAL_UART_GetError: if nonzero, they save the flags, request recovery and neither copy suspect data nor rearm. This preserves the outer HAL ORE/error handling. HAL_UART_ErrorCallback only stores aggregate flags/counter and recovery_pending.

Pinned HAL treats ORE/RTO in IT reception as blocking; PE/FE/NE without blocking conditions can notify while a transfer could continue. This course deliberately takes conservative main-context recovery for all notified errors: HAL_UART_AbortReceive clears ICR flags and flushes stale RQR receive data, queued/partial data are discarded, and the selected receive API is restarted. In8N1 parity is disabled, so PE behavior is a documented library feature, not an executed parity test. Aggregate uart_error_flags persists; no physical error injection has been done.

## Bounded test protocol

Send `S,<uint32 decimal sequence>,<0..32 payload bytes as hex>,<2hex sum8>\n`. sum8 is the modulo256 sum of ASCII bytes before the last comma. Example generation is in protocol_model.py; do not hand-copy an unchecked checksum. A valid line returns `A,<sequence>,<sum8>\r\n` and togglesPB6. Sequence wraps uint32. sequence_discontinuities counts mismatched sequence transitions, not the exact number of missing bytes. Sum8 is an illustrative checksum with collisions, not CRC, security or proof of zero corruption.

Reply construction and HAL_UART_Transmit with finite100ms timeout run only in main. Main can be delayed during transmission; the ISR ring continues until capacity/latency limits. At1152008N1, one ideal character takes86.806us;255bytes represent about22.135ms of ideal backlog. This budget depends on real execution, IRQ latency and sender behavior. Compile success cannot establish the Word experiment's no-loss condition.

Run `python verify_model.py`:12 pure arithmetic/parser/ring checks include100frames, byte versus32byte chunk feeding, CRLF, checksum corruption example, sequence wrap, ring capacity/wrap, overflow/NUL discard and error-before-rearm decision. This is not MCU execution. Run `python host_verify_serial.py --self-test` without hardware or pyserial. For a real operator-run test install pyserial in a chosen environment, connect compatible3.3V serial logic with crossedTX/RX and commonGND, then use `--port COMx --count 100 --window 1`; increasewindow for a declared burst experiment. Missing/duplicate/badACKs are reported. Reset and flash the intended variant before testing. No serial port was opened in this delivery.

For deliberate overrun, use a controlled debugger exercise: temporarily mask USART1IRQ while sending more than hardware receive capacity, restore it, and record error flags/recovery and later valid frames. This is a proposed bench procedure, not a performed test. Do not globally stop SysTick while expecting finite HAL transmit timeouts. Fill the pending hardware worksheet with firmware variant, sender seed/window, VDD, host adapter and actual results.

## Official references actually inspected

STM32CubeF3V1.11.6 `Projects/STM32F3-Discovery/Examples/UART/UART_TwoBoards_ComIT/Src/main.c`, `Src/stm32f3xx_it.c` and `Inc/main.h` were inspected as relevant extracted source. That example uses USART2PD5/PD6 at9600, fixed arrays and readiness callbacks; this course uses USART1PA9/PA10 at115200 and adds original bounded parsing/ring/error recovery.

https://github.com/STMicroelectronics/STM32CubeF3/tree/663d2baae3604244f90ed80d0d757df17e36ada9/Projects/STM32F3-Discovery/Examples/UART/UART_TwoBoards_ComIT

Pinned HAL source commit953955afe65f89e60e556bbcdba752597f5da65d, especially uart.c IRQ/RxISR/error handling and uart_ex.c ReceiveToIdle_IT. RM0316 USART and DS9118Rev14 pin/clock limits are the hardware references. No official ring/parser example is claimed verbatim. No hardware run, terminal trace, actual throughput/error measurement, CubeIDE GUI session or hardware verification is claimed here.


Fresh v2 projects separately regenerated and clean-built2026-11-02. Old published resources unchanged. No GUI or board execution. New images and final resources bundle prepared separately.

Additional nominal calculations: `python calculate_budget.py`. Not board measurements.

[دانلود همهٔ منابع درس 13](lesson-13-resources-v2.zip)
