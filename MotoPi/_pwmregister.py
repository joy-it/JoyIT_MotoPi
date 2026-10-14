import MotoPi
from .pwmchannel import PWMChannel

class _PWMRegister:

    """
    Provide low-level access to the 16 PCA9685 PWM register pairs.
    Each entry is a tuple of 12-bit on/off counters with the optional
    0x1000 full-on/full-off flag bit. This class is intended for internal use.

    :param MotoPi pca: MotoPi object to controll pwm registers
    """
    
    _LED0 = 0x06
    
    @staticmethod
    def __checkValue(value, min, max):
        """
        Validate an integer against a half-open interval [min, max).
        :param int value: parameter to check if it is in range
        :param int min: minimum of value range
        :param int max: maximum of value range
        """
        if not min <= value < max:
            raise ValueError(f"Value is not in range of {min} and {max}")
        return value
    
    def __init__(self, pca: "MotoPi"):
        self._pca = pca

    def __len__(self):
        """
        Return the number of register groups (16).
        """
        return 16

    def __getitem__(self, index):
        """
        Read the on/off counter values for a channel index from 0 to 15.
        :param int index: index of channel to read on/off values from
        """
        index = self.__checkValue(index, 0, len(self))
        self._pca._enable_auto_increment()
        data = self._pca._read_block(self._LED0 + index * 4, 4)
        return (data[0] | (data[1] << 8), data[2] | (data[3] << 8))#

    def __setitem__(self, index, value):
        """
        Write the on/off counter values for a channel index from 0 to 15.
        The values must each be in the inclusive range 0x0000 through 0x1000.
        :param int index: index of channel to write value on
        :param int value: value to write onto channel
        """
        index = self.__checkValue(index, 0, len(self))
        on, off = value
        on = self.__checkValue(value[0], 0x00, 0x1001)
        off = self.__checkValue(value[1], 0x00, 0x1001)
        self._pca._enable_auto_increment()
        self._pca._write_block(self._LED0 + index * 4, [on & 0xFF, on >> 8, off & 0xFF, off >> 8])