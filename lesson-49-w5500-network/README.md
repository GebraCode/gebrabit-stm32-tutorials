# GebraBit STM32 lesson 49

## Scope and validation

STM32F303CBT6 LQFP48 / GebraBit GB100ST V2.0

Actual WindowslocalCMakeDebugclean-first build with-O0 -g3 -Wall -Werror,zero warnings; no-Wextra/-Wpedantic. ELFvectors,Flash/RAM,source,HEX/BINchecked. NOphysicalSDcard/file-on-PC/network/W5500board/oscilloscope/GUIexecutionperformed. Compilationnotruntimevalidation.

Authored composition of real CubeMX6.14.0 DB6.0.140 CubeF3V1.11.6 lesson27SPI and lesson21ADC generated baselines. Manualmiddleware/applicationintegration and manuallyupdatedIOC; no freshCubeMXgeneration or GUItest for47/49. SPI mode0overrideinSPI1_Init USER2 callsHAL_SPI_InitafterbaselineinitwithCSheldhigh. ADCgeneratedfilecopiedfrom21; ADCmoduleenabled.

Baremetal mainloop, NOT FreeRTOS. HAL SysTick1ms remainsrunning; maincallsApp_Poll. BlockingHAL/SPI/filesystem/networkoperationscan delayADCsampling. NoDMA, noCCMbuffers, noDcacheclaim.

## Rebuild and provenance

Extract project-and-build.zip beside rebuild.py. Install Arm GNU Toolchain13.2.rel1 GCC13.2.1, CMake3.31.10 and Ninja1.11.1; add their bin directories to PATH. Run `python rebuild.py`. Or enter `gebrabit_lesson49_w5500` and run:

```sh
cmake --preset Debug
cmake --build --preset Debug --clean-first
```

For the independent DHCP firmware use `cmake --preset DHCP` and `cmake --build --preset DHCP --clean-first`; program ELF from build/DHCP and reset. Debug is the static-IP example. Do not change a fallback C macro when CMake supplies its value.

The IOC is manually composed from real generated baselines and records desired ADC/SPI inputs; it is not proof of a new CubeMX run. Preserve application under App/Lesson, CMake middleware integration, ADC HAL enable, main.c USERincludes/App_Init/App_Poll, SPI USER2 mode0 override, and preferred hardware configuration after regeneration. Rebuild and inspect after any regeneration. No CubeIDE import or GUI build was tested.

WIZnetioLibrary_Driver officialtagv3.1.3 pin069a81350e8ea0da2d210ab01db97895bba20399. Explicit-D_WIZCHIP_=5500. NOTmaster andnotv3.2.0. Threevendorfileshave documentedlocalpatches;restbyteidenticaltoupstream. Readvendor-patches.jsonfordiff,donotclaimallsourceunchanged.

## Wiring and configuration

PA5=SPI1_SCK AF5; PA6=SPI1_MISO AF5; PA7=SPI1_MOSI AF5; PA4=externalactive-lowCS,baselinegeneratedlabelSENSOR_CS reused; PA1=ADC1_IN2; PB6=onboardactive-highLED

W5500modulewithmagnetics/RJ45,25MHzcrystal,poweranddecouplingexternal.3.3Vlogic/supplyasmoduleverified,noGPIOpower. PA5SCLK,PA6MISO,PA7MOSI,PA4SCSn;PB0RSTnlow2ms,high100ms;commonGND;optionalINTnnotused,pollingmain. W5500RSTnmin500usperdatasheetp60. Needexternalsufficientcurrent3.3Vsupply,modulepinoutverified;moduleVCC5Vlabelonlyifitsregulatordocumented,GPIOstill3.3V.

HSE8MHz/PREDIV1/PLL9/SYSCLK72MHz/AHBdiv1/APB1div2=36MHz/APB2div1=72MHz/FLASH2WS. SPI1 kernel72MHz.

Mode0,MSBfirst,8bit,4.5MHz=72MHz/16. W5500supportsMode0/3 andadvertises80MHztheoreticalchipinterface,butdatasheetv1.1.0SPI tablealsohas33.3MHzguaranteedtimingfootnote;hostlimits/wiringapply. No80MHzonF303claim,no100Mbit/sapplicationthroughputclaim.

PA1 ADC1_IN2,12bit,singleended,softwaretrigger,syncPCLKdiv4=18MHz,181.5cycles sampling,HALcalibrationbeforefirstsample. Acceptonly0..VDDA3.3V. ADCvalidrequiresStart/Poll10ms/Get/Stopallaccepted. Neverapply5V.

## Network setup and tests

