# GebraBit STM32 lesson 46

Target STM32F303CBT6 LQFP48 / GB100ST V2.0. Flash128KiB; main SRAM32KiB; CCM8KiB (not DMA-accessible). Native FreeRTOS V11.2.0, pinned 0adc196d4bd52a2d91102b525b0aafc1e14a2386. Actual generated CubeMX6.14.0 DB6.0.140 CubeF3V1.11.6 hardware modules plus explicitly manual kernel/application integration. Preserve included ST/CMSIS/FreeRTOS licenses.

## Validation actually performed
Local clean CMake Debug with Arm GNU Toolchain13.2.rel1/GCC13.2.1, CMake3.31.10, Ninja1.11.1. All C units -O0 -g3 -Wall -Werror; no Wextra/Pedantic. No warnings. ELF vectors/memory/BIN/HEX and pinned kernel source checked. No board execution, GUI demonstration or current/timing/trace measurement. Compilation is not runtime proof.

## Rebuild
Extract project-and-build.zip. Put the toolchain, CMake and Ninja bin directories on PATH. From each project directory run cmake --preset Debug, then cmake --build --preset Debug --clean-first. Export BIN with arm-none-eabi-objcopy -O binary build/Debug/PROJECT.elf build/Debug/PROJECT.bin. Keep one heap implementation and native kernel handler aliases. Original hardware/provenance IOCs are retained; these are not claims of a newly regenerated final combined configuration. Regeneration must preserve manual CMake entries, App modules, TIM6 HAL timebase and port ownership of SVC/PendSV/SysTick. main.c header and App_Start call remain in USER CODE Includes/2. Rebuild and re-audit vectors after changes.

## Actual project facts and behavior

### kernel

Native FreeRTOS V11.2.0

### kernel_commit

0adc196d4bd52a2d91102b525b0aafc1e14a2386

### generation

Real generated hardware baseline37 plus copied real generated ADC1lesson21, UART1/DMAlesson15, IWDGlesson28 peripheral modules/IOCs. Manual explicit integration and UART/DMA NVICpriority2->5 changes. App modules are user-authored, not CubeMX generated. Old IWDG lessonUSERCODEreportcalls removed; generated initialization retained.

### clock

HSE8MHz PLL9 HCLK72MHz APB1/2=36/72MHz Flash2WS. TIM6 HAL1ms, SysTick RTOS1000Hz. Tickless0. ADC synchronousHCLK/4=18MHz. LSI enabledforIWDG.

### architecture

App/Config/app_config.h centralconstants; App/Drivers/board_io ownsHAL/peripheralinitialization and wrappers; App/Model/app_logic is pureC ADCscaling/debounce/CSVformatter withoutHAL orRTOS includes; App/Services sensor/logger/button/supervisor owntaskbehaviors and dependonlyonHAL-free BoardResult/BoardUartEvent driverinterface plusRTOS; App/Rtos/rtos_app.c createsobjects/tasks thenstartscheduler. No blanket globalsascommunication: samplequeuecopies20byteSampleMessage; modequeue length1 xQueueOverwrite latestmode; healthEventGroup3bits clearedwhenALL observed.

### task_config

Sensor priority2 stack384words; Logger priority2 stack384words soleUARTTXowner; Button priority1 stack256words; Supervisor priority3 stack256words. Idle128words; heap_4 12288bytes; USART1 andDMA1ch4 IRQpriority5/sub0; configmaxsyscall5/encoded0x50.

### adc

ADC1channel2 PA1 analog, single12bit conversion, synchronous18MHz, sample181.5cycles +12.5conversion=194cycles, nominal10.7778us conversiononly. Calibration onceinBoard_Init beforetasks; SensorHALStart/Poll5ms/Get/Stop checksreturnstatus. App_ToMillivolts uses(raw*3300+2047)/4095, assumesVDDA3300mV; not calibratedrealvoltage. Inputpotentiometer betweenactual3.3V/GND, wiperPA1, no5V.

### message_flow

