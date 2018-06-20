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
# Insert the given set of gadgets into the assembly file(s) and prepare
# the specified amount of payload bytes.
#
# Requires Python 2.7+.
#

import sys
import pickle
import random
import math
import fileinput
import getopt

from parse_asm import get_code_lines, get_opcode, get_jmp_target, \
                      is_unconditional_jmp, count_unconditional_jmps
from dump_gadgets_asm import dump_gadget_asm
from obfuscate_gadget import obfuscate_gadget
from generate_immediate_instr import generate_immediate_instr
from generate_opaque_jmp import generate_opaque_jmp


# Architecture dependent configuration
x86_mode = 32             # 32 bit mode.
bytes_per_immediate = 4   # Bytes per immediate on x86-32.
payload_per_immediate = 2 # Payload bytes per immediate on x86-32.
short_jmp = "eb"          # Opcode for short jmp.

# Options and globals derived from options
verbose = True            # Verbose.
hardcoded_payload = False # Hardcoded payload
max_groups = 10           # Maximum number of instruction groups per asm file.
output_probability = 0.1  # Probability that we output an instruction group.
payload_bytes = 0         # Required amount of payload bytes.
nr_immediates = 0         # Number of immediates required for payload bytes.

# Configuration of ropc parameters.
#skip_postfix_len = 7*4 # The last 7*4 payload bytes contain a "crash address",
#                       # we skip this as we aim to exit gracefully.


def test_file_exists(filename, mode):
    try:
        with open(filename, mode) as f:
            pass
    except IOError:
        print >> sys.stderr, "file not found: %s" % (filename)
        return False

    return True


def gadget_to_hex_string(gadget):
    gadget_hex = ""
    for insn in gadget:
        (_, insn_hex, _) = insn
        gadget_hex = gadget_hex + insn_hex

    return gadget_hex


def dump_bins_histogram(bins, total_items):
    for asm, items in bins.iteritems():
        print "%-32s :" % (asm),
        if len(items) > 0 and total_items > 0:
            print "*" * int(math.ceil(80*(len(items)/float(total_items)))),
        print "(%d)" % (len(items))


def distribute_items_over_asm_files(items, asm_files, asm_loc, total_loc):
    bins = {}
    i = 0
    nr_items = len(items)
    for asm in asm_files:
        count = int(math.ceil(nr_items*(asm_loc[asm]/float(total_loc))))
        bins[asm] = items[i:i + count]
        i = i + count

    return bins


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


def scan_gadgets(gadgets, code_lines):
    # Scan the given code lines for existing gadgets from the given gadget
    # set, including unaligned candidates in the code lines.

    # Build list of candidate hex strings, consisting of consecutive 
    # opcodes in the code lines.
    # NOTE: this heuristic is not ideal, as it also filters out gadgets
    #       which are consecutive in the binary, but are not on consecutive 
    #       lines due to label lines etc.
    candidates = []
    candidate_hex = ""
    prev_line_number = -1
    for line_number, line in code_lines:
        if prev_line_number + 1 != line_number:
            if len(candidate_hex) > 0:
                candidates.append(candidate_hex.lower())
                candidate_hex = ""
        prev_line_number = line_number
        candidate_hex = candidate_hex + get_opcode(line, x86_mode)

    # Add trailing candidate if any.
    if len(candidate_hex) > 0:
        candidates.append(candidate_hex.lower())

    # Try to find the given gadgets in the candidate hex strings.
    matches = []
    for g in gadgets:
        gadget_hex = gadget_to_hex_string(g)
        found_match = False
        for c in candidates:
            offsets = find_all(c, gadget_hex)
            for off in offsets:
                if off != -1 and off % 2 == 0:
                    # Found a match!
                    matches.append(g)
                    found_match = True
                    break
            if found_match:
                break

    return matches


