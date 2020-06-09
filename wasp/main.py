# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp
import apps.calc
import apps.snake

wasp.system.register(apps.calc.CalculatorApp(), False)
wasp.system.register(apps.snake.SnakeGameApp(), False)
wasp.system.run()