Sensor sendsSampleMessage {sequence,tick,raw,millivolts,mode},20bytesbycopy,queue8entries payload160B. Queuefulldropsnewest andincrementsg_log_dropped; nounboundedwait. Mode0nominal100ms delayAFTEReachsample,mode1nominal500ms, notexactperiod. ButtonPA3releasedHIGH/pressedLOW, GPIOpullup,5consecutiveidenticalsamples atnominal10ms; observedspanfirsttolast40ms, physicalqualificationroughly40-50ms pluslatency, notexact50ms. Eachdebouncedpress togglesmode, overwritequeue preserveslatestcommand; noEXTIused.

### uart_dma

UART1 PA9TX/PA10RXAF7 1152008N1, RXnotstarted. TXDMA1_Channel4normalmode; unusedRXDMAIRQ5disabled. SingleLoggerformatsintegerCSV sequence,tick,raw,millivolts,mode CRLF into static96bytebufferinmainSRAM (.bss), nofloatprintf/newlibmalloc. Generic5uint32fieldsmaximum56byteCSV; appvaluesusuallyshorter. BufferunchangeduntilfinalUARTTCcallbacknotmerelyDMAtransfercomplete. USART1IRQ5requiredafterDMATC. DriverHALcallbacksforwardstatusviaregisteredBoardUartEvent callback. Logger registersUartEventFromISR and notifiesitsownTask withvTaskNotifyGiveFromISR/portYIELD, withnoHALtypesorHALincludesinServices. ErrorcallbackrecordsHALerrorbeforeforwarding. Taskclearsstalenotificationsbeforestart andwaits50ms. Anyformat/start/timeout/errorfailure abortsTX, setsfatal, neverreusesbufferagain evenifabortfails; supervisorstopsfeedingIWDG. NoDcacheonF303, DMAcannotCCM. Noend-to-endrecipientack: completedUARTtransmissiondoesnotprovehostreceiveddata.

### watchdog

IWDGprescaler64,reload624,window4095. Nominal40kHzLSI=>1s; assumed30/50kHz=>1.333/0.8s, notmeasuredfrequencyguarantee. SupervisorwaitsALLSensor/Logger/Buttonhealthbits with600ms timeout,clearOnExitTRUE. Onlyifsawallandfatal0doesitrefreshIWDG. Loggerreportsevenonhealthyqueuewaittimeout; SensorreportsonlysuccessfulADC. Onafailure setsfatalandneverrefreshes; IWDGresetslater. NoISR/Idleunconditionalfeed. g_test_pause_sensor1invTaskSuspend simulatesstalledSensor; resetclearscommandBSS. g_reset_flags capturesRCCCSRbeforeclear; flagsarenotmutuallyexclusive. HardwareIWDGstartsBoard_Init beforetaskcreation,sofatalallocationhooksalsoultimatelyreset.

### testability

PureApp/Model hasnoHAL/FreeRTOSdependency andcanbecompiledagainsthosttests; driverwrapperscanbereplacedbystubs inaseparatehosttesttarget. Providedcalculationmodelisnotactualfirmwareexecution. Provided tests/app_logic_host_test.c callsactualpureCfunctions and passedseparateArmGCCcrosscompilation only; hostassertions wereNOTexecuted. No host compiler or target runtime execution performed.

## Limitations

ActualcleanWallWerrorcompilation andELF/HEX/BIN/sourcechecks; nophysicalADC/UART/button/watchdogresetmeasurements.

Modeoverwritecanmergequickcommands; queuefullrejectsnewdata; neitherqueueisendless.

IWDGhealthywindowandactualclocktolerancesmustbehardwarevalidated,includingworstcasescheduler/IRQlatency; nominal1s isnotexacttimeout.

Supervisorhealthchecksprogressnotallsemanticcorrectness; e.g UARTTCcannotproveconnectedhostreceivedbytes.

Recoverfromfatalwithwatchdogreset; noattempttomodifyinflightDMAdataorpretendtransientautorecovery.

App_ToMillivolts assumesvalidsupply_mv<=3600 and12bitADC input; actualinputprotection/VDDA mustbechecked.
