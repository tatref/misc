#!/usr/bin/env python

class ERR(object):
	def __init__(self, args, vm):
		self.vm = vm

	def execute(self):
		raise Exception("'ERR' instruction")

	def __str__(self):
		return "ERR"

class NOP(object):
	def __init__(self, args, vm):
		self.vm = vm

	def execute(self):
		return self.vm.cpu.ip + 4

	def __str__(self):
		return "NOP"

class MOV_ABS(object):
	def __init__(self, args, vm):
		self.vm = vm
		self.src = args[0]
		self.dst = args[1]

	def execute(self):
		self.vm.mem[self.dst] = self.vm.mem[self.src]
		return self.vm.cpu.ip + 4

	def __str__(self):
		return "MOV_ABS " + str(self.dest)

class MOV_REL(object):
	def __init__(self, args, vm):
		self.vm = vm
		self.src = args[0]
		self.dst = args[1]

	def execute(self):
		self.vm.mem[self.vm.cpu.ip + self.dst] = self.vm.mem[self.vm.cpu.ip + self.src]
		return self.vm.cpu.ip + 4

	def __str__(self):
		return "MOV_REL " + str(self.dest)

class MOV_IND(object):
	def __init__(self, args, vm):
		self.vm = vm
		self.src = args[0]
		self.dst = args[1]

	def execute(self):
		raise Exception(str(type(self)) + "not implemented yet")

	def __str__(self):
		return "MOV_IND " + str(self.dest)

class JMP_ABS(object):
	def __init__(self, args, vm):
		self.vm = vm
		self.dest = args[0]

	def execute(self):
		return self.dest

	def __str__(self):
		return "MOV_ABS " + str(self.dest)

class JMP_REL(object):
	def __init__(self, args, vm):
		self.vm = vm
		self.dest = args[0]

	def execute(self):
		return self.vm.cpu.ip + self.dest

	def __str__(self):
		return "MOV_REL " + str(self.dest)

class JMP_IND(object):
	def __init__(self, args, vm):
		self.vm = vm
		self.dest = args[0]

	def execute(self):
		raise Exception(str(type(self)) + "not implemented yet")

	def __str__(self):
		return "JMP_IND " + str(self.dest)

class PRINT_DIR(object):
	def __init__(self, args, vm):
		self.vm = vm
		self.arg = args[0]

	def execute(self):
		self.vm.display(self.vm.mem[self.arg])
		return self.vm.cpu.ip + 4

	def __str__(self):
		return "PRINT_DIR " + str(self.arg)

class Instruction(object):
	opcodes =  {0x00 : ERR,
				0x01 : NOP,
				0x02 : JMP_ABS,
				0x03 : JMP_REL,
				0x04 : JMP_IND,
				0x05 : MOV_ABS,
				0x06 : MOV_REL,
				0x07 : MOV_IND,
				0xf0 : PRINT_DIR}

	@staticmethod
	def CreateInstruction(_instr, vm):
		opcode = _instr[0]
		args = _instr[1:]

		if not opcode in Instruction.opcodes:
			raise Exception("Invalid opcode : " + str(opcode))
		else:
			return Instruction.opcodes[opcode](args, vm)
