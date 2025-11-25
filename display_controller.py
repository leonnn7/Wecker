"""
TM1637 4-digit 7-segment display controller
"""
import time
import RPi.GPIO as GPIO
from config import TM1637_CLK_PIN, TM1637_DIO_PIN, DISPLAY_BRIGHTNESS

# TM1637 Commands
TM1637_CMD1 = 0x40  # Data command
TM1637_CMD2 = 0xC0  # Address command
TM1637_CMD3 = 0x80  # Display control
TM1637_DSP_ON = 0x08  # Display on

# Digit patterns for 0-9
DIGITS = {
    '0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F, '4': 0x66,
    '5': 0x6D, '6': 0x7D, '7': 0x07, '8': 0x7F, '9': 0x6F,
    ' ': 0x00, '-': 0x40, '_': 0x08, 'A': 0x77, 'b': 0x7C,
    'C': 0x39, 'd': 0x5E, 'E': 0x79, 'F': 0x71
}


class TM1637Display:
    def __init__(self, clk_pin=TM1637_CLK_PIN, dio_pin=TM1637_DIO_PIN):
        self.clk_pin = clk_pin
        self.dio_pin = dio_pin
        self.brightness = DISPLAY_BRIGHTNESS
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.clk_pin, GPIO.OUT)
        GPIO.setup(self.dio_pin, GPIO.OUT)
        GPIO.output(self.clk_pin, GPIO.HIGH)
        GPIO.output(self.dio_pin, GPIO.HIGH)
        
        self._init_display()
    
    def _init_display(self):
        """Initialize the display"""
        self._start()
        self._write_byte(TM1637_CMD1)
        self._stop()
        
        self._start()
        self._write_byte(TM1637_CMD3 | DISPLAY_BRIGHTNESS | TM1637_DSP_ON)
        self._stop()
    
    def _start(self):
        """Start signal for I2C communication"""
        GPIO.output(self.dio_pin, GPIO.LOW)
        time.sleep(0.000002)
        GPIO.output(self.clk_pin, GPIO.LOW)
        time.sleep(0.000002)
    
    def _stop(self):
        """Stop signal for I2C communication"""
        GPIO.output(self.clk_pin, GPIO.LOW)
        time.sleep(0.000002)
        GPIO.output(self.dio_pin, GPIO.LOW)
        time.sleep(0.000002)
        GPIO.output(self.clk_pin, GPIO.HIGH)
        time.sleep(0.000002)
        GPIO.output(self.dio_pin, GPIO.HIGH)
        time.sleep(0.000002)
    
    def _write_byte(self, data):
        """Write a byte to the display"""
        for i in range(8):
            GPIO.output(self.clk_pin, GPIO.LOW)
            time.sleep(0.000002)
            GPIO.output(self.dio_pin, GPIO.LOW if (data & 0x01) else GPIO.HIGH)
            time.sleep(0.000002)
            GPIO.output(self.clk_pin, GPIO.HIGH)
            time.sleep(0.000002)
            data >>= 1
        
        # Wait for ACK
        GPIO.output(self.clk_pin, GPIO.LOW)
        GPIO.output(self.dio_pin, GPIO.HIGH)
        time.sleep(0.000002)
        GPIO.output(self.clk_pin, GPIO.HIGH)
        time.sleep(0.000002)
        GPIO.setup(self.dio_pin, GPIO.IN)
        
        ack = GPIO.input(self.dio_pin)
        if ack == 0:
            GPIO.setup(self.dio_pin, GPIO.OUT)
            GPIO.output(self.dio_pin, GPIO.LOW)
        
        GPIO.setup(self.dio_pin, GPIO.OUT)
        time.sleep(0.000002)
    
    def _write_data(self, addr, data):
        """Write data to a specific address"""
        self._start()
        self._write_byte(TM1637_CMD1)
        self._stop()
        
        self._start()
        self._write_byte(TM1637_CMD2 | addr)
        self._write_byte(data)
        self._stop()
        
        self._start()
        self._write_byte(TM1637_CMD3 | self.brightness | TM1637_DSP_ON)
        self._stop()
    
    def set_brightness(self, brightness):
        """Set display brightness (0-7)"""
        if 0 <= brightness <= 7:
            self.brightness = brightness
            self._start()
            self._write_byte(TM1637_CMD3 | self.brightness | TM1637_DSP_ON)
            self._stop()
    
    def show_time(self, hours, minutes, colon=True):
        """Display time in HH:MM format"""
        # Ensure hours and minutes are within valid range
        hours = hours % 24
        minutes = minutes % 60
        
        hours_str = f"{hours:02d}"
        minutes_str = f"{minutes:02d}"
        
        # Display hours (digits 0 and 1)
        self._write_data(0, DIGITS.get(hours_str[0], 0x00))
        self._write_data(1, DIGITS.get(hours_str[1], 0x00) | (0x80 if colon else 0))
        
        # Display minutes (digits 2 and 3)
        self._write_data(2, DIGITS.get(minutes_str[0], 0x00))
        self._write_data(3, DIGITS.get(minutes_str[1], 0x00))
    
    def show_text(self, text):
        """Display text (up to 4 characters) or scroll if longer"""
        text = str(text).upper()
        
        # Wenn Text länger als 4 Zeichen, scrolle
        if len(text) > 4:
            padding = "    " # 4 Leerzeichen
            display_text = padding + text + padding
            for i in range(len(display_text) - 3):
                window = display_text[i:i+4]
                self._show_fixed_text(window)
                time.sleep(0.3)
        else:
            self._show_fixed_text(text)
            
    def _show_fixed_text(self, text):
        """Helper to show exactly 4 chars"""
        for i, char in enumerate(text):
            if i < 4:
                self._write_data(i, DIGITS.get(char, 0x00))
        # Fill remaining digits with spaces
        for i in range(len(text), 4):
            self._write_data(i, DIGITS.get(' ', 0x00))
    
    def clear(self):
        """Clear the display"""
        for i in range(4):
            self._write_data(i, DIGITS.get(' ', 0x00))
    
    def cleanup(self):
        """Cleanup GPIO pins"""
        self.clear()
        GPIO.cleanup([self.clk_pin, self.dio_pin])

