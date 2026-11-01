# درس 17: Polling، شمارندهٔ TIM2 و DWT

پروژهٔ واقعی STM32F303CBT6/GB100ST V2.0 با CubeMX6.14.0 و CubeF3V1.11.6 تولید و با GCC13.2.1، مسیر CMake Debug و `-O0 -g3 -Wall -Werror` بدون هشدار ساخته شده است. ELF/MAP همان ساخت جداگانه همراه است. روی برد اجرا یا اندازه‌گیری نشده و CubeIDE اجرا نشده است. مقدارهای زمان اجرای تابع در worksheet خالی هستند؛ عدد ساختگی اندازه‌گیری ارائه نمی‌شود.

## تنظیم ثابت

HSE8MHz، PREDIV/1، PLL×9، SYSCLK/HCLK72MHz، APB1/2=36MHz و APB2/1=72MHz، Flash2WS. TIM2 کلاک72MHz، PSC71 و ARR0xFFFFFFFF دارد؛ شمارش صعودی با preload فعال، بدون وقفه و بدون پین خروجی. SysTick مبنای زمان HAL باقی است.

## کد و خواندن نتیجه

در USER CODE2، HAL_TIM_GenerateEvent رخداد UG را در حالت توقف تایمر ایجاد می‌کند. انتظار UIF پیش از پاک‌کردن1 و پس از __HAL_TIM_CLEAR_FLAG صفر است؛ این‌ها پیش‌بینی‌اند، نه مشاهده. سپس CNT صفر و HAL_TIM_Base_Start اجرا می‌شود. macro پاک‌کردن، SR را با مکمل پرچم می‌نویسد تا در بیت W0C صفر نوشته شود؛ از عملیات خواندن/تغییر/نوشتن نامطمئن روی SR استفاده نشده است. UIF یک بیت است، نه شمارندهٔ تعداد سرریزهای ازدست‌رفته.

DWT با CoreDebug DEMCR/TRCENA و CTRL/CYCCNTENA فعال می‌شود و NOCYCCNT بررسی شده است. اگر پشتیبانی اعلام نشود، Error_Handler اجرا می‌شود. تابع WorkFunction با متغیر volatile و محاسبهٔ unsigned تعریف‌شده مانع حذف اثر کار می‌شود؛ شمار1024 تکرار دارد. در حلقه ابتدا تابع با صفر تکرار برای baseline و سپس1024 تکرار اندازه‌گیری می‌شود. measured_timer_ticks شمار تیک1us و measured_dwt_cycles شمار سیکل هستند. خواندن متغیرها از دیباگر پس از اجرای آزاد ممکن است؛ توقف/گام‌به‌گام پنجرهٔ اندازه‌گیری را معتبر نمی‌کند.

ترتیب پنجره دقیقاً DWT-start، TIM-start، تابع، TIM-end، DWT-end است. بنابراین دو پنجره یکسان نیستند و DWT هزینهٔ خواندن TIM را هم دربر می‌گیرد. هزینهٔ فراخوانی و خواندن رجیستر، کوانتیزه‌بودن تیک1us، وقفهٔ SysTick و تغییرات اجرای حافظه مؤثرند. baseline کمک به تخمین سربار است؛ تفریقش تضمین حذف همهٔ خطاها نیست. وضوح شمارنده معادل دقت زمان اجرای تابع یا تأخیر نیست.

## تأخیر و حدود

DelayUsBounded تفاضل unsigned CNT را Poll می‌کند، درخواست بیش از1000000us را رد می‌کند و با HAL_GetTick یک guard حدود us/1000+10ms دارد. مثال100us در main و با SysTick/وقفه‌های فعال اجرا می‌شود. اگر تایمر یا SysTick متوقف شود، guard ممکن است معتبر نباشد؛ در ISR، با وقفهٔ غیرفعال یا هنگام halt استفاده نشود. این زمان انتظار دقیقِ بدون سربار نیست؛ وقفه‌ها و polling می‌توانند خروج را دیر کنند. CPU در این مدت مشغول انتظار است.

تعداد تیک درخواستی با زمان دقیق بین ورود و خروج تابع یکسان نیست. برای100 افزایش شمارنده، فاز قرائت اولیه می‌تواند نزدیک یک تیک با100us اسمی اختلاف ایجاد کند؛ سربار و وقفه‌ها عوامل دیگری‌اند. هیچ حد عددی زمان فیزیکی این تابع اندازه‌گیری نشده است.

تفاضل32بیتی تنها وقتی فاصلهٔ واقعی کمتر از یک دور کامل باشد، زمان گذرکرده را یکتا می‌دهد: TIM2 در1MHz حدود4294.967296s، DWT در72MHz حدود59.6523236s. بیش از یک دور قابل بازیابی نیست؛ ARR کوچک‌تر نیز با تفاضل طبیعی modulo2^32 سازگار نیست. در پروژه ARR کامل انتخاب شده است.

## آزمایش خواننده

با ST-LINK، اتصال SWDPA13/PA14، زمین مشترک و مرجع3.3V مطابق شماتیکV2.0 کار کنید؛ تغذیهٔ5V فقط به ورودی مجاز برد، نه VDD/3V3. ابتدا پرچم‌های قبل/بعد و سپس زمان تابع و baseline را ثبت کنید. خطای آموزشی: در اجرای آزمایش، TIM2 را متوقف و محدودیت guard را با SysTick فعال بررسی کنید؛ تغییر کدِ چاپ‌نشده لازم نیست و هیچ نتیجه‌ای اینجا ادعا نشده است. برای مقایسه، اندازه‌گیری‌ها را چند بار بدون breakpoint تکرار کنید. کمترین/بیشترین نتیجه و شرایط را بنویسید؛ snapshotها لزوماً هم‌زمان نیستند.

```text
python verify_polling.py
cmake --preset Debug
cmake --build --preset Debug --clean-first
```

نیاز ساخت: CMake>=3.22، Ninja و arm-none-eabi-gcc. برای CubeIDE، IOC را در CubeMX مستقل باز و در پوشهٔ جدا خروجی STM32CubeIDE تولید و وارد کنید؛ این مسیر بررسی اجرایی نشده است. مجوز ST/Arm همراه منابع حفظ شده است.

## Educational figures

Six original educational diagrams/models with captions in image-metadata.json; no screenshots or physical measurements. draw_figures.py reproduces figures using Python3/Pillow and an installed Segoe UI font (not redistributed). Full-resolution files are included. The drawings represent configuration, reasoning and expected behavior, not actual board evidence.

## Download all files

[Download lesson17 resources ZIP](lesson-17-resources.zip)

Complete project sources/IOC, actual ELF/MAP and reports, scripts, worksheet and six editable diagrams are INSIDE this ZIP.
