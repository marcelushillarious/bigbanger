"""
Repository: https://github.com/FilMarini/bigbanger
License: Apache License, Version 2.0

Notes:
This file is part of an open-source project. Feel free to contribute or report issues on the project's repository.

ADS1231 load cell amplifier interface
"""

import time
import struct
import esp32
from machine import Pin
from config import *

class ADS1231BB:
    def __init__(self, data_pin=21, clk_pin=5, device='WH-C07'):
        self.data_pin = Pin(data_pin, Pin.IN, Pin.PULL_DOWN)
        self.clk_pin = Pin(clk_pin, Pin.OUT)
        self.clk_pin.value(0)
        
        self.current_weight = 0
        self.tara_offset = 0
        self.tara_triggered = True  # Trigger initial TARA
        self.tara_throwaway_samples = 50
        self.tara_samples = 100
        self.tara_counter = 0
        self.tara_accumulator = 0
        
        # Scaling: from Arduino, 203700 LSB for 3269 grams
        self.scale = 203700 / 3269  # LSB per gram
        
        # NVS for persistent scale
        self.nvs = esp32.NVS("storage")
        try:
            saved_scale = self.nvs.get_i32("ads_scale")
            self.scale = saved_scale / 1000.0  # Store as int * 1000
        except:
            if device in PROG_SCALE.keys():
                self.scale = PROG_SCALE.get(device)
            else:
                self.scale = PROG_SCALE.get('WH-C07')
        
        self.tare()

    def read_raw(self):
        """Read 24-bit raw value from ADS1231"""
        # Wait for data ready (DOUT low)
        while self.data_pin.value() == 1:
            pass
        
        raw = 0
        for _ in range(24):
            self.clk_pin.value(1)
            time.sleep_us(1)
            bit = self.data_pin.value()
            raw = (raw << 1) | bit
            self.clk_pin.value(0)
            time.sleep_us(1)
        
        # Toggle clock once more
        self.clk_pin.value(1)
        self.clk_pin.value(0)
        
        # Left align 24 bits
        raw <<= 8
        
        # Convert to signed
        value = raw
        if value & 0x80000000:
            value -= 0x100000000
        
        # Right align
        value //= 256
        
        # Negate if needed (soldering backwards)
        value = -value
        
        return value

    def update(self):
        """Update weight reading, called periodically"""
        value = self.read_raw()
        
        if self.tara_triggered:
            if self.tara_counter == 0:
                self.tara_counter = self.tara_throwaway_samples + self.tara_samples
                self.tara_accumulator = 0
            if self.tara_counter <= self.tara_samples:
                self.tara_accumulator += value
            self.tara_counter -= 1
            if self.tara_counter == 0:
                self.tara_offset = self.tara_accumulator // self.tara_samples
                self.tara_triggered = False
            return
        
        # Remove TARA offset
        value -= self.tara_offset
        
        # Scale to grams
        weight = value / self.scale
        
        # Exponential moving average (alpha=1/8)
        self.current_weight = (weight + 7 * self.current_weight) // 8

    def get_weight(self):
        """Get current weight in grams"""
        return self.current_weight

    def get_ble_units(self):
        """Get weight as bytearray for BLE"""
        weight_data = bytearray(struct.pack('f', self.current_weight))
        return weight_data

    def get_ble_pkt(self, start_time_us):
        """Get full BLE packet"""
        weight_data = self.get_ble_units()
        elapsed_us = time.ticks_diff(time.ticks_us(), start_time_us)
        elapsed_us_data = bytearray(elapsed_us.to_bytes(4, "little"))
        size = 8
        byte_pkt = bytearray([RES_WEIGHT_MEAS, size]) + weight_data + elapsed_us_data
        return byte_pkt

    def set_start_time(self, new_time):
        self._start_time_us = new_time

    def tare(self):
        """Trigger TARA"""
        self.tara_triggered = True

    def calibrate(self, known_weight=1000):
        """Calibrate with known weight"""
        # Read current raw value
        raw = self.read_raw()
        # Assume current weight is known_weight grams
        self.scale = raw / known_weight
        # Save to NVS
        self.nvs.set_i32("ads_scale", int(self.scale * 1000))
        self.nvs.commit()</content>
<parameter name="filePath">/Users/marcelhill/Documents/git/bigbanger/firmware/upython/ads1231_bb.py