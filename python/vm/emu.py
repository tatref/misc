#!/usr/bin/env python

from instructions import *


class Emulator(object):
    def __init__(self, rom):
        try:
            self.mem = rom.read()
        except:
            raise Exception("rom (" + str(rom) + ") must be a file)")
        self.cpu = Cpu(self)

    def run(self):
        print('Starting...\n')
        while True:
            raw_input()
            self.cpu.step()

    def __str__(self):
        res = "CPU registers:\n" + str(self.cpu)
        return res


class Cpu(object):
    def __init__(self, vm):
        self.vm = vm
        self.mem = vm.mem

        # Next instruction pointer
        self.ip = 0

        # Registers
        self.regs = [0] * 4

        # Stack pointer
        self.sp = []

    def step(self):
        """
            Execute a single instruction
        """
        next_instr = Instruction.CreateInstruction(map(ord, self.mem[self.ip:self.ip + 2]), self.vm)
        next_instr.execute()

        print(len(self.sp))
