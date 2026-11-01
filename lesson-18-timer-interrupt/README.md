# درس 18: وقفهٔ TIM6

دو پروژهٔ واقعی برای STM32F303CBT6 روی GB100ST V2.0 با CubeMX6.14.0 و CubeF3V1.11.6 تولید و با GCC13.2.1/CMake Debug به صورت clean و با `-O0 -g3 -Wall -Werror` بدون هشدار ساخته شده‌اند. پروژهٔ IRQ حلقهٔ اصلی بدون تأخیر و پروژهٔ slowmain همان وقفه با HAL_Delay(500) در main دارد. همهٔ منابع/IOC و مجوزهای ST/Arm در ZIP منابع، و ELF/MAP همان ساخت در ZIP جداگانه قرار دارند. آزمون روی برد و اجرای CubeIDE انجام نشده‌اند.

## تنظیم واقعی

HSE8MHz، PREDIV/1، PLL×9، SYSCLK/HCLK72MHz، APB1/2=36MHz اما کلاک TIM6 برابر72MHz؛ APB2/1=72MHz؛ Flash2WS. TIM6 شمارش صعودی، PSC71 و ARR999 با preload فعال دارد. مبنای HAL همان SysTick با اولویت15 است؛ TIM6_DAC_IRQn با اولویت2 و زیراولویت0 در GROUP4 فعال است. GROUP4 برای این Cortex-M4 چهار بیت اولویت پیش‌دستی و صفر بیت زیراولویت می‌دهد. TIM6 برای مبنای HAL استفاده نشده است.

قبل از Start_IT، CNT صفر، UIF ایجادشده توسط UG در init پاک و pending متناظر NVIC پاک می‌شود. در HAL این نسخه، TIM_Base_SetConfig پس از نوشتن ARR/PSC رخداد UG می‌دهد؛ HAL_TIM_Base_Start_IT به خودی خود آن پرچم را پاک نمی‌کند. همهٔ این توابع در source-evidence.txt از فایل واقعی آورده شده‌اند.

## مسیر وقفه و هم‌روندی

TIM6_DAC_IRQHandler ابتدا UIF و UIE تایمر6 را بررسی می‌کند؛ اگر هر کدام فعال نباشد خارج می‌شود. DAC در این پروژه فعال نیست. اگر در آینده DAC اضافه شود، منبع DAC نیز باید در همین بردار مشترک dispatch و acknowledge شود؛ صرف بازگشت از handler درخواست DAC را پاک نمی‌کند.

در handler، PB7 قبل از HAL_TIM_IRQHandler بالا و بعد از آن پایین می‌رود. HAL پرچم Update را پاک و HAL_TIM_PeriodElapsedCallback را اجرا می‌کند. callback فقط برای Instance=TIM6، PB6 را Toggle و pending_ticks و total_irq_count را زیاد می‌کند. هیچ HAL_Delay یا printf داخل ISR نیست. شمارندهٔ volatile تنها مشاهده‌پذیری را فراهم می‌کند و counter++ را اتمیک نمی‌کند. main با ذخیرهٔ PRIMASK، غیرفعال‌کردن وقفه، کپی و صفرکردن pending_ticks، DMB و بازگرداندن PRIMASK قبلی تبادل را حفاظت می‌کند. NMI/HardFault به این متغیر دست نمی‌زنند.

در main مقدار آخرین batch و مجموع پردازش‌شده ثبت می‌شود. این مثال پردازش batch را نشان می‌دهد و timestamp هر رخداد را نگه نمی‌دارد. در slowmain، تأخیر500ms به معنی توقف وقفهٔ TIM6 نیست؛ انتظار انباشت حدود500 رخداد داریم، نه عدد دقیق تضمین‌شده. تعداد batch بزرگ به معنای اجرای به‌موقع کار اصلی نیست. UIF یک بیت است؛ اگر وقفه برای بیش از یک دوره مسدود شود، شمار رخدادهای ادغام‌شده قابل بازیابی نیست. شمارنده‌های32بیتی نیز پیمانه‌ای‌اند و در نرخ1kHz حدود49.71روز دور می‌زنند.

## پیش‌بینی و آزمایش

