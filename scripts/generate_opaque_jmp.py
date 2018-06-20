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
# Generate an opaquely true or false jmp.
#

import sys
import random

# Opaquely true predicates
true_predicates = [
    # (x + x*x) % 2 == 0
    ("\tpush	%eax\n"
     "\tadd	$0x1,%eax\n"
     "\timul	(%esp),%eax\n"
     "\tand	$0x1,%eax\n"
     "\ttest	%eax,%eax\n"
     "\tpop	%eax\n"
     "\tje	")
]

# Opaquely false predicates
false_predicates = [
    # (x + x*x) % 2 != 0
    ("\tpush	%eax\n"
     "\tadd	$0x1,%eax\n"
     "\timul	(%esp),%eax\n"
     "\tand	$0x1,%eax\n"
     "\ttest	%eax,%eax\n"
     "\tpop	%eax\n"
     "\tjne	")
]

def generate_opaquely_true_jmp(target):
    return true_predicates[random.randint(0, len(true_predicates) - 1)] \
               + target + "\n"

def generate_opaquely_false_jmp(target):
    return false_predicates[random.randint(0, len(false_predicates) - 1)] \
               + target + "\n"

def generate_opaque_jmp(target, outcome=True):
    if outcome:
        return generate_opaquely_true_jmp(target)
    else:
        return generate_opaquely_false_jmp(target)

def main():
    if len(sys.argv) < 3:
        print >> sys.stderr, "Usage: %s <target> <true|false>" % (sys.argv[0])
        return 1

    if sys.argv[2] == "true":
        listing = generate_opaquely_true_jmp(sys.argv[1])
    else:
        listing = generate_opaquely_false_jmp(sys.argv[1])
    print listing,

    return 0

if __name__ == "__main__":
    sys.exit(main())

