# نمونه‌برداری منظم و پردازش نیمهٔ بافر

هدف این درس آن است که هر100us یک نمونهٔ PA1 بگیریم، 64 نمونهٔ تمام‌شده را در main پردازش کنیم و اگر برنامه عقب ماند، دادهٔ نامطمئن را معتبر نشان ندهیم. نتیجهٔ واقعی برد هنوز ثبت نشده است؛ مدل و فایل‌های ساخته‌شده همراه‌اند.

## سه پروژه

- `gebrabit_lesson23_adc_dma`: DMA چرخشی128نمونه‌ای با پردازش هر نیمه.
- `gebrabit_lesson23_late`: همان تنظیم، اما main عمداً20ms صبر می‌کند؛ انتظار تشخیص عقب‌ماندگی و توقف کنترل‌شده داریم، نه بازیابی بدون افت داده.
- `gebrabit_lesson23_adc_it`: همان تحریک TIM3 در10kHz، بدون DMA؛ در callback هر نمونه خوانده می‌شود و فقط آخرین مقدار نگه می‌ماند. این نسخه صف همهٔ نمونه‌ها ندارد.

## اتصال و پیش‌بینی

ورودیPA1 همان ADC1_IN2 است. پتانسیومتر با دو سر متصل به ریل مجاز3V3 و GND و جاروبک به PA1، یا منبع کم‌امپدانس سازگار با محدودهٔ آنالوگ به‌کار رود. ولتاژ ورودی را مستقل با مولتی‌متر کنترل کنید؛ پایهٔ آنالوگ را5V فرض نکنید. زمین مشترک لازم است. PB7 خروجی مشاهدهٔ callbackهاست، نه سیگنال ورودی؛ از پروب پرامپدانس سازگار3.3V استفاده کنید. شمارهٔ پایهٔ بدنه با شمارهٔ هدر فرق دارد و باید از شماتیک V2.0 تطبیق داده شود.

در نسخهٔ DMA، HT و TC هر64نمونه callback می‌دهند: فاصلهٔ ایده‌آل6.4ms، دورهٔ کامل بافر12.8ms و موج Toggle روی PB7 برابر78.125Hz. در نسخهٔ IT، Toggle در هر نمونه است و موج اسمی5kHz می‌شود. نرخ نمونه، نرخ callback و نرخ پردازش main سه نرخ متفاوت‌اند. در10ثانیهٔ دقیق مدل100000نمونه یعنی781بافر کامل و32نمونهٔ اضافه داریم؛ شمارنده‌های واقعی هنوز نامعلوم‌اند.

## محافظت از نیمهٔ تمام‌شده

DMA با قطع وقفه متوقف نمی‌شود. callback فقط شمارهٔ نیمه و sequence را منتشر می‌کند. main با حفظ PRIMASK یک snapshot کوتاه می‌گیرد، وقفه را برمی‌گرداند و فقط sequence بعدی را قبول می‌کند. CNDTR بررسی می‌شود تا DMA در نیمهٔ دیگر مشغول باشد.64عنصر به owned_copy در SRAM کپی می‌شوند؛ زمان کپی با DWT و بودجهٔ محافظه‌کارانهٔ باقی‌مانده کنترل و sequence و CNDTR دوباره بررسی می‌شوند. فقط کپی پذیرفته‌شده جمع/کمینه/بیشینه تولید می‌کند.

این کنترل‌ها برای همین ساعت‌ها، اجرای آزاد و سرویس به‌موقع طراحی شده‌اند؛ اثبات تشخیص همهٔ وقفه‌های ازدست‌رفته، خرابی ساعت، توقف دیباگر یا دورزدن‌های بسیار طولانی نیستند. DWT هنگام halt مرجع زمان دیواری مستقل نیست. از breakpoint وسط کپی نتیجهٔ معتبر زمان‌سنجی نگیرید. دو نیمهٔ یک آرایه، Double Buffer سخت‌افزاری نیستند. این Cortex-M4 حافظهٔ D-Cache ندارد و کد نگهداری کش لازم نیست؛ DMA نیز به CCM دسترسی ندارد. آدرس بافرهای واقعی در گزارش نقشه ordinary SRAM است.

