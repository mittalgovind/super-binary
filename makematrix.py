import re
import sys
import pdb

func_names = open("funcs_"+sys.argv[1]+".txt", "r")
func_names = list(func_names)
func_names  = [func[1:-2] for func in func_names]
no_of_funcs = len(func_names)

cfg = open(sys.argv[1]+".c.011t.cfg",  "r")
cfg = list(cfg)

asm = open(sys.argv[1]+".s", "r")
# asm = open("asm.s", "r")
asm = list(asm)
functions = dict([(i, '') for i in func_names])
func_name = ''

funcname_regex = re.compile(r'<([A-Za-z_0-9]+)>:$')
flag = 0
for instr in asm:
	match = re.search(funcname_regex, instr)
	if match and func_names.__contains__(match.group(1)):
		flag = 1
		currFunc = []
		func_name = match.group(1)
		continue
		
	if flag == 1:
		if instr != '\n':
			currFunc += [instr]
		else :
			functions[func_name] = currFunc
			flag = 0

pdb.set_trace()

# asm = open(sys.argv[1]+".S", "r")
# asm = list(asm)
jump_regex = re.compile(r'                	j[a-z]*    ([a-f0-9]+)')
i = 0

# while i < no_of_funcs:
# 	for instr in asm:
# 		match = re.search(jump_regex, instr)
# 		if match:




# regex = r";; (\d+) succs { ([\d+ ]*) }"
# match = re.search(regex, l[-1])
# n = int(match.group(1)) + 1

# mat = [[0 for i in range(n)] for j in range(n)]
# e = 0
# for line in l:
# 	match = re.search(regex, line)
# 	i = int(match.group(1))
# 	js = match.group(2).split(' ')
# 	for j in js:
# 		if mat[i][int(j)] == 1:
# 			continue
# 		else:
# 			e += 1
# 			mat[i][int(j)] = 1
# out = str(n) + " " +  str(e) + '\n'
# fout.write(out)
# first = True
# for i in range(n):
# 	for j in range(n):
# 		if mat[i][j] == 1:
# 			if first == True:
# 				first = False
# 				for k in range(i):
# 					out = str(k) + " " + str(k+1) + '\n'
# 					fout.write(out) 
# 			out = str(i) + " " + str(j) + '\n'
# 			fout.write(out)

# f.close()
# fout.close()