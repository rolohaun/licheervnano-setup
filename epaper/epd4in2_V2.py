"""
Waveshare 4.2inch e-Paper Module (Rev 2.1) driver.
Adapted from Waveshare's official epd4in2_V2.py for LicheeRV Nano
(spidev + sysfs GPIO instead of RPi.GPIO).
"""

import epdconfig
from PIL import Image

EPD_WIDTH  = 400
EPD_HEIGHT = 300

GRAY1 = 0xFF   # white
GRAY2 = 0xC0
GRAY3 = 0x80   # gray
GRAY4 = 0x00   # black


class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin    = epdconfig.DC_PIN
        self.busy_pin  = epdconfig.BUSY_PIN
        self.cs_pin    = epdconfig.CS_PIN
        self.width     = EPD_WIDTH
        self.height    = EPD_HEIGHT
        self.Seconds_1_5S = 0
        self.Seconds_1S   = 1
        self.GRAY1 = GRAY1
        self.GRAY2 = GRAY2
        self.GRAY3 = GRAY3
        self.GRAY4 = GRAY4

    LUT_ALL = [
        0x01, 0x0A, 0x1B, 0x0F, 0x03, 0x01, 0x01,
        0x05, 0x0A, 0x01, 0x0A, 0x01, 0x01, 0x01,
        0x05, 0x08, 0x03, 0x02, 0x04, 0x01, 0x01,
        0x01, 0x04, 0x04, 0x02, 0x00, 0x01, 0x01,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,
        0x01, 0x0A, 0x1B, 0x0F, 0x03, 0x01, 0x01,
        0x05, 0x4A, 0x01, 0x8A, 0x01, 0x01, 0x01,
        0x05, 0x48, 0x03, 0x82, 0x84, 0x01, 0x01,
        0x01, 0x84, 0x84, 0x82, 0x00, 0x01, 0x01,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,
        0x01, 0x0A, 0x1B, 0x8F, 0x03, 0x01, 0x01,
        0x05, 0x4A, 0x01, 0x8A, 0x01, 0x01, 0x01,
        0x05, 0x48, 0x83, 0x82, 0x04, 0x01, 0x01,
        0x01, 0x04, 0x04, 0x02, 0x00, 0x01, 0x01,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,
        0x01, 0x8A, 0x1B, 0x8F, 0x03, 0x01, 0x01,
        0x05, 0x4A, 0x01, 0x8A, 0x01, 0x01, 0x01,
        0x05, 0x48, 0x83, 0x02, 0x04, 0x01, 0x01,
        0x01, 0x04, 0x04, 0x02, 0x00, 0x01, 0x01,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,
        0x01, 0x8A, 0x9B, 0x8F, 0x03, 0x01, 0x01,
        0x05, 0x4A, 0x01, 0x8A, 0x01, 0x01, 0x01,
        0x05, 0x48, 0x03, 0x42, 0x04, 0x01, 0x01,
        0x01, 0x04, 0x04, 0x42, 0x00, 0x01, 0x01,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x02, 0x00, 0x00, 0x07, 0x17, 0x41, 0xA8,
        0x32, 0x30,
    ]

    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(100)
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(2)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(100)

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data2(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte2(data)
        epdconfig.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        while epdconfig.digital_read(self.busy_pin) == 1:
            epdconfig.delay_ms(20)

    def TurnOnDisplay(self):
        self.send_command(0x22)
        self.send_data(0xF7)
        self.send_command(0x20)
        self.ReadBusy()

    def TurnOnDisplay_Fast(self):
        self.send_command(0x22)
        self.send_data(0xC7)
        self.send_command(0x20)
        self.ReadBusy()

    def TurnOnDisplay_Partial(self):
        self.send_command(0x22)
        self.send_data(0xFF)
        self.send_command(0x20)
        self.ReadBusy()

    def TurnOnDisplay_4GRAY(self):
        self.send_command(0x22)
        self.send_data(0xCF)
        self.send_command(0x20)
        self.ReadBusy()

    def init(self):
        if epdconfig.module_init() != 0:
            return -1
        self.reset()
        self.ReadBusy()
        self.send_command(0x12)  # SWRESET
        self.ReadBusy()
        self.send_command(0x21)
        self.send_data(0x40)
        self.send_data(0x00)
        self.send_command(0x3C)
        self.send_data(0x05)
        self.send_command(0x11)
        self.send_data(0x03)
        self.send_command(0x44)
        self.send_data(0x00)
        self.send_data(0x31)
        self.send_command(0x45)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x2B)
        self.send_data(0x01)
        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)
        self.ReadBusy()
        return 0

    def init_fast(self, mode):
        if epdconfig.module_init() != 0:
            return -1
        self.reset()
        self.ReadBusy()
        self.send_command(0x12)
        self.ReadBusy()
        self.send_command(0x21)
        self.send_data(0x40)
        self.send_data(0x00)
        self.send_command(0x3C)
        self.send_data(0x05)
        if mode == self.Seconds_1_5S:
            self.send_command(0x1A)
            self.send_data(0x6E)
        else:
            self.send_command(0x1A)
            self.send_data(0x5A)
        self.send_command(0x22)
        self.send_data(0x91)
        self.send_command(0x20)
        self.ReadBusy()
        self.send_command(0x11)
        self.send_data(0x03)
        self.send_command(0x44)
        self.send_data(0x00)
        self.send_data(0x31)
        self.send_command(0x45)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x2B)
        self.send_data(0x01)
        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)
        self.ReadBusy()
        return 0

    def Lut(self):
        self.send_command(0x32)
        for i in range(227):
            self.send_data(self.LUT_ALL[i])
        self.send_command(0x3F)
        self.send_data(self.LUT_ALL[227])
        self.send_command(0x03)
        self.send_data(self.LUT_ALL[228])
        self.send_command(0x04)
        self.send_data(self.LUT_ALL[229])
        self.send_data(self.LUT_ALL[230])
        self.send_data(self.LUT_ALL[231])
        self.send_command(0x2C)
        self.send_data(self.LUT_ALL[232])

    def Init_4Gray(self):
        if epdconfig.module_init() != 0:
            return -1
        self.reset()
        self.ReadBusy()
        self.send_command(0x12)
        self.ReadBusy()
        self.send_command(0x21)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_command(0x3C)
        self.send_data(0x03)
        self.send_command(0x0C)
        self.send_data(0x8B)
        self.send_data(0x9C)
        self.send_data(0xA4)
        self.send_data(0x0F)
        self.Lut()
        self.send_command(0x11)
        self.send_data(0x03)
        self.send_command(0x44)
        self.send_data(0x00)
        self.send_data(0x31)
        self.send_command(0x45)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x2B)
        self.send_data(0x01)
        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)
        self.ReadBusy()
        return 0

    def getbuffer(self, image):
        buf = [0xFF] * (int(self.width / 8) * self.height)
        image_mono = image.convert('1')
        imwidth, imheight = image_mono.size
        pixels = image_mono.load()
        if imwidth == self.width and imheight == self.height:
            for y in range(imheight):
                for x in range(imwidth):
                    if pixels[x, y] == 0:
                        buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        elif imwidth == self.height and imheight == self.width:
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[int((newx + newy * self.width) / 8)] &= ~(0x80 >> (y % 8))
        return buf

    def getbuffer_4Gray(self, image):
        buf = [0xFF] * (int(self.width / 4) * self.height)
        image_gray = image.convert('L')
        imwidth, imheight = image_gray.size
        pixels = image_gray.load()
        i = 0
        if imwidth == self.width and imheight == self.height:
            for y in range(imheight):
                for x in range(imwidth):
                    if pixels[x, y] == 0xC0:
                        pixels[x, y] = 0x80
                    elif pixels[x, y] == 0x80:
                        pixels[x, y] = 0x40
                    i += 1
                    if i % 4 == 0:
                        buf[int((x + y * self.width) / 4)] = (
                            (pixels[x-3, y] & 0xC0) |
                            (pixels[x-2, y] & 0xC0) >> 2 |
                            (pixels[x-1, y] & 0xC0) >> 4 |
                            (pixels[x,   y] & 0xC0) >> 6)
        elif imwidth == self.height and imheight == self.width:
            for x in range(imwidth):
                for y in range(imheight):
                    if pixels[x, y] == 0xC0:
                        pixels[x, y] = 0x80
                    elif pixels[x, y] == 0x80:
                        pixels[x, y] = 0x40
                    i += 1
                    if i % 4 == 0:
                        buf[int((y + x * self.width) / 4)] = (
                            (pixels[x, y-3] & 0xC0) |
                            (pixels[x, y-2] & 0xC0) >> 2 |
                            (pixels[x, y-1] & 0xC0) >> 4 |
                            (pixels[x, y  ] & 0xC0) >> 6)
        return buf

    def Clear(self):
        linewidth = int(self.width / 8) if self.width % 8 == 0 else int(self.width / 8) + 1
        self.send_command(0x24)
        self.send_data2([0xFF] * (self.height * linewidth))
        self.send_command(0x26)
        self.send_data2([0xFF] * (self.height * linewidth))
        self.TurnOnDisplay()

    def display(self, image):
        self.send_command(0x24)
        self.send_data2(image)
        self.send_command(0x26)
        self.send_data2(image)
        self.TurnOnDisplay()

    def display_Fast(self, image):
        self.send_command(0x24)
        self.send_data2(image)
        self.send_command(0x26)
        self.send_data2(image)
        self.TurnOnDisplay_Fast()

    def display_Partial(self, image):
        self.send_command(0x3C)
        self.send_data(0x80)
        self.send_command(0x21)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_command(0x3C)
        self.send_data(0x80)
        self.send_command(0x44)
        self.send_data(0x00)
        self.send_data(0x31)
        self.send_command(0x45)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x2B)
        self.send_data(0x01)
        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_command(0x24)
        self.send_data2(image)
        self.TurnOnDisplay_Partial()

    def display_4Gray(self, image):
        linewidth = int(self.width / 8) if self.width % 8 == 0 else int(self.width / 8) + 1
        buf = [0x00] * (self.height * linewidth)

        self.send_command(0x24)
        for i in range(int(EPD_WIDTH * EPD_HEIGHT / 8)):
            temp3 = 0
            for j in range(2):
                temp1 = image[i * 2 + j]
                for k in range(2):
                    temp2 = temp1 & 0xC0
                    temp3 |= 0x01 if temp2 in (0xC0, 0x40) else 0x00
                    temp1 <<= 2
                    temp2 = temp1 & 0xC0
                    temp3 |= 0x01 if temp2 in (0xC0, 0x40) else 0x00
                    if j != 1 or k != 1:
                        temp3 <<= 1
                    temp1 <<= 2
            buf[i] = temp3
        self.send_data2(buf)

        self.send_command(0x26)
        for i in range(int(EPD_WIDTH * EPD_HEIGHT / 8)):
            temp3 = 0
            for j in range(2):
                temp1 = image[i * 2 + j]
                for k in range(2):
                    temp2 = temp1 & 0xC0
                    temp3 |= 0x01 if temp2 in (0xC0, 0x80) else 0x00
                    temp1 <<= 2
                    temp2 = temp1 & 0xC0
                    temp3 |= 0x01 if temp2 in (0xC0, 0x80) else 0x00
                    if j != 1 or k != 1:
                        temp3 <<= 1
                    temp1 <<= 2
            buf[i] = temp3
        self.send_data2(buf)

        self.TurnOnDisplay_4GRAY()

    def sleep(self):
        self.send_command(0x10)  # DEEP_SLEEP
        self.send_data(0x01)
        epdconfig.delay_ms(2000)
        epdconfig.module_exit()