def hex_string_to_byte_declaration(hex_string, identifier):
    # Create an assembly byte declaration line out of a hex string.

    result = "\t.byte "
    n = 2
    hex_string = [hex_string[i:i+n] for i in range(0, len(hex_string), n)]
    i = len(hex_string) - 1
    for byte in hex_string:
        if i == 0:
            # Mark each byte declaration with an identifier comment.
            result = result + "0x%s\t/* <%s> */\n" % (byte, identifier)
        else:
            result = result + "0x%s, " % (byte)
        i = i - 1
    return result


def create_instruction_groups(file_id, gadgets, fake_imms, nr_groups):
    # Scatter the given gadgets and fake immediates over the groups.

    groups = [".group_" + str(file_id) + "_" + str(label) + ":\n" \
              for label in range(0, nr_groups)]

    i = 0
    gadgets = list(gadgets)
    fake_imms = list(fake_imms)
    while len(gadgets) > 0 or len(fake_imms) > 0:
        n = random.randint(0,1)
        if n == 0 and len(gadgets) > 0:
            groups[i] = groups[i] + hex_string_to_byte_declaration(
                                        gadgets.pop(), "gadget")
        elif len(fake_imms) > 0:
            # Give every fake immediate a label so we can find it back in the
            # binary and patch it later. For convenience, the numbering of
            # fake immediates runs from high to low.
            groups[i] = groups[i] + ".immediate_" + str(file_id) + "_" \
                                    + str(len(fake_imms) - 1) + ":\n"
            groups[i] = groups[i] + hex_string_to_byte_declaration(
                                        fake_imms.pop(), "payload")
        i = (i + 1) % len(groups)

    return groups


def write_bins_to_file(bins, asm_loc):
    # Write all gadgets/fake_jmps/fake_immediates from each bin 
    # to their appointed file.

    file_id = 0 # Used to generate globally unique labels.
    for asm, (gadgets, fake_jmps, fake_imms) in bins.iteritems():
        # Check if there is anything to do for this file.
        if len(gadgets) == 0 and len(fake_jmps) == 0 and len(fake_imms) == 0:
            continue

        # Divide gadgets and fake immediates into groups, at most one group 
        # per unconditional jmp
        nr_groups = count_unconditional_jmps(asm, False)
        if nr_groups < 1:
            raise Exception("no unconditional jmps found in %s" % (asm))
        elif nr_groups > max_groups:
            nr_groups = max_groups
        groups = \
            create_instruction_groups(file_id, gadgets, fake_imms, nr_groups)

        # Distribute the groups over the unconditional jmps.
        # Multiple passes may be necessary because the groups are added 
        # probabilistically.
        while len(groups) > 0:
            is_text_section = False
            for line in fileinput.input(asm, inplace=1):
                if line.strip().startswith(".text"):
                    is_text_section = True
                elif line.strip().startswith(".section"):
                    is_text_section = False
    
                if is_text_section and is_unconditional_jmp(line, False) and \
                   len(groups) > 0 and random.random() < output_probability:

                    # Replace the original unconditional jmp with an opaquely
                    # true jmp -- this makes the inserted instruction group
                    # seem reachable through the fallthrough edge
                    print generate_opaque_jmp(get_jmp_target(line), True),
                    print groups.pop(),
                else:
                    print line,

        file_id = file_id + 1

        # TODO: write fake jmps

        print "%s written" % (asm)


def print_usage(myname):
    print >> sys.stderr, "Usage: %s [Hmrpvsqh] gadgets asm [asm ...]" % (myname)
    print >> sys.stderr, "Insert the given set of gadgets into the assembly file(s)."
    print >> sys.stderr, ""
    print >> sys.stderr, "-H, --hardcoded-payload                  prepare for hardcoded payload"
    print >> sys.stderr, "-m, --max-groups=<count>                 max instruction groups per asm file"
    print >> sys.stderr, "-r, --payload-bytes=<count>              amount of payload bytes to be reserved"
    print >> sys.stderr, "-p, --output-probability=<probability>   probability that an instruction group is emitted"
    print >> sys.stderr, "-v                                       verbose"
    print >> sys.stderr, "-s, -q                                   silent/quiet"
    print >> sys.stderr, "-h                                       help"


