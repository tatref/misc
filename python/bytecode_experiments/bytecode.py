#!/usr/bin/env python

import dis
import re
import types
import logging


def clean_code(dis_dump):
    """ Remove line number, offsets, and comments/empy lines from dis.dis dumps
    """

    stripped = ''

    l = 0  # line counter for debug
    for line in dis_dump.split('\n'):
        l += 1

        if re.match(r'^\s*(?:#.*)?$', line):
            # ignore comments or empty lines
            continue
        try:
            stripped += re.findall(r'[A-Z_]+(?:\s+[0-9]+)?', line)[0] + '\n'
        except:
            raise Exception("Problem on line " + str(l) + " " + line)

    # remove last \n
    return stripped[:-1]


def assemble(assembly):
    """ assemble clean asembly code
    """

    bytecode = ''

    for line in assembly.split('\n'):
        opname = re.findall(r'[A-Z_]+', line)[0]

        try:
            opcode = dis.opmap[opname]
        except:
            raise Exception('Unknown opcode: ' + opname)

        opcode_str = chr(opcode)

        # append opcode to bytecode
        bytecode += opcode_str

        if opcode > dis.HAVE_ARGUMENT:
            try:
                argument = int(re.findall(r'[0-9]+', line)[0])
            except:
                raise Exception(opname + ' must have argument')

            msb = argument >> 8 & 0xff
            lsb = argument & 0xff

            # append argument to bytecode
            arg_str = chr(lsb) + chr(msb)
            bytecode += arg_str

            logging.debug(opname + ' ' + str(argument))
        else:
            # no arg
            logging.debug(opname)

    # end loop through lines

    return bytecode


def disassemble(bytecode):
    """ Try to disassemble python bytecode, return a string of instructions
    """

    all_opcodes = {dis.opmap[x]:x  for x in dis.opmap}  # reversed opmap dict

    output = ''  # output dis dump

    counter = 0  # instruction pointer
    while counter < len(bytecode):
        opcode = ord(bytecode[counter])

        if not opcode in all_opcodes:
            raise Exception('Invalid opcode: ' + str(opcode))

        current_opname = all_opcodes[opcode]
        output += str(counter) + '\t' + current_opname + '\t\t'

        if opcode > dis.HAVE_ARGUMENT:
            arg = ord(bytecode[counter + 1]) + (ord(bytecode[counter + 2]) << 8)
            output += str(arg)

            counter += 2

        output += '\n'

        counter += 1
    return output

def assemble_example():
    """ Example of compilation & execution of homemade bytecode (jump into middle of instruction)
    """

    # JUMP into middle of opcode (0x09 = NOP)
    dis_dump = """

0  JUMP_ABSOLUTE 5

3  JUMP_ABSOLUTE 2313 # 0x0909

6 LOAD_CONST 0
9 RETURN_VALUE

"""

    cleaned_assembly = clean_code(dis_dump)

    # generate bytecode
    my_bytecode = assemble(cleaned_assembly)
    print ':'.join(x.encode('hex') for x in my_bytecode)

    # function to bind to
    def f():
        a = None
        b = 1

    c = f.__code__

    # create new code object
    my_code = types.CodeType(c.co_argcount, c.co_nlocals, c.co_stacksize, c.co_flags, my_bytecode, c.co_consts, c.co_names, c.co_varnames, c.co_filename, c.co_name, c.co_firstlineno, c.co_lnotab)

    # bind to function
    f.__code__ = my_code

    # execute byte code
    val = f()
    print val


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.DEBUG)

    bytecode = '|\x00\x00|\x01\x00k\x04\x00r\x14\x00d\x01\x00GHn\x04\x00t\x00\x00Sd\x00\x00S'

    print disassemble(bytecode)
