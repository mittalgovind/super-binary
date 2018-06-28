#!/bin/python

import r2pipe
import sys

r2 = r2pipe.open(filename=sys.argv[1], flags=['-w'])
r2.syscmd("./vuln")
r2.cmd("s 0x08048456")
r2.cmd("wa call 0x0804840b")
r2.syscmd("./vuln")