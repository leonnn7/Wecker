# Raspberry Pi Wecker - Komplette Installationsanleitung

**Für: Raspberry Pi 4 Model B**

## ⚡ Schnellstart - Wichtige Commands

### Status prüfen - Läuft der Wecker?
```bash
# Option 1: Wenn als systemd Service installiert:
sudo systemctl status wecker

# Option 2: Prozess prüfen (funktioniert immer):
ps aux | grep app.py | grep -v grep

# Option 3: Port prüfen (Port 5000):
sudo netstat -tlnp | grep 5000
# Oder mit ss (moderner):
sudo ss -tlnp | grep 5000

# Option 4: Kurz-Check ob Port offen ist:
curl -s http://localhost:5000/api/time > /dev/null && echo "Wecker läuft!" || echo "Wecker läuft nicht!"

# Option 5: Logs anzeigen (wenn als Service):
sudo journalctl -u wecker -f  # Live-Logs
sudo journalctl -u wecker -n 50  # Letzte 50 Zeilen
```

### Server neu starten
```bash
# Wenn als systemd Service installiert:
sudo systemctl restart wecker

# Oder manuell (wenn im Terminal gestartet):
# Strg+C zum Stoppen, dann:
cd ~/Wecker
source venv/bin/activate  # Falls Virtual Environment verwendet wird
python3 app.py
```

### Software aktualisieren (neueste Version von GitHub holen)
```bash
cd ~/Wecker

# Änderungen speichern (falls eigene Änderungen vorhanden):
# git stash  # Optional: Eigene Änderungen temporär speichern

# Neueste Version von GitHub holen:
git pull origin main

# Falls Konflikte auftreten:
# git reset --hard origin/main  # ACHTUNG: Überschreibt lokale Änderungen!

# Abhängigkeiten aktualisieren (falls requirements.txt geändert wurde):
source venv/bin/activate  # Falls Virtual Environment verwendet wird
pip install -r requirements.txt --upgrade

# Server neu starten:
sudo systemctl restart wecker  # Falls als Service installiert
# Oder manuell neu starten
```

### GitHub Repository URL
```
https://github.com/leonnn7/Wecker
```

### Erste Installation vom GitHub Repository
```bash
# Repository klonen:
cd ~
git clone https://github.com/leonnn7/Wecker.git
cd Wecker

# Virtual Environment erstellen (empfohlen):
python3 -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren:
pip install -r requirements.txt
```

---

