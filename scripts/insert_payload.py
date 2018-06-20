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
# Insert the given ROP payload into the fake immediates in the given binary.
#
# Requires Python 2.7+, PyCrypto, readelf and objdump.
#

import sys
import os
import subprocess
import binascii
import math
import struct
import traceback
from Crypto.Cipher import ARC4

from get_patch_addr_mapping import get_disasm_opcode_addrs, scan_gadgets

# Architecture-specific configuration.
imm_bytes = 4                  # Bytes per immediate.
max_offset = 65535             # Maximum offset to next immediate.
imm_payload_bytes = 2          # Payload bytes per immediate.
imm_offset_bytes = 2           # Offset bytes per immediate.
imm_payload_mask = 0xffff0000  # Mask for payload part of immediate.
imm_offset_mask = 0x0000ffff   # Mask for offset part of immediate.
imm_payload_pack_type = "<H"   # Type of payload part -- little endian ushort.
imm_offset_pack_type = "<H"    # Type of offset part -- little endian ushort.
imm_pack_type = "<I"           # Pack type of immediate -- little endian uint.
pop_esp_gadget = [(0, "5c", ""), (0, "c3", "")] # Opcodes for pop esp, ret.

# Label strings.
text_section_label = ".text"
data_section_label = ".data"
immediate_label = ".immediate"
call_site_label = ".ropfuscate_call_"
pop_esp_gadget_pointer_label = ".gadget_pointer_pop_esp"
payload_buf_sym = "payload"
payload_len_sym = "payload_len"
hardcoded_label_postfix = "_hardcoded"

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

def find_instr_operand_addend(f, offset):
    # Find the addend that must be added to the instruction offset to obtain
    # the location of the instruction's unpatched operand. Assume that the 
    # operand is initially zeroed out.

    limit = 20
    addend = 0
    while addend < limit:
        f.seek(offset + addend)
        if f.read(imm_bytes) == "\0" * imm_bytes:
            # Found the instruction's immediate operand, roll back the file 
            # pointer to point to the operand, and return the addend.
            f.seek(offset + addend)
            return addend
        addend = addend + 1

    return -1

def patch_immediate(f, offset, value):
    # Patch the immediate instruction at offset in file f so that its operand 
    # contains value. Value must be a byte string.

    if len(value) > imm_bytes:
        print >> sys.stderr, "value too large for %s byte immediate" % (imm_bytes)
        return False

    addend = find_instr_operand_addend(f, offset)
    if addend < 0:
        return False
    else:
        print "patching %d bytes at 0x%x+0x%x to 0x%s" % \
              (len(value), offset, addend, binascii.hexlify(value))
        f.write(value)
        return True

