# GebraBit lesson 48 USB CDC echo

This project turns an STM32F303CBT6 on the GebraBit GB100ST V2.0 board into a USB Full-Speed CDC ACM echo device. It uses a bounded, single-packet mailbox and USB backpressure. It is a teaching example rather than a high-throughput bridge or a USB-certified product.

## Validation and versions

The complete hardware and CDC skeleton was actually generated for this lesson by headless STM32CubeMX 6.14.0, DB 6.0.140, using STM32CubeF3 V1.11.6. The CubeF3 repository commit is `663d2baae3604244f90ed80d0d757df17e36ada9`. The application additions are confined to USER CODE regions; CMake/toolchain warning and path-mapping flags are manual additions.

ST USB Device Library V2.5.3 is pinned to `e5a58ee2260204bfed632c7c56da0fdb41514a51`. All 10 generated library files were compared byte for byte with that official commit and matched. The middleware's `License.md` references ST Ultimate Liberty SLA0044; ST/CMSIS license files are preserved. This middleware is not presented as MIT licensed.

A local clean CMake Debug build with Arm GNU Toolchain 13.2.rel1, GCC 13.2.1, compiled 30 C files using `-O0 -g3 -Wall -Werror`, without warnings. `-Wextra` and `-Wpedantic` were not enabled. Fourteen ELF/vector/BIN/HEX checks passed. The image uses 31932 bytes of Flash and reserves 6608 bytes of main RAM, including linker heap/stack reservations. USB PMA is a separate 512-byte peripheral memory.

**No hardware execution, enumeration, COM-port test, echo test, throughput measurement or GUI test was performed.** The numerical model is not a USB trace. The host script is supplied for the reader to run and was not run against a device during preparation.

## Hardware for the bench experiment

The board has no USB connector. Use a USB 2.0 Type-B or Micro-B female breakout with clearly marked VBUS, D-, D+ and GND, plus a USB data cable. With all power disconnected:

- Connect D- to PA11, MCU LQFP48 pin 32.
- Connect D+ to PA12, MCU LQFP48 pin 33.
- Connect USB GND to board GND.
- Add an external 1.5 kOhm pull-up from D+/PA12 to board 3.3 V, **never to 5 V or VBUS**. The GPIO's internal pull-up is not a replacement.
- For this bus-powered example, feed USB VBUS 5 V into the board's 5 V regulator input. Do not apply it to the 3.3 V rail or either data pin. Disconnect other power supplies. A probe's reference/sense pin is not an additional supply.

Keep data wires short and together. Real PCB designs need proper USB routing and suitable low-capacitance ESD protection; a loose-wire bench setup does not establish electrical compliance. BOOT0 must remain in user-Flash boot mode, normally GND. Program via SWD on PA13/PA14.

The board and the pull-up must lose power when USB VBUS is absent. A self-powered product requires VBUS-presence detection and pull-up/connection control not implemented here. The external fixed pull-up is not physically disconnected by the generated PCD connection callback; unplug and reconnect the USB cable after programming or resetting if necessary. This application is CDC, not the ROM DFU bootloader.

## Clocks, endpoints and descriptors

HSE is 8 MHz, PREDIV is 1, PLL multiplier is 9, SYSCLK is 72 MHz, AHB divider is 1, APB1 is 36 MHz and APB2 is 72 MHz. Flash latency is 2 wait states. USB uses the PLL output divided by 1.5, giving 48 MHz. USB Full-Speed line signalling is 12 Mbit/s, a different quantity. HAL uses the ordinary 1 ms SysTick; no RTOS is included.

PA11 and PA12 use AF14 USB. The generated USB low-priority ISR calls `HAL_PCD_IRQHandler(&hpcd_USB_FS)`, with NVIC priority 5. The interrupt's historical name `USB_LP_CAN_RX0_IRQHandler` does not prove that USB and CAN share packet memory.

The CDC communication and data interfaces are 0 and 1. EP0 handles control requests. Bulk IN endpoint 0x81 and bulk OUT endpoint 0x01 have a 64-byte maximum packet; interrupt IN endpoint 0x82 has an 8-byte maximum packet. IN and OUT are named from the host's perspective. A USB byte stream does not preserve the boundaries of application writes or messages.

The actual generated identifiers are ST's demonstration VID 0x0483 and PID 0x5740, with the generated ST product strings. They are not an independently assigned GebraBit VID/PID. A production product needs appropriate identifier authorization, descriptors and compliance work. The IOC sets two interfaces and bus-powered operation (`USBD_SELF_POWERED = 0`). The descriptor's default 100 mA budget is a declared value, not a measurement of this board.

The virtual serial line starts at 115200, 8 data bits, no parity and 1 stop bit. GET/SET_LINE_CODING store and return the seven descriptor bytes. They do not configure a UART or change USB signalling speed. This project does not gate echo on DTR and is not a USB-to-UART bridge.

## Build and regenerate

