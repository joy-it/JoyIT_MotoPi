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
from .pwmchannel import PWMChannel
import operator

class PCAChannel:
    """
    Provide indexed, lazily created access to the 16 PWM channels.
    Channel objects are cached so repeated lookup returns the same object.
    Integer indices and Python slices are supported.

    :param MotoPi pca: object of MotoPi
    """

    def __init__(self, pca: "MotoPi") -> None:
        self._pca = pca
        self._channels = [None] * len(self)

    def __len__(self) -> int:
        """
        Return the number of PWM output channels (16).
        """
        return 16

    def __getitem__(self, index: int) -> PWMChannel:
        """
        Return a PWMChannel or a list of channels for a slice.
        Negative integer indices are supported as in a Python sequence.

        Raises IndexError: If an integer index is outside the available channels.
        
        :param int index: index of pwm channel
        """
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(len(self)))]
        index = operator.index(index)
        if index < 0:
            index += len(self)
        if not 0 <= index < 16:
            raise IndexError("Index is not in range")
        if self._channels[index] is None:
            self._channels[index] = PWMChannel(self._pca, index)
        return self._channels[index]