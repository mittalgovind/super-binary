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
# Scan aligned gadget opcodes and mnemonics from the given range in the binary.
#
# Requires Python 2.7+ and objdump.
#

import sys
import subprocess
import pickle
import pdb

def main():
    if len(sys.argv) < 5:
        print >> sys.stderr, "Usage: %s <binary> <start> <end> <out>" % (sys.argv[0])
        return 1

    binfile = sys.argv[1]
    start   = sys.argv[2]
    end     = sys.argv[3]
    out     = sys.argv[4]

    print "disassembling %s..." % (binfile)
    try:
        disasm = subprocess.check_output([
                     "objdump", "-d", 
                     "--start-address=" + start,
                     "--stop-address=" + end,
                     binfile
                 ])
    except OSError:
        print >> sys.stderr, "cannot execute objdump"
        return 1
    except subprocess.CalledProcessError:
        print >> sys.stderr, "disassembly failed"
        return 1
    print "done"

    print "parsing gadgets..."
    g = [] # each gadget is a list of instructions
    gadgets = [] # list of all gadgets
    for line in iter(disasm.splitlines()):
        line = line.strip()
        try:
            (addr, opcode, mnemonic) = line.split("\t", 2)
            # get the address in hex without trailing characters
            addr = addr.split(":", 1)[0].strip()
            # get the opcode as a hex string
            opcode = "".join(opcode.split()).strip().lower()
            # filter objdump comments from mnemonic
            if "#" in mnemonic:
                (mnemonic, _) = mnemonic.split("#", 1)
            if "<" in mnemonic:
                (mnemonic, _) = mnemonic.split("<", 1)
            mnemonic = mnemonic.strip()
            # append instructions to the gadget until a ret is hit, then add
            # a copy of the gadget to the gadget list
            insn = (addr, opcode, mnemonic)
            g.append(insn)
            if opcode == "c3":
                # pdb.set_trace()
                gadgets.append(g)
                g = []
        except:
            # Ignore bad lines.
            pass
    print "done"

    print "dumping gadgets to %s..." % (out)
    with open(out, "wb") as f:
        pickle.dump(gadgets, f, pickle.HIGHEST_PROTOCOL)
    print "done"

    return 0

if __name__ == "__main__":
    sys.exit(main())

