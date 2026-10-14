# This is a edited library from Adafruit 
# Original can be found here: https://github.com/adafruit/Adafruit_CircuitPython_PCA9685

"""
The MIT License (MIT)

Copyright (c) 2016 Radomir Dopieralski, written for Adafruit Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from ._pwmregister import _PWMRegister
from .pcachannel import PCAChannel 
import math
import time

class MotoPi:
    """
    Control the Joy-IT RB-Moto3 PCA9685 PWM controller over I2C.
    
    The controller exposes 16 PWM outputs that share one frequency. By default
    it uses I2C bus 1, address 0x41, an external 25 MHz clock, and BCM GPIO 7
    as the board-enable output. Pass ``enable_pin=None`` to skip GPIO control.

    Use the controller as a context manager to release hardware resources on exit.
    ``external_clock_hz`` specifies the clock rate for PWM calculations; it does
    not measure or generate the external clock.

    :param i2c_bus: I2C bus number (default: 1) or an SMBus-compatible bus object
    :param int address: I2C device address (default: 0x41)
    :param int external_clock_hz: Clock frequency used to calculate PWM timing in Hz (default: 25_000_000)
    :param bool external_clock: if board is using external clock during reset (default: True)
    :param int enable_pin: BCM GPIO number used to enable board or None to omit it (default: 7) 
    """

    _MODE1 = 0x00
    _MODE2 = 0x01
    _PRESCALE = 0xFE
    _RESTART = 0x80
    _EXTCLK = 0x40
    _AI = 0x20
    _SLEEP = 0x10
    _LED0 = 0x06

    def __init__(
        self,
        i2c_bus=1,
        *,
        address: int = 0x41,
        external_clock_hz: int = 25_000_000,
        external_clock=True,
        enable_pin = 7,
    ) -> None:
        
        self._address = address
        if self._address == 0x70:
            raise ValueError("0x70 is the all-call-address of the PCA9685")
        self.reference_clock_speed = external_clock_hz
        self._external_clock = bool(external_clock)
        self._closed = False
        self._owns_bus = isinstance(i2c_bus, int)
        self._bus = None
        self._enable = None
        try:
            if enable_pin is not None:
                from gpiozero import OutputDevice
                self._enable = OutputDevice(enable_pin, active_high = True, initial_value = True)
            if self._owns_bus:
                from smbus2 import SMBus
                self._bus = SMBus(i2c_bus)
            else:
                self._bus = i2c_bus
            self.channels = PCAChannel(self)
            self.pwm_regs = _PWMRegister(self)
            self.reset()
        except Exception:
            try:
                self._release_resources()
            finally:
                self._closed = True
            raise

    @staticmethod
    def _positiveValue(value):
        """
        Convert a value to a finite, strictly positive float.
        Raises ValueError: If the converted value is zero, negative, or non-finite.
        
        :param float value: value to check if finite and positive
        """
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise ValueError("Value is not above 0")
        return value
    
    @property
    def reference_clock_speed(self):
        """
        Return the configured reference-clock frequency in hertz.
        """
        return self._clock_hz

    @reference_clock_speed.setter
    def reference_clock_speed(self, value):
        """
        Set the clock rate used for PWM calculations (greater than 0, at most 50 MHz).

        :param int value: new value to set clock rate to
        """
        value = self._positiveValue(value)
        if value > 50_000_000:
            raise ValueError("The PCA9685 only supports a maximum of 50 MHz.")
        self._clock_hz = value

    def _check_open(self):
        """
        Raises RuntimeError: this controller has already been closed.
        """
        if self._closed:
            raise RuntimeError("PCA9685 was already closed")

    def _read8(self, register):
        """
        Read one byte from an I2C register of the configured controller.

        :param int register: register to read byte from
        """
        self._check_open()
        return self._bus.read_byte_data(self._address, register)

    def _write8(self, register, value):
        """
        Write one byte to an I2C register of the configured controller.

        :param int register: register to write byte onto
        :param int value: byte to write onto register
        """
        self._check_open()
        self._bus.write_byte_data(self._address, register, value)

    def _read_block(self, register, length):
        """
        Read exactly ``length`` consecutive bytes from an I2C register.
        Raises OSError: If the bus returns fewer bytes than requested.
        
        :param int register: register to read from
        :param int length: anmount of bytes to read from register
        """
        self._check_open()
        data = self._bus.read_i2c_block_data(self._address, register, length)
        if len(data) != length:
            raise OSError("Incomplete I2C answer")
        return data

    def _write_block(self, register, data):
        """
        Write a sequence of bytes beginning at the given I2C register.

        :param int register: register to write onto
        :param int[] data: bytes to write onto register
        """
        self._check_open()
        self._bus.write_i2c_block_data(self._address, register, data)

    @property
    def mode1_reg(self):
        """
        Read the PCA9685 MODE1 configuration register.
        """
        return self._read8(self._MODE1)

    @mode1_reg.setter
    def mode1_reg(self, value):
        """
        Write the PCA9685 MODE1 configuration register.

        :param int value: value to write onto MODE1 configuration register
        """
        self._write8(self._MODE1, value)

    @property
    def mode2_reg(self):
        """
        Read the PCA9685 MODE2 output configuration register.
        """
        return self._read8(self._MODE2)

    @mode2_reg.setter
    def mode2_reg(self, value):
        """
        Write the PCA9685 MODE2 output configuration register.
        
        :param int value: value to write onto MODE2 configuration register
        """
        self._write8(self._MODE2, value)

    @property
    def prescale_reg(self):
        """
        Read the PWM frequency prescaler register.
        """
        return self._read8(self._PRESCALE)

    @prescale_reg.setter
    def prescale_reg(self, value):
        """
        Write the PWM frequency prescaler register.
        
        :param int value: value to write onto frequency prescaler register
        """
        self._write8(self._PRESCALE, value)

    def _enable_auto_increment(self):
        """
        Enable automatic I2C register-address increment for block transfers.
        """
        mode = self.mode1_reg
        if not mode & self._AI:
            self.mode1_reg = (mode & ~self._RESTART) | self._AI

    def reset(self) -> None:
        """
        Reset PWM output configuration and initialize the selected clock source.
        All 16 PWM channels are switched off. The PCA9685 is configured with
        auto-increment enabled and MODE2 set to 0x04.

        Raises RuntimeError: If an active external clock conflicts with the requested internal-clock configuration. Power-cycle the device if necessary.
        """
        mode = self.mode1_reg
        if mode & self._EXTCLK and not self._external_clock:
            raise RuntimeError("EXTCLK is already active. External tact has to be configured or switch board on and off again to use internal tact.")
        base = self._AI | (mode & self._EXTCLK)
        self.mode1_reg = base
        self.all_off()
        self.mode1_reg = base | self._SLEEP
        if self._external_clock:
            base |= self._EXTCLK
            self.mode1_reg = base | self._SLEEP
        self.mode2_reg = 0x04
        self.mode1_reg = base
        time.sleep(0.005)

    @property
    def frequency(self) -> float:
        """
        Get the common PWM frequency in hertz, calculated from the prescaler.
        """
        prescale = self.prescale_reg
        if prescale < 3:
            raise ValueError("The device pre_scale register (0xFE) was not read or returned a value < 3")
        return self.reference_clock_speed / (4096 * (prescale + 1))

    @frequency.setter
    def frequency(self, freq: float) -> None:
        """
        Set the PWM frequency shared by all 16 channels, in hertz.
        The frequency is quantized to the PCA9685 prescaler resolution.

        Raises ValueError: If the requested frequency cannot be represented.

        :param float freq: new PWM frequency shared by all 16 channels in Hz
        """
        freq = self._positiveValue(freq)
        prescale = int(self.reference_clock_speed / (4096.0 * freq) + 0.5) - 1
        if not 3 <= prescale <= 0xFF:
            raise ValueError("PCA9685 cannot output at the given frequency")
        mode = self.mode1_reg  # Mode 1
        base = (mode & ~(self._RESTART | self._SLEEP)) | self._AI
        self.mode1_reg = base | self._SLEEP
        self.prescale_reg = prescale  # Prescale
        self.mode1_reg = base  # Mode 1
        time.sleep(0.005)
        # Mode 1, autoincrement on, fix to stop pca9685 from accepting commands at all addresses
        self.mode1_reg = base | self._RESTART

    def set_pwm(self, channel, on, off):
        """
        Set raw 12-bit PWM on/off counter positions for a channel.
        
        :param int channel: PWM output index from 0 to 15
        :param int on: Counter value for the rising edge, or 0x1000 for full-on
        :param int off: Counter value for the falling edge, or 0x1000 for full-off
        """
        self.pwm_regs[channel] = (on, off)

    def write_microseconds(self, channel, microseconds):
        """
        Set a channel's high pulse width in microseconds.
        The width is converted to 12-bit ticks using the current shared PWM
        frequency. A width of zero switches the channel off. Set ``frequency``
        before using this method.

        Raises ValueError: If the width is invalid or cannot fit into one PWM period.
        
        :param int channel: PWM output index from 0 to 15
        :param int microseconds: Non-negative pulse duration in microseconds
        """
        microseconds = float(microseconds)
        if not math.isfinite(microseconds) or microseconds < 0:
            raise ValueError("Pulse length must be finite and >= 0")
        if microseconds == 0:
            self.channels[channel].duty_cycle = 0
            return
        ticks = int(microseconds * self.frequency * 4096 / 1_000_000 + 0.5)
        if not 1 <= ticks <= 4095:
            raise ValueError("Pulse length is not within PWM period")
        self.set_pwm(channel, 0, ticks)

    def all_off(self):
        """
        Switch all 16 PWM outputs fully off using block I2C writes.
        """
        self._enable_auto_increment()
        for first in range(0, 16, 4):
            self._write_block(self._LED0 + first * 4, [0, 0, 0, 0x10] * 4)

    def __enter__(self) -> "MotoPi":
        """
        Return the open controller for use in a ``with`` statement.
        """
        self._check_open()
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        """
        Release the controller when leaving a ``with`` statement.
        """
        self.deinit()

    def deinit(self) -> None:
        """
        Turn off all channels and release the owned I2C bus and GPIO device.
        This operation is idempotent. ``close`` is an alias of this method.
        """
        if self._closed:
            return
        try:
            self.all_off()
        finally:
            self._closed = True
            self._release_resources()
    
    close = deinit

    def _release_resources(self):
        """
        Close the I2C bus if owned and deactivate/close the GPIO output.
        """
        if self._owns_bus:
            self._bus.close()
        if self._enable is not None:
            self._enable.off()
            self._enable.close()