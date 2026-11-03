# Timer نرم‌افزاری و مدیریت زمان در FreeRTOS

فایل‌های همراه درس 43 جبرابیت. [دانلود بستهٔ کامل](lesson-43-resources.zip) شامل پروژه، خروجی ساخت، اسکریپت‌ها، برگهٔ آزمایش و 6 تصویر آموزشی است.

وضعیت: کامپایل واقعی بدون هشدار انجام شده؛ اجرای روی برد و اندازه‌گیری فیزیکی انجام نشده است.

# GebraBit STM32 lesson 43

Target: STM32F303CBT6 LQFP48 / GebraBit GB100ST V2.0.

## Validation and limits

Actual local Windows clean CMake Debug compilation -O0 -g3 -Wall -Werror and ELF/BIN/HEX/kernel source audit passed. No -Wextra/-Wpedantic; no physical board execution, SWV capture, GUI execution, DWT/timing measurement or runtime heap measurement performed.

Build variants and exact sizes are in build-*.json. These are static linker reservations, not runtime heap consumption. No hardware measurement values are supplied. Fill measurement-worksheet.csv after your own continuous run.

## Rebuild

Install Arm GNU Toolchain13.2.rel1 (GCC13.2.1), CMake3.31.10 and Ninja1.11.1; put their bin directories on PATH. Extract project-and-build.zip and enter gebrabit_lesson43_timers:

```sh
cmake --preset Debug
cmake --build --preset Debug --clean-first
arm-none-eabi-objcopy -O binary build/Debug/gebrabit_lesson43_timers.elf build/Debug/gebrabit_lesson43_timers.bin
```

## Provenance and regeneration

Real CubeMX 6.14.0 DB6.0.140 hardware baseline lesson37, CubeF3 V1.11.6. Copied hardware sources and renamed IOC/project; app and native kernel integration are manually authored, not CubeMX-generated middleware. No new CubeMX generation or GUI test for42/43.

FreeRTOS-Kernel V11.2.0 commit 0adc196d4bd52a2d91102b525b0aafc1e14a2386. Native FreeRTOS, no CMSIS-RTOS wrapper. Only heap_4.c is linked. Native kernel sources and application are user-managed. Preserve main.c USER includes and App_Start() in USER2; preserve custom CMake integration and the port aliases for SVC/PendSV/SysTick. Do not regenerate conflicting handlers. HAL timebase remains TIM6. Regeneration was not performed for this derived project, so recheck and rebuild after any CubeMX changes.

HSE8MHz/PREDIV1/PLL9/SYSCLK72MHz/AHBdiv1/APB1div2=36MHz/APB2div1=72MHz/FLASH2WS.

HAL 1ms from generated TIM6 (timer72MHz PSC71 ARR999). Kernel SysTick1000Hz. Port aliases own SVC/PendSV/SysTick; no duplicate generated handler.

Flash128KiB; main SRAM32KiB; CCM8KiB separate, not used for DMA. heap_4 static arena12288bytes; application stacks256words=1024bytes; Idle128words=512bytes; StackType_t32bits. Stack high-water results require real execution.

## Run and observe

Only PB6 onboard active-high userLED is used. No additional wires are required. SWD and proper board power required to run; no UART output in42/43.

Softwareperiodictimer250ticks autoreload=true andoneshottimer2000ticks autoreload=false share onecallback in daemonTASKcontext. Eachcallback snapshots tick/kind and nonblocking xQueueSend(...,0) to8element TimerEventQueue; periodic togglesPB6. Worker priority2 waits queue, ononeshotevent changesperiodictimer to500ticks using xTimerChangePeriod(...,10ticks) fromapplicationtask. Monitorpriority1 samplesactivity every1000ticks. Bothappstacks256words. OneShot doesnotrestart.

Expected, NOT MEASURED: Nominalinitialperiod250ticks=250ms,PB6fullwave500ms. AfterOneShot2s,Workerrequests500msperiod,nominalfullwave1s. Countsandcallbackorderaroundchange dependrealdaemon/workerexecution; noexact8callbacks claim. OneShotcounter expected1perreset ifcommandsprocessed. Usecontinuousrunandexternalanalyzerforactualjitter; haltingdebuggerinvalidatestiming.

Watch globals: g_periodic_callbacks, g_oneshot_callbacks, g_event_drops, g_processed_events, g_period_changed, g_last_periodic_tick, g_last_oneshot_tick, g_change_requested_tick, g_periodic_active, g_oneshot_active.

g_app_error=1 assert;2 malloc failure;3 stack overflow hook. Hooks halt without printf, logging or allocations.

## Timer context and queue pressure

configUSE_TIMERS1; configTIMER_TASK_PRIORITY3; configTIMER_QUEUE_LENGTH8; configTIMER_TASK_STACK_DEPTH256words. Idlepriority0. Both xTimerStart commands queuedbefore scheduler with0block; length8 accommodates2startupcommands. Timercontrolsandprivatecommandqueue createddynamically; checkNULL/pdPASS.

Callback executes in same daemon/service TASK for all software timers, not hardware IRQ. Use task-context APIs, neverFromISRjustbecausecalledtimer.

No vTaskDelay, noqueue/semaphorewait, noUARTblocking, noheavywork incallback. Thisexample xQueueSend blocktime0 and incrementsg_event_drops iffull. If timerAPIneededinsidecallback useblocktime0 toavoiddeadlock onits owncommandqueue.

Callbacks are serialized; a slowcallbackdelaysothertimersandcommandprocessing. Daemonprioritycanreduceinterference butdoesnotmakeharddeadlineguarantee; starvationandIRQloadstillmatter.

xTimerCreate returns dormanttimer; NULL allocationfailure. xTimerStart pdPASS meanscommandqueued, notcallbackexecuted orcommandalreadyprocessed. xTicksToWait istimewaitforspace incommandqueue, nottimerperiod. Before scheduler itcannotblock.

xTimerChangePeriod updatesperiodandactivatesdormanttimer; thisonecalledfromWorker changesnewexpiryrelative tocommandprocessing currenttick, unlike normalauto-reloadschedule. g_change_requested_tick recordsrequesttime, notactualprocessingtime.

Auto-reload timers schedule relativepreviousnominalexpiry, notsimplylastcallbackfinish. Ifdaemonlate,multipleexpiredcallbacks cancatchup inrapid succession; noautomaticguarantee of250ms pinspacing.

xTimerIsTimerActive issnapshotonly, notproofcommandcompleted atrequesttime. OneShot becomesdormant afterexpiry unlessexplicitrestart. Whenperiodic andoneshot dueat2000ticks, relativecallbackorder mustnotbeclaimedstable.

## Source and licenses

https://github.com/FreeRTOS/FreeRTOS-Kernel/tree/0adc196d4bd52a2d91102b525b0aafc1e14a2386

FreeRTOS MIT license and ST/CMSIS licenses retained; instructional application MIT.

The download includes generated hardware source, IOC, manually integrated pinned kernel, application, CMake source, ELF/BIN/HEX/MAP and compiler reports. Temporary cache/object files, local login data and internal writing prompts are excluded. MAP report paths are normalized; executable bytes are the compiled files.

## Portable helper scripts

After extracting project-and-build.zip beside rebuild.py, run `python rebuild.py` with the toolchain, CMake and Ninja on PATH. This rebuilds all reviewed presets and writes local reports.
