import re
import sys

funcs = open("funcs_" + sys.argv[1] + ".txt", "r")
funcprot = open("funcprot_" + sys.argv[1] + ".txt", "r")
funcs = list(funcs)
funcs  = [func.split(' ')[1][:-1] for func in funcs]
funcprot = list(funcprot)

functions = dict((func, 0) for _, func in enumerate(funcs))

funcprot_regex = re.compile(r'^([A-Za-z_0-9]+) \((.*)\)')

for line in funcprot:
	match = re.search(funcprot_regex, line)
	if match:
		if functions.has_key(match.group(1)):
			if len(match.group(2)) == 0:
				functions[match.group(1)] = 0
			else:	
				functions[match.group(1)] = match.group(2).count(',') + 1

proc_func = open("processed_funcs_"+ sys.argv[1] + ".txt", "w")

for func, args in functions.iteritems():
	proc_func.write(func + "\t" + str(args) + "\n")