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
# Randomly generate an instruction with the given immediate operand.
#

import sys
import random

# Opcodes which take a long immediate operand.
opcodes = [
# add eax, or eax, adc eax, sbb eax, and eax, sub eax, xor eax, cmp eax
    "05",  "0d",   "15",    "1d",    "25",    "2d",    "35",    "3d",
#   push, test eax, mov <eax/ecx/edx/ebx/esp/ebp/esi/edi>
    "68",  "a9",    "b8", "b9", "ba", "bb", "bc", "bd", "be", "bf"
]

def generate_immediate_instr(immediate):
    # immediate should be a hex string.

    return opcodes[random.randint(0, len(opcodes) - 1)] + immediate

def main():
    if len(sys.argv) < 2:
        print >> sys.stderr, "Usage: %s <immediate>" % (sys.argv[0])
        return 1

    instr = generate_immediate_instr(sys.argv[1])
    print instr

    return 0

if __name__ == "__main__":
    sys.exit(main())

