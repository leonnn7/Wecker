# Spezielle Anleitung: Button-Modul und Lautsprecher

## Deine Komponenten

### Button-Modul
- **Typ:** Momentary Tactile Push Button Modul
- **Pins:** 3 Stück (VCC, GND, OUT)
- **Funktion:** High Level Output (gibt HIGH aus wenn gedrückt)
- **Spannung:** Funktioniert mit 3.3V oder 5V

### Lautsprecher
- **Typ:** Mini Lautsprecher 3 Watt 8 Ohm
- **Stecker:** JST-PH2.0 2-Pin
- **Impedanz:** 8Ω
- **Leistung:** 3W

---

## Button-Modul Anschluss

### Pin-Belegung des Moduls:
```
┌─────────────┐
│  [Button]   │
│             │
│  VCC  GND   │
│   │    │    │
│   │    │    │
│   │    │  OUT│
└───┼────┼────┼──┘
    │    │    │
   Rot Schwarz Gelb/Weiss
```

### Verbindung zum Raspberry Pi:

```
Button-Modul      →    Raspberry Pi
─────────────────────────────────────
VCC (Rot)         →    Pin 1 (3.3V) ODER Pin 2 (5V)
GND (Schwarz)     →    Pin 14 (GND)
OUT (Gelb/Weiss)  →    Pin 12 (GPIO 18)
```

### Schritt-für-Schritt:

1. **VCC (Rot)** → Pin 1 (3.3V) oder Pin 2 (5V)
   - Pin 1 ist oben links am Raspberry Pi
   - Pin 2 ist oben rechts (neben Pin 1)
   - Beide funktionieren, 5V ist sicherer

2. **GND (Schwarz)** → Pin 14 (GND)
   - Pin 14 ist rechts, 7. Reihe von oben

3. **OUT (Gelb/Weiss)** → Pin 12 (GPIO 18)
   - Pin 12 ist rechts, 6. Reihe von oben

### Funktionsweise:

- **Button losgelassen:** OUT = LOW (0V)
- **Button gedrückt:** OUT = HIGH (3.3V oder 5V)
- Das Modul hat bereits interne Logik, kein externer Widerstand nötig!

### Test:

```bash
python3 -c "import RPi.GPIO as GPIO; import time; GPIO.setmode(GPIO.BCM); GPIO.setup(18, GPIO.IN); print('Button test - drücke den Button:'); [print('Status:', 'GEDRÜCKT' if GPIO.input(18) == 1 else 'LOSGELASSEN') or time.sleep(0.5) for _ in range(10)]"
```

---

## Lautsprecher Anschluss

### Option 1: Direkt an GPIO 25 (PWM)

#### Vorbereitung:

Die JST-PH2.0 Stecker müssen angepasst werden:

**Methode A: Stecker abschneiden**
1. Schneide die JST-PH2.0 Stecker vorsichtig ab
2. Entferne die Isolierung (ca. 5mm)
3. Verbinde die Kabel mit Dupont-Steckern oder direkt an die Pins

**Methode B: Adapter verwenden**
- Kaufe JST-PH2.0 zu Dupont-Kabel Adapter
- Oder: Verwende ein Adapter-Kabel

#### Verbindung:

```
Lautsprecher      →    Raspberry Pi
─────────────────────────────────────
+ (Rot)           →    Pin 22 (GPIO 25)
- (Schwarz)       →    Pin 20 (GND)
```

### Option 2: Über Audio-Jack (EMPFOHLEN)

#### Vorbereitung:

**Methode A: Kabel anpassen**
1. Schneide JST-PH2.0 Stecker ab
2. Verbinde die Kabel mit einem 3.5mm Audio-Stecker:
   - Rot (+) → Spitze des Audio-Steckers
   - Schwarz (-) → Ring/Masse des Audio-Steckers

**Methode B: Adapter-Kabel**
- Verwende ein Kabel: JST-PH2.0 (weiblich) zu 3.5mm Audio-Stecker

#### Verbindung:

```
Lautsprecher      →    Raspberry Pi
─────────────────────────────────────
+ (Rot)           →    Audio-Jack (3.5mm)
- (Schwarz)       →    Audio-Jack (Masse)
```

#### Audio-Jack konfigurieren:

```bash
# Audio-Ausgang auf Audio-Jack setzen
sudo raspi-config
# Navigiere zu: Advanced Options → Audio → Force 3.5mm ('headphone') jack

# Oder per Command:
sudo amixer cset numid=3 1

# Lautstärke testen:
speaker-test -t sine -f 1000 -l 1
```

---

## Komplette Übersicht

### Alle Verbindungen auf einen Blick:

```
Raspberry Pi Pin    →    Komponente
─────────────────────────────────────
Pin 1 (3.3V)        →    Display VCC
Pin 2 (5V)          →    Button-Modul VCC (Alternative)
Pin 6 (GND)         →    Display GND
Pin 12 (GPIO 18)    →    Button-Modul OUT
Pin 14 (GND)        →    Button-Modul GND
Pin 16 (GPIO 23)    →    Display CLK
Pin 18 (GPIO 24)    →    Display DIO
Pin 20 (GND)        →    Lautsprecher - (Option 1)
Pin 22 (GPIO 25)    →    Lautsprecher + (Option 1)
Audio-Jack          →    Lautsprecher (Option 2)
```

---

## Troubleshooting

### Button funktioniert nicht:

1. **Prüfe Verbindungen:**
   ```bash
   # Teste ob VCC Spannung hat:
   python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(18, GPIO.IN); print('GPIO 18 Status:', GPIO.input(18))"
   ```

2. **Prüfe ob Modul mit Strom versorgt ist:**
   - VCC muss an 3.3V oder 5V
   - GND muss an GND

3. **Teste Button direkt:**
   - Drücke Button und prüfe ob OUT HIGH wird

### Lautsprecher funktioniert nicht:

1. **Bei GPIO-Anschluss:**
   ```bash
   # Teste PWM:
   python3 -c "import RPi.GPIO as GPIO; import time; GPIO.setmode(GPIO.BCM); GPIO.setup(25, GPIO.OUT); pwm = GPIO.PWM(25, 1000); pwm.start(50); time.sleep(2); pwm.stop(); print('PWM Test OK')"
   ```

2. **Bei Audio-Jack:**
   ```bash
   # Teste Audio:
   speaker-test -t sine -f 1000 -l 1
   
   # Prüfe Lautstärke:
   alsamixer
   # Mit Pfeiltasten nach oben/unten Lautstärke ändern
   ```

3. **Prüfe Verbindungen:**
   - Rot (+) muss richtig verbunden sein
   - Schwarz (-) muss an GND

---

## Wichtige Hinweise

1. **Button-Modul:**
   - Funktioniert mit 3.3V oder 5V
   - Kein externer Widerstand nötig
   - OUT gibt HIGH wenn gedrückt (umgekehrt zu normalen Buttons!)

2. **Lautsprecher:**
   - 8Ω Impedanz ist OK für GPIO-PWM
   - Audio-Jack gibt bessere Qualität
   - JST-PH2.0 Stecker müssen angepasst werden

3. **Sicherheit:**
   - Immer GND verbinden!
   - Vorsicht mit 5V - nicht auf GPIO-Pins (außer VCC vom Button-Modul)
   - GPIO-Pins sind 3.3V, max. 16mA

---

Viel Erfolg! 🎉

