# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Digital clock
~~~~~~~~~~~~~~~~

Shows a time (as HH:MM) together with a battery meter and the date.
"""

import wasp

import icons
import fonts.clock as digits
import math

red, yellow, green, cyan, blue, magenta, white, black = 0xf800, 0xffe0, 0x07e0, 0x07ff, 0x001f, 0xf81f, 0xffff, 0x0000
hourhand, minutehand, bezel  = {}, {}, {}

bgcolor = black
bezel = True
hourhand["color"] = white
hourhand["length"] = 55
hourhand["width"] = 1
minutehand["color"] = red
minutehand["length"] = 100
minutehand["width"] = 1

DIGITS = (
        digits.clock_0,
        digits.clock_1,
        digits.clock_2,
        digits.clock_3,
        digits.clock_4,
        digits.clock_5,
        digits.clock_6,
        digits.clock_7,
        digits.clock_8,
        digits.clock_9
)

MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'

class ClockApp():
    """Simple digital clock application.
    """
    NAME = 'Clock'
    ICON = icons.clock

    def __init__(self):
        self.meter = wasp.widgets.BatteryMeter()
        self.faces = ('Digital', 'Analog')
        self.face = self.faces[0]

    def foreground(self):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw()
        wasp.system.request_tick(1000)
        wasp.system.request_event(wasp.EventMask.TOUCH)

    def sleep(self):
        return True

    def wake(self):
        self.update()

    def tick(self, ticks):
        self.update()

    def touch(self, event):
        if self.face == self.faces[0]:
            self.face = self.faces[1]
        else:
            self.face = self.faces[0]
        
        self.draw()
        self.update()

    def draw(self):
        """Redraw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()
        if self.face == self.faces[0]:
            draw.rleblit(digits.clock_colon, pos=(2*48, 80), fg=0xb5b6)
        else:
            if bezel:
                for minute in range(0,60):
                    for pix in range(107,118): # 5-minunte-step bezel
                        mid = 120
                        shift = -90
                        thecos = math.cos(math.radians(6*minute+shift))
                        thesin = math.sin(math.radians(6*minute+shift))
                        x = mid + thecos*pix
                        y = mid + thesin*pix
                        if minute % 5 == 0:
                            width = 4
                            color = blue
                        else:
                            width = 1
                            color = white
                        draw.fill(color, int(x-width//2), int(y-width//2), int(width), int(width))
        
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.update()
        self.meter.draw()

    def update(self):
        """Update the display (if needed).

        The updates are a lazy as possible and rely on an prior call to
        draw() to ensure the screen is suitably prepared.
        """
        now = wasp.watch.rtc.get_localtime()
        if self.face == self.faces[0]:
            if now[3] == self.on_screen[3] and now[4] == self.on_screen[4]:
                if now[5] != self.on_screen[5]:
                    self.meter.update()
                    self.on_screen = now
                return False
        else:
            if now[3] == self.on_screen[3] and now[4] == self.on_screen[4] and now[5] == self.on_screen[5]:
                if now[5] != self.on_screen[5]:
                    self.meter.update()
                    self.on_screen = now
                return False
        
        draw = wasp.watch.drawable

        if self.face == self.faces[0]:
            draw.rleblit(DIGITS[now[4]  % 10], pos=(4*48, 80))
            draw.rleblit(DIGITS[now[4] // 10], pos=(3*48, 80), fg=0xbdb6)
            draw.rleblit(DIGITS[now[3]  % 10], pos=(1*48, 80))
            draw.rleblit(DIGITS[now[3] // 10], pos=(0*48, 80), fg=0xbdb6)

            month = now[1] - 1
            month = MONTH[month*3:(month+1)*3]
            draw.string('{} {} {}'.format(now[2], month, now[0]),
                    0, 180, width=240)
        
        else:
            for pix in range(0,90): #second hand
                mid = 120
                shift = -90
                width = 1
                if (self.on_screen[5] > -1): # clear previous position
                    thecos = math.cos(math.radians(6*self.on_screen[5]+shift))
                    thesin = math.sin(math.radians(6*self.on_screen[5]+shift))
                    x = mid + thecos*pix
                    y = mid + thesin*pix
                    draw.fill(bgcolor, int(x-width//2), int(y-width//2), int(width), int(width))
                thecos = math.cos(math.radians(6*now[5]+shift))
                thesin = math.sin(math.radians(6*now[5]+shift))
                x = mid + thecos*pix
                y = mid + thesin*pix
                draw.fill(yellow, int(x-width//2), int(y-width//2), int(width), int(width))

            for pix in range(0,minutehand["length"]): #minute hand
                mid = 120
                shift = -90
                width = minutehand["width"]
                if (self.on_screen[4] > -1): # clear previous position
                    thecos = math.cos(math.radians(6*self.on_screen[4]+shift))
                    thesin = math.sin(math.radians(6*self.on_screen[4]+shift))
                    x = mid + thecos*pix
                    y = mid + thesin*pix
                    draw.fill(bgcolor, int(x-width//2), int(y-width//2), int(width), int(width))
                thecos = math.cos(math.radians(6*now[4]+shift))
                thesin = math.sin(math.radians(6*now[4]+shift))
                x = mid + thecos*pix
                y = mid + thesin*pix
                draw.fill(minutehand["color"], int(x-width//2), int(y-width//2), int(width), int(width))
            
            for pix in range(0,hourhand["length"]): #hour hand
                mid = 120
                shift = -90
                width = hourhand["width"]     
                if (self.on_screen[3] > -1): # clear previous position
                    thecos = math.cos(math.radians(30*(self.on_screen[3]+self.on_screen[4]/60)+shift))
                    thesin = math.sin(math.radians(30*(self.on_screen[3]+self.on_screen[4]/60)+shift))
                    x = mid-int(thecos) + thecos*pix
                    y = mid-int(thesin) + thesin*pix
                    draw.fill(bgcolor, int(x-width//2), int(y-width//2), int(width), int(width))
                # draw new position
                thecos = math.cos(math.radians(30*(now[3]+now[4]/60)+shift))
                thesin = math.sin(math.radians(30*(now[3]+now[4]/60)+shift))
                x = mid-int(thecos) + thecos*pix
                y = mid-int(thesin) + thesin*pix
                draw.fill(hourhand["color"], int(x-width//2), int(y-width//2), int(width), int(width))

        self.on_screen = now
        self.meter.update()
        return True