def parse_arguments(argv):
    global verbose
    global hardcoded_payload
    global max_groups
    global output_probability
    global payload_bytes
    global nr_immediates

    try:
        opts, args = getopt.getopt(argv[1:], "Hm:r:p:vsqh", ["hardcoded-payload", 
                                   "max-groups=", "payload-bytes=", "output-probability="])
    except getopt.GetoptError as err:
        print >> sys.stderr, str(err)
        print_usage(argv[0])
        sys.exit(1)

    if len(args) < 2:
        print_usage(argv[0])
        sys.exit(1)

    gadget_file = args[0]
    asm_files = args[1:]

    # Remove duplicates from asm file list.
    asm_files = list(set(asm_files))

    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o == "-s" or o == "-q":
            verbose = False
        elif o == "-h":
            print_usage(argv[0])
            sys.exit(1)
        elif o in ("-H", "--hardcoded-payload"):
            hardcoded_payload = True
        elif o in ("-m", "--max-groups"):
            max_groups = int(a)
            if not max_groups > 0:
                print >> sys.stderr, "-m, --max-groups must be > 0"
                print_usage(argv[0])
                sys.exit(1)
        elif o in ("-r", "--payload-bytes"):
            payload_bytes = int(a) 
            # Don't reserve space for ropc's "crash addresses"
            #print ("stripping %d payload bytes to compensate for "
            #       "ropc crash addresses") % (skip_postfix_len)
            #payload_bytes = payload_bytes - skip_postfix_len
            if not payload_bytes > 0:
                #print >> sys.stderr, "-r, --payload-bytes must be > %d" % (skip_postfix_len)
                print >> sys.stderr, "-r, --payload-bytes must be > 0"
                print_usage(argv[0])
                sys.exit(1)
        elif o in ("-p", "--output-probability"):
            gadget_probability = float(a)
            if not gadget_probability < 1.0 or not gadget_probability > 0.0:
                print >> sys.stderr, "-p, --output-probability must be > 0.0 and < 1.0"
                print_usage(argv[0])
                sys.exit(1)
        else:
            print >> sys.stderr, "unhandled option %s" % (o)
            print_usage(argv[0])
            sys.exit(1)

    if payload_bytes == 0:
        print >> sys.stderr, "warning: no payload bytes will be reserved"

    if hardcoded_payload:
        nr_immediates = 0
    else:
        nr_immediates = int(math.ceil(payload_bytes/float(payload_per_immediate)))

    return (gadget_file, asm_files)


