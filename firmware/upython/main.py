"""
Repository: https://github.com/FilMarini/bigbanger
License: Apache License, Version 2.0

Notes:
This file is part of an open-source project. Feel free to contribute or report issues on the project's repository.

"""

import asyncio
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

# User imports
from config import *
from utils import *
from ads1231_bb import *
from bb_gatt_server import *

async def BigBanger(name = 'Progressor_BB', device = 'WH-C07'):
    # Define pins
    data_pin = 21
    clk_pin = 5
    tare_pin = Pin(9, Pin.IN)
    led_pin = Pin(4, Pin.OUT)
    
    # I2C for display
    i2c = I2C(0, scl=Pin(23), sda=Pin(22))
    oled = SSD1306_I2C(128, 32, i2c)

    # BLE
    ble = bluetooth.BLE()
    p = BLEBigBanger(
        ble,
        data_pin = data_pin,
        clk_pin = clk_pin,
        tare_pin = tare_pin,
        led_pin = led_pin,
        oled = oled,
        name = name,
        device = device)

    # Keep the main loop running
    while True:
        await asyncio.sleep(1)

asyncio.run(BigBanger(
    name = 'Progressor_BB', # Bluetooth advertising name, must start with "Progressor"
    device = 'WH-C07'       # Host device. Supported values are 'WH-C07', 'WH-C100'
))
