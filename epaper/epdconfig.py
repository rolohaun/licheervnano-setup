"""
LicheeRV Nano hardware abstraction layer for Waveshare e-Paper displays.

Pin wiring (all 3.3V logic):
  E-Paper VCC   -> 3V3  (right side, bottom pin)
  E-Paper GND   -> GND  (left side, pin 3)
  E-Paper DIN   -> SPI1_MOSI / GPIOA25  (left side, pin 10)
  E-Paper CLK   -> SPI1_SCK  / GPIOA22  (left side, pin 11)
  E-Paper CS    -> SPI1_CS   / GPIOA24  (left side, pin 7)
  E-Paper DC    -> GPIOA15              (left side, pin 4)
  E-Paper RST   -> GPIOA18              (right side, pin 2)
  E-Paper BUSY  -> GPIOA19              (right side, pin 1)
"""

import os
import time
import spidev

# SPI bus 1, chip select 0  (/dev/spidev1.0)
SPI_BUS    = 1
SPI_DEVICE = 0

# Linux sysfs GPIO numbers  (GPIOA base = 480)
RST_PIN  = 498   # GPIOA18  (right side, pin 2)
DC_PIN   = 495   # GPIOA15  (left side,  pin 4)
BUSY_PIN = 499   # GPIOA19  (right side, pin 1)
CS_PIN   = -1    # CS managed by spidev hardware (no manual control needed)

_spi      = None
_exported = set()


def _export(pin):
    if pin in _exported:
        return
    gpio_path = f'/sys/class/gpio/gpio{pin}'
    if not os.path.exists(gpio_path):
        with open('/sys/class/gpio/export', 'w') as f:
            f.write(str(pin))
        time.sleep(0.1)
    _exported.add(pin)


def digital_write(pin, value):
    if pin < 0:
        return
    with open(f'/sys/class/gpio/gpio{pin}/value', 'w') as f:
        f.write('1' if value else '0')


def digital_read(pin):
    with open(f'/sys/class/gpio/gpio{pin}/value') as f:
        return int(f.read().strip())


def delay_ms(ms):
    time.sleep(ms / 1000.0)


def spi_writebyte(data):
    _spi.writebytes(data)


def spi_writebyte2(data):
    _spi.writebytes2(data)


def module_init():
    global _spi

    # Output pins: RST, DC
    for pin in (RST_PIN, DC_PIN):
        _export(pin)
        with open(f'/sys/class/gpio/gpio{pin}/direction', 'w') as f:
            f.write('out')
        digital_write(pin, 0)

    # Input pin: BUSY
    _export(BUSY_PIN)
    with open(f'/sys/class/gpio/gpio{BUSY_PIN}/direction', 'w') as f:
        f.write('in')

    # SPI
    _spi = spidev.SpiDev()
    _spi.open(SPI_BUS, SPI_DEVICE)
    _spi.max_speed_hz = 4000000
    _spi.mode = 0

    return 0


def module_exit():
    global _spi
    if _spi:
        _spi.close()
        _spi = None
    digital_write(RST_PIN, 0)
    digital_write(DC_PIN, 0)
