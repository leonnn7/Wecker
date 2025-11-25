# Button-Modul Pin-Beschriftung: S, V, G

## Dein Button-Modul hat folgende Beschriftung:

```
┌─────────────┐
│  [Button]   │
│             │
│   V    G    │
│   │    │    │
│   │    │    │
│   │    │   S│
└───┼────┼────┼──┘
    │    │    │
   Rot Schwarz Gelb/Weiss
```

## Pin-Bedeutung:

- **V** = VCC (Versorgungsspannung)
  - Meist rotes Kabel
  - Braucht 3.3V oder 5V vom Raspberry Pi
  
- **G** = GND (Ground/Masse)
  - Meist schwarzes Kabel
  - Muss an GND (Masse) des Raspberry Pi
  
- **S** = Signal/OUT (Ausgang)
  - Meist gelbes oder weisses Kabel
  - Gibt das Signal aus (HIGH wenn gedrückt)

## Verbindung zum Raspberry Pi:

```
Button-Modul Pin    →    Raspberry Pi Pin
─────────────────────────────────────────
V (VCC, Rot)        →    Pin 1 (3.3V) ODER Pin 2 (5V)
G (GND, Schwarz)    →    Pin 14 (GND)
S (Signal, Gelb)    →    Pin 12 (GPIO 18)
```

## Schritt-für-Schritt Anschluss:

1. **V (VCC)** → Pin 1 oder Pin 2
   - Pin 1 = 3.3V (oben links)
   - Pin 2 = 5V (oben rechts)
   - Beide funktionieren, 5V ist sicherer

2. **G (GND)** → Pin 14
   - Pin 14 ist rechts, 7. Reihe von oben
   - Wichtig: Muss an GND!

3. **S (Signal)** → Pin 12 (GPIO 18)
   - Pin 12 ist rechts, 6. Reihe von oben
   - Das ist der Signal-Ausgang

## Funktionsweise:

- **Button losgelassen:** S = LOW (0V)
- **Button gedrückt:** S = HIGH (3.3V oder 5V)
- Das Modul hat bereits interne Logik
- Kein externer Widerstand nötig!

## Test:

```bash
python3 -c "import RPi.GPIO as GPIO; import time; GPIO.setmode(GPIO.BCM); GPIO.setup(18, GPIO.IN); print('Button Test - drücke den Button:'); [print('Status:', 'GEDRÜCKT' if GPIO.input(18) == 1 else 'LOSGELASSEN') or time.sleep(0.5) for _ in range(10)]"
```

**Erwartetes Verhalten:**
- Button losgelassen: "LOSGELASSEN" (S = 0V)
- Button gedrückt: "GEDRÜCKT" (S = HIGH)

## Wichtige Hinweise:

1. **V** muss immer mit Spannung versorgt werden (3.3V oder 5V)
2. **G** muss immer an GND (Masse)
3. **S** ist der Ausgang, der an GPIO 18 geht
4. Das Modul funktioniert mit 3.3V oder 5V
5. Kein externer Widerstand nötig - Modul hat interne Logik

Viel Erfolg! 🎉

