# GebraBit STM32 lesson 47

## Scope and validation

STM32F303CBT6 LQFP48 / GebraBit GB100ST V2.0

Actual WindowslocalCMakeDebugclean-first build with-O0 -g3 -Wall -Werror,zero warnings; no-Wextra/-Wpedantic. ELFvectors,Flash/RAM,source,HEX/BINchecked. NOphysicalSDcard/file-on-PC/network/W5500board/oscilloscope/GUIexecutionperformed. Compilationnotruntimevalidation.

Authored composition of real CubeMX6.14.0 DB6.0.140 CubeF3V1.11.6 lesson27SPI and lesson21ADC generated baselines. Manualmiddleware/applicationintegration and manuallyupdatedIOC; no freshCubeMXgeneration or GUItest for47/49. SPI mode0overrideinSPI1_Init USER2 callsHAL_SPI_InitafterbaselineinitwithCSheldhigh. ADCgeneratedfilecopiedfrom21; ADCmoduleenabled.

Baremetal mainloop, NOT FreeRTOS. HAL SysTick1ms remainsrunning; maincallsApp_Poll. BlockingHAL/SPI/filesystem/networkoperationscan delayADCsampling. NoDMA, noCCMbuffers, noDcacheclaim.

## Rebuild and provenance

Extract project-and-build.zip beside rebuild.py. Install Arm GNU Toolchain13.2.rel1 GCC13.2.1, CMake3.31.10 and Ninja1.11.1; add their bin directories to PATH. Run `python rebuild.py`. Or enter `gebrabit_lesson47_fatfs_sd` and run:

```sh
cmake --preset Debug
cmake --build --preset Debug --clean-first
```

The IOC is manually composed from real generated baselines and records desired ADC/SPI inputs; it is not proof of a new CubeMX run. Preserve application under App/Lesson, CMake middleware integration, ADC HAL enable, main.c USERincludes/App_Init/App_Poll, SPI USER2 mode0 override, and preferred hardware configuration after regeneration. Rebuild and inspect after any regeneration. No CubeIDE import or GUI build was tested.

OfficialChaN FatFsR0.16 (2025-07-22) archiveff16.zip SHA25699f7dc1f7e095356e4a9e3dbe29959090d8b948afe2bbc5441e52fdf4b85449e. Sourceff.c/ff.h/diskio.h unchanged;ffconfuserconfigmodified. NOTR0.15frominitialproposedplan; noCubeMXgeneratedFatFsmiddlewareclaim.

## Wiring and configuration

PA5=SPI1_SCK AF5; PA6=SPI1_MISO AF5; PA7=SPI1_MOSI AF5; PA4=externalactive-lowCS,baselinegeneratedlabelSENSOR_CS reused; PA1=ADC1_IN2; PB6=onboardactive-highLED

Use3.3V-compatibleSDsocket/modulewithproper3.3Vsupplyandlogic,shortSPIwires,commonGND. PA5→CLK,PA7→DI/CMD,PA6←DO/DAT0,PA4→CS/DAT3. ExternalCS10kpullup;unusedSDDAT1/DAT2pullupasrequiredbycard/socketdesign. Barecard2.7..3.6V,never5V; modulewith5Vregulatornotproof5Vlogiccompatibility. Localdecoupling/supplymustsupportwritecurrentbursts. Recommend4..32GBSDHCalreadysafelyFAT32formattedonPC; backupexistingfiles. Donotformatanycardinfirmware.

HSE8MHz/PREDIV1/PLL9/SYSCLK72MHz/AHBdiv1/APB1div2=36MHz/APB2div1=72MHz/FLASH2WS. SPI1 kernel72MHz.

Mode0,8bit,MSBfirst,softwareCS. Init72MHz/256=281.25kHz (<400kHz);afterready72MHz/16=4.5MHz. Actualthroughputnot4.5Mbit/sapplicationduetoSPIframing/FAT/cardbusy/HALoverhead.

PA1 ADC1_IN2,12bit,singleended,softwaretrigger,syncPCLKdiv4=18MHz,181.5cycles sampling,HALcalibrationbeforefirstsample. Acceptonly0..VDDA3.3V. ADCvalidrequiresStart/Poll10ms/Get/Stopallaccepted. Neverapply5V.

## SD disk layer and CSV run

