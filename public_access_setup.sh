#!/bin/bash
# Script zum Einrichten des öffentlichen Zugriffs

echo "=== Raspberry Pi Wecker - Öffentlicher Zugriff Setup ==="
echo ""

# 1. Firewall konfigurieren
echo "1. Firewall konfigurieren..."
sudo ufw allow 5000/tcp
echo "   Port 5000 für HTTP freigegeben"
echo ""

# 2. IP-Adresse anzeigen
echo "2. Netzwerk-Informationen:"
echo "   Lokale IP-Adresse:"
hostname -I | awk '{print "   " $1}'
echo ""
echo "   Öffentliche IP-Adresse (falls verfügbar):"
curl -s ifconfig.me 2>/dev/null || echo "   Nicht verfügbar (hinter Router)"
echo ""

# 3. ngrok Setup (optional)
echo "3. ngrok Setup (für temporären öffentlichen Zugriff):"
echo "   Installiere ngrok:"
echo "   wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz"
echo "   tar xvzf ngrok-v3-stable-linux-arm64.tgz"
echo "   sudo mv ngrok /usr/local/bin/"
echo ""
echo "   Starte ngrok:"
echo "   ngrok http 5000"
echo ""

# 4. Port-Forwarding Hinweis
echo "4. Port-Forwarding im Router einrichten:"
echo "   - Öffne Router-Administration (meist 192.168.1.1 oder 192.168.0.1)"
echo "   - Gehe zu Port-Forwarding / Virtual Server"
echo "   - Erstelle neue Regel:"
echo "     * Externer Port: 5000 (oder anderer Port)"
echo "     * Interner Port: 5000"
echo "     * IP-Adresse: $(hostname -I | awk '{print $1}')"
echo "     * Protokoll: TCP"
echo ""

echo "=== Setup abgeschlossen ==="

