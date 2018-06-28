import sys

asm = open(sys.argv[1] + ".s", "rw+")
asm = list(asm)

.cfi_def_cfa_register