Read/write,onevolume512bytesectors,8.3names,LFN0,exFAT0,REENTRANT0,MKFS0,TRIM0,codepage437,NORTC1fixed2026-01-01. CSVuptimeisnotRTCtime;filetimestampplaceholdernotrealtime. f_mkfsnotlinked. Baremetalonesingleowner,noRTOSsafetyclaim.

Powerwait10ms;80clocksCShigh/MOSIhigh;CMD0withCRC0x95→idle1;CMD8arg0x1AA/CRC0x87checkR7voltage/checkpattern (response5legacySDv1fallback);CMD55+ACMD41(HCSbitforv2) bounded1500ms;CMD58checksreadyOCR,CCSdistinguishes512byteblockaddressingvsSDSCbyteaddresses;SDSCsetsCMD16block512. CMD17readone512sector, CMD24writeone512sectorrepeatedforcount; CMD9CSDgivessectorcount. NoMMC/CMD1/SDUCsupport. CRCnotcheckedfornormalSPIblocks(defaultCRCoff); notend-to-enddataintegrityproof.

disk_initialize/status/read/write/ioctl implementedfordrive0. Countsandsectorwrapchecked. HALonebytetransfer20mstimeout,cardready500ms,readtoken200ms;HALtickmustremainlive. SingleblocksnotCMD18/CMD25multi-blockperformance. CTRL_SYNCwaitscardnotbusy;GET_SECTOR_SIZE512;GET_SECTOR_COUNTCSDv1/v2parser;GET_BLOCK_SIZEandCTRL_TRIMreturnRES_PARERRbecauseMKFS/TRIMdisabled. Cachedstatus,nohardwarecarddetect/writeprotect/hotplug;resetaftermediaerror/removal.

AfterresetNOcardwritesuntiluserwithdebuggersetsg_start_request=1thenresumes. f_mount0:immediate,requireFAT32. f_openFA_WRITE|FA_CREATE_NEW tries0:ADC000.CSV..ADC999.CSV skippingFR_EXISTandneveroverwritesexistingfiles. Headeruptime_ms,adc_raw,estimated_mv. Every~1000msbest-effortonesample;ADCvaliditychecked. mVest=(raw*3300+2047)/4095usingassumedVDDA3300mV,notcalibratedtruevoltage;quantLSBVDDA/4096. f_writechecksFRESULTANDbw==requested;f_syncafterheaderand10rows;finishafter100validrowsoruserg_stop_request. f_syncandf_closeresultsseparatelyrecorded. ADCfailuresdonotwriteastalesample. Failedwrite/partialwriteattemptscloseandstops.

NoCSVrecorded/readonPCyet. Expected100rowsabout100sbutblockedSDI/OandADCfailurescanextendinterval;timestampsactualHALuptime. f_syncreducesdirtycachewindowbutnotatomicpowerlossprotection;cardFTL/metadatapowerlossstillcorruptsfiles. Requirevalidresults+closedfilebeforesafelyremovingcard,avoidpowercutduringwrites. FiletimestampfixeddatefromNORTC,notmeasuredwallclock.

Connect a suitable ADC test voltage to PA1. Use a backed-up FAT32 SDHC card. Firmware has no formatting command. On reset the logger is idle. Set g_start_request=1 in the debugger and RESUME; then run without breakpoints. Wait for g_log_active=0 and successful g_fs_result/g_close_result before safely powering down/removing the card. 100 valid samples finish automatically; g_stop_request=1 requests earlier completion. No more than1000 unused 8.3 file names are tried, and existing CSVs are never overwritten. After a media error or removal, reset before retrying with a verified card. Runtime writing was not performed by the authors.

Copy the actual ADCnnn.CSV to your computer and run `python analyze_csv.py ADCnnn.CSV`. This checks ADC integer bounds, the assumed-VDDA voltage calculation and timestamp intervals. It does not authenticate measurements or calibrate VDDA.

## Download contents and licensing

Project source, authored IOC, native middleware, CMake, licensed vendor headers, ELF/BIN/HEX/MAP for reviewed build presets, compiler reports, this README and companion scripts are included. Build caches, objects, login data and internal authoring prompts are excluded. Source/executable __FILE__/DWARF paths and MAP reports are normalized. Fresh local builds may contain your local paths in reports; review them before sharing.

FatFsChaN BSD-style1conditionnoticepreservedLICENSE.txt andsourceheaders; ownSDdiskio/applicationMIT; ST/CMSISlicensesretained.

https://elm-chan.org/fsw/ff/archives.html
