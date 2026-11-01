# درس ۱۹: تولید PWM با تایمر STM32

[مقالهٔ آموزشی جبرابیت](https://gebrabit.com/blog/stm32-timer-pwm-tutorial/)

برد: GB100ST، شماتیک V2.0؛ تراشه: STM32F303CBT6؛ خروجی: PA6 / TIM3_CH1 / AF2.

## فایل‌ها

- `lesson19-pwm-project.zip`: پروژهٔ کامل تولیدشده با CubeMX، فایل IOC، سورس و خروجی ساخت CMake.
- `lesson19-verify-pwm.py`: اسکریپت مستقل Python 3 برای محاسبات درس؛ بدون کتابخانهٔ جانبی.
- `lesson19-calculations.json`: نتایج محاسبات مرجع.
- `lesson19-build-report.txt`: گزارش کامپایل و مصرف حافظه.
- `lesson19-project-sha256.json`: اثر انگشت فایل‌های منبع پروژه.
- `lesson19-hal-reference.json`: commit رسمی درایور HAL همراه بسته.

## اجرای محاسبات

```sh
python lesson19-verify-pwm.py
```

## وضعیت اعتبارسنجی

پروژه با CubeMX 6.14.0 و STM32CubeF3 V1.11.6 تولید شده و با Arm GNU GCC 13.2.1 و CMake/Ninja در حالت Debug با `-Wall -Werror` بدون هشدار ساخته شده است. گزارش و خروجی ساخت در فایل‌ها موجود است.

ساخت در STM32CubeIDE و آزمون روی برد یا اسیلوسکوپ هنوز انجام نشده است. پروژهٔ حاضر CMake است؛ وجود فایل IOC تأیید ساخت در CubeIDE نیست. فرکانس نامی نمونه ۱ کیلوهرتز با PSC=71 و ARR=999 است.

متغیر `lesson_mode`: مقدار ۰ نمایش ۲۵/۵۰/۷۵ درصد، ۱ آزمایش Preload روشن، ۲ آزمایش Preload خاموش، ۳ توقف و GPIO Low. برای اجرا و محدودیت‌های آزمایش مقاله را بخوانید.

فایل‌های درایور و CMSIS تابع مجوزهای موجود در همان فایل‌ها هستند. انتشار در این مخزن مجوز آن فایل‌ها را تغییر نمی‌دهد.