Install Arm GNU Toolchain 13.2.rel1, CMake 3.31.10 and Ninja 1.11.1 and put their executables on PATH. In the project directory:

```sh
cmake --preset Debug
cmake --build --preset Debug --clean-first
arm-none-eabi-objcopy -O binary build/Debug/gebrabit_lesson48_usb_cdc.elf build/Debug/gebrabit_lesson48_usb_cdc.bin
```

The complete IOC is included. When regenerating, preserve the user sections in `USB_DEVICE/App/usbd_cdc_if.c`, its header's exported declaration, and the `USB_EchoPoll()` call in the main loop's USER CODE region. Keep the USB clock divider, two-interface configuration, bus-powered descriptor and warning flags. Rebuild and review after regeneration.

## Echo ownership and backpressure

`CDC_Receive_FS` runs through the USB interrupt. It copies at most 64 received bytes into the static mailbox and marks it ready. It deliberately does not rearm OUT. Consequently, later OUT transactions are NAKed until the mailbox is released. This bounds storage without discarding a new packet just because the previous echo is in progress.

`USB_EchoPoll` runs in the main loop. It submits the stable mailbox with `CDC_Transmit_FS`, handles `USBD_BUSY` by trying again in a later poll, and keeps the bytes unchanged while the class's TxState remains nonzero. The V2.5.3 driver clears TxState after IN completion, including any required zero-length packet after a full-size transfer. Only then does the application release the mailbox and rearm OUT.

The poll saves PRIMASK, briefly masks interrupts while accessing the USB class and mailbox state, and restores the previous value. No RTOS APIs are used. There is no blocking retry loop in the USB ISR. Do not add a second concurrent transmitter or reuse the buffer early without redesigning ownership and synchronization. Session deinitialization discards unfinished data; this is not persistent storage or a reconnect queue.

## Reader experiment

After checking the wiring and rails, flash the normal Debug image and connect the USB data cable. Expected behavior is CDC enumeration with a host-selected virtual serial port. Neither a specific COM number nor driver behavior is claimed as tested. Open the actual port with terminal local echo disabled and compare a short transmitted ASCII line with the returned bytes.

For a binary test, install pyserial in the host Python environment and explicitly select the correct port:

```sh
python echo_test.py COM7
```

The script compares exact payloads of 1, 63, 64, 65, 128, 257 and 1024 bytes, including binary zero. It does not discover ports or run unless the reader supplies one. Replace COM7 with the actual port; Linux may use a path such as `/dev/ttyACM0`. This is a functional echo check, not a throughput or USB compliance test.

Record actual results in the blank `usb-observation.csv`. Useful globals include `g_usb_sessions`, `g_rx_packets`, `g_rx_bytes`, `g_echo_completed`, `g_tx_busy`, `g_tx_failures`, `g_rx_errors`, `g_rx_rearms`, `g_line_coding_changes` and `g_usb_session_discards`. `g_tx_busy` counts retry polls, not lost packets. Debugger halts disturb the USB link and timing; use them for diagnosis, not throughput claims.

If the host never reads returned data, an IN transfer can remain pending and the application intentionally stops rearming OUT. If enumeration fails, check the data cable, D+/D- wiring, external pull-up, 3.3 V supply and 48 MHz USB clock before changing buffer code. Closing/reopening the port and reconnecting the cable begins a new test after a reset or disconnect.

## Correction to the lesson-order document

The Word order document incorrectly attributes the STM32F103 shared USB/CAN memory restriction to STM32F303xB/C. Official AN4228 Rev 6, Table 6 on printed page 12 states that the F303/302xB/C CAN memory is not shared with USB and the USB memory is not shared with CAN. AN4879's family table also distinguishes these parts from F103.

This does not remove pin-multiplexing conflicts: USB uses PA11/PA12, which can also carry CAN on another mapping. This project leaves CAN disabled and does not demonstrate simultaneous CAN/USB operation. The Word file was not modified.

## References

- [Pinned ST USB Device Library V2.5.3 source](https://github.com/STMicroelectronics/stm32-mw-usb-device/tree/e5a58ee2260204bfed632c7c56da0fdb41514a51)
- [AN4228 official PDF, Table 6](https://www.st.com.cn/resource/en/application_note/an4228-migrating-from-stm32f1-series-to-stm32f3-series-microcontrollers-stmicroelectronics.pdf#page=12)
- [AN4879 family implementation table](https://www.st.com/content/st_com/en/technical-documents/an4879-introduction-to-usb-hardware-and-pcb-guidelines-using-stm32-mcus-stmicroelectronics_asset/chunk-001-topic-an4879-usb-on-stm32-products.html)
- [AN2606, F302xB/C and F303xB/C bootloader hardware table](https://www.st.com.cn/resource/en/application_note/an2606-stm32-microcontroller-system-memory-boot-mode-stmicroelectronics.pdf)

Application code and arithmetic model were authored for GebraBit. The third-party source and license notices are retained.
