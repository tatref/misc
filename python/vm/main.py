#!/usr/bin/env python
#-*- coding:utf-8 -*-

import emu


if __name__ =='__main__':
	f = open("rom")
	emu = emu.Emulator(f)
	emu.run()
