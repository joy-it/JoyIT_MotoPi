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
import MotoPi

class PWMChannel:
    """
    Represent one of the 16 PCA9685 PWM output channels.
    The public ``duty_cycle`` property uses the 16-bit PWMOut-style scale, while the underlying PCA9685 chip has 12-bit timing resolution.

    :param MotoPi pca: The MotoPi object
    :param int index: The index of the channel
    """

    @staticmethod
    def __checkIndex(index: int, min=0, max=15):
        """
        Validate that a channel index falls within the inclusive bounds."""
        if not min <= index <= max:
            raise ValueError(f"Index is not in range of {min} and {max}")
        return index
    
    def __init__(self, pca: "MotoPi", index: int):
        self._pca = pca
        self._index = self.__checkIndex(index)

    @property
    def frequency(self) -> float:
        """
        Return the shared PCA9685 PWM frequency in Hertz.
        """
        return self._pca.frequency

    @frequency.setter
    def frequency(self, value):
        """
        The overall PWM frequency in Hertz (read-only).
        A PWMChannel's frequency cannot be set individually.
        All channels share a common frequency, set by PCA9685.frequency.
        """
        raise NotImplementedError("frequency cannot be set on individual channels")
    
    @property
    def duty_cycle(self) -> int:
        """
        Read duty cycle as a 16-bit value between 0 and 65535.
        
        Zero means fully off, while 65535 means fully on. 
        Because the chip uses 12-bit PWM timing, intermediate values have limited resolution.
        """
        pwm = self._pca.pwm_regs[self._index]
        if pwm[1] == 0x1000:
                    return 0x0000
        if pwm[0] == 0x1000:
            return 0xFFFF
        return ((pwm[1] - pwm[0]) & 0x0FFF) << 4

    @duty_cycle.setter
    def duty_cycle(self, value: int) -> None:
        """
        Set the channel duty cycle using a 16-bit value (0 to 65535).

        Zero selects full-off and 65535 selects full-on. 
        Other values are quantized to the controller's 12-bit PWM resolution.

        Raises ValueError: If the value is outside the supported range.
        """
        if not 0 <= value <= 0xFFFF:
            raise ValueError(f"Out of range: value {value} not 0 <= value <= 65,535")
        if value == 0xFFFF: # Special case for "fully on":
            self._pca.pwm_regs[self._index] = (0x1000, 0)
        elif value < 0x0010: # Special case for "fully off":
            self._pca.pwm_regs[self._index] = (0, 0x1000)
        else: # Shift our value by four because the PCA9685 is only 12 bits but our value is 16
            # value should never be zero here because of the test for the "fully off" case
            # (the LEDn_ON and LEDn_OFF registers should never be set with the same values)
            self._pca.pwm_regs[self._index] = (0, value >> 4)