#!/usr/bin/env python

from instructions import *


class Disk(object):
	def __init__(self, arg):
		if type(arg) == int:
			self.data = [0] * size
		elif type(arg) == file:
			self.data = map(lambda x : ord(x), arg.read())

class Emulator(object):
	def __init__(self, mem_size, disk):
		self.mem = [0] * mem_size
		self.cpu = Cpu(self)
		self.disk = Disk(disk)

	def load_bootloader(self):
		bootloader = self.disk.data[:64]

		for i in range(len(bootloader)):
			self.mem[i] = bootloader[i]

	def run(self):
		print(Instruction.opcodes)

		self.load_bootloader()

		while True:
			print(str(self) + "\n")
			raw_input()
			self.cpu.step()

	def display(self, arg):
		print(arg)

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
		self.sp = len(self.mem)

	def __str__(self):
		res = "ip: " + str(self.ip) + "\nRegisters: \n"

		for i in range(len(self.regs)):
			res += "  reg" + str(i) + ": " + str(self.regs[i]) + "\n"
		res += "sp: " + str(self.sp)

		return res

	def step(self):
		"""
			Execute a single instruction
		"""
		next_instr = self.fetch_and_decode()
		print("Executing: " + str(next_instr))
		self.ip = next_instr.execute()

	def fetch_and_decode(self):
		"""
			Return the next instruction to be executed
		"""
		instr = self.mem[self.ip:self.ip + 4]
		return Instruction.CreateInstruction(instr, self.vm)
