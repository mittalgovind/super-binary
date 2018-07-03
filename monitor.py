import sys
import time
import pdb
from generate_verification_graph import verG 
import re


def follow(verification_file):
    verification_file.seek(0,2)
    while True:
        line = verification_file.readline()
        if not line:
            continue
        yield line

stack = []
logfile = open("verify_"+sys.argv[1]+".txt","r")
loglines = follow(logfile)
curr_node = ""
next_node = ""
ret_regex = re.compile(r'(ret_[A-Za-z0-9_]+)\n')
jump_regex = re.compile(r'(jump_([A-Za-z0-9_]+)_....)\n')
called_regex = re.compile(r'(call_([A-Za-z0-9_]+)_....)\n')

print "MONITOR RUNNING-------------"
for line in loglines:
    called_match = re.search(called_regex, line)
    jump_match = re.search(jump_regex, line)
    ret_match = re.search(ret_regex, line)
    if 'main' in line[:-1]:
        curr_node = "main"
        stack.append('main')
        print "running correctly"
        continue
    elif called_match:
        stack.append(called_match.group(2))
        if (curr_node, called_match.group(2), called_match.group(1)) in verG.edges(data='label'):
            curr_node = called_match.group(2)
            print "running correctly"
            continue
    elif jump_match:
        # pdb.set_trace()
        if (curr_node, jump_match.group(2), jump_match.group(1)) in verG.edges(data='label'):
            print "running correctly"
            continue
    elif ret_match:
        try:
            stack.pop()
        except:
            print "The stack is empty but still trying to return!!"
        curr_node = stack[-1]
        print "running correctly"
        continue
    print "Control Flow has been HIJACKED!"


# call_main
# call_E_1aeb
# call_T_7015
# call_check_c2d4
# jump_L15_dfe6
# ret_check
# jump_L9_bda2
# call_Tprime_4946
# ret_Tprime
# ret_T
# call_Eprime_8cc6
# ret_Eprime
# ret_E
# ret_main
