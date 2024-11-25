#!/bin/bash

# رنگ‌ها برای خروجی بهتر
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# بررسی رزبری پای
if ! grep -q "Raspberry Pi" "/proc/cpuinfo"; then
    echo -e "${RED}این اسکریپت فقط برای رزبری پای طراحی شده است.${NC}"
    exit 1
fi

echo -e "${GREEN}شروع نصب GuardAI روی رزبری پای...${NC}"

# آپدیت سیستم
echo -e "${YELLOW}در حال آپدیت سیستم...${NC}"
sudo apt update && sudo apt upgrade -y

# نصب پیش‌نیازها با توجه به محدودیت‌های رزبری پای
echo -e "${YELLOW}نصب پیش‌نیازهای سیستم...${NC}"
sudo apt install -y \
    python3-pip \
    python3-dev \
    git \
    libatlas-base-dev \
    python3-opencv \
    libgstreamer1.0-0 \
    python3-picamera2 \
    python3-libcamera \
    python3-numpy \
    build-essential \
    python3-setuptools \
    python3-wheel \
    libpq-dev \
    v4l-utils \
    python3-django \
    python3-djangorestframework \
    libcap-dev \
    python3-venv  # نصب بسته venv برای ایجاد محیط مجازی

# ایجاد محیط مجازی
echo -e "${YELLOW}ایجاد محیط مجازی...${NC}"
python3 -m venv venv

# فعال‌سازی محیط مجازی
echo -e "${YELLOW}فعال‌سازی محیط مجازی...${NC}"
source venv/bin/activate

# نصب پکیج‌های اضافی مورد نیاز برای رزبری پای
pip install RPi.GPIO
pip install picamera2
pip install django-apscheduler
pip install djangorestframework-simplejwt
pip install python-telegram-bot
pip install gunicorn
pip install transformers
pip install torch --index-url https://download.pytorch.org/whl/cpu  # نسخه سبک‌تر برای رزبری پای
pip install torchvision --index-url https://download.pytorch.org/whl/cpu

# نصب django-cors-headers
pip install django-cors-headers

# عال‌سازی دوربین رزبری پای
echo -e "${YELLOW}فعال‌سازی دوربین رزبری پای...${NC}"
if ! grep -q "start_x=1" /boot/config.txt; then
    sudo sh -c 'echo "start_x=1" >> /boot/config.txt'
    sudo sh -c 'echo "gpu_mem=128" >> /boot/config.txt'
fi

# ایجاد دایرکتوری پروژه
echo -e "${YELLOW}ایجاد دایرکتوری پروژه...${NC}"
if [ -d "$HOME/guardai" ]; then
    echo -e "${YELLOW}پاک کردن دایرکتوری قبلی...${NC}"
    rm -rf "$HOME/guardai"
fi

mkdir -p "$HOME/guardai"
cd "$HOME/guardai"

# کلون پروژه
echo -e "${YELLOW}دریافت کد از گیت‌هاب...${NC}"
git clone https://github.com/roundstudio/GuardAI-API.git .

# نصب پکیج‌های پایتون
echo -e "${YELLOW}نصب پکیج‌های مورد نیاز...${NC}"
pip install --upgrade pip wheel setuptools

# نصب پکیج‌های اصلی از requirements.txt موجود
pip install -r requirements.txt

