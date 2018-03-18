#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2018 Florian Lagg <github@florian.lagg.at>
# Under Terms of GPL v3

import readchar
from threading import Thread, Lock

class InputHandler():
    def __init__(self):
        self._charsLock = Lock()
        self._chars = []

        pInput = Thread(name="Input handler", target=self._inputHandler)
        pInput.daemon = True
        pInput.start()

    def _inputHandler(self):
        while True:
            c = readchar.readchar()
            with self._charsLock:
                self._chars.append(c)

    def ConsumeChar(self):
        with self._charsLock:
            if len(self._chars):
                return self._chars.pop(0)
        return None