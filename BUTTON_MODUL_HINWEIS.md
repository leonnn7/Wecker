# Wichtiger Hinweis: Button-Modul Konfiguration

## Dein Button-Modul

Dein Button-Modul hat eine **High Level Output** Funktion:
- **Button losgelassen:** OUT = LOW (0V)
- **Button gedrückt:** OUT = HIGH (3.3V oder 5V)

Das ist **umgekehrt** zu normalen Buttons, die LOW ausgeben wenn gedrückt!

## Code-Anpassung

Der Code wurde bereits angepasst:
- `GPIO.RISING` statt `GPIO.FALLING` (reagiert auf LOW → HIGH)
- Kein Pull-up nötig (Modul hat bereits interne Logik)

## Falls Button nicht funktioniert

Falls der Button nicht richtig funktioniert, kannst du die Logik in `hardware_controller.py` anpassen:

```python
# Aktuell (für High Level Output Modul):
GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, ...)

# Falls dein Modul anders funktioniert, ändere zu:
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, ...)
```

## Test

Teste dein Button-Modul:

```bash
python3 -c "import RPi.GPIO as GPIO; import time; GPIO.setmode(GPIO.BCM); GPIO.setup(18, GPIO.IN); print('Button Test - drücke den Button:'); [print('Status:', 'GEDRÜCKT' if GPIO.input(18) == 1 else 'LOSGELASSEN') or time.sleep(0.5) for _ in range(10)]"
```

**Erwartetes Verhalten:**
- Button losgelassen: "LOSGELASSEN" (GPIO = 0)
- Button gedrückt: "GEDRÜCKT" (GPIO = 1)

Falls es umgekehrt ist, musst du den Code anpassen!

