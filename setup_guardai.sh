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
    python3-venv \
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
    python3-djangorestframework

# فعال‌سازی دوربین رزبری پای
echo -e "${YELLOW}فعال‌سازی دوربین رزبری پای...${NC}"
if ! grep -q "start_x=1" /boot/config.txt; then
    sudo sh -c 'echo "start_x=1" >> /boot/config.txt'
    sudo sh -c 'echo "gpu_mem=128" >> /boot/config.txt'
fi

# ایجاد دایرکتوری پروژه
echo -e "${YELLOW}ایجاد دایرکتوری پروژه...${NC}"
if [ -d "~/guardai" ]; then
    echo -e "${YELLOW}دایرکتوری guardai از قبل وجود دارد. در حال به‌روزرسانی...${NC}"
    cd ~/guardai
    # ذخیره تغییرات احتمالی محلی
    git stash
    # دریافت آخرین تغییرات
    git fetch origin
    # اعمال تغییرات
    git reset --hard origin/main
else
    mkdir -p ~/guardai
    cd ~/guardai
    # کلون پروژه
    echo -e "${YELLOW}دریافت کد از گیت‌هاب...${NC}"
    git clone https://github.com/roundstudio/GuardAI-API.git .
fi

# ایجاد محیط مجازی
echo -e "${YELLOW}ایجاد محیط مجازی پایتون...${NC}"
python3 -m venv venv
source venv/bin/activate

# نصب پکیج‌های پایتون
echo -e "${YELLOW}نصب پکیج‌های مورد نیاز...${NC}"
pip install --upgrade pip wheel setuptools

# نصب پکیج‌های اصلی
pip install -r requirements.txt

# نصب پکیج‌های اضافی مورد نیاز
pip install RPi.GPIO
pip install picamera2
pip install django-apscheduler
pip install djangorestframework-simplejwt

# ایجاد دایرکتوری static
mkdir -p static

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

# اجرای مایگریشن‌ها
echo -e "${YELLOW}اجرای مایگریشن‌های دیتابیس...${NC}"
python manage.py migrate

# ایجاد سوپریوزر
echo -e "${YELLOW}ایجاد کاربر ادمین...${NC}"
python manage.py createsuperuser

# جمع‌آوری فایل‌های استاتیک
echo -e "${YELLOW}جمع‌آوری فایل‌های استاتیک...${NC}"
python manage.py collectstatic --noinput

# نصب و تنظیم whitenoise
pip install whitenoise

# ایجاد دایرکتوری‌های مورد نیاز
mkdir -p static
mkdir -p staticfiles
mkdir -p media

# جمع‌آوری فایل‌های استاتیک
python manage.py collectstatic --noinput --clear

# تنظیم دسترسی‌ها
sudo chown -R $USER:$USER static media staticfiles
chmod -R 755 static media staticfiles

# ایجاد سرویس systemd با تنظیمات مناسب برای رزبری پای
echo -e "${YELLOW}ایجاد سرویس سیستمی...${NC}"
sudo tee /etc/systemd/system/guardai.service << EOL
[Unit]
Description=GuardAI Django Service
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$HOME/guardai
Environment="PATH=$HOME/guardai/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=guardai_api.settings"
Environment="PYTHONUNBUFFERED=1"
Environment="LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1"
ExecStart=$HOME/guardai/venv/bin/gunicorn guardai_api.wsgi:application --bind 0.0.0.0:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

# تنظیم دسترسی‌های مورد نیاز برای رزبری پای
echo -e "${YELLOW}تنظیم دسترسی‌های سیستمی...${NC}"
sudo usermod -a -G gpio,video,i2c,spi $USER

# نصب و تنظیم gunicorn
pip install gunicorn

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