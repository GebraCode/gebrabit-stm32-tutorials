# درس 16: ساختمان تایمر

دو پروژهٔ واقعی با TIM2 و پیش‌تقسیم‌کننده‌های 71 و 7199 برای STM32F303CBT6 تولید و با GCC/CMake به صورت clean و با `-O0 -g3 -Wall -Werror` بدون هشدار کامپایل شده‌اند. خروجی همراه CMake است؛ اجرای CubeIDE و آزمون روی برد انجام نشده‌اند. هر ZIP منابع، IOC و مجوزهای ST/Arm را دارد؛ ZIP جداگانهٔ ELF/MAP نیز از همان ساخت است.

کلاک پایه: HSE برابر 8 MHz، PLL ×9، SYSCLK/HCLK برابر 72 MHz، APB1 برابر 36 MHz با کلاک TIM2 برابر 72 MHz، APB2 برابر 72 MHz و Flash برابر 2WS. SysTick مبنای زمان HAL باقی می‌ماند. TIM2 بدون کانال خروجی و بدون وقفه، با ARR برابر 0xFFFFFFFF و preload فعال است.

در USER CODE2 شمارنده صفر و UIF پاک و تایمر با HAL_TIM_Base_Start راه‌اندازی می‌شود. قابلیت توقف TIM2 هنگام halt دیباگر صریحاً فعال شده است. در حلقه، CNT و PSC و ARR در متغیرهای volatile ذخیره می‌شوند؛ HAL_Delay(100) فقط خواندن‌ها را کند می‌کند و فاصلهٔ دقیق اندازه‌گیری نیست. Snapshotهای هر متغیر هم‌زمان نیستند. توقف و resume دیباگر زمان دیواری را برای تایمر متوقف می‌کند؛ در Live Expressions انتظار شمارش پیوسته فقط در اجرای آزاد داشته باشید.

پیش‌بینی: PSC=71 تیک 1us و PSC=7199 تیک 100us دارد. در فاصلهٔ ایده‌آل 100ms به ترتیب 100000 و 1000 تیک؛ مقدار خوانده‌شده به زمان حلقه و دیباگر وابسته است. اسکریپت `python verify_timers.py` فقط محاسبهٔ مدل است، نه لاگ سخت‌افزار.

برای آزمایش، ST-LINK را با SWDIO=PA13 و SWCLK=PA14، زمین مشترک، مرجع 3.3V و NRST مطابق شماتیک V2.0 وصل کنید. برد را از ورودی مجاز تغذیه کنید؛ اتصال 5V به پایهٔ 3V3 یا MCU مجاز نیست. نتیجه‌ها را در hardware-worksheet.csv ثبت کنید؛ همهٔ ردیف‌ها هنوز pending هستند. جابه‌جایی PSC آزمایش عمدی آموزشی است؛ پیکربندی هر پروژه در IOC خودش ذخیره شده است.

ساخت در محیط دارای Ninja، CMake>=3.22 و GCC سازگار، از پوشهٔ پروژه:

```text
cmake --preset Debug
cmake --build --preset Debug --clean-first
```

برای CubeIDE، IOC را در CubeMX مستقل باز و خروجی STM32CubeIDE را در پوشه‌ای جدا تولید کنید؛ آن مسیر اینجا اجرا و تأیید نشده است. بعد از تولید دوباره، گزینه‌های هشدار ساخت را بازبینی کنید. گزارش RAM شامل رزرو linker برای heap/stack است و مصرف واقعی هنگام اجرا نیست.

مرجع ویژگی‌ها: DS9118 Rev14، جدول 5 و بخش 3.17؛ TIM1/TIM8 پیشرفتهٔ 16 بیتی، TIM2 شمارندهٔ 32 بیتی با PSC شانزده‌بیتی، TIM3/4 شمارندهٔ 16 بیتی، TIM15 دارای 2 کانال، TIM16/17 دارای 1 کانال، TIM6/7 پایهٔ 16 بیتی بدون کانال Capture/Compare. وجود تایمر به معنی دسترسی به تمام پایه‌های کانال روی LQFP48 نیست. عبارت «PSC سی‌ودوبیتی TIM2» در متن بخش 3.17.2 دیتاشیت با جدول 5/رجیستر PSC سازگار نیست؛ عدد معتبر PSC برابر 0 تا 65535 است.

## Educational figures

Six original educational diagrams/models with captions in image-metadata.json; no screenshots or physical measurements. draw_figures.py reproduces figures using Python3/Pillow and an installed Segoe UI font (not redistributed). Full-resolution files are included. The drawings represent configuration, reasoning and expected behavior, not actual board evidence.

## Download all files

[Download lesson16 resources ZIP](lesson-16-resources.zip)

Complete project sources/IOC, actual ELF/MAP and reports, scripts, worksheet and six editable diagrams are INSIDE this ZIP.