def main():
    # Parse command line arguments.
    (gadget_file, asm_files) = parse_arguments(sys.argv)

    # Check that the gadget file exists.
    if not test_file_exists(gadget_file, "rb"):
        return 1

    # Check that the asm files exist.
    for asm in asm_files:
        if not test_file_exists(asm, "r"):
            return 1

    # Load gadgets from previously pickled file.
    print "loading gadgets from %s..." % (gadget_file)
    with open(gadget_file, "rb") as f:
        gadgets = pickle.load(f)
    nr_bytes = 0
    for g in gadgets:
        for (_, opcode, _) in g:
            nr_bytes = nr_bytes + len(opcode)/2
    print "loaded %d gadgets (%d bytes)" % (len(gadgets), nr_bytes)

    # Scan opcodes of existing instructions in the asm files to see which 
    # gadgets are already there.
    print "scanning for existing gadgets..."
    existing_gadgets = []
    for asm in asm_files:
        matches = scan_gadgets(gadgets, get_code_lines(asm))
        print "matched %d gadgets in %s" % (len(matches), asm),
        n = 0
        for m in matches:
            if m not in existing_gadgets:
                existing_gadgets.append(m)
                n = n + 1
        print "(%d new)" % (n)
    print "found %d existing gadgets" % (len(existing_gadgets))

    if verbose:
        for g in existing_gadgets:
            dump_gadget_asm(g)

    # Remove existing gadgets from the gadget list -- no need to add them.
    print "updating required gadget list..."
    for g in existing_gadgets:
        gadgets.remove(g)
    print "new list length is %d gadgets" % (len(gadgets))

    # Select short gadgets (at most 2 bytes) for use as jmp offsets
    print "selecting gadgets for fake jmps..."
    fake_jmps = []
    nr_bytes = 0
    # NOTE: fake jmps are disabled for now, as jmp offsets containing gadgets
    # are typically too long
    print "feature disabled"
    #for g in gadgets:
    #    g = gadget_to_hex_string(g)
    #    if len(g)/2 <= 2:
    #        nr_bytes = nr_bytes + len(g)/2
    #        fake_jmps.append(g)
    print "selected %d gadgets (%d bytes)" % (len(fake_jmps), nr_bytes)

    # Generate fake immediate instructions.
    print "generating %d fake immediate instructions..." % (nr_immediates)
    fake_immediates = []
    for i in range(0, nr_immediates):
        fake_immediates.append(
            generate_immediate_instr("00" * bytes_per_immediate))
    print "done"

    # Obfuscate the gadgets.
    print "obfuscating remaining gadgets..."
    obfuscated_gadgets = []
    nr_bytes = 0
    for g in gadgets:
        g_hex = gadget_to_hex_string(g)
        if g_hex not in fake_jmps:
            g_hex = obfuscate_gadget(g_hex)
            nr_bytes = nr_bytes + len(g_hex)/2
            obfuscated_gadgets.append(g_hex)
    print "done, obfuscated %d gadgets (%d bytes)" % \
              (len(obfuscated_gadgets), nr_bytes)

    # TODO: add opaque predicates to fake jmps

    # Permute the gadget list.
    print "permuting gadget list..."
    random.shuffle(gadgets)
    print "done"

    # Permute the fake jmp target list.
    print "permuting fake jmp list..."
    random.shuffle(fake_jmps)
    print "done"

    # Compute lines of code per asm file
    asm_loc = {}
    total_loc = 0
    for asm in asm_files:
        asm_loc[asm] = len(get_code_lines(asm))
        total_loc = total_loc + asm_loc[asm]

    # Distribute fake jmps over asm files.
    print "distributing fake jmps over asm files..."
    fake_jmp_bins = distribute_items_over_asm_files(fake_jmps, asm_files, 
                                                    asm_loc, total_loc)
    print "done"
    if verbose:
        dump_bins_histogram(fake_jmp_bins, len(fake_jmps))

    # Distribute gadgets over asm files.
    print "distributing obfuscated gadgets over asm files..."
    gadget_bins = distribute_items_over_asm_files(obfuscated_gadgets, asm_files,
                                                  asm_loc, total_loc)
    print "done"
    if verbose:
        dump_bins_histogram(gadget_bins, len(obfuscated_gadgets))

    # Distribute fake immediates over asm files.
    if nr_immediates > 0:
        print "distributing fake immediates over asm files..."
        fake_imm_bins = distribute_items_over_asm_files(fake_immediates, asm_files,
                                                        asm_loc, total_loc)
        print "done"
        if verbose:
            dump_bins_histogram(fake_imm_bins, len(fake_immediates))
    else:
        fake_imm_bins = {}
        for asm in asm_files:
            fake_imm_bins[asm] = []

    # Merge bin dictionaries into a dictionary of tuples per asm file
    # (gadgets, fake jmps, fake immediates).
    bins = {}
    for asm, gadgets in gadget_bins.iteritems():
        bins[asm] = (gadgets, fake_jmp_bins[asm], fake_imm_bins[asm])

    # Write output.
    print "writing to asm files (%d gadgets, %d fake jmps, %d immediates)..." %\
              (len(obfuscated_gadgets), len(fake_jmps), len(fake_immediates))
    try:
        write_bins_to_file(bins, asm_loc)
    except Exception as e:
        print >> sys.stderr, e
        return 1
    print "done"

    return 0

if __name__ == "__main__":
    sys.exit(main())

