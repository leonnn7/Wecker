"""
Hardware controller for button and sound
"""
import RPi.GPIO as GPIO
import threading
import time
import os
from config import BUTTON_PIN, SOUND_PIN

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class HardwareController:
    def __init__(self, button_callback=None):
        self.button_callback = button_callback
        self.sound_playing = False
        self.sound_thread = None
        self.alarm_active = False
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Setup button interrupt
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, 
                             callback=self._button_pressed, 
                             bouncetime=300)
        
        # Setup sound pin (PWM)
        GPIO.setup(SOUND_PIN, GPIO.OUT)
        self.pwm = GPIO.PWM(SOUND_PIN, 1000)  # 1kHz frequency
        self.pwm.start(0)  # Start with 0% duty cycle (silent)
        
        # Try to initialize pygame for better sound
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            except:
                pass
    
    def _button_pressed(self, channel):
        """Handle button press interrupt"""
        if self.button_callback:
            self.button_callback()
    
    def start_alarm_sound(self, frequency=1000, duration=None, sound_file=None):
        """Start playing alarm sound"""
        if self.sound_playing:
            return
        
        self.alarm_active = True
        self.sound_playing = True
        
        # If custom sound file provided, try to play it
        if sound_file and os.path.exists(sound_file):
            if PYGAME_AVAILABLE:
                try:
                    pygame.mixer.init()
                    self.sound_thread = threading.Thread(
                        target=self._play_custom_sound,
                        args=(sound_file,),
                        daemon=True
                    )
                    self.sound_thread.start()
                    return
                except Exception as e:
                    print(f"Error playing custom sound: {e}")
        
        # Fallback to default sound
        if PYGAME_AVAILABLE and pygame.mixer.get_init():
            # Use pygame for better sound quality
            self.sound_thread = threading.Thread(
                target=self._play_pygame_sound,
                daemon=True
            )
        else:
            # Use PWM for simple beep
            self.sound_thread = threading.Thread(
                target=self._play_pwm_sound,
                args=(frequency, duration),
                daemon=True
            )
        
        self.sound_thread.start()
    
    def _play_custom_sound(self, sound_file):
        """Play a custom sound file"""
        try:
            pygame.mixer.music.load(sound_file)
            while self.alarm_active and self.sound_playing:
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() and self.alarm_active:
                    time.sleep(0.1)
                if not self.alarm_active:
                    break
                time.sleep(0.5)  # Small pause between loops
        except Exception as e:
            print(f"Error in custom sound playback: {e}")
            # Fallback to default
            self._play_pygame_sound()
    
    def _play_pwm_sound(self, frequency, duration):
        """Play sound using PWM"""
        self.pwm.ChangeFrequency(frequency)
        self.pwm.ChangeDutyCycle(50)  # 50% duty cycle
        
        if duration:
            time.sleep(duration)
            self.stop_sound()
        else:
            # Play until stopped
            while self.alarm_active and self.sound_playing:
                time.sleep(0.1)
            self.stop_sound()
    
    def _play_pygame_sound(self):
        """Play sound using pygame (if available)"""
        try:
            # Generate a simple beep sound
            import numpy as np
            sample_rate = 22050
            duration = 0.5  # 500ms beep
            frequency = 800
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.sin(2 * np.pi * frequency * t)
            wave = (wave * 32767).astype(np.int16)
            
            sound = pygame.sndarray.make_sound(wave)
            
            while self.alarm_active and self.sound_playing:
                sound.play()
                time.sleep(0.5)  # Play beep every 500ms
                if not self.alarm_active:
                    break
        except:
            # Fallback to PWM if pygame fails
            self._play_pwm_sound(800, None)
    
    def stop_sound(self):
        """Stop playing alarm sound"""
        self.alarm_active = False
        self.sound_playing = False
        self.pwm.ChangeDutyCycle(0)  # Stop PWM
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.stop()
            except:
                pass
    
    def cleanup(self):
        """Cleanup GPIO pins"""
        self.stop_sound()
        GPIO.remove_event_detect(BUTTON_PIN)
        self.pwm.stop()
        GPIO.cleanup([BUTTON_PIN, SOUND_PIN])
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.quit()
            except:
                pass

