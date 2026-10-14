# JoyIT_MotoPi

Python library for controlling the **Joy-IT RB-Moto3** motor/servo expansion board on a Raspberry Pi. The board uses a **PCA9685 16-channel, 12-bit PWM controller** connected via I²C. The library provides access to the PWM channels, a shared frequency setting, raw PWM counter values and microsecond pulse generation.

This implementation communicates directly with the controller through `smbus2` and uses `gpiozero` for the optional board-enable GPIO. **It does not require Adafruit CircuitPython PCA9685.** The included servo example uses `adafruit-circuitpython-motor`, which is a separate package.

## Requirements

- Raspberry Pi with Python **3.9 or later** and the I²C interface enabled.
- Joy-IT RB-Moto3 connected to the appropriate Raspberry Pi GPIO/I²C interface.
- Python packages: `smbus2`, `gpiozero` and `adafruit-circuitpython-motor` (declared in `pyproject.toml`).
- The Linux user must have access to the I²C device and the configured GPIO pin.

Enable I²C using `sudo raspi-config` (Interface Options → I2C), then reboot if prompted.

## Installation

```bash
pip3 install JoyIT_MotoPi
```

## API reference

| API | Description |
| --- | --- |
| `MotoPi(...)` | Open the PWM controller and initialize its channels. |
| `motopi.frequency` | Read or set the frequency shared by all 16 PWM outputs, in Hz. |
| `motopi.channels[index]` | Get a channel (`0` through `15`); slices are also supported. |
| `channel.duty_cycle` | Read/set a 16-bit duty-cycle value, from `0` (off) to `65535` (fully on). |
| `channel.frequency` | Read-only shared frequency; cannot be changed per channel. |
| `motopi.set_pwm(channel, on, off)` | Write raw PWM on/off counter values (0–4095; `0x1000` is a special full-on/full-off flag). |
| `motopi.write_microseconds(channel, duration)` | Set the high pulse duration in µs at the current PWM frequency; `0` turns the channel off. |
| `motopi.all_off()` | Turn off all outputs. |
| `motopi.reset()` | Reinitialize the controller and clock selection; turns all channels off. |
| `motopi.deinit()` / `motopi.close()` | Turn outputs off and release resources. |

>[!Note]
> Prefer the `with MotoPi(...) as motopi:` form: it calls `deinit()` when the block ends, including on exceptions. Without a context manager, call `motopi.close()` explicitly. When the library opens the I²C bus itself, it closes that bus; when you pass an existing bus object, it leaves ownership of that bus with the caller.


## License and attribution

See [LICENSE](LICENSE). Portions of the implementation are adapted from the [Adafruit CircuitPython PCA9685 library](https://github.com/adafruit/Adafruit_CircuitPython_PCA9685); the corresponding copyright and MIT license notices are retained in the source files.