def main():
    global pop_esp_gadget_pointer_label

    if len(sys.argv) < 4:
        print >> sys.stderr, "Usage: %s <binary> <rop-payload> <RC4-key> [--win32] [--hardcoded-payload]" % (sys.argv[0])
        return 1

    binfile = sys.argv[1]
    payloadfile = sys.argv[2]
    RC4_key = sys.argv[3]

    windows = False
    if sys.argv[4] == "--win32":
        print "entering Windows mode"
        windows = True

    hardcoded_payload = False
    if sys.argv[4] == "--hardcoded-payload" or sys.argv[5] == "--hardcoded-payload":
        print "hardcoding payload"
        hardcoded_payload = True

    if hardcoded_payload:
        pop_esp_gadget_pointer_label = pop_esp_gadget_pointer_label + hardcoded_label_postfix

    if not test_file_exists(binfile, "rb"):
        return 1
    elif not test_file_exists(payloadfile, "rb"):
        return 1

    print "using RC4 for encryption, key = \"%s\"" % (RC4_key)

    try:
        f = open(payloadfile, "rb")
        payload = f.read()
        #payload = payload[:(-1)*skip_postfix_len] # Strip "crash addresses".
        f.close()
    except IOError:
        print >> sys.stderr, "failed to read file: %s" % (payloadfile)
        return 1

    print "read %d payload bytes" % (len(payload))
    if len(payload) == 0:
        print >> sys.stderr, "nothing to do"
        return 1

    # Scan the binary for the location of the text section, immediates, and
    # any items that need to be patched.
    print "scanning binary"
    if windows:
        section_scanner = ["objdump", "--wide", "--section-headers", binfile]
        symbol_scanner = ["objdump", "--wide", "--syms", binfile]
    else:
        section_scanner = ["readelf", "--wide", "--sections", binfile]
        symbol_scanner = ["readelf", "--wide", "--syms", binfile]

    text_section_info = None
    data_section_info = None
    try:
        data = subprocess.check_output(section_scanner)
        for line in iter(data.splitlines()):
            if text_section_label in line:
                # Found text section address and file offset.
                text_section_info = line
            elif data_section_label in line:
                # Found data section address and file offset.
                data_section_info = line
            if not text_section_info is None and not data_section_info is None:
                break
    
        immediate_info = []
        call_sites = []
        gadget_pointers = []
        payload_buf_info = None
        payload_len_info = None
        data = subprocess.check_output(symbol_scanner)
        for line in iter(data.splitlines()):
            if immediate_label in line:
                # Found immediate which can be used for storing payload.
                immediate_info.append(line)
            elif (call_site_label + 
                  os.path.splitext(os.path.basename(payloadfile))[0] in line):
                # Found call site which needs to be patched.
                call_sites.append(line)
            elif pop_esp_gadget_pointer_label in line:
                # Found pop esp gadget pointer which needs to be patched.
                gadget_pointers.append(line)
            elif payload_len_sym in line:
                payload_len_info = line
            elif payload_buf_sym in line:
                payload_buf_info = line
    
        disasm_opcode_addrs = get_disasm_opcode_addrs(binfile)
        data = scan_gadgets([pop_esp_gadget], disasm_opcode_addrs)
        if len(data) == 0:
            pop_esp_addr = None
        else:
            (_, pop_esp_addr) = data.popitem()
    except OSError:
        print >> sys.stderr, "cannot execute %s" % (symbol_scanner[0],)
        return 1
    except subprocess.CalledProcessError:
        print >> sys.stderr, "%s failed" % (symbol_scanner[0],)
        return 1
    except:
        print >> sys.stderr, traceback.format_exc()
        return 1

    if text_section_info is None:
        print >> sys.stderr, "failed to locate text section"
        return 1
    else:
        # Get the text section memory address, file offset, and length.
        if windows:
            text_section_info = text_section_info.split()
            text_mem_start = int(text_section_info[3], base=16)
            text_file_start = int(text_section_info[5], base=16)
            text_len = int(text_section_info[2], base=16)
        else:
            text_section_info = text_section_info.split()
            text_mem_start = int(text_section_info[3], base=16)
            text_file_start = int(text_section_info[4], base=16)
            text_len = int(text_section_info[5], base=16)

    print ".text at  mem 0x%x  file 0x%x  len 0x%x" % \
              (text_mem_start, text_file_start, text_len)

    if data_section_info is None:
        print >> sys.stderr, "failed to locate data section"
        return 1
    else:
        # Get the data section memory address, file offset, and length.
        if windows:
            data_section_info = data_section_info.split()
            data_mem_start = int(data_section_info[3], base=16)
            data_file_start = int(data_section_info[5], base=16)
            data_len = int(data_section_info[2], base=16)
        else:
            data_section_info = data_section_info.split()
            data_mem_start = int(data_section_info[3], base=16)
            data_file_start = int(data_section_info[4], base=16)
            data_len = int(data_section_info[5], base=16)

    print ".data at  mem 0x%x  file 0x%x  len 0x%x" % \
              (data_mem_start, data_file_start, data_len)

    if hardcoded_payload:
        print "hardcoded payload, skipping search for fake immediates"
        immediate_info = []
        required_immediates = 0
    else:
        if len(immediate_info) == 0:
            print >> sys.stderr, "no immediates found"
            return 1
        else:
            # Get each immediate's memory address, file offset, and offset to the
            # next immediate.
            if windows:
                immediate_info = [int(i.split()[-2], base=16) for i in immediate_info]
                immediate_info.sort()
                immediate_info = \
                    [(text_mem_start + i, text_file_start + i, 0) for i in immediate_info]
            else:
                immediate_info = [int(i.split()[1], base=16) for i in immediate_info]
                immediate_info.sort()
                immediate_info = \
                    [(i, i - text_mem_start + text_file_start, 0) for i in immediate_info]
            for i in range(0, len(immediate_info)):
                (imm_mem, imm_file, imm_next) = immediate_info[i]
                if i + 1 < len(immediate_info):
                    imm_next = immediate_info[i + 1][0] - imm_mem
                    if imm_next > max_offset:
                        print >> sys.stderr, "offset too large (have %d, max %d)" % \
                                             (imm_next, max_offset)
                        print >> sys.stderr, "-> immediate at  mem 0x%x  file 0x%x  next +0x%x" % \
                                             (imm_mem, imm_file, imm_next)
                        return 1
                else:
                    imm_next = 0
                immediate_info[i] = (imm_mem, imm_file, imm_next)
    
        print "found %d immediates at" % (len(immediate_info))
        for i in immediate_info:
            print "  mem 0x%x  file 0x%x  next +0x%x" % (i[0], i[1], i[2])
    
        required_immediates = int(math.ceil(len(payload)/float(imm_payload_bytes)))
        if len(immediate_info) < required_immediates:
            print >> sys.stderr, "not enough immediates to store payload (have %d, need %d)" % \
                                 (len(immediate_info), required_immediates)
            return 1

    if hardcoded_payload:
        print "hardcoded payload, skipping search for call sites"
        call_sites = []
    else:
        if len(call_sites) == 0:
            print >> sys.stderr, "no call sites found for payload %s" % (payloadfile)
            return 1
        else:
            # Get the address and file offset of each call site.
            if windows:
                call_sites = [int(c.split()[-2], base=16) for c in call_sites]
                call_sites = \
                    [(text_mem_start + c, text_file_start + c) for c in call_sites]
            else:
                call_sites = [int(c.split()[1], base=16) for c in call_sites]
                call_sites = \
                    [(c, c - text_mem_start + text_file_start) for c in call_sites]
    
        print "found %d call sites at" % (len(call_sites))
        for c in call_sites:
            print "  mem 0x%x  file 0x%x" % (c[0], c[1])

    if hardcoded_payload:
        #### If we're using a hardcoded payload, we need the address of the 
        #### reserved payload buffer and the variable storing its length
        if payload_buf_info is None:
            print >> sys.stderr, "cannot find reserved payload buffer \"%s\"" % (payload_buf_sym,)
            return 1
        elif payload_len_info is None:
            print >> sys.stderr, "cannot find reserved payload length \"%s\"" % (payload_len_sym,)
            return 1
        pbi = payload_buf_info
        pli = payload_len_info
        if windows:
            pbi = (int(pbi.split()[-2], base=16), 0, pbi.split()[-1])
            pbi = (data_mem_start + pbi[0], data_file_start + pbi[0], pbi[2])
            pli = (int(pli.split()[-2], base=16), 0, pli.split()[-1])
            pli = (data_mem_start + pli[0], data_file_start + pli[0], pli[2])
        else:
            pbi = (int(pbi.split()[1], base=16), 0, pbi.split()[7])
            pbi = (pbi[0], pbi[0] - data_mem_start + data_file_start, pbi[2])
            pli = (int(pli.split()[1], base=16), 0, pli.split()[7])
            pli = (pli[0], pli[0] - data_mem_start + data_file_start, pli[2])
        payload_buf_info = pbi
        payload_len_info = pli

        print "found payload buffer at"
        print "  mem 0x%x  file 0x%x  symbol %s" % (pbi[0], pbi[1], pbi[2])
        print "found payload length at"
        print "  mem 0x%x  file 0x%x  symbol %s" % (pli[0], pli[1], pli[2])

    if len(gadget_pointers) == 0:
        print >> sys.stderr, "no gadget pointers found"
    else:
        # Get the address, file offset, and type of each gadget pointer.
        if windows:
            gadget_pointers = [(int(g.split()[-2], base=16), 0, g.split()[-1]) for g in gadget_pointers]
            gadget_pointers = [(text_mem_start + soff, text_file_start + soff, name) for (soff, _, name) in gadget_pointers]
        else:
            gadget_pointers = [(int(g.split()[1], base=16), 0, g.split()[7]) for g in gadget_pointers]
            gadget_pointers = [(mem, mem - text_mem_start + text_file_start, name) for (mem, _, name) in gadget_pointers]

    if len(gadget_pointers) > 0:
        print "found %d gadget pointers at" % (len(gadget_pointers))
        for g in gadget_pointers:
            print "  mem 0x%x  file 0x%x  type %s" % (g[0], g[1], g[2])

    if pop_esp_addr is None:
        print >> sys.stderr, "cannot locate pop esp gadget"
        return 1
    else:
        pop_esp_addr_int = int(pop_esp_addr, base=16)
        pop_esp_addr = struct.pack(imm_pack_type, pop_esp_addr_int)

    print "pop esp at  mem 0x%x" % (pop_esp_addr_int)

    f = open(binfile, "r+b")

    if hardcoded_payload: #### Hardcoded payload is easier to handle than a scattered one
        # Copy the payload to the buffer reserved for it
        f.seek(0)
        print "inserting %d payload bytes at 0x%x" % (len(payload), payload_buf_info[1])
        f.seek(payload_buf_info[1])
        f.write(payload)
        payload_len_packed = struct.pack(imm_pack_type, len(payload))
        print "patching payload length at 0x%x to 0x%s" % (payload_len_info[1], binascii.hexlify(payload_len_packed))
        f.seek(payload_len_info[1])
        f.write(payload_len_packed)
    else: #### Scattered payload requires crypted chunks distributed over fake immediates
        # First is the address of the first immediate where payload is stored.
        addend = find_instr_operand_addend(f, immediate_info[0][1])
        if addend < 0:
            print >> sys.stderr, "cannot locate first immediate"
            return 1
        first = struct.pack(imm_pack_type, immediate_info[0][0] + addend)
        f.seek(0)
    
        # Get an RC4 instance for encrypting first and the payload.
        cipher = ARC4.new(RC4_key)
    
        # Encrypt first.
        print "first 0x%s  ->  " % (binascii.hexlify(first)),
        first = cipher.encrypt(first)
        print "RC4(first) 0x%s" % (binascii.hexlify(first))
    
        # Patch each of the immediates in the binary file such that the first
        # half contains a payload chunk and the second half contains an offset to
        # the next immediate. Encrypt each of the patched immediates.
        print "inserting %d payload bytes in %d immediates" % \
              (len(payload), required_immediates)
        imm_idx = 0
        for i in range(0, len(payload), imm_payload_bytes):
            imm = immediate_info[imm_idx]
            imm_idx = imm_idx + 1
    
            chunk = payload[i:i + imm_payload_bytes]
            chunk = struct.unpack(imm_payload_pack_type, chunk)[0]
    
            if i + imm_payload_bytes >= len(payload):
                # End of payload, let the next pointer for this immediate be 0.
                next_off = 0
            else:
                # Use the true next pointer for this immediate.        
                next_off = imm[2]
            
            plaintext = (chunk << imm_offset_bytes*8) | (next_off & imm_offset_mask)
            plaintext = struct.pack(imm_pack_type, plaintext)
    
            ciphertext = cipher.encrypt(plaintext)
    
            print "plaintext 0x%s  ->  ciphertext 0x%s" % \
                  (binascii.hexlify(plaintext), binascii.hexlify(ciphertext))
    
            if not patch_immediate(f, imm[1], ciphertext):
                print >> sys.stderr, "failed to patch immediate"
                print >> sys.stderr, "-> immediate at  mem 0x%x  file 0x%x  next +0x%x" % \
                                     (imm[0], imm[1], imm[2])
                return 1
    
        # Randomize remaining immediates.
        print "randomizing excess immediates"
        while imm_idx < len(immediate_info):
            imm = immediate_info[imm_idx]
            imm_idx = imm_idx + 1
    
            if not patch_immediate(f, imm[1], os.urandom(imm_bytes)):
                print >> sys.stderr, "failed to patch immediate"
                print >> sys.stderr, "-> immediate at  mem 0x%x  file 0x%x  next +0x%x" % \
                                     (imm[0], imm[1], imm[2])
                return 1
    
        # Patch each of the call sites to this payload such that the correct
        # first address ciphertext is set.
        print "patching %d call sites" % (len(call_sites))
        for c in call_sites:
            if not patch_immediate(f, c[1], first):
                print >> sys.stderr, "failed to patch call site"
                print >> sys.stderr, "-> call site at  mem 0x%x  file 0x%x" % (c[0], c[1])
                return 1

    #### Patching the address of the pop esp gadget needs to be done whether
    #### or not we're using a hardcoded payload

    # Patch each of the gadget pointers so that they point to the actual
    # gadget addresses.
    print "patching %d gadget pointers" % (len(gadget_pointers))
    for g in gadget_pointers:
        if g[2] == pop_esp_gadget_pointer_label:
            if not patch_immediate(f, g[1], pop_esp_addr):
                print >> sys.stderr, "failed to patch gadget pointer"
                print >> sys.stderr, "-> gadget pointer at  mem 0x%x  file 0x%x  type %s" % \
                                     (g[0], g[1], g[2])
                return 1
        else:
            print >> sys.stderr, "cannot patch gadget pointer, gadget address unknown"
            print >> sys.stderr, "-> gadget pointer at  mem 0x%x  file 0x%x  type %s" % \
                                 (g[0], g[1], g[2])
            return 1

    f.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())

