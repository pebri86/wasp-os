# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Hynitron CST816S touch contoller driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import array
import time
from machine import Pin

class CST816S:
    """Hynitron CST816S I2C touch controller driver.

    .. automethod:: __init__
    """
    
    def __init__(self, bus, _int, _rst):
        """Specify the bus used by the touch controller.

        :param machine.I2C bus: I2C bus for the CST816S.
        """
        self.i2c = bus
        self.tp_int = _int  
        self.tp_rst = _rst
        self.dbuf = bytearray(6)
        self.event = array.array('H', (0, 0, 0))
        self.touch_en = True

        self._reset()
        self.tp_int.irq(trigger=Pin.IRQ_FALLING, handler=self.get_touch_data)

    def _reset(self):
        self.tp_rst.off()
        time.sleep_ms(5)
        self.tp_rst.on()
        time.sleep_ms(50)

    def get_touch_data(self, pin_obj):
        """Receive a touch event by interrupt.

        Check for a pending touch event and, if an event is pending,
        prepare it ready to go in the event queue.
        """
        dbuf = self.dbuf

        try:
            self.i2c.readfrom_mem_into(21, 1, dbuf)
        except OSError:
            return None

        # This is a good event, lets save it
        self.event[0] = dbuf[0] # event
        self.event[1] = ((dbuf[2] & 0xf) << 8) + dbuf[3] # x coord
        self.event[2] = ((dbuf[4] & 0xf) << 8) + dbuf[5] # y coord

    def get_event(self):
        """Receive a touch event.

        Check for a pending touch event and, if an event is pending,
        prepare it ready to go in the event queue.

        :return: An event record if an event is received, None otherwise.
        """
        if self.event[0] == 0:
            return None

        if not self.touch_en:
            return None

        return self.event

    def reset_touch_data(self):
        """Reset touch data.

        Reset touch data, call this function after processed an event.
        """
        self.event[0] = 0

    def wake(self):
        """Wake up touch controller chip.

        Just reset the chip in order to wake it up
        """
        self._reset()
        self.touch_en = True

    def sleep(self):
        """Put touch controller chip on sleep mode to save power.
        """
        self._reset()
        # send 0x03 to register 0xA5 to put the controller on sleep mode
        dbuf = bytearray([0xA5, 0x03])
        self.i2c.writeto(21, dbuf)
        self.touch_en = False
