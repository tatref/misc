#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function


class CLS(object):
    def __init__(self, opcode, vm):
        self.vm = vm

    def execute(self):
        self.vm.cpu.ip += 2

    def __str__(self):
        return 'CLS'


class RET(object):
    def __init__(self, opcode, vm):
        self.vm = vm

    def execute(self):
        self.vm.cpu.ip = self.vm.cpu.sp.pop() + 2  # TODO +2 or +0?

    def __str__(self):
        return 'RET'


class JP(object):
    def __init__(self, opcode, vm):
        self.vm = vm
        self.dst = ((opcode[0] & 0x0F) << 8) + opcode[1]

    def execute(self):
        self.vm.cpu.ip = self.dst

    def __str__(self):
        return 'JP ' + str(self.dst)


class CALL(object):
    def __init__(self, opcode, vm):
        self.vm = vm
        self.callee = ((opcode[0] & 0x0F) << 8) + opcode[1]

    def execute(self):
        self.vm.cpu.sp.append(self.vm.cpu.ip)
        self.vm.cpu.ip = self.callee

    def __str__(self):
        return 'CALL ' + str(self.callee)


class SE_VX_BYTE(object):
    def __init__(self, opcode, vm):
        self.vm = vm
        self.reg = opcode[0] & 0x0F
        self.byte = opcode[1]

    def execute(self):
        if self.vm.cpu.regs[self.reg] == self.byte:
            self.vm.cpu.ip += 4
        else:
            self.vm.cpu.ip += 2


class SNE_VX_BYTE(object):
    def __init__(self, opcode, vm):
        self.vm = vm
        self.reg = opcode[0] & 0x0F
        self.byte = opcode[1]

    def execute(self):
        if self.vm.cpu.regs[self.reg] != self.byte:
            self.vm.cpu.ip += 4
        else:
            self.vm.cpu.ip += 2


class Instruction(object):
    opcodes = {(0x00E0, 0xFFFF): CLS,
               (0x00EE, 0xFFFF): RET,
               (0x1000, 0xF000): JP,
               (0x2000, 0xF000): CALL,
               (0x3000, 0xF000): SE_VX_BYTE,
               (0x4000, 0xF000): SNE_VX_BYTE}

    @staticmethod
    def CreateInstruction(opcode, vm):
        for i in Instruction.opcodes.iterkeys():
            #print(str((opcode[0] << 8) + opcode[1]) + ', ' + str(i) )
            if ((opcode[0] << 8) + opcode[1]) & i[1] == i[0]:
                instruction = Instruction.opcodes[i](opcode, vm)
                print(instruction)
                return instruction
        raise Exception('No matching instruction found' + str(opcode))
