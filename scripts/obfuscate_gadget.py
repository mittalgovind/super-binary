#!/usr/bin/env python

#
# This file is part of ROPfuscate.
#
# Copyright (C) 2013 Dennis Andriesse <da.andriesse@few.vu.nl>
#
# ROPfuscate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ROPfuscate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ROPfuscate. If not, see <http://www.gnu.org/licenses/>.
#
# See README for more information.
#

#
# Obfuscate a gadget by adding bogus bytes such that it disassembles to 
# incorrect but feasible mnemonics.
#
# Requires Python 2.7+ and distorm3.
#

import sys
import binascii
import random
import distorm3 as distorm

debug = False

# Whitelist of instructions that are allowed in the obfuscated disassembly.
# Most notably, we don't allow privileged or RET instructions.
whitelist = [
    "AAA", "AAS", "ADC", "ADD", "AND", "BOUND", "CALL", # "ARPL"
    "CALLF", "CMP", "CDQ", "CWD", "CLC", "STC", "CLI", 
    "STI", "CLD", "STD", "DAA", "DAS", "DEC", "DIV", "IMUL", 
    "INC", "JO", "JNO", "JB", "JNB", "JE", "JNE", "JBE", 
    "JA", "JS", "JNS", "JPE", "JPO", "JL", "JGE", "JLE", 
#    "JG", "JMP", "LAHF", "LEA", "MOV", "NOP", "OR", "PUSH",
    "JG", "LAHF", "LEA", "MOV", "NOP", "OR", "PUSH", 
    "PUSHAD", "PUSHFD", "POP", "POPAD", "POPFD", "SAHF", "SBB", "SUB", 
    "TEST", "XCHG", "XLAT", "XOR", "BSWAP", "CMPXCHG", "MOVSX", "MOVZX", 
    "LAR", "LSL", "NOT", "NEG", "SHL", "SHR", "SETO", "SETNO", 
    "SETB", "SETNB", "SETE", "SETNE", "SETBE", "SETA", "SETS", "SETNS", 
    "SETPE", "SETPO", "SETL", "SETGE", "SETLE", "SETG", "ROL", "ROR", 
    "RCL", "RCR", "SAL", "SAR", "IMUL", "IDIV"
]

short_jmp = "eb"

def print_disasm(disasm):
    # Human readable disassembly dump.
    if debug:
        for insn in disasm:
            print "0x%08x (%02x) %-20s %s" % (insn[0],  insn[1],  insn[3],  insn[2])
        print

    # Combined amount of bytes in all opcodes of the gadget.
    gadget_len = 0
    for insn in disasm:
        gadget_len = gadget_len + len(insn[3]) / 2

    if gadget_len > 127:
        raise Exception("Offset too large for short jmp.")

    # Byte declarations for embedding in gcc inline AT&T code.
    print "__asm__(\".byte",
    print "0x%s, 0x%02x," % (short_jmp, gadget_len),
    i = len(disasm) - 1
    for insn in disasm:
        # Split opcode hex string at every two characters.
        n = 2
        opcode = insn[3]
        opcode = [opcode[k:k+n] for k in range(0, len(opcode), n)]
        j = len(opcode) - 1
        for o in opcode:
            if i == 0 and j == 0:
                print "0x%s\");" % (o)
            else:
                print "0x%s," % (o),
            j = j - 1
        i = i - 1

def obfuscate_gadget(gadget, mode=32):
    # gadget should be a hex string and mode should be 16, 32 or 64.

    if mode == 16:
        mode = distorm.Decode16Bits
    elif mode == 64:
        mode = distorm.Decode64Bits
    else:
        mode = distorm.Decode32Bits

    true_disasm = distorm.Decode(0, binascii.unhexlify(gadget), mode)

    if debug:
        print_disasm(true_disasm)
        print

    # Add some random prefix and postfix bytes to the gadget until the original
    # gadget is no longer visible in disassembly.
    done = False
    prefix_len = 1
    tries = 0
    max_tries = 250
    while not done:
        if tries == max_tries:
            prefix_len = prefix_len + 1
            tries = 0
        tries = tries + 1

        prefix = ""
        for i in range(0, prefix_len):
            prefix = prefix + "%02x" % (random.randint(0,255))

        obfuscated = prefix + gadget

        bad_disasm = distorm.Decode(0, binascii.unhexlify(obfuscated), mode)

        done = True
        for i in bad_disasm:
            mnem = i[2].split()[0]
            if not mnem in whitelist:
                done = False
                break
        if not done:
            continue

    if debug:
        print_disasm(bad_disasm)
        print

    return obfuscated

def main():
    if len(sys.argv) < 2:
        print >> sys.stderr, "Usage: %s <bytes> [16|32|64]" % (sys.argv[0])
        return 1

    gadget = sys.argv[1]
    if len(sys.argv) > 2:
        mode = int(sys.argv[2])
    else:
        mode = 32

    obfuscated = obfuscate_gadget(gadget, mode)
    print obfuscated

    return 0

if __name__ == "__main__":
    sys.exit(main())

