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
# Get a mapping from the original placeholder gadget addresses to the actual 
# addresses found in the binary.
#
# Requires Python 2.7+ and objdump.
#

import sys
import subprocess
import pickle

from dump_gadgets_asm import dump_gadget_asm


def test_file_exists(filename, mode):
    try:
        with open(filename, mode) as f:
            pass
    except IOError:
        print >> sys.stderr, "file not found: %s" % (filename)
        return False

    return True


def parse_candidate_hex_strings(disasm_opcode_addrs):

    # Build dictionary of candidate hex strings, keyed by start address.
    # Each hex string is a consecutive byte sequence in the binary, so 
    # gadgets can be found using a simple string search.
    candidates = {}
    candidate_hex = ""
    next_addr = -1
    start_addr = 0
    for (d_addr, d_opcode) in disasm_opcode_addrs:
        if d_addr != next_addr:
            if len(candidate_hex) > 0:
                candidates[start_addr] = candidate_hex.lower()
                candidate_hex = ""

        if len(candidate_hex) == 0:
            start_addr = d_addr

        next_addr = format(int(d_addr, base=16) + len(d_opcode)/2, "x")
        candidate_hex = candidate_hex + d_opcode

    # Add trailing candidate if any.
    if len(candidate_hex) > 0:
        candidates[start_addr] = candidate_hex.lower()

    return candidates


def gadget_to_hex_string(gadget):
    gadget_hex = ""
    for insn in gadget:
        (_, insn_hex, _) = insn
        gadget_hex = gadget_hex + insn_hex

    return gadget_hex


def find_all(haystack, needle):
    # Find all offsets into the haystack string where the needle
    # substring is contained.

    start = 0
    found = []
    while start != -1:
        start = haystack.find(needle, start)
        if start != -1:
            found.append(start)
            start = start + 1

    return found


def scan_gadgets(gadgets, disasm_opcode_addrs):

    # Find gadgets in the candidate hex strings using simple string matching.
    # Compute gadget start addresses by adding the byte offset into the string
    # to the start address of the string.

    candidates = parse_candidate_hex_strings(disasm_opcode_addrs)
    matches = {}
    for g in gadgets:
        (g_addr, _, _) = g[0]
        gadget_hex = gadget_to_hex_string(g)
        found_match = False
        for c_start, c_hex in candidates.iteritems():
            offsets = find_all(c_hex, gadget_hex)
            for off in offsets:
                if off != -1 and off % 2 == 0:
                    # Found a match!
                    matches[g_addr] = format(int(c_start, base=16) + off/2, "x")
                    found_match = True
                    break
            if found_match:
                break

    return matches


def get_disasm_opcode_addrs(binary_file):

    # Disassemble binary file.
    try:
        disasm = subprocess.check_output([
                     "objdump", "-d", 
                     binary_file
                 ])
    except OSError:
        raise Exception("cannot execute objdump")
    except subprocess.CalledProcessError:
        raise Exception("disassembly failed")

    # Parse disassembly into (address, opcode) tuples.
    disasm_opcode_addrs = []
    for line in iter(disasm.splitlines()):
        line = line.strip()
        try:
            (addr, opcode, mnemonic) = line.split("\t", 2)
            # get the address in hex without trailing characters
            addr = addr.split(":", 1)[0].strip()
            # get the opcode as a hex string
            opcode = "".join(opcode.split()).strip().lower()

            disasm_opcode_addrs.append((addr, opcode))
        except:
            # Ignore bad lines.
            pass

    return disasm_opcode_addrs


def main():
    if len(sys.argv) < 3:
        print >> sys.stderr, "Usage: %s <gadgets> <binary>" % (sys.argv[0])
        return 1

    gadget_file = sys.argv[1]
    binary_file = sys.argv[2]

    if not test_file_exists(gadget_file, "rb"):
        return 1
    if not test_file_exists(binary_file, "rb"):
        return 1

    # Load previously parsed gadgets.
    with open(gadget_file, "rb") as f:
        gadgets = pickle.load(f)

    # Get list of (address, opcode) tuples for the binary.
    try:
        disasm_opcode_addrs = get_disasm_opcode_addrs(binary_file)
    except Exception as e:
        print >> sys.stderr, e
        return 1

    # Create address map.
    gadget_addrs = scan_gadgets(gadgets, disasm_opcode_addrs)
    addr_map = []
    for g in gadgets:
        (g_addr, _, _) = g[0]
        try:
            d_addr = gadget_addrs[g_addr]
            addr_map.append((g_addr, d_addr))
        except KeyError,e:
            print >> sys.stderr, "Unable to find match for the following gadget "
	    dump_gadget_asm(g)
            return 1

    # Resolve conflicts which occur when a previously patched address
    # reappears as the left hand side of a patch.
    max_rounds = 50
    for r in range(0, max_rounds):
        patches = []
        have_conflicts = False
        for i in range(0, len(addr_map)):
            (addr, patch) = addr_map[i]
            if addr in patches:
                # Addr appears as lhs, but was previously patched. Resolve
                # the conflict by moving addr to the front of the list.
                have_conflicts = True
                addr_map.pop(i)
                addr_map.insert(0, (addr, patch))

            patches.append(patch)

        if not have_conflicts:
            break

    if have_conflicts:
        print >> sys.stderr, "unable to resolve patch ordering conflicts"
        return 1

    for (addr, patch) in addr_map:
        print "0x%s -> 0x%s" % (addr, patch)

    return 0

if __name__ == "__main__":
    sys.exit(main())

