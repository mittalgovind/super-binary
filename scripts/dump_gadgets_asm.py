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
# Dump assembly for the gadgets in the given file, which should be a
# gadgets file created by scan_gadgets.py.
#

import sys
import pickle

def dump_gadget_asm(g):
    for insn in g:
        (addr, opcode, mnemonic) = insn
        print "%-8s: %-32s %s" % (addr, opcode, mnemonic)

def main():
    if len(sys.argv) < 2:
        print >> sys.stderr, "Usage: %s <file>" % (sys.argv[0])
        return 1

    infile = sys.argv[1]

    with open(infile, "rb") as f:
        gadgets = pickle.load(f)

    for g in gadgets:
        dump_gadget_asm(g)

    return 0

if __name__ == "__main__":
    sys.exit(main())