fault_bits بیت1 برای دیرکرد/مالکیت، بیت2 برای خطای ADC/DMA و بیت4 برای شکست توقف است. main ابتدا TIM3 سپس ADC_DMA را متوقف و وضعیت HAL را بررسی می‌کند؛ خطای توقف به Error_Handler می‌رود. stopped=1 یعنی توابع توقف HAL موفق شده‌اند؛ هیچ تأیید سخت‌افزاری ادعا نمی‌شود. شروع مجدد خودکار وجود ندارد. adc_overruns و dma_errors تعداد callbackهای خطای اطلاع‌داده‌شده‌اند، نه شمار قطعی همهٔ نمونه‌های فیزیکی افتاده.

## ترتیب شروع

کالیبراسیون single-ended پیش از فعال‌شدن ADC انجام می‌شود، سپس HAL_ADC_Start_DMA یا HAL_ADC_Start_IT و در پایان HAL_TIM_Base_Start برای TIM3 اجرا می‌شوند. Continuous Conversion خاموش است؛ ADC هر تریگر را به یک تبدیل محدود می‌کند. DMA Continuous Requests در نسخه‌های DMA روشن و DMA1Channel1 هر دو سمت Half-word و Circular است. نگاشت ثابت کانال همین تراشه با سیستم Stream خانواده‌های دیگر فرق دارد.

## ثبت آزمون

ابتدا نسخهٔ عادی را بسازید/پروگرام کنید، شمار callback و زمان مشاهده و faultها را ثبت کنید. سپس نسخهٔ late را اجرا کنید؛ از دست‌رفتن مهلت و توقف را ثبت کنید، نه دادهٔ پردازش‌شدهٔ تضمینی. observation_ms زمان پنجرهٔ واقعی برحسب tickHAL را همراه buffers_in_observation_window ثبت می‌کند؛ عدد781.25 مدل است و پنجرهٔ خطادار/متوقف را نباید نرخ پیوسته دانست. همهٔ ردیف‌های hardware-worksheet.csv اکنون pending هستند.

```text
python verify_adc_dma.py
cmake --preset Debug
cmake --build --preset Debug --clean-first
```

## نسخه‌ها و اعتبارسنجی

هر سه پروژهٔ واقعی با CubeMX6.14.0، DB6.0.140، CubeF3V1.11.6 و GCC13.2.1 در CMake Debug با `-O0 -g3 -Wall -Werror`، ساخت پاک و بدون هشدار ساخته شده‌اند. پروژهٔ CubeIDE و اجرای روی برد تأیید نشده‌اند. برای CubeIDE فایلIOC را در CubeMX مستقل باز و خروجیSTM32CubeIDE را در پوشهٔ جدا تولید کنید. ZIPمنابع و ELF/MAP هر ساخت جدا هستند؛ مجوز ST/Arm حفظ شده است.

کلاکHSE8MHz/PLL×9/HCLK72MHz/APB1=36MHz/APB2=72MHz/Flash2WS است؛ TIM3PSC71ARR99 و TRGOUpdate10kHz، ADC1 synchronousAHB/4=18MHz و sampling181.5cycles، تبدیل12بیتی194سیکل یعنی10.7778us اسمی. نسبت به100us فرصت دارد ولی این رابطه جای کنترل امپدانس، تلرانس و آزمون واقعی را نمی‌گیرد.

نمونهٔ رسمی نزدیک بررسی‌شده: `Projects/STM32303C_EVAL/Examples/ADC/ADC_TriggerMode` از CubeF3commit663d2baae3604244f90ed80d0d757df17e36ada9؛ آن نمونه TIM2/برد دیگری دارد و پایه/کلاک پروژهٔ حاضر مستقل تولید شده‌اند. رفتار API از فایل‌های واقعی stm32f3xx_hal_adc_ex.c و adc.c در HALcommit953955afe65f89e60e556bbcdba752597f5da65d استخراج شده است. جزئیات در source-evidence.txt و toolchain-and-validation.json است.

## Original educational diagrams

Six original diagrams/models and editable draw_figures.py are included. They are not GUI/scope captures or physical measurements. Metadata records sources, assumptions, captions and alt text. Python3/Pillow and the system Segoe UI font regenerate the drawings; font files are not redistributed.

## Download the complete package

[All lesson 23 files](lesson-23-resources.zip)

Source/IOC, ELF/MAP, build reports, calculation model, hardware worksheet, third-party licenses and six editable diagrams are INSIDE the ZIP. Hardware validation is pending.
