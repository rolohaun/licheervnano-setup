#!/bin/sh
# Install Waveshare 4.2" e-Paper driver and demo to /opt/epaper
set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST="/opt/epaper"

mkdir -p "$DEST"
cp "$REPO_DIR/epaper/epdconfig.py"   "$DEST/"
cp "$REPO_DIR/epaper/epd4in2_V2.py" "$DEST/"
cp "$REPO_DIR/epaper/demo.py"        "$DEST/"
chmod +x "$DEST/demo.py"

echo "Installed to $DEST"
echo ""
echo "Wiring (all 3.3V):"
echo "  E-Paper VCC  -> 3V3         (right side, bottom pin)"
echo "  E-Paper GND  -> GND         (left side,  pin 3)"
echo "  E-Paper DIN  -> SPI1_MOSI   (left side,  pin 10  / GPIOA25)"
echo "  E-Paper CLK  -> SPI1_SCK    (left side,  pin 11  / GPIOA22)"
echo "  E-Paper CS   -> SPI1_CS     (left side,  pin 7   / GPIOA24)"
echo "  E-Paper DC   -> GPIOA15     (left side,  pin 4)"
echo "  E-Paper RST  -> GPIOA18     (right side, pin 2)"
echo "  E-Paper BUSY -> GPIOA19     (right side, pin 1)"
echo ""
echo "Run the demo:"
echo "  cd $DEST && python3 demo.py"
