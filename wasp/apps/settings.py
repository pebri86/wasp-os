# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Ultra-simple settings application.

Currently the settings application contains only one setting: brightness
"""

import wasp
import icons

class SettingsApp():
    NAME = 'Settings'
    ICON = icons.settings

    def __init__(self):
        self.pages = ('Brightness', 'Sleep Timer', 'Wake Lift')
        self.page = self.pages[0]
        self._scroll = wasp.widgets.ScrollIndicator()
        self._slider = wasp.widgets.Slider(3, 10, 90)
        self._slider2 = wasp.widgets.Slider(3, 10, 90)

    def foreground(self):
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH|
                                  wasp.EventMask.SWIPE_UPDOWN)

    def touch(self, event):
        if self.page == self.pages[0]:
            self._slider.touch(event)
            wasp.system.brightness = self._slider.value + 1
        elif self.page == self.pages[1]:
            self._slider2.touch(event)
            wasp.system.blank_after = (self._slider2.value + 1) * 5
        elif self.page == self.pages[2]:
            if wasp.system.wake_lift:
                wasp.system.wake_lift = False
            else:
                wasp.system.wake_lift = True
            
        self._update()

    def swipe(self, event):
        pages = self.pages
        i = pages.index(self.page)

        if event[0] == wasp.EventType.UP:
            i += 1
            if i >= len(pages):
                i = 0
        else:
            i -= 1
            if i < 0:
                i = len(pages) - 1
        self.page = pages[i]
        self._draw()

    def _draw(self):
        """Redraw the display from scratch."""
        wasp.watch.drawable.fill()
        if self.page == self.pages[0]:
            wasp.watch.drawable.string('Brightness', 0, 6, width=240)
            self._slider.draw()
        elif self.page == self.pages[1]:
            wasp.watch.drawable.string('Sleep Timer', 0, 6, width=240)
            self._slider2.draw()
        elif self.page == self.pages[2]:
            wasp.watch.drawable.string('Wake by Lift', 0, 6, width=240)           

        self._update()

    def _update(self):
        if self.page == self.pages[0]:
            if wasp.system.brightness == 3:
                say = "High"
            elif wasp.system.brightness == 2:
                say = "Mid"
            else:
                say = "Low"            
            self._slider.update()
            wasp.watch.drawable.string(say, 0, 150, width=240)
        elif self.page == self.pages[1]:
            if wasp.system.blank_after == 5:
                say = "5s"
            elif wasp.system.blank_after == 10:
                say = "10s"
            else:
                say = "15s"
            self._slider2.update()
            wasp.watch.drawable.string(say, 0, 150, width=240)        
        elif self.page == self.pages[2]:
            if wasp.system.wake_lift:
                wasp.watch.drawable.string("Enabled", 0, 150, width=240)
            else:
                wasp.watch.drawable.string("Disabled", 0, 150, width=240)

        self._scroll.draw()
