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
# Completely naive parser for filtering out code lines in assembly produced 
# by gcc and getting their corresponding opcodes.
#
# Requires Python 2.7+ and as.
#

import sys
import binascii
from subprocess import Popen, PIPE

def get_opcode(code_line, mode=32):
    # Return the opcode for the given code line as a hex string.

    try:
        if mode == 64:
            mode = "--64"
        else:
            mode = "--32"

        p = Popen(
                ["as", "-o", "/dev/null", "-al", mode, 
                 "--listing-lhs-width=7", "--listing-cont-lines=0"], 
                stdin = PIPE, stdout = PIPE, stderr = PIPE
            )
        data, err = p.communicate(code_line)

        instr = code_line.split()[0]
        opcode = ""
        for line in iter(data.splitlines()):
            if instr in line:
                opcode = line.split(None, 2)[2]
                opcode = opcode[0:opcode.find(instr)]
                opcode = "".join(opcode.split())
                break

        # Make sure the opcode is a hex string -- this goes wrong if as
        # fails to handle the instruction correctly.
        binascii.unhexlify(opcode)

        return opcode
    except OSError:
        raise Exception("cannot execute as")
    except TypeError:
        raise Exception("failed to get opcode for instruction %s" % (instr))

def get_jmp_target(code_line):
    # Return the target of the jmp on the given code line.
    # The result may be bogus if the line does not contain a jmp instruction.

    return code_line.strip().split()[1]

def get_code_lines(filename, parse_opcodes=False, mode=32):
    # Get a list of all code lines in the given file.
    # Each code line is a (line_number, line) tuple.

    f = open(filename, "rw")

    code_lines = []
    line_number = 1
    is_text_section = False
    for line in f:
        line = line.strip()
        if line.startswith(".text"):
            is_text_section = True
        elif line.startswith(".section"):
            is_text_section = False

        if is_text_section:
            if (line and line[0].isalnum()
                and not line.endswith(":")):
                # This is a code line.
                if parse_opcodes:
                    code_lines.append((line_number, get_opcode(line, mode)))
                else:
                    code_lines.append((line_number, line))

        line_number = line_number + 1

    f.close()

    return code_lines

def is_unconditional_jmp(code_line, include_indirect=True):
    result = code_line.strip().startswith("jmp")
    if include_indirect:
        return result
    else:
        # Only return true if it is not an indirect jmp.
        return result and not code_line.split()[1].startswith("*")

def count_unconditional_jmps(filename, include_indirect=True):
    # Get the number of unconditional jmp instructions in the given
    # file's text sections.

    code_lines = get_code_lines(filename)

    count = 0
    for (line_number, line) in code_lines:
        if is_unconditional_jmp(line, include_indirect):
            count = count + 1

    return count

def dump_code_lines(filename):
    # Dump all code lines in the given file to stdout.

    code_lines = get_code_lines(filename)

    for (line_number, line) in code_lines:
        print "%-5d %-32s %s" % (line_number, get_opcode(line), line)

def main():
    if len(sys.argv) < 2:
        print >> sys.stderr, "Usage: %s <file>" % (sys.argv[0])
        return 1

    dump_code_lines(sys.argv[1])

if __name__ == "__main__":
    sys.exit(main())

