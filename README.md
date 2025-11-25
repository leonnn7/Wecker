# Raspberry Pi Wecker System

Ein vollstaendiges Wecker-System mit Web-Interface und REST API fuer die Fernsteuerung.

## 📚 Dokumentation

- **[INSTALLATION.md](INSTALLATION.md)** - Komplette Installationsanleitung mit allen Commands
- **[PIN_DIAGRAM.txt](PIN_DIAGRAM.txt)** - Detaillierte Pin-Belegung und Schaltplan
- **[QUICK_START_PINS.md](QUICK_START_PINS.md)** - Schnellstart: Einfache Pin-Verbindungen
- **[BUTTON_LAUTSPRECHER_ANLEITUNG.md](BUTTON_LAUTSPRECHER_ANLEITUNG.md)** - Spezielle Anleitung für Button-Modul und Lautsprecher
- **[RASPBERRY_PI_4_HINWEISE.md](RASPBERRY_PI_4_HINWEISE.md)** - Spezielle Hinweise für Raspberry Pi 4 Model B

## Hardware-Komponenten

- **Display**: 0.36" 4-Bit 7-Segment LED Display mit TM1637 Treiberchip
- **Button**: GPIO-Button fuer lokale Steuerung (Snooze/Dismiss)
- **Sound**: Passive Lautsprecher ueber GPIO/PWM oder Audio-Ausgang
- **Raspberry Pi**: Host fuer Web-Server und Steuerung

## Installation

### 1. Abhaengigkeiten installieren

```bash
pip install -r requirements.txt
```

Optional fuer bessere Sound-Qualitaet:
```bash
pip install pygame numpy
```

### 2. Hardware anschliessen

#### TM1637 Display
- CLK Pin -> GPIO 23
- DIO Pin -> GPIO 24
- VCC -> 5V
- GND -> GND

#### Button
- Ein Pin -> GPIO 18
- Anderer Pin -> GND
- (Interner Pull-up wird verwendet)

#### Sound
- Option 1: Lautsprecher ueber PWM (GPIO 25)
- Option 2: Audio-Jack des Raspberry Pi

### 3. GPIO-Pins anpassen (optional)

Die Pin-Konfiguration kann in `config.py` angepasst werden:

```python
TM1637_CLK_PIN = 23
TM1637_DIO_PIN = 24
BUTTON_PIN = 18
SOUND_PIN = 25
```

## Verwendung

### Server starten

```bash
python app.py
```

Der Server laeuft standardmaessig auf Port 5000 und ist von allen Netzwerk-Interfaces erreichbar.

### Web-Interface

Oeffne im Browser:
```
http://<raspberry-pi-ip>:5000
```

### Oeffentlicher Zugang

#### Option 1: Port-Forwarding im Router
1. Router-Administration oeffnen
2. Port-Forwarding einrichten: Externer Port -> Raspberry Pi IP:5000
3. Von ueberall erreichbar ueber: `http://<deine-oeffentliche-ip>:5000`

#### Option 2: ngrok (temporaer)
```bash
ngrok http 5000
```

#### Option 3: VPN
Verwende ein VPN (z.B. WireGuard) fuer sicheren Zugang.

## API-Endpoints

### GET /api/alarms
Alle Alarme abrufen

**Response:**
```json
{
  "alarms": [
    {
      "id": 1,
      "time": "07:00",
      "days": [0, 1, 2, 3, 4],
      "enabled": true,
      "label": "Aufstehen"
    }
  ],
  "active_alarm": null
}
```

### POST /api/alarms
Neuen Alarm erstellen

**Request:**
```json
{
  "time": "07:00",
  "days": [0, 1, 2, 3, 4],
  "enabled": true,
  "label": "Aufstehen"
}
```

**Response:**
```json
{
  "id": 1,
  "time": "07:00",
  "days": [0, 1, 2, 3, 4],
  "enabled": true,
  "label": "Aufstehen"
}
```

### PUT /api/alarms/<id>
Alarm aktualisieren

### DELETE /api/alarms/<id>
Alarm loeschen

### POST /api/alarms/<id>/snooze
Alarm snoozen (5 Minuten Standard)

**Request:**
```json
{
  "minutes": 5
}
```

### POST /api/alarms/<id>/dismiss
Alarm ausschalten

### GET /api/status
System-Status abrufen

### GET /api/time
Aktuelle Zeit abrufen

## Funktionen

- **Mehrere Alarme**: Bis zu 10 Alarme gleichzeitig
- **Wiederholungen**: Taeglich, woechentlich oder einmalig
- **Snooze**: 5 Minuten Snooze-Funktion
- **Web-Interface**: Modernes, responsives Web-Interface
- **REST API**: Vollstaendige API fuer Webhooks und Remote-Steuerung
- **Button-Steuerung**: Lokaler Button zum Ausschalten des Alarms
- **Display**: Aktuelle Zeit wird auf dem Display angezeigt

## Sicherheit

Fuer oeffentlichen Zugang wird empfohlen:

1. **Basic Authentication** hinzufuegen (in `app.py`)
2. **API-Key** System implementieren
3. **HTTPS** verwenden (z.B. mit nginx reverse proxy)
4. **Firewall** konfigurieren

## Fehlerbehebung

### Hardware wird nicht erkannt
- Pruefe GPIO-Verbindungen
- Stelle sicher, dass RPi.GPIO installiert ist
- Pruefe Berechtigungen (sudo moeglicherweise erforderlich)

### Display zeigt nichts
- Pruefe VCC und GND Verbindungen
- Stelle sicher, dass CLK und DIO richtig verbunden sind
- Pruefe Helligkeit in `config.py`

### Sound funktioniert nicht
- Pruefe Lautsprecher-Verbindungen
- Teste mit `sudo python -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(25, GPIO.OUT); pwm = GPIO.PWM(25, 1000); pwm.start(50)"`

## Lizenz

Freie Verwendung fuer private Projekte.

