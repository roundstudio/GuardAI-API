#!/bin/bash

# آپدیت سیستم
sudo apt update
sudo apt upgrade -y

# نصب پیش‌نیازها
sudo apt install -y python3-pip python3-dev libatlas-base-dev
sudo apt install -y python3-opencv
sudo apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev
sudo apt install -y git

# ایجاد محیط مجازی
python3 -m venv venv
source venv/bin/activate

# نصب پکیج‌های مورد نیاز
pip install --upgrade pip
pip install -r requirements.txt

# نصب RPi.GPIO
pip install RPi.GPIO

# اجرای مایگریشن‌های جنگو
python manage.py migrate

# ایجاد سوپریوزر (اختیاری)
# python manage.py createsuperuser

# ایجاد سرویس systemd
sudo tee /etc/systemd/system/guardai.service << EOF
[Unit]
Description=GuardAI Django Service
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/python manage.py runserver 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
EOF

# فعال‌سازی سرویس
sudo systemctl daemon-reload
sudo systemctl enable guardai
sudo systemctl start guardai 