# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Bosch BMA421 accelerometer driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import bma42x
import time
from machine import Pin

class BMA421:
    """BMA421 driver

    .. automethod:: __init__
    """
    def __init__(self, i2c):
        """Configure the driver.

        :param machine.I2C i2c: I2C bus used to access the sensor.
        """
        self._dev = bma42x.BMA42X(i2c)
        self.last_y_acc = 0

    def reset(self):
        """Reset and reinitialize the sensor."""
        dev = self._dev
        any_no_mot = {}

        # Init, reset, wait for reset, enable I2C watchdog
        dev.init()
        dev.set_command_register(0xb6)
        time.sleep(0.20)
        dev.set_reg(bma42x.NV_CONFIG_ADDR, 6);

        # Configure the sensor for basic step counting
        dev.write_config_file()
        dev.set_accel_enable(True)
        dev.set_accel_config(odr=bma42x.OUTPUT_DATA_RATE_100HZ,
                               range=bma42x.ACCEL_RANGE_2G,
                               bandwidth=bma42x.ACCEL_NORMAL_AVG4,
                               perf_mode=bma42x.CIC_AVG_MODE)
        dev.feature_enable(bma42x.STEP_CNTR, True)
        dev.feature_enable(bma42x.STEP_ACT, True)

        # Select the axis for which any/no motion interrupt should be generated
        any_no_mot['axes_en'] = bma42x.EN_ALL_AXIS;

        # Set the slope threshold:
        # Interrupt will be generated if the slope of all the axis exceeds the
        # threshold (1 bit = 0.48mG)
        any_no_mot['threshold'] = 2000;

        # Set the duration for any/no motion interrupt:
        # Duration defines the number of consecutive data points for which
        # threshold condition must be true(1 bit = 20ms)
        any_no_mot['duration'] = 1;

        # Set the threshold, duration and axis enable configuration
        dev.set_any_mot_config(**any_no_mot);
        # Map the interrupt pin with that of any-motion and no-motion interrupts.
        # Interrupt will be generated when any or no-motion is recognized.
        dev.map_interrupt(bma42x.INTR1_MAP,
                        bma42x.ANY_MOT_INT, True)

    @property
    def steps(self):
        """Report the number of steps counted."""
        return self._dev.step_counter_output()

    @steps.setter
    def steps(self, value):
        if value != 0:
            raise ValueError()
        # TODO: There is a more efficient way to reset the step counter
        #       but I haven't looked it up yet!
        self.reset()

    def read_axis(self):
        return self._dev.read_accel_xyz()

    def get_event(self):
        int_status = self._dev.read_int_status()
        if int_status & bma42x.ANY_MOT_INT:
            data = self.read_axis()
            if (data[0] + 335) <= 670 and data[2] < 0:
                if data[1] >= 0:
                    self.last_y_acc = 0
                    return None
                if (data[1] + 230) < self.last_y_acc:
                    self.last_y_acc = data[1]
                    return True

        return None
