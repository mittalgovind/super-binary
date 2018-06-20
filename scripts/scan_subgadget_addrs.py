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
# Sometimes ropc uses "unintended" gadgets which are inside other gadgets.
# The addresses of these gadgets are not found by the normal patching routine,
# so we explicitly enumerate them here to allow for patching them.
#

import sys
import pickle
import traceback

def main():
    if len(sys.argv) < 4:
        print >> sys.stderr, "Usage: %s <intended-gadgets> <used-gadgets> <out>" % (sys.argv[0])
        return 1

    intended_gadgets = sys.argv[1]
    used_gadgets = sys.argv[2]
    out = sys.argv[3]

    with open(intended_gadgets, "rb") as f:
        intended_gadgets = pickle.load(f)

    print "scanning for subgadgets"
    subgadgets = []
    with open(used_gadgets, "r") as f:
        for line in f.readlines():
            try:
                # Extract start and end address of used gadget.
                line = line.split("(")[2]
                line = line.split(")")[0]

                start = line.split(",")[0].strip()
                end = line.split(",")[1].strip()

                start = start[2:].strip()
                end = end[2:].strip()
                
                # Try to find the start address in the intended gadgets.
                found = False
                start = int(start, base=16)
                for g in intended_gadgets:
                    (addr, _, _) = g[0]
                    addr = int(addr, base=16)
                    if addr == start:
                        found = True
                        break
                if not found:
                    # This is a "subgadget", find the gadget it is in.
                    for g in intended_gadgets:
                        (s_addr, _, _) = g[0]
                        s_addr = int(s_addr, base=16)
                        (e_addr, e_opcode, _) = g[len(g) - 1]
                        e_addr = int(e_addr, base=16) + len(e_opcode)/2
                        if start >= s_addr and start < e_addr:
                            #print "(0x%s, 0x%s) is in (0x%s, 0x%s)" % \
                            #      (format(start, "x"), end, 
                            #       format(s_addr, "x"), format(e_addr, "x"))
                            diff = start - s_addr
                            print "0x%s + 0x%s" % \
                                  (format(s_addr, "x"), format(diff, "x"))

                            # Add subgadget to the subgadgets list.
                            sub_g = []
                            for (addr, opcode, mnemonic) in g:
                                if int(addr, base=16) >= start:
                                    sub_g.append((addr, opcode, mnemonic))
                            subgadgets.append(sub_g)
                            break
            except:
                pass

    # Add the subgadgets to the gadgets list       
    print "adding subgadgets to gadget list"
    subgadgets_uniq = []
    for sub_g in subgadgets:
        if not sub_g in subgadgets_uniq:
            subgadgets_uniq.append(sub_g)
    for sub_g in subgadgets_uniq:
        intended_gadgets.append(sub_g)

    print "dumping updated gadget list to %s" % (out)
    with open(out, "wb") as f:
        pickle.dump(intended_gadgets, f, pickle.HIGHEST_PROTOCOL)

    return 0

if __name__ == "__main__":
    sys.exit(main())

