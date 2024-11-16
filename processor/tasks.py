import logging
from camera.models import Camera
from rule.models import Rule
from gpio.models import Gpio
from object_detection.models import UserObjectRequest
from utils.stream import IPCamera

import time

# تنظیم لاگر
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# اضافه کردن StreamHandler برای نمایش در کنسول
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def process_database_task():
    rules = Rule.objects.all()
    for rule in rules:
        logger.info(f"{rule.name}")
        cameras = rule.camera.all()

        object_types = rule.object_types.all()
        gpio = rule.gpio.all()
        while True:
            camera = cameras.first()
            logger.info(f"{camera}")
            ip_camera = IPCamera(ip_address=camera.ip, username=camera.username, password=camera.password, port=camera.port, path=camera.path)
            logger.info(ip_camera.connect())
            time.sleep(5)




