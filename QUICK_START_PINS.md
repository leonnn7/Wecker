# Schnellstart: Pin-Verbindungen

## Einfache Anleitung - Nur die wichtigsten Pins

### TM1637 Display (4 Kabel)

```
Display-Kabel    →    Raspberry Pi Pin
─────────────────────────────────────
VCC (Rot)        →    Pin 1 (3.3V) - oben links
GND (Schwarz)    →    Pin 6 (GND) - links, 3. Reihe
DIO (Gelb)       →    Pin 18 (GPIO 24) - rechts, 9. Reihe
CLK (Grün)       →    Pin 16 (GPIO 23) - rechts, 8. Reihe
```

### Button-Modul (3-Pin Modul mit High Level Output)

```
Button-Modul     →    Raspberry Pi Pin
─────────────────────────────────────
V (VCC, Rot)      →    Pin 1 (3.3V) oder Pin 2 (5V)
G (GND, Schwarz)  →    Pin 14 (GND) - rechts, 7. Reihe
S (Signal, Gelb)  →    Pin 12 (GPIO 18) - rechts, 6. Reihe
```

**Pin-Beschriftung:**
- **V** = VCC (Versorgungsspannung)
- **G** = GND (Ground/Masse)
- **S** = Signal/OUT (Ausgang)

**Wichtig:** 
- Das Modul hat bereits interne Logik
- S (Signal) gibt HIGH aus wenn Button gedrückt
- Funktioniert mit 3.3V oder 5V

### Lautsprecher (Mini 3W 8Ω mit JST-PH2.0 Stecker)

**Option 1: Direkt an GPIO 25 (PWM)**
```
Lautsprecher     →    Raspberry Pi Pin
─────────────────────────────────────
+ (Rot)          →    Pin 22 (GPIO 25) - rechts, 11. Reihe
- (Schwarz)      →    Pin 20 (GND) - rechts, 10. Reihe
```

**Hinweis:** 
- JST-PH2.0 Stecker müssen abgeschnitten werden
- Oder: Verwende Adapter-Kabel (JST-PH2.0 zu Dupont)

**Option 2: Audio-Jack (empfohlen für besseren Sound)**
```
Lautsprecher     →    Raspberry Pi
─────────────────────────────────────
+ (Rot)          →    Audio-Jack (Spitze)
- (Schwarz)      →    Audio-Jack (Ring/Masse)
```

**Hinweis:**
- JST-PH2.0 Stecker an Audio-Kabel anpassen
- Oder: Audio-Kabel mit 3.5mm Stecker verwenden

## Pin-Finder Hilfe

### So findest du Pin 1:
- Schaue auf den Raspberry Pi von oben
- GPIO-Header ist oben
- Pin 1 ist **oben links** (neben dem "3.3V" Label)

### Pin-Nummerierung:
- **Links** = ungerade Pins (1, 3, 5, 7, ...)
- **Rechts** = gerade Pins (2, 4, 6, 8, ...)
- Von **oben nach unten** zählen

### Wichtige Pins im Überblick:

| Was du brauchst | Pin-Nummer | Position |
|----------------|------------|----------|
| 3.3V (Display) | Pin 1      | Oben links |
| 5V (Display)   | Pin 2      | Oben rechts |
| GND (Display)  | Pin 6      | Links, 3. Reihe |
| GND (Button)   | Pin 14     | Rechts, 7. Reihe |
| GND (Sound)    | Pin 20     | Rechts, 10. Reihe |
| GPIO 18 (Button) | Pin 12   | Rechts, 6. Reihe |
| GPIO 23 (Display CLK) | Pin 16 | Rechts, 8. Reihe |
| GPIO 24 (Display DIO) | Pin 18 | Rechts, 9. Reihe |
| GPIO 25 (Sound) | Pin 22    | Rechts, 11. Reihe |

## Test-Commands

Nach dem Anschließen kannst du testen:

```bash
# Display CLK testen (Pin 16)
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(23, GPIO.OUT); GPIO.output(23, GPIO.HIGH); print('Pin 16 (GPIO 23) OK')"

# Display DIO testen (Pin 18)
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(24, GPIO.OUT); GPIO.output(24, GPIO.HIGH); print('Pin 18 (GPIO 24) OK')"

# Button-Modul testen (Pin 12)
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(18, GPIO.IN); print('Button Status:', 'Gedrückt' if GPIO.input(18) == 1 else 'Losgelassen')"

# Sound testen (Pin 22)
python3 -c "import RPi.GPIO as GPIO; import time; GPIO.setmode(GPIO.BCM); GPIO.setup(25, GPIO.OUT); pwm = GPIO.PWM(25, 1000); pwm.start(50); time.sleep(1); pwm.stop(); print('Pin 22 (GPIO 25) OK')"
```

## Wichtige Hinweise

1. **Immer GND verbinden!** Jede Komponente braucht eine Masse-Verbindung
2. **Vorsicht mit 5V:** Nur für Display VCC, nicht auf GPIO-Pins!
3. **Pin 1 finden:** Oben links, neben "3.3V" Label
4. **Reihen zählen:** Von oben nach unten, links und rechts getrennt

## Hilfe bei Problemen

- **Display zeigt nichts:** Prüfe ob VCC richtig verbunden ist (Pin 1 oder 2)
- **Button funktioniert nicht:** Prüfe ob beide Pins richtig verbunden sind
- **Kein Sound:** Versuche Audio-Jack statt GPIO
- **Falsche Pins:** Zähle nochmal von Pin 1 aus

Viel Erfolg! 🎉