## Inhaltsverzeichnis
1. [Hardware-Vorbereitung](#hardware-vorbereitung)
2. [Raspberry Pi Setup](#raspberry-pi-setup)
3. [Software-Installation](#software-installation)
4. [Pin-Verbindungen](#pin-verbindungen)
5. [Konfiguration](#konfiguration)
6. [Erste Schritte](#erste-schritte)
7. [Fehlerbehebung](#fehlerbehebung)

> **Hinweis:** Diese Anleitung ist speziell für Raspberry Pi 4 Model B optimiert und enthält alle notwendigen Informationen.

---

## Hardware-Vorbereitung

### Benötigte Hardware:
- **Raspberry Pi 4 Model B** (dein Modell)
- MicroSD-Karte (mindestens 16GB, Class 10, empfohlen: 32GB+)
- **Netzteil für Raspberry Pi 4** (5V, **mindestens 3A** - wichtig für Pi 4!)
- USB-C Kabel (für Pi 4)
- **TM1637 4-Bit 7-Segment Display** (0.36" rot)
- **Button/Schalter** (momentaner Taster)
- **Lautsprecher** (passive Lautsprecher mit Kabeln)
- Jumper-Kabel (mindestens 6 Stück)
- Optional: Breadboard für einfachere Verbindungen

---

## Raspberry Pi Setup

### 1. Raspberry Pi OS installieren

#### Option A: Raspberry Pi Imager (Empfohlen)
1. Lade den **Raspberry Pi Imager** herunter: https://www.raspberrypi.com/software/
2. Installiere und öffne den Imager
3. Wähle **"Raspberry Pi OS (64-bit)"** - empfohlen für Pi 4!
4. Klicke auf das Zahnrad-Symbol für erweiterte Optionen:
   - Aktiviere SSH
   - Setze Benutzername und Passwort
   - Konfiguriere WLAN (optional)
   - **Wichtig für Pi 4:** Aktiviere "Enable 64-bit OS" falls verfügbar
5. Schreibe das Image auf die SD-Karte

#### Option B: Manuelle Installation
```bash
# Auf einem Linux/Mac System:
# 1. Image herunterladen von https://www.raspberrypi.com/software/operating-systems/
# 2. Image auf SD-Karte schreiben:
sudo dd if=raspios-image.img of=/dev/sdX bs=4M status=progress
# Ersetze /dev/sdX mit deinem SD-Karten-Gerät
```

### 2. Erste Inbetriebnahme

#### Mit Monitor und Tastatur:
1. Stecke die SD-Karte in den Raspberry Pi
2. Verbinde Monitor, Tastatur, Maus
3. Schalte den Raspberry Pi ein
4. Folge dem Setup-Assistenten

#### Headless (ohne Monitor):
1. Erstelle nach dem Schreiben eine leere Datei namens `ssh` im Boot-Verzeichnis der SD-Karte
2. Falls WLAN konfiguriert: Raspberry Pi einschalten und warten
3. Finde die IP-Adresse:
   ```bash
   # Auf deinem Computer:
   ping raspberrypi.local
   # Oder im Router nachsehen
   ```
4. Verbinde per SSH:
   ```bash
   ssh pi@<raspberry-pi-ip>
   # Oder mit deinem konfigurierten Benutzernamen:
   ssh <benutzername>@<raspberry-pi-ip>
   ```

### 3. System aktualisieren

```bash
# System aktualisieren
sudo apt update
sudo apt upgrade -y

# System neu starten (falls Kernel-Updates installiert wurden)
sudo reboot
```

---

## Software-Installation

### 1. Python und pip installieren

```bash
# Python 3 sollte bereits installiert sein, aber sicherstellen:
python3 --version

# pip installieren/aktualisieren
sudo apt install python3-pip -y

# pip aktualisieren
python3 -m pip install --upgrade pip
```

### 2. System-Pakete installieren

```bash
# GPIO-Bibliothek und Audio-Tools
sudo apt install -y \
    python3-dev \
    python3-rpi.gpio \
    python3-pygame \
    python3-numpy \
    alsa-utils \
    portaudio19-dev \
    python3-pyaudio

# Git für Code-Download (falls nicht installiert)
sudo apt install git -y
```

### 3. Projekt-Dateien übertragen

#### Option A: Via Git (wenn Repository vorhanden)
```bash
cd ~
git clone <dein-repository-url>
cd Wecker
```

#### Option B: Via SCP (vom Computer)
```bash
# Auf deinem Computer:
scp -r Wecker/ pi@<raspberry-pi-ip>:~/
```

#### Option C: Via USB-Stick
1. Kopiere den Wecker-Ordner auf einen USB-Stick
2. Stecke den USB-Stick in den Raspberry Pi
3. Kopiere die Dateien:
   ```bash
   mkdir -p ~/Wecker
   cp /media/usb/Wecker/* ~/Wecker/
   cd ~/Wecker
   ```

### 4. Python-Abhängigkeiten installieren

```bash
cd ~/Wecker

# Virtuelle Umgebung erstellen (empfohlen)
python3 -m venv venv

# Virtuelle Umgebung aktivieren
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Falls Fehler bei RPi.GPIO auftreten:
pip install RPi.GPIO --upgrade
```

### 5. Verzeichnisse erstellen

```bash
# Sounds-Verzeichnis erstellen
mkdir -p sounds

# Berechtigungen setzen
chmod 755 sounds
```

### 6. Datenbank (wird automatisch erstellt)

**Wichtig:** Die SQLite-Datenbank wird automatisch beim ersten Start erstellt!

```bash
# Die Datenbank wird automatisch erstellt wenn du app.py startest
# Keine manuelle Einrichtung nötig!

# Datenbank-Datei: wecker.db (wird im Projekt-Verzeichnis erstellt)
# Enthält: Users, Alarms, Settings, Sounds, Sessions
```

**Standard-Admin-Account:**
- **Benutzername:** `admin`
- **Passwort:** `admin`
- **WICHTIG:** Ändere das Passwort sofort nach dem ersten Login!

Falls die Datenbank neu erstellt werden muss:
```bash
cd ~/Wecker
rm wecker.db  # Alte Datenbank löschen
python3 -c "from database import init_database; init_database()"
```

---

## Pin-Verbindungen

### Übersicht der GPIO-Pins

```
       3.3V  [1]  [2]  5V
     GPIO2  [3]  [4]  5V
     GPIO3  [5]  [6]  GND
     GPIO4  [7]  [8]  GPIO14
       GND  [9]  [10] GPIO15
    GPIO17 [11]  [12] GPIO18  ← BUTTON
    GPIO27 [13]  [14] GND
    GPIO22 [15]  [16] GPIO23  ← TM1637 CLK
       3.3V [17]  [18] GPIO24  ← TM1637 DIO
    GPIO10 [19]  [20] GND
     GPIO9 [21]  [22] GPIO25  ← SOUND (PWM)
    GPIO11 [23]  [24] GPIO8
       GND [25]  [26] GPIO7
```

### Detaillierte Verbindungen

#### TM1637 Display (4-Pin Modul)

```
TM1637 Modul          Raspberry Pi
─────────────────────────────────
VCC (Rot)      →      Pin 1 (3.3V) oder Pin 2 (5V)
GND (Schwarz)  →      Pin 6 (GND)
DIO (Gelb)     →      Pin 18 (GPIO 24)
CLK (Grün)     →      Pin 16 (GPIO 23)
```

**Wichtig:** 
- Das Display kann mit 3.3V oder 5V betrieben werden
- Wenn das Display nicht richtig funktioniert, versuche 5V (Pin 2) statt 3.3V

#### Button-Modul (3-Pin Modul mit High Level Output)

```
Button-Modul          Raspberry Pi
─────────────────────────────────
V (VCC, Rot)          →      Pin 1 (3.3V) oder Pin 2 (5V)
G (GND, Schwarz)      →      Pin 14 (GND)
S (Signal, Gelb)      →      Pin 12 (GPIO 18)
```

**Pin-Beschriftung am Modul:**
- **V** = VCC (Versorgungsspannung)
- **G** = GND (Ground/Masse)
- **S** = Signal/OUT (Ausgang)

**Wichtig:**
- Das Modul hat bereits interne Logik und Pull-up Widerstand
- S (Signal) gibt HIGH (3.3V/5V) aus wenn Button gedrückt
- S (Signal) gibt LOW (0V) aus wenn Button losgelassen
- Das Modul funktioniert mit 3.3V oder 5V
- Kein externer Widerstand nötig!

#### Lautsprecher (Mini 3W 8Ω mit JST-PH2.0 Stecker)

**Option 1: Direkt über GPIO 25 (PWM)**

```
Lautsprecher          Raspberry Pi
─────────────────────────────────
+ (Rot)               →      Pin 22 (GPIO 25)
- (Schwarz)           →      Pin 20 (GND)
```

**Wichtig für Option 1:**
- Die JST-PH2.0 Stecker müssen abgeschnitten werden
- Oder: Verwende Adapter-Kabel (JST-PH2.0 zu Dupont)
- Der 8Ω Lautsprecher kann direkt an GPIO 25 (PWM) angeschlossen werden
- Für bessere Qualität: Audio-Jack verwenden!

**Option 2: Über Audio-Jack (Empfohlen für bessere Sound-Qualität)**

```
Lautsprecher          Raspberry Pi
─────────────────────────────────
+ (Rot)               →      Audio-Jack (Spitze)
- (Schwarz)           →      Audio-Jack (Ring/Masse)
```

**Hinweis für Option 2:**
- JST-PH2.0 Stecker müssen an Audio-Kabel angepasst werden
- Oder: Verwende ein Audio-Kabel mit 3.5mm Stecker
- Bessere Sound-Qualität als GPIO-PWM

### Komplette Pin-Belegung Tabelle

| Komponente | Pin Name | GPIO | Physischer Pin | Farbe (falls vorhanden) |
|------------|----------|------|----------------|-------------------------|
| TM1637 VCC | 3.3V/5V | - | Pin 1 oder 2 | Rot |
| TM1637 GND | GND | - | Pin 6 | Schwarz |
| TM1637 DIO | GPIO 24 | 24 | Pin 18 | Gelb |
| TM1637 CLK | GPIO 23 | 23 | Pin 16 | Grün |
| Button V (VCC) | 3.3V/5V | - | Pin 1 oder 2 | Rot |
| Button G (GND) | GND | - | Pin 14 | Schwarz |
| Button S (Signal) | GPIO 18 | 18 | Pin 12 | Gelb/Weiss |
| Sound (PWM) | GPIO 25 | 25 | Pin 22 | Rot |
| Sound GND | GND | - | Pin 20 | Schwarz |

### Visuelle Darstellung (von oben gesehen)

```
        [Display]          [Button-Modul]
           │                  │
    VCC ───┘                  │
    GND ───┘                  │
    DIO ───┘ (Pin 18)        │
    CLK ───┘ (Pin 16)        │
                             │
                    V (VCC) ──────┘ (Pin 1 oder 2)
                    G (GND) ──────┘ (Pin 14)
                    S (Signal) ──────┘ (Pin 12 - GPIO 18)

    [Lautsprecher]
         │
    GPIO 25 ───┘ (Pin 22)
    GND ────────┘ (Pin 20)
```

---

## Raspberry Pi 4 Model B - Wichtige Hinweise

### Stromversorgung
- **Netzteil:** Mindestens **3A** (nicht 2.5A!)
- **Stecker:** **USB-C** (nicht Micro-USB!)
- Verwende ein offizielles Pi 4 Netzteil oder hochwertiges USB-C Netzteil

### GPIO-Pins
- ✅ Die GPIO-Pins sind **identisch** zu anderen Pi-Modellen
- Alle Anleitungen funktionieren ohne Änderungen
- Pin-Belegung ist gleich

### Audio-Ausgabe (Pi 4)
- Audio-Jack muss aktiviert werden (nicht automatisch)
- Pi 4 hat bessere HDMI-Audio-Unterstützung
- Stelle sicher, dass Audio-Jack aktiviert ist

### Performance
- **64-bit OS empfohlen** für Pi 4
- Pi 4 ist schnell genug für den Web-Server
- Temperatur überwachen: `vcgencmd measure_temp` (sollte unter 80°C bleiben)

---

## Konfiguration

### 1. GPIO-Pins anpassen (falls nötig)

```bash
nano ~/Wecker/config.py
```

Bearbeite die Pin-Nummern falls du andere Pins verwendest:
```python
TM1637_CLK_PIN = 23  # Clock pin
TM1637_DIO_PIN = 24  # Data pin
BUTTON_PIN = 18      # Button pin
SOUND_PIN = 25       # Sound pin (PWM) oder None für Audio-Jack
```

### 2. Audio-Konfiguration (für Audio-Jack) - Raspberry Pi 4

```bash
# Audio-Ausgang auf Audio-Jack setzen (Pi 4)
sudo raspi-config
# Navigiere zu: Advanced Options → Audio → Force 3.5mm ('headphone') jack

# Oder per Command:
sudo amixer cset numid=3 1

# Für Raspberry Pi 4 - prüfe Audio-Geräte:
aplay -l

# Teste Audio:
speaker-test -t sine -f 1000 -l 1 -c 2

# Lautstärke einstellen:
alsamixer
# Mit Pfeiltasten nach oben/unten Lautstärke ändern
# ESC zum Beenden
```

### 3. Button-Modul Pin-Beschriftung (S, V, G)

Dein Button-Modul hat folgende Beschriftung:
- **V** = VCC (Versorgungsspannung) → Pin 1 oder Pin 2
- **G** = GND (Ground/Masse) → Pin 14
- **S** = Signal/OUT (Ausgang) → Pin 12 (GPIO 18)

**Funktionsweise:**
- Button losgelassen: S = LOW (0V)
- Button gedrückt: S = HIGH (3.3V oder 5V)
- Modul hat bereits interne Logik, kein externer Widerstand nötig!

**Test:**
```bash
python3 -c "import RPi.GPIO as GPIO; import time; GPIO.setmode(GPIO.BCM); GPIO.setup(18, GPIO.IN); print('Button Test - drücke den Button:'); [print('Status:', 'GEDRÜCKT' if GPIO.input(18) == 1 else 'LOSGELASSEN') or time.sleep(0.5) for _ in range(10)]"
```

### 4. Berechtigungen für GPIO

```bash
# Benutzer zur gpio-Gruppe hinzufügen (falls nötig)
sudo usermod -a -G gpio $USER

# Ausloggen und wieder einloggen, damit Änderungen wirksam werden
```

---

## Schnellstart: Pin-Verbindungen im Überblick

### TM1637 Display (4 Kabel)
```
VCC (Rot)        →    Pin 1 (3.3V) - oben links
GND (Schwarz)    →    Pin 6 (GND) - links, 3. Reihe
DIO (Gelb)       →    Pin 18 (GPIO 24) - rechts, 9. Reihe
CLK (Grün)       →    Pin 16 (GPIO 23) - rechts, 8. Reihe
```

### Button-Modul (S, V, G)
```
V (VCC, Rot)      →    Pin 1 (3.3V) oder Pin 2 (5V)
G (GND, Schwarz)  →    Pin 14 (GND) - rechts, 7. Reihe
S (Signal, Gelb)  →    Pin 12 (GPIO 18) - rechts, 6. Reihe
```

### Lautsprecher
**Option 1 (GPIO):** Pin 22 (GPIO 25) + Pin 20 (GND)  
**Option 2 (Audio-Jack):** Audio-Jack des Raspberry Pi (empfohlen)

### Pin 1 finden:
- Schaue auf den Raspberry Pi von oben
- GPIO-Header ist oben
- Pin 1 ist **oben links** (neben dem "3.3V" Label)

### Test-Commands nach dem Anschließen:
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

---

## Erste Schritte

### 1. Server starten

```bash
cd ~/Wecker
source venv/bin/activate  # Falls virtuelle Umgebung verwendet wird

# Server starten
python3 app.py
```

Du solltest folgende Ausgabe sehen:
```
Starting Wecker server on 0.0.0.0:5000
Web interface: http://localhost:5000/
Default admin: username='admin', password='admin'
WARNING: Change default password!
 * Running on http://0.0.0.0:5000
```

### 2. Web-Interface öffnen

#### Lokal auf dem Raspberry Pi:
```bash
# Öffne Browser und gehe zu:
http://localhost:5000
```

#### Von einem anderen Gerät im Netzwerk:
```bash
# Finde die IP-Adresse des Raspberry Pi:
hostname -I

# Öffne im Browser (vom Computer/Handy):
http://<raspberry-pi-ip>:5000
# Beispiel: http://192.168.1.100:5000
```

### 3. Erste Anmeldung

- **Benutzername:** `admin`
- **Passwort:** `admin`
- **WICHTIG:** Ändere das Passwort sofort nach dem ersten Login!

**Datenbank:**
- Die SQLite-Datenbank (`wecker.db`) wird automatisch beim ersten Start erstellt
- Keine manuelle Einrichtung nötig!
- Enthält: Users, Alarms, Settings, Sounds, Sessions

### 4. Server im Hintergrund laufen lassen

#### Option A: screen (Einfach)
```bash
# Screen installieren
sudo apt install screen -y

# Screen-Session starten
screen -S wecker

# Server starten
cd ~/Wecker
source venv/bin/activate
python3 app.py

# Screen verlassen: Strg+A, dann D
# Screen wieder verbinden:
screen -r wecker
```

#### Option B: systemd Service (Professionell)

**WICHTIG:** Passe die Pfade an deinen Benutzer an!

1. Finde deinen Benutzernamen und den richtigen Pfad:
```bash
# Benutzername herausfinden:
whoami

# Aktuelles Verzeichnis prüfen:
pwd

# Beispiel-Ausgabe: /home/admin/Wecker
```

2. Erstelle den Service:
```bash
sudo nano /etc/systemd/system/wecker.service
```

3. Füge folgendes ein (ersetze `admin` mit deinem Benutzernamen!):
```ini
[Unit]
Description=Raspberry Pi Wecker Service
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/Wecker
Environment="PATH=/home/admin/Wecker/venv/bin"
ExecStart=/home/admin/Wecker/venv/bin/python3 /home/admin/Wecker/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**WICHTIG:** Ersetze `admin` mit deinem tatsächlichen Benutzernamen (z.B. `pi`, `admin`, etc.)!

4. Service aktivieren:
```bash
# Service-Datei neu laden
sudo systemctl daemon-reload

# Service aktivieren
sudo systemctl enable wecker.service

# Service starten
sudo systemctl start wecker.service

# Status prüfen
sudo systemctl status wecker.service

# Logs ansehen
sudo journalctl -u wecker.service -f
```

**Service korrigieren (falls Pfad falsch):**
```bash
# 1. Service stoppen
sudo systemctl stop wecker.service

# 2. Service-Datei bearbeiten
sudo nano /etc/systemd/system/wecker.service

# 3. Prüfe ALLE Pfade - sie müssen konsistent sein!
#    Beispiel für Benutzer "admin":
#    User=admin
#    WorkingDirectory=/home/admin/Wecker
#    ExecStart=/home/admin/Wecker/venv/bin/python3 /home/admin/Wecker/app.py
#    Environment="PATH=/home/admin/Wecker/venv/bin"
#
#    WICHTIG: Alle Pfade müssen den gleichen Benutzer haben!
#    NICHT mischen: /home/admin/... und /home/pi/...

# 4. Service neu laden
sudo systemctl daemon-reload

# 5. Service starten
sudo systemctl start wecker.service

# 6. Status prüfen
sudo systemctl status wecker.service

# 7. Falls Fehler: Logs prüfen
sudo journalctl -u wecker.service -n 50
```

---

## Fehlerbehebung

### Problem: "Permission denied" bei GPIO

**Lösung:**
```bash
sudo usermod -a -G gpio $USER
# Ausloggen und wieder einloggen
```

### Problem: Display zeigt nichts

**Lösung:**
1. Prüfe alle Verbindungen
2. Versuche 5V statt 3.3V für VCC
3. Prüfe ob Pins richtig verbunden sind:
   ```bash
   # Test-Script erstellen:
   python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(23, GPIO.OUT); GPIO.output(23, GPIO.HIGH); print('GPIO 23 OK')"
   ```

### Problem: Button funktioniert nicht

**Lösung:**
1. Prüfe Verbindung zwischen Button und GPIO 18 + GND
2. Teste Button mit Multimeter
3. Prüfe ob Pull-up aktiviert ist (sollte automatisch sein)

### Problem: Kein Sound

**Lösung:**
1. **Bei PWM (GPIO 25):**
   ```bash
   # Teste PWM:
   python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(25, GPIO.OUT); pwm = GPIO.PWM(25, 1000); pwm.start(50); import time; time.sleep(2); pwm.stop()"
   ```

2. **Bei Audio-Jack (Raspberry Pi 4):**
   ```bash
   # Prüfe Audio-Geräte:
   aplay -l
   
   # Audio testen:
   speaker-test -t sine -f 1000 -l 1 -c 2
   
   # Lautstärke prüfen und einstellen:
   alsamixer
   # Mit Pfeiltasten Lautstärke erhöhen
   # 'M' für Mute/Unmute
   
   # Falls Audio-Jack nicht funktioniert, prüfe ob HDMI-Audio aktiv ist:
   # Deaktiviere HDMI-Audio falls nötig:
   sudo raspi-config
   # Advanced Options → Audio → Force 3.5mm jack
   ```

### Problem: "Module not found: RPi.GPIO"

**Lösung:**
```bash
sudo apt install python3-rpi.gpio -y
# Oder:
pip3 install RPi.GPIO
```

### Problem: Server startet nicht

**Lösung:**
```bash
# Prüfe ob Port 5000 bereits belegt ist:
sudo netstat -tulpn | grep 5000

# Falls belegt, ändere Port in config.py:
nano ~/Wecker/config.py
# Ändere: WEB_PORT = 5000 zu WEB_PORT = 8080
```

### Problem: Kann nicht von außen zugreifen

**Lösung:**
1. Prüfe Firewall:
   ```bash
   sudo ufw allow 5000
   sudo ufw status
   ```

2. Prüfe ob Server auf 0.0.0.0 läuft:
   ```bash
   # In config.py sollte stehen:
   WEB_HOST = '0.0.0.0'  # Nicht '127.0.0.1' oder 'localhost'!
   ```

3. Prüfe ob Server läuft:
   ```bash
   sudo netstat -tulpn | grep 5000
   # Sollte zeigen: 0.0.0.0:5000
   ```

4. Für externen Zugang (von überall):

   **Empfehlung: Cloudflare Tunnel (Kostenlos & Sicher)**
   
   Dies ist die beste Methode, um deinen Wecker sicher ins Internet zu bringen, ohne Ports am Router zu öffnen.
   
   1. Erstelle einen Account bei [Cloudflare](https://www.cloudflare.com/)
   2. Installiere `cloudflared` auf dem Raspberry Pi:
      ```bash
      # Add Cloudflare GPG key
      sudo mkdir -p --mode=0755 /usr/share/keyrings
      curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
      
      # Add repo
      echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared bookworm main' | sudo tee /etc/apt/sources.list.d/cloudflared.list
      
      # Install
      sudo apt-get update && sudo apt-get install cloudflared
      ```
   3. Starte den Tunnel (Quick Setup ohne Domain):
      ```bash
      cloudflared tunnel --url http://localhost:5000
      ```
      -> Kopiere die URL, die angezeigt wird (z.B. `https://random-name.trycloudflare.com`).
      
   **Alternative: Port-Forwarding (Nur für Fortgeschrittene)**
   - Port 5000 im Router an die IP des Raspberry Pi weiterleiten.
   - Achtung: Unsicher ohne HTTPS!
   
   **Alternative: ngrok (Schnelltest)**
   ```bash
   # ngrok installieren und starten
   ngrok http 5000
   ```

5. Prüfe Router-Einstellungen:
   - Falls Port-Forwarding genutzt wird: Ist Port 5000 offen?

### Problem: Datenbank-Fehler

**Lösung:**
```bash
# Datenbank neu erstellen:
cd ~/Wecker
rm wecker.db
python3 -c "from database import init_database; init_database()"
```

**Hinweis:** Die Datenbank wird automatisch beim ersten Start von `app.py` erstellt. Falls Probleme auftreten, kann sie manuell neu erstellt werden.

### Problem: Raspberry Pi 4 wird zu heiß

**Lösung:**
```bash
# Temperatur prüfen
vcgencmd measure_temp

# Falls über 70°C:
# - Kühlkörper aufsetzen
# - Lüfter verwenden
# - Pi in gut belüftetem Gehäuse
```

### Problem: Button-Modul funktioniert nicht

**Lösung:**
1. Prüfe Verbindungen:
   - **V (VCC)** muss an Pin 1 oder Pin 2
   - **G (GND)** muss an Pin 14
   - **S (Signal)** muss an Pin 12 (GPIO 18)

2. Teste Button:
   ```bash
   python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(18, GPIO.IN); print('Button Status:', 'Gedrückt' if GPIO.input(18) == 1 else 'Losgelassen')"
   ```

3. Prüfe ob Modul mit Strom versorgt ist (V an 3.3V oder 5V)

---

## Nützliche Commands

### Server stoppen
```bash
# Im Terminal: Strg+C
# Oder wenn als Service:
sudo systemctl stop wecker.service
```

### Logs ansehen
```bash
# Wenn als Service:
sudo journalctl -u wecker.service -f

# Oder direkt:
tail -f ~/Wecker/app.log  # Falls Logging aktiviert
```

### IP-Adresse herausfinden
```bash
hostname -I
```

### System-Status prüfen
```bash
# CPU-Temperatur
vcgencmd measure_temp

# Speicher
free -h

# Festplatte
df -h
```

---

## Sicherheitshinweise

1. **Passwort ändern:** Ändere das Standard-Admin-Passwort sofort!
2. **Firewall:** Aktiviere eine Firewall für externen Zugang
3. **HTTPS:** Für Produktion HTTPS einrichten (z.B. mit nginx + Let's Encrypt)
4. **Updates:** Regelmäßig System-Updates durchführen:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## Support

Bei Problemen:
1. Prüfe die Fehlerbehebung oben
2. Prüfe die Logs: `sudo journalctl -u wecker.service -n 50`
3. Prüfe GPIO-Verbindungen mit Multimeter
4. Teste Komponenten einzeln

---

**Viel Erfolg mit deinem Raspberry Pi Wecker! 🎉**