DebugpresetAPP_USE_DHCP0 staticEXAMPLE192.168.50.50/24gwDNS192.168.50.1,locallyadminMAC02:00:00:00:49:01mustbeuniqueanduseradapted. DHCPpresetAPP_USE_DHCP1 usesUDPsocket7and548bytebuffer. DHCP_init/run callbacksassign/update/conflict;App_Tick1ms fromSysTickuserblockcallsDHCP_time_handlereach1000ticks,includingduringlibrary2sconflictbusywait. Runningtimeronlyinmainwoulddeadlockconflictpath. Initialnoaddress45stimeoutstops,noautomaticstaticfallback;DHCP_FAILEDstopsservices/resetneededtoretry. RenewalDHCP_runcontinueswhilevalid;IPchangecloses/reopensappconnections.

reg_wizchip_cs_cbfunc andreg_wizchip_spi_cbfunc bindactive-lowCS+HALbyteSPI. SinglemaincontextownsallSPIandnetworkcalls;defaultcriticalcallbacksno-opnotRTOSmutex. HAL20msperbyteand5saggregateAPIguardfailstopg_net_error1/2 withCSdeasserted. LiveHALSysTickrequired. IRQonly1secondDHCPcounter,nosocket/SPIcallsISR. APIguardprotectspollingloopsbycheckingoneachbyte;notnormalnetworkrequestdeadline.

W5500all8socketTX/RX2KiBeach. TCPsocket0port5000echo, TCPsocket1port8080minimalHTTP GET /sensorpage, UDPsocket2port5001echo<=256bytepayload. DHCPsocket7reserved. Other3..6unused. Thisbaremetalexampleissingleconnectionperserverport;noTLS/authentication/Internetdeploymentclaim.

CLOSED→socket(Sn_MR_TCP,SF_IO_NONBLOCK),INIT→listen,ESTABLISHED/CLOSE_WAITservebuffereddata;10sidle/FIN-stateappdeadlinecloses/resetconnection. recv>0 queuesdatainpersistentConnection.bytes768;send>0 maypartialadvancesoffsetonlyacceptedbytes,SOCK_BUSY0retriedlater,negativecloses. AwaitSENDOKbeforeHTTPdisconnect;donotclearSENDOKinappbecauseioLibrarysendconsumesitnextcall. Bufferpersistentuntilfinalack;protocolframingTCPstreamnotdatagrams. W5500RCR3/RTR200msnetworkretryisnotappdeadline.

RequestaccumulatedacrossTCPfragmentsuntilCRLFCRLFwithmax767bytes. OnlyGET / path,oversized/otherrequestcloses. BuildHTTP1.1200Content-Type/Content-Length/Connection:close usingboundedinteger-onlysnprintf. BodyrawADC12bit+validflag;ADCsample~1sbest-effortlatestvalue,canshowinvalidstalevaluewithvalid0. NoactualsensorvalueorHTTPtestclaimed.

recvfromretainspeerIP/port,echoesonecomplete<=256bytedatagram. SO_REMAINSIZE detectsoversizeddatagram,closesUDPsocket/discardsandcountsg_udp_oversize_drops,insteadofpartialTCP-likesplit. UDPnoTCPdelivery/retransmissionguarantee.

Read your assigned/configured IP from g_network.ip. Static example requires a matching isolated LAN and nonconflicting local MAC/IP; edit g_network only to match your own setup. The web address is http://YOUR-BOARD-IP:8080/. For a user-initiated endpoint test, run `python test_network.py --host YOUR-BOARD-IP`; the client makes no request without an explicit host. No ping, DHCP lease, TCP/UDP echo or HTTP request was executed during preparation. This educational example has no authentication/TLS; it is not a general-purpose Internet HTTP server.

g_net_error:1 SPI HALfailure,2 aggregate vendor-call guard exceeded5s,3 responsebufferformatfailure,4 VERSIONRnot0x04,5 W5500memoryinitializationfailure,6 ADCcalibrationfailure. It fail-stops with CS high; reset after fixing hardware. The guard needs live HALtick and is not a realtime guarantee. RCR/RTR network retry counters are not application session deadlines. g_http_responses counts response construction; g_tcp_echo_bytes counts bytes accepted into W5500TX, not proof the peer read them.

## Download contents and licensing

Project source, authored IOC, native middleware, CMake, licensed vendor headers, ELF/BIN/HEX/MAP for reviewed build presets, compiler reports, this README and companion scripts are included. Build caches, objects, login data and internal authoring prompts are excluded. Source/executable __FILE__/DWARF paths and MAP reports are normalized. Fresh local builds may contain your local paths in reports; review them before sharing.

RepoMITlicense.txtANDindividualBSD-style3conditionWIZnetcopyrightheadersbothretained;notblanketallfilesMIT. OwnapplicationMIT;ST/CMSISlicensesretained.

https://github.com/Wiznet/ioLibrary_Driver/tree/069a81350e8ea0da2d210ab01db97895bba20399
