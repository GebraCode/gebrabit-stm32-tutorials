# GebraBit STM32 lesson 45

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

Real CubeMX6.14.0 DB6.0.140/CubeF3V1.11.6 hardware baseline37; native kernel integration and low-power module are user-authored. No new CubeMX generation claimed.

### clock

HSE8MHz PLL9 HCLK72MHz APB1/2=36/72MHz Flash2WS. TIM6 HAL1ms, SysTick kernel1000Hz. TIM2 APB1 timer72MHz PSC71 ARR0xffffffff =>1MHz runtime counter with no IRQ.

### config

heap_4 12288bytes; Worker priority1 stack256words; Monitor priority2 stack384words; Idle stack128words. 32bit ticks, IdleHook1, runtime stats1, trace1, raw TaskStatus_t capacity4.

### behavior

Worker performs finite10000iteration NOP load, togglesPB6 and vTaskDelay1000ms. Monitor delays2000ms then uxTaskGetSystemState(g_task_stats,4,&g_stats_total). IdleHook only increments g_idle_calls, never blocks or prints. Snapshot g_stats_entries should be3 for2applicationTasks+Idle; failed snapshot0 means capacity insufficient. No UART or external DMA in45.

### sleep_variant

APP_USE_STOP_TICKLESS0 configUSE_TICKLESS_IDLE1 invokes stock ARM_CM4F weak vPortSuppressTicksAndSleep. It is shallow Sleep, not Stop; SysTick long reload is limited by24bit counter: floor16777215/72000=233ticks. PRE hook disables HAL TIM6 tick IRQ so it does not wake every1ms; POST hook uses free-runningTIM2 elapsedus to approximately compensate HALtick and reenableTIM6. Normal port still compensates RTOS ticks. DefaultSleep does not initialize/use RTC.

### stop_variant

APP_USE_STOP_TICKLESS1 configUSE_TICKLESS_IDLE2 uses explicitly custom App_SuppressTicksAndSleep. At least5expected ticks; caprequested sleep200ms, RTCWUT target2ms earlier. Confirm sleep state underPRIMASK, stopSysTick, thenrecheckpendingtick withcounterfrozen. Ifpending, restoreunchangedcounter/phaseandabort soexistingISRcountsitonce. Preserve remainingpartialphase; snapshotRTC32768Hz. SuspendHALtick, armRTCWUT clockLSE/16=2048Hz, WFIStop lowpowerregulator, then bounded directregister polling restoresHSE/PLL/HCLK72MHz whileHALtick is unavailable. ReadRTCelapsed cycles, handlemidnight, computefullticks/fraction withuint64. vTaskStepTick onlysafeportion before nextunblock/tickwrap; anyremaininglate ticks usexTaskIncrementTick while scheduler is still suspended, then xTaskResumeAll kernel path drains pended ticks normally. HALtick compensatedapproximately, SysTickpartialperiod restored then normal72000count reload. RTC IRQ6onlyclearsflags/counts, noRTOSAPI. Stock port never claims to supportStop itself.

### rtc_profile

LSE32768Hz; RTC async0 sync32767 gives32768Hz subsecond resolution~30.52us. Wake clockLSE/16. RetainedRTC withanotherclocksource/prescaler is refused byassert ratherthan silently resettingbackupdomain/calendar. Freshcalendar initializedto Jan1 2026 00:00 onlydemonstrationepoch. ForcustomStop onaboardpreviouslyusinglesson29profile127/255, backupexistingcalendar and deliberatelypreparecompatibleRTCprofile beforeusingthisfirmware; noautomaticerase.

### runtime_stats

TIM2 is1MHz onlyatsteady72MHz and wrapsafter4294.967296s(~71.58min). ForstockSleepitkeepsrunning soIdleSleep countsintoIdle runtime. InStopTIM2 stops andduringHSIclockrestorerate differs; rawstats therefore excludeStopduration and areNOTwallclockCPU-load percentages. UseRTCwalltime forpowerdutycycle. No uA saving, latency, GUI trace or runtime fractions measured. Resetbeforecounterwrapforbasiccomparison; snapshotsanddebuggerhaltsperturbtiming.

### attempt_counters

g_sleep_entries and g_stop_entries count entry attempts, not measuredproof of reaching lowpower state. A pendinginterrupt can make WFI return immediately.

### gui_and_trace

RTOS-aware debugger capability depends on installed CubeIDE/debugplugin version. No exactGUI menu path or trace capture tested. Raw uxTaskGetSystemState data/globals provide a concrete independent observation path. SystemView/Tracealyzer may be introduced as tools needing explicit integration/license/trace transport; none was configured or captured here.

## Limitations

All builds clean WallWerror; no board execution, current measurement, RTOS GUI, waveform or trace acquisition performed.

CustomStop path is an educational porting experiment, not production-validated lowpower support; oscillatorstartup, interrupt races, retainedRTC state and realtickerror must be hardwarevalidated. RTCquantization and codeoverhead produce bounded-resolution/drift effects, not exacttimingguarantees.

IdleHook must not call blocking APIs; do notfeedWatchdogunconditionallyfromIdle.

HALtimecounter compensation is approximate; calendarRTC isindependent. NoLPTIMexists onthisF303CB; do notdescribeLPTIM implementation.

Runtime stats snapshots suspend scheduling andaddoverhead; do not infer deadlines from task percentages.

Boardregulator/LED/debugprobe andexternalcircuits affectmeasuredcurrent; siliconStopnumbers arenotboardcurrent.