هر1ms یک Toggle روی PB6: فاصلهٔ لبه‌ها1ms، دورهٔ موج2ms و فرکانس500Hz. این پیش‌بینی مدل است؛ هیچ عکس یا عدد اندازه‌گیری‌شده ارائه نشده است. PB7 پوش زمان اجرای داخل handler را نشان می‌دهد که HAL و callback را دربر می‌گیرد؛ ورود/خروج سخت‌افزاری استثنا و شرط اولیهٔ قبل از بالا رفتن marker داخل این پهنا نیستند. از آن به عنوان کل تأخیر ورود یا زمان کامل ISR یاد نکنید.

اتصال اسیلوسکوپ: کانال1 PB6 و کانال2 PB7 با زمین مشترک و پروب ورودی پرامپدانس3.3V سازگار، نه اتصال مستقیم خروجی مولد سیگنال. PB6 پایهٔ منطقی LED است؛ مسیر LED از ترانزیستور می‌گذرد. ولتاژ را روی خود پایه/هدر درست بررسی کنید. ST-LINK با SWDPA13/PA14، زمین، مرجع3.3V و NRST مطابق شماتیکV2.0 متصل شود. ورودی5V فقط برای ورودی مجاز برد است، نه پایهٔ3V3/MCU.

ابتدا پروژهٔ IRQ سپس slowmain را پروگرام و بدون breakpoint اندازه‌گیری کنید. debugfreeze تایمر6 عمداً فعال است؛ توقف دیباگر تایمر را متوقف می‌کند و برای بررسی دوره معتبر نیست. جدول hardware-worksheet.csv همهٔ نتیجه‌های واقعی را pending نگه داشته است. معیار: دورهٔ موج PB6 با2ms و تلرانس منبع کلاک/ابزار سازگار باشد، در slowmain وقفه ادامه یابد، تأخیر کار main با نرخ وقفه اشتباه نشود. اثر تغییر اولویت و بار CPU بر jitter لبهٔ GPIO نیاز به اندازه‌گیری دارد.

## محاسبه و ساخت

اسکریپت با فرض شمارش صعودی رابطهٔ `(PSC+1)(ARR+1)/f_TIM` را بررسی می‌کند: نمونه1ms با71/999 و500ms با7199/4999. مثال500ms فقط محاسبه است و پروژهٔ جداگانهٔ ساخته‌شده نیست؛ برای waveform در هر Toggle، فرکانس خروجی نصف نرخ Update است. جست‌وجوی کامل PSC برای1234Hz نمونهٔ خطای گردکردن را گزارش می‌دهد. ARR0 برای این تایمر حالت قابل استفادهٔ این آزمایش نیست: مستند F3 LL_TIM_SetAutoReload صریحاً توقف شمارنده با مقدار autoreload صفر را ذکر می‌کند، پس فرمول را بی‌قید بهARR0 تعمیم ندهید.

```text
python verify_interrupt_periods.py
cmake --preset Debug
cmake --build --preset Debug --clean-first
```

نیاز ساخت: CMake>=3.22، Ninja و arm-none-eabi-gcc. برای مسیر CubeIDE، IOC را با CubeMX مستقل باز کنید، در پوشهٔ جدا STM32CubeIDE تولید و وارد کنید؛ این مسیر اجرا نشده است. بعد از تولید مجدد، تنظیم هشدارها را دوباره بررسی کنید. RAM گزارش ساخت شامل رزرو linker برای heap/stack است، نه مصرف واقعی اندازه‌گیری‌شده. تمرین دو کار10ms و250ms به زمان‌بندی در main و ارزیابی بار/از‌دست‌رفتن مهلت نیاز دارد؛ callback محل کار مسدودکننده نیست.

## Educational figures

Six original educational diagrams/models with captions in image-metadata.json; no screenshots or physical measurements. draw_figures.py reproduces figures using Python3/Pillow and an installed Segoe UI font (not redistributed). Full-resolution files are included. The drawings represent configuration, reasoning and expected behavior, not actual board evidence.

## Download all files

[Download lesson18 resources ZIP](lesson-18-resources.zip)

Complete project sources/IOC, actual ELF/MAP and reports, scripts, worksheet and six editable diagrams are INSIDE this ZIP.
