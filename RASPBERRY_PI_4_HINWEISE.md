# Raspberry Pi 4 Model B - Spezielle Hinweise

## Dein Modell: Raspberry Pi 4 Model B

Die Raspberry Pi 4 Model B hat einige Besonderheiten, die wichtig sind:

## Wichtige Unterschiede zur Pi 3

### 1. Stromversorgung
- **Netzteil:** Mindestens **3A** (nicht 2.5A wie bei Pi 3!)
- **Stecker:** **USB-C** (nicht Micro-USB!)
- **Wichtig:** Verwende ein offizielles Pi 4 Netzteil oder ein hochwertiges USB-C Netzteil mit mindestens 3A

### 2. GPIO-Pins
- **Gut:** Die GPIO-Pins sind **identisch** zu anderen Pi-Modellen
- Alle Anleitungen funktionieren ohne Änderungen
- Pin-Belegung ist gleich

### 3. Audio-Ausgabe
- **Audio-Jack:** Funktioniert wie bei anderen Modellen
- **HDMI-Audio:** Pi 4 hat bessere HDMI-Audio-Unterstützung
- **Wichtig:** Stelle sicher, dass Audio-Jack aktiviert ist (nicht HDMI)

### 4. Performance
- **64-bit OS empfohlen:** Pi 4 kann 64-bit OS nutzen
- **Mehr RAM:** Je nach Modell 2GB, 4GB oder 8GB
- **Schneller:** Bessere Performance für Web-Server

## Spezifische Konfiguration für Pi 4

### Audio-Jack aktivieren

```bash
# Audio auf Audio-Jack setzen
sudo raspi-config
# Advanced Options → Audio → Force 3.5mm ('headphone') jack

# Oder per Command:
sudo amixer cset numid=3 1

# Prüfe ob es funktioniert:
aplay -l
```

### GPIO-Test für Pi 4

Alle GPIO-Tests funktionieren identisch:

```bash
# Display CLK testen
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(23, GPIO.OUT); GPIO.output(23, GPIO.HIGH); print('GPIO 23 OK')"

# Display DIO testen
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(24, GPIO.OUT); GPIO.output(24, GPIO.HIGH); print('GPIO 24 OK')"

# Button testen
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(18, GPIO.IN); print('Button:', 'Gedrückt' if GPIO.input(18) == 1 else 'Losgelassen')"

# Sound PWM testen
python3 -c "import RPi.GPIO as GPIO; import time; GPIO.setmode(GPIO.BCM); GPIO.setup(25, GPIO.OUT); pwm = GPIO.PWM(25, 1000); pwm.start(50); time.sleep(1); pwm.stop(); print('GPIO 25 OK')"
```

### Temperatur-Überwachung

Pi 4 kann wärmer werden, überwache die Temperatur:

```bash
# Aktuelle Temperatur anzeigen
vcgencmd measure_temp

# Sollte unter 80°C bleiben
# Falls zu heiß: Kühlkörper oder Lüfter verwenden
```

### Netzwerk-Performance

Pi 4 hat besseres WLAN und Ethernet:

```bash
# IP-Adresse anzeigen
hostname -I

# Netzwerk-Geschwindigkeit testen (optional)
speedtest-cli
```

## Wichtige Hinweise für Pi 4

1. **Netzteil:** Verwende mindestens 3A USB-C Netzteil
2. **Kühlung:** Pi 4 kann wärmer werden - Kühlkörper empfohlen
3. **64-bit OS:** Verwende 64-bit Raspberry Pi OS für beste Performance
4. **GPIO:** Funktioniert identisch zu anderen Pi-Modellen
5. **Audio:** Audio-Jack muss aktiviert werden (nicht automatisch)

## Troubleshooting speziell für Pi 4

### Problem: Pi startet nicht oder stürzt ab

**Lösung:**
- Prüfe Netzteil (muss mindestens 3A haben)
- Verwende hochwertiges USB-C Kabel
- Prüfe SD-Karte (sollte Class 10 oder besser sein)

### Problem: Audio funktioniert nicht

**Lösung:**
```bash
# Audio-Jack explizit aktivieren
sudo raspi-config
# Advanced Options → Audio → Force 3.5mm jack

# Prüfe Audio-Geräte
aplay -l

# Teste Audio
speaker-test -t sine -f 1000 -l 1
```

### Problem: GPIO funktioniert nicht

**Lösung:**
- GPIO-Pins sind identisch zu anderen Modellen
- Prüfe Verbindungen nochmal
- Stelle sicher, dass RPi.GPIO installiert ist:
  ```bash
  sudo apt install python3-rpi.gpio -y
  ```

### Problem: Pi wird zu heiß

**Lösung:**
```bash
# Temperatur prüfen
vcgencmd measure_temp

# Falls über 70°C:
# - Kühlkörper aufsetzen
# - Lüfter verwenden
# - Pi in gut belüftetem Gehäuse
```

## Performance-Tipps für Pi 4

1. **64-bit OS verwenden** - bessere Performance
2. **SSD statt SD-Karte** - optional, aber schneller
3. **Adequate Kühlung** - für beste Performance
4. **Genug RAM** - Pi 4 hat 2GB, 4GB oder 8GB (je nach Modell)

## Zusammenfassung

✅ **GPIO-Pins:** Identisch zu anderen Pi-Modellen - alle Anleitungen funktionieren  
✅ **Audio:** Audio-Jack muss aktiviert werden  
✅ **Netzteil:** Mindestens 3A USB-C Netzteil verwenden  
✅ **OS:** 64-bit Raspberry Pi OS empfohlen  
✅ **Performance:** Pi 4 ist schneller - Web-Server läuft flüssig  

Viel Erfolg mit deinem Raspberry Pi 4 Model B! 🎉

