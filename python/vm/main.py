#!/usr/bin/env python
#-*- coding:utf-8 -*-

import emu


if __name__ =='__main__':
	f = open("disk.dat")
	emu = emu.Emulator(128, f)
	emu.run()