# تنظیم فایل‌های استاتیک
echo -e "${YELLOW}تنظیم فایل‌های استاتیک...${NC}"
# پاک کردن فایل‌های استاتیک قبلی
rm -rf static/*

# ایجاد دایرکتوری‌های مورد نیاز
mkdir -p static
mkdir -p staticfiles
mkdir -p media

# جمع‌آوری مجدد فایل‌های استاتیک
python3 manage.py collectstatic --noinput --clear

# تنظیم دسترسی‌ها
sudo chown -R $USER:$USER static media staticfiles
chmod -R 755 static media staticfiles

# ایجاد فایل .env
echo -e "${YELLOW}ایجاد فایل .env...${NC}"
cat > .env << EOL
DEBUG=False
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
ALLOWED_HOSTS=localhost,127.0.0.1,$(hostname -I | cut -d' ' -f1)
STATIC_ROOT=$(pwd)/static
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://$(hostname -I | cut -d' ' -f1):3000
DATABASE_URL=sqlite:///db.sqlite3
EOL

# حذف پایگاه داده و مایگریشن‌ها
echo -e "${YELLOW}حذف پایگاه داده و مایگریشن‌ها...${NC}"
if [ -f db.sqlite3 ]; then
    rm db.sqlite3
    echo -e "${GREEN}پایگاه داده حذف شد.${NC}"
fi

echo -e "${YELLOW}اجرای مایگریشن‌های دیتابیس...${NC}"
# حذف پوشه‌های مایگریشن
for app in rule camera notification gpio object_detection telegram contact stream processor; do
    if [ -d "$app/migrations" ]; then
        echo -e "${YELLOW}حذف مایگریشن‌های اپلیکیشن $app...${NC}"
        rm -rf "$app/migrations/*"
        rm -f "$app/migrations/__init__.py"  # حذف فایل __init__.py
    fi
    python3 manage.py makemigrations $app
    python3 manage.py migrate $app
done

# اجرای مایگریشن‌های دیتابیس


python3 manage.py makemigrations
python3 manage.py migrate

# ایجاد کاربر ادمین به صورت خودکار با استفاده از createsuperuser
echo -e "${YELLOW}ایجاد کاربر ادمین...${NC}"
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123!@#')" | python manage.py shell

# بررسی وجود کاربر و ایجاد در صورت عدم وجود
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}سوپر یوزر از قبل وجود دارد یا خطایی در ایجاد آن رخ داده است.${NC}"
else
    echo -e "${GREEN}سوپر یوزر با موفقیت ایجاد شد.${NC}"
fi

# جمع‌آوری فایل‌های استاتیک
echo -e "${YELLOW}جمع‌آوری فایل‌های اتاتیک...${NC}"
python3 manage.py collectstatic --noinput

# نصب و تنظیم whitenoise
pip install whitenoise

# ایجاد دایرکتوری‌های مورد نیاز
mkdir -p static
mkdir -p staticfiles
mkdir -p media

# جمع‌آوری فایل‌های استاتیک
python3 manage.py collectstatic --noinput --clear

# تنظیم دسترسی‌ها
sudo chown -R $USER:$USER static media staticfiles
chmod -R 755 static media staticfiles

# ایجاد سرویس systemd با تنظیمات به‌روز شده
echo -e "${YELLOW}ایجاد سرویس سیستمی...${NC}"
sudo tee /etc/systemd/system/guardai.service << EOL
[Unit]
Description=GuardAI Django Service
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$HOME/guardai
Environment="DJANGO_SETTINGS_MODULE=guardai_api.settings"
Environment="PYTHONUNBUFFERED=1"
ExecStart=gunicorn guardai_api.wsgi:application --bind 0.0.0.0:8000 --timeout 120
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

# تنظیم دسترسی‌های مورد نیاز برای رزبری پای
echo -e "${YELLOW}تنظیم دسترسی‌های سیستمی...${NC}"
sudo usermod -a -G gpio,video,i2c,spi $USER

# راه‌اندازی و فعال‌سازی سرویس
echo -e "${YELLOW}راه‌اندازی سرویس...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable guardai
sudo systemctl start guardai

# نمایش وضعیت سرویس
echo -e "${YELLOW}وضعیت سرویس:${NC}"
sudo systemctl status guardai

echo -e "${GREEN}نصب GuardAI با موفقیت انجام شد!${NC}"
echo -e "${YELLOW}نکات مهم:${NC}"
echo -e "1. آدرس IP رزبری پای: ${GREEN}$(hostname -I | cut -d' ' -f1)${NC}"
echo -e "2. پنل مدیریت: ${GREEN}http://$(hostname -I | cut -d' ' -f1):8000/admin${NC}"
echo -e "3. مشاهده لاگ‌ها: ${GREEN}sudo journalctl -u guardai -f${NC}"
echo -e "4. راه‌اندازی مجدد: ${GREEN}sudo systemctl restart guardai${NC}"

# پیشنهاد ریبوت
echo -e "${YELLOW}برای اعمال تمام تغییرات، پیشنهاد می‌شود سیستم را ریبوت کنید:${NC}"
echo -e "${GREEN}sudo reboot${NC}" 