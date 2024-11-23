# GuardAI

سیستم هوشمند نظارت تصویری مبتنی بر هوش مصنوعی برای رزبری پای

## پیش‌نیازها
- رزبری پای (نسخه 3 یا بالاتر)
- دوربین رزبری پای
- اتصال به اینترنت
- سیستم‌عامل Raspberry Pi OS (قبلاً Raspbian)

## نصب

برای نصب GuardAI، دستورات زیر را در ترمینال رزبری پای اجرا کنید: 

# دانلود اسکریپت نصب
wget https://raw.githubusercontent.com/roundstudio/GuardAI-API/main/setup_guardai.sh

# دادن دسترسی اجرا به فایل
chmod +x setup_guardai.sh

# اجرای اسکریپت نصب
./setup_guardai.sh

یا همه مراحل در یک خط:
wget https://raw.githubusercontent.com/roundstudio/GuardAI-API/main/setup_guardai.sh && chmod +x setup_guardai.sh && ./setup_guardai.sh

## دستورات کاربردی

### مدیریت سرویس
# راه‌اندازی سرویس
sudo systemctl start guardai

# توقف سرویس
sudo systemctl stop guardai

# راه‌اندازی مجدد سرویس
sudo systemctl restart guardai

# بررسی وضعیت سرویس
sudo systemctl status guardai

# فعال‌سازی اجرای خودکار در هنگام بوت
sudo systemctl enable guardai

# غیرفعال‌سازی اجرای خودکار
sudo systemctl disable guardai

### مشاهده لاگ‌ها
# مشاهده لاگ‌های سرویس
sudo journalctl -u guardai -f

# مشاهده لاگ‌های سرویس از ابتدا
sudo journalctl -u guardai

# مشاهده لاگ‌های امروز
sudo journalctl -u guardai --since today

### کار با محیط مجازی و جنگو
# ورود به محیط مجازی
cd ~/guardai
source venv/bin/activate

# اجرای مایگریشن‌ها
python manage.py migrate

# ایجاد کاربر ادمین جدید
python manage.py createsuperuser

# ورود به شل جنگو
python manage.py shell

# فعال‌سازی محیط مجازی
cd ~/guardai
source venv/bin/activate

# غیرفعال‌سازی محیط مجازی
deactivate

# نصب مجدد پکیج‌ها
pip install -r requirements.txt

### به‌روزرسانی و گیت
# دریافت آخرین تغییرات
cd ~/guardai
git fetch origin
git reset --hard origin/main

# مشاهده وضعیت فعلی
git status

# مشاهده تغییرات
git log

### فایل‌های استاتیک
# جمع‌آوری فایل‌های استاتیک
cd ~/guardai
source venv/bin/activate
python manage.py collectstatic --noinput

### دستورات سیستمی
# بررسی وضعیت دوربین
vcgencmd get_camera

# بررسی دمای CPU
vcgencmd measure_temp

# بررسی فضای دیسک
df -h

# بررسی مصرف RAM
free -h

# مشاهده پردازش‌های در حال اجرا
top

# راه‌اندازی مجدد سیستم
sudo reboot

# خاموش کردن سیستم
sudo shutdown -h now

## پشتیبانی
در صورت بروز مشکل یا نیاز به پشتیبانی:
- ایمیل: support@roundstudio.org
- تلگرام: @roundstudio
- گیت‌هاب: [صفحه Issues](https://github.com/roundstudio/GuardAI-API/issues)

## لایسنس
این پروژه تحت لایسنس MIT منتشر شده است. برای اطلاعات بیشتر، فایل LICENSE را مطالعه کنید.
