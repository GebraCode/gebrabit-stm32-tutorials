# از عدد به ولتاژ: آزمایش پله‌های DAC

در این درس، عددهای0،1024،2048،3072 و4095 را به خروجی PA4 می‌دهیم. هر عدد حدود2ثانیه نگه داشته می‌شود تا بتوانید ولتاژ را با مولتی‌متر ثبت کنید. هدف دیدن رابطهٔ کد و ولتاژ و اثر بافر/بار است؛ ولتاژ واقعی هنوز روی برد اندازه‌گیری نشده است.

## دو پروژه و اتصال

`gebrabit_lesson24_buffer_on` بافر خروجی روشن و `gebrabit_lesson24_buffer_off` همان برنامه با بافر خاموش است. CH1 روی PA4 استفاده شده است. این تراشه دو کانال یک DAC دارد: PA4=DAC_OUT1 و PA5=DAC_OUT2؛ PA5 یک DAC2 مستقل نیست و در برنامهٔ همراه فعال نشده است.

برد را مطابق شماتیکV2.0 تغذیه کنید، مولتی‌متر پرامپدانس را به PA4 و GND مشترک متصل و ریل مرجع/VDDA را جدا اندازه بگیرید. 5V فقط به ورودی مجاز برد وصل می‌شود، نه به PA4 یا3V3. DAC برای بلندگو، اتصال کوتاه یا ترمینیشن50اهم طراحی نشده است. ابتدا بی‌بار به‌جز ابزار اندازه‌گیری، سپس با مقاومت10kohm به زمین مقایسه کنید. مشخصات واقعی ورودی ابزار و ظرفیت بار را بررسی کنید.

## انتظار مدل در برابر ولتاژ واقعی

رابطهٔ ایده‌آل12بیتی `Vout=VREF+×DOR/4096` است؛ مخرج4095 سند سفارش برای این تراشه اصلاح شده است. کد4095 یکLSB زیر مرجع ایده‌آل است، نه دقیقاً خود مرجع. با فرض3.3V مرجع، سطح‌های مدل0،0.825،1.65،2.475 و3.2991943359375V هستند؛ این‌ها مقدار واقعی خروجی بافر نیستند. کد0 و4095 عمداً برای دیدن محدودیت نزدیک ریل انتخاب شده‌اند.

DS9118Rev14 جدول75 برای بافر روشن محدودهٔ خروجی0.2V تاVDDA−0.2V و VDDA2.4..3.6V را با شرایط مشخص می‌دهد. بار مقاومتی به زمین باید حداقل5kohm و بهVDDA حداقل25kohm باشد؛ ظرفیت بار حداکثر50pF است. زمان نشست تمام‌مقیاس تا±1LSB در شرط R>=5kohm و C<=50pF، نوعی3us و حداکثر4us؛ زمان بیدارشدن حداکثر10us است. این شرایط جای اندازه‌گیری روی برد را نمی‌گیرند.

با بافر خاموش امپدانس خروجی طبق همین جدول حداکثر15kohm است؛ این عدد مقدار دقیق یا نوعی مقاومت منبع نیست. بار10kohm می‌تواند ولتاژ را شدیداً تغییر دهد. مدل تقسیم مقاومتی همراه فقط مثال با فرض15kohm است و خروجی واقعی را پیش‌بینی دقیق نمی‌کند. نزدیک ریل‌ها و تحت بار، رابطهٔ ایده‌آل به‌تنهایی کافی نیست؛ مرجع، offset، gain، خطی‌بودن و ابزار نیز اثر دارند.

## کد چه می‌کند؟

در CubeMX، DAC_CHANNEL_1 و DAC_TRIGGER_NONE انتخاب شده‌اند. NONE یعنی تریگر غیرفعال و انتقال از نوشتن DHR، نه انتخاب literal نرم‌افزاری SWTRIG. DAC_TRIGGER_SOFTWARE انتخاب متفاوتی است؛ HAL_DAC_Start تنها با آن انتخاب، مسیر SWTRIG مربوط را فعال می‌کند. در این درس SetValue با DAC_ALIGN_12B_R انجام می‌شود، ابتدا مقدار اولیه سپس Start و در حلقه هر2ثانیه کد بعدی نوشته می‌شود.

requested_dac_code کد درخواست‌شده است. dac_output_register از HAL_DAC_GetValue می‌آید و فقط رجیستر دیجیتال DOR را می‌خواند؛ سنجش ولتاژ نیست. active_step بعد از پایان توقف جلو می‌رود، پس خواندن غیرهم‌زمان متغیرها را با یک snapshot دقیق ابزار یکی نگیرید. برگشت HAL هر SetValue/Start بررسی می‌شود و خطا به Error_Handler می‌رود. هیچ تابع تولیدشده دوباره تعریف نشده است.

## آزمایش خواننده

جدول hardware-worksheet.csv برای هر کد، مرجع واقعی، بافر، بار و خروجی مشاهده‌شده را ثبت می‌کند. چهار حالت بافر روشن/خاموش و با/بدون10kohm را مقایسه کنید. ابتدا سطح میانی را بررسی کنید؛ اختلاف کد4095 با3.3V اسمی به‌تنهایی خطای برنامه را ثابت نمی‌کند. همهٔ نتیجه‌ها فعلاً pending هستند.

```text
python verify_dac_levels.py
cmake --preset Debug
cmake --build --preset Debug --clean-first
```

## ساخت و منابع

دو پروژهٔ واقعی با CubeMX6.14.0، DB6.0.140، CubeF3V1.11.6 و GCC13.2.1 در مسیر CMake Debug، ساخت پاک `-O0 -g3 -Wall -Werror` بدون هشدار ساخته شده‌اند. پروگرام، اجرای سخت‌افزار و CubeIDE گرافیکی انجام نشده‌اند. برای CubeIDE، IOC را در CubeMX مستقل باز و خروجی STM32CubeIDE را در پوشهٔ جدا تولید کنید. ابزار ساخت همراه به CMake>=3.22، Ninja و arm-none-eabi-gcc نیاز دارد.

مرجع انتقال: RM0316 بخش16.5.3 و AN3126Rev6October2026 صفحه2؛ مرجع محدودیت‌ها DS9118Rev14 جدول75 و پایه‌ها جدول13. نمونهٔ رسمی نزدیک بررسی‌شده Projects/STM32303C_EVAL/Examples/DAC/DAC_SimpleConversion است؛ رفتار HAL از فایل‌های همان HALcommit953955afe65f89e60e556bbcdba752597f5da65d استخراج شده است. مجوزهای ST/Arm در ZIP منابع باقی‌اند. گزارش RAM شامل رزرو heap/stack لینک است و مصرف واقعی زمان اجرا نیست.

## Original educational diagrams

Six original diagrams/models and editable draw_figures.py are included. They are not GUI/scope captures or physical measurements. Metadata records sources, assumptions, captions and alt text. Python3/Pillow and the system Segoe UI font regenerate the drawings; font files are not redistributed.

## Download the complete package

[All lesson 24 files](lesson-24-resources.zip)

Source/IOC, ELF/MAP, build reports, calculation model, hardware worksheet, third-party licenses and six editable diagrams are INSIDE the ZIP. Hardware validation is pending.
