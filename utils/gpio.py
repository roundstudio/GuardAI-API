import platform
import time
from typing import Dict, Optional
from threading import Lock
import logging

logger = logging.getLogger(__name__)

# کلاس Mock برای GPIO در ویندوز
class MockGPIO:
    BCM = "BCM"
    BOARD = "BOARD"
    OUT = "OUT"
    IN = "IN"
    
    @staticmethod
    def setmode(mode):
        logger.debug(f"Mock GPIO: Setting mode to {mode}")
        
    @staticmethod
    def setup(pin, direction, initial=None):
        logger.debug(f"Mock GPIO: Setup pin {pin} as {direction} with initial value {initial}")
        
    @staticmethod
    def output(pin, state):
        logger.debug(f"Mock GPIO: Setting pin {pin} to {state}")
        
    @staticmethod
    def input(pin):
        logger.debug(f"Mock GPIO: Reading pin {pin}")
        return False
        
    @staticmethod
    def cleanup(pin=None):
        if pin:
            logger.debug(f"Mock GPIO: Cleaning up pin {pin}")
        else:
            logger.debug("Mock GPIO: Cleaning up all pins")

# انتخاب کتابخانه مناسب بر اساس سیستم عامل
if platform.system().lower() == 'windows':
    GPIO = MockGPIO()
    logger.info("Using Mock GPIO for Windows")
else:
    try:
        import RPi.GPIO as GPIO
        logger.info("Using RPi.GPIO")
    except ImportError:
        GPIO = MockGPIO()
        logger.warning("RPi.GPIO not found, using Mock GPIO")

class GPIOManager:
    """مدیریت پین‌های GPIO برای رزبری‌پای"""
    
    def __init__(self, mode: str = "BCM"):
        """
        راه‌اندازی مدیریت GPIO
        
        Args:
            mode: حالت شماره‌گذاری پین‌ها ('BCM' یا 'BOARD')
        """
        self.mode = GPIO.BCM if mode.upper() == "BCM" else GPIO.BOARD
        GPIO.setmode(self.mode)
        self.active_pins: Dict[int, str] = {}  # نگهداری وضعیت پین‌های فعال
        self._lock = Lock()  # قفل برای عملیات‌های همزمان
        
    def setup_pin(self, pin: int, direction: str, initial: Optional[bool] = None) -> None:
        """
        تنظیم یک پین GPIO
        
        Args:
            pin: شماره پین
            direction: 'IN' یا 'OUT'
            initial: مقدار اولیه برای پین‌های خروجی (True/False)
        """
        with self._lock:
            if direction.upper() == "OUT":
                if initial is not None:
                    GPIO.setup(pin, GPIO.OUT, initial=initial)
                else:
                    GPIO.setup(pin, GPIO.OUT)
                self.active_pins[pin] = "OUT"
            else:
                GPIO.setup(pin, GPIO.IN)
                self.active_pins[pin] = "IN"
    
    def set_output(self, pin: int, state: bool) -> None:
        """
        تنظیم وضعیت یک پین خروجی
        
        Args:
            pin: شماره پین
            state: وضعیت مورد نظر (True/False)
        """
        if pin not in self.active_pins or self.active_pins[pin] != "OUT":
            raise ValueError(f"پین {pin} به عنوان خروجی تنظیم نشده است")
        
        with self._lock:
            GPIO.output(pin, state)
    
    def read_input(self, pin: int) -> bool:
        """
        خواندن وضعیت یک پین ورودی
        
        Args:
            pin: شماره پین
            
        Returns:
            وضعیت پین (True/False)
        """
        if pin not in self.active_pins or self.active_pins[pin] != "IN":
            raise ValueError(f"پین {pin} به عنوان ورودی تنظیم نشده است")
        
        return GPIO.input(pin)
    
    def toggle_output(self, pin: int) -> None:
        """
        تغییر وضعیت یک پین خروجی
        
        Args:
            pin: شماره پین
        """
        if pin not in self.active_pins or self.active_pins[pin] != "OUT":
            raise ValueError(f"پین {pin} به عنوان خروجی تنظیم نشده است")
        
        with self._lock:
            current_state = GPIO.input(pin)
            GPIO.output(pin, not current_state)
    
    def pulse_output(self, pin: int, duration: float = 0.1) -> None:
        """
        ارسال یک پالس به پین خروجی
        
        Args:
            pin: شماره پین
            duration: مدت زمان پالس به ثانیه
        """
        if pin not in self.active_pins or self.active_pins[pin] != "OUT":
            raise ValueError(f"پین {pin} به عنوان خروجی تنظیم نشده است")
        
        with self._lock:
            GPIO.output(pin, True)
            time.sleep(duration)
            GPIO.output(pin, False)
    
    def cleanup(self, pin: Optional[int] = None) -> None:
        """
        پاکسازی پین‌های GPIO
        
        Args:
            pin: شماره پین برای پاکسازی (اگر None باشد، همه پین‌ها پاکسازی می‌شوند)
        """
        with self._lock:
            if pin is None:
                GPIO.cleanup()
                self.active_pins.clear()
            else:
                GPIO.cleanup(pin)
                self.active_pins.pop(pin, None)
    
    def __del__(self):
        """پاکسازی خودکار در هنگام حذف شیء"""
        self.cleanup